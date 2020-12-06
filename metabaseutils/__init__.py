import os
import io
from pathlib import Path
from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


__version__ = "0.0.1"


CSV, JSON, XLSX, PNG, JPG, PDF = 'csv', 'json', 'xlsx', 'png', 'jpg', 'pdf'
QUESTION, DASHBOARD = 'question', 'dashboard'


class MetabaseUtilsError(Exception):
    """ An exception class for MetabaseUtils-related errors. """

class MetabaseWebDriver:
    def __init__(self, chrome_driver_path, metabase_url, metabase_username, metabase_password, output_dir):
        self.metabase_url = metabase_url
        self.output_dir = output_dir

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
        self.wait = WebDriverWait(self.driver, 60)
        self.driver.get(self.metabase_url)

        user_id_elem = self.driver.find_element(By.NAME, "username")
        user_id_elem.clear()
        user_id_elem.send_keys(metabase_username)

        password_elem = self.driver.find_element(By.NAME, "password")
        password_elem.clear()
        password_elem.send_keys(metabase_password)

        self.driver.find_element(By.CSS_SELECTOR, ".Button").click()
        
        self.wait.until(EC.url_changes(self.driver.current_url))
    
    def _get_visualization(self, id, visualization_format, class_name, page_name):
        self.driver.get(f"{self.metabase_url}/{page_name}/{id}")
        card = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, class_name)))
        location = card.location
        size = card.size
        screen = self.driver.get_screenshot_as_png()

        x = location['x']
        y = location['y']
        width = location['x']+size['width']
        height = location['y']+size['height']
        im = Image.open(io.BytesIO(screen))
        im = im.crop((int(x), int(y), int(width), int(height)))
        im = im.convert('RGB')
        fpath = self.output_dir / f'{page_name}_{id}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.{visualization_format}'
        im.save(fpath, quality=100)
        return str(fpath)

    
class MetabaseUtils:
    """
    This class is used to export 'question' and 'dashboard' in Metabase business intelligence tool (see https://www.metabase.com)
    ...

    Attributes
    ----------
    chrome_driver_path : str
        The absolute file path the Chrome driver
    metabase_host : str
        The host IP address or host name where Metabase service is running
    metabase_port : int
        The port number where Metabase service is running on
    metabase_username : str
        The username used to login into Metabase
    metabase_password: str
        The password used to login into Metabase
    output_dir: str, optional
        The output directory for the downloaded files, default is current working directory
    Methods
    -------
    export(id, what, output_dir, with_data=True, with_visualization=True, data_format=XLSX,
        visualization_format=PDF, package_as_zip=True, single_pdf=False)
        Optionally packages and exports the specified question by its id into a zip file or separate data and visualization files
    """
    def __init__(self, chrome_driver_path, metabase_host, metabase_port, metabase_username, metabase_password, output_dir=None):
        self.metabase_username = metabase_username
        self.metabase_password = metabase_password
        self.output_dir = Path(os.getcwd()) if output_dir is None else Path(output_dir)
        self.metabase_url = f"http://{metabase_host}:{metabase_port}"

        self._metabase_session_id = self._get_metabase_api_session_id()

        self._mb_web_driver = MetabaseWebDriver(
            Path(chrome_driver_path),
            self.metabase_url,
            metabase_username,
            metabase_password,
            self.output_dir
        )

    
    def _get_metabase_api_session_id(self):
        response = requests.post(
            f'{self.metabase_url}/api/session',
            json={'username': self.metabase_username, 'password': self.metabase_password}
        )
        response_dict = response.json()
        if 'id' not in response_dict:
            raise MetabaseUtilsError('Invalid Metabase credentials.')
        return response_dict['id']
    
    def _get_data(self, id, data_format):
        with requests.post(
            f"{self.metabase_url}/api/card/{id}/query/{data_format}",
            headers={'X-Metabase-Session': self._metabase_session_id, 'Content-Type': 'application/json'},
            stream=True
        ) as response:
            response.raise_for_status()
            fname = f'query_result_{id}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.{data_format}'
            data_fpath = self.output_dir / fname
            with open(data_fpath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return str(data_fpath)
    
    def _get_question_id_list(self, dashboard_id):
        question_id_list = []
        with requests.get(
            f"{self.metabase_url}/api/{DASHBOARD}/{dashboard_id}",
            headers={'X-Metabase-Session': self._metabase_session_id, 'Content-Type': 'application/json'},
        ) as response:
            response_dict = response.json()
            for card_dict in response_dict['ordered_cards']:
                if 'name' not in card_dict['card'] or 'id' not in card_dict['card']:
                    continue
                else:
                    question_id_list.append((card_dict['card']['id'], card_dict['card']['name']))
        return question_id_list, {'name': response_dict['name'], 'description': response_dict['description']}
    
    def export(self,
                id,
                what=QUESTION,
                with_data=True,
                with_visualization=True,
                data_format=XLSX,
                visualization_format=PDF,
                keep_individual_visualization=False,
                keep_individual_data=False,
                output_dir=None):
        """Export question/dashboard data from Metabase in csv|xlsx|json format
        along with its visualization in jpg|png|pdf format given the question ID.

        Parameters
        ----------
        id : int
            The ID of the question in Metabase
        with_data : boolean, optional
            Whether or not to include the data in one of the csv|xlsx|json formats
        with_visualization: boolean, optional
            Whether or not to include the visualization in one of the jpg|png|pdf formats
        data_format : str, optional
            Format in which the data must be returned, default is xlsx. Valid formats: csv|xlsx|json
        visualization_format : str, optional
            Format in which the visualization must be returned, default is pdf. Valid formats: jpg|png|pdf
        keep_individual_visualization : boolean, optional
            Whether or not to keep individual visualizations extracted from the dashboard
            when 'what' is set to dashboard
        keep_individual_data : boolean, optional
            Whether or not to keep individual data files extracted from the dashboard
            when 'what' is set to dashboard
        output_dir : str, optional
            Output directory in which the data and/or visualization must be stored,
            default is current working directory or the one specified while creating MetabaseUtils object

        Raises
        ------
        MetabaseUtilsError
            If data_format other than csv|xlsx|json is passed (case sensitive),
            if visualization_format other than jpg|png|pdf is passed (case sensitive)
        """
        
        if output_dir is not None:
            self.output_dir = output_dir
        
        if what not in [QUESTION, DASHBOARD]:
            raise MetabaseUtilsError('Invalid option for Metabase entity. Supported: question|dashboard')

        if with_data or with_visualization:
            question_id_list, dashboard_info_dict = self._get_question_id_list(id)
        else:
            return
        
        if with_data:
            if data_format not in [CSV, XLSX, JSON]:
                raise MetabaseUtilsError('Invalid data format. Supported: csv|xlsx|json')
            if what == DASHBOARD:
                data_fpath_list = []
                for question_id, _ in question_id_list:
                    data_fpath = self._get_data(question_id, data_format)
                    data_fpath_list.append(data_fpath)
                if not keep_individual_data and data_format==XLSX:
                    pass
            else:
                self._get_data(id, data_format)
        
        if with_visualization:
            if visualization_format not in [PNG, JPG, PDF] and what == QUESTION:
                raise MetabaseUtilsError('Invalid visualization format. Supported: png|jpg|pdf when \'what\' is set to \'question\'')
            if visualization_format not in [PNG, JPG] and what == DASHBOARD:
                raise MetabaseUtilsError('Invalid visualization format. Supported: png|jpg when \'what\' is set to \'dashboard\'')
            class_name = '.CardVisualization'
            
            if what == DASHBOARD:
                fnt = ImageFont.truetype("arial.ttf", 20)
                fnt2 = ImageFont.truetype("arial.ttf", 40)
                img_list, img_fpath_list = [], []
                for idx, (question_id, title) in enumerate(question_id_list):
                    fpath = self._mb_web_driver._get_visualization(question_id, visualization_format, class_name, QUESTION)
                    img_fpath_list.append(fpath)
                    im = Image.open(fpath)
                    width, height = im.size
                    dy = 50
                    if idx == 0:
                        landing = Image.new("RGB", (width, height+dy), (255,255,255,255))
                        draw = ImageDraw.Draw(landing)
                        msg = f"{dashboard_info_dict['name']}\n{dashboard_info_dict['description']}"
                        w, h = draw.textsize(msg, font=fnt2)
                        draw.text(((width-w)/2,(height+dy-h)/2), msg, font=fnt2, fill="black")
                        img_list.append(landing)
                    background = Image.new('RGB', (width, height+dy), (255,255,255,255))
                    draw = ImageDraw.Draw(background)
                    draw.text((10,10), title, font=fnt, fill=(0,0,0))
                    background.paste(im, (0,40))
                    img_list.append(background)
                self._mb_web_driver.driver.quit()
                if img_list:
                    pdf_fpath = self.output_dir / f'{DASHBOARD}_{id}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.{PDF}'
                    img_list[0].save(pdf_fpath, PDF.upper() ,resolution=100.0, save_all=True, append_images=img_list[1:], quality=100)
                if img_fpath_list and not keep_individual_visualization:
                    for img_fpath in img_fpath_list:
                        os.remove(img_fpath)
            else:
                self._mb_web_driver._get_visualization(id, visualization_format, class_name, what)
