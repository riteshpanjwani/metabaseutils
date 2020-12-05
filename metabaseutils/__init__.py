import os
from pathlib import Path
from datetime import datetime

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


__version__ = "0.0.1"


CSV='csv'
JSON='json'
XLSX='xlsx'
PNG='png'
JPG='jpg'
PDF='pdf'


class MetabaseUtilsError(Exception):
    """ An exception class for IndoWordNet-related errors. """


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
    export_question(id, output_dir, with_data=True, with_visualization=True, data_format=XLSX,
        visualization_format=PDF, package_as_zip=True, single_pdf=False)
        Optionally packages and exports the specified question by its id into a zip file or separate data and visualization files
    export_dashboard()
        TODO
    """
    def __init__(self, chrome_driver_path, metabase_host, metabase_port, metabase_username, metabase_password, output_dir=None):
        self.chrome_driver_path = Path(chrome_driver_path)
        self.metabase_host = metabase_host
        self.metabase_port = metabase_port
        self.metabase_username = metabase_username
        self.metabase_password = metabase_password
        self.output_dir = Path(os.getcwd()) if output_dir is None else Path(output_dir)
        
        self._metabase_url = f"http://{metabase_host}:{metabase_port}"
        self._metabase_session_id = self._get_metabase_api_session_id()
    
    def _get_metabase_api_session_id(self):
        response = requests.post(
            f'{self._metabase_url}/api/session',
            json={'username': self.metabase_username, 'password': self.metabase_password}
        )
        response_dict = response.json()
        if 'id' not in response_dict:
            raise MetabaseUtilsError('Invalid Metabase credentials.')
        return response_dict['id']
    
    def _get_data(self, id, data_format):
        with requests.post(
            f"{self._metabase_url}/api/card/{id}/query/{data_format}",
            headers={'X-Metabase-Session': self._metabase_session_id, 'Content-Type': 'application/json'},
            stream=True
        ) as response:
            response.raise_for_status()
            fname = f'query_result_{id}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.{data_format}'
            with open(self.output_dir / fname, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    def _get_visualization(self, id, visualization_format):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(self.chrome_driver_path, chrome_options=options)
        wait = WebDriverWait(driver, 10)
        driver.get(self._metabase_url)

        user_id_elem = driver.find_element(By.NAME, "username")
        user_id_elem.clear()
        user_id_elem.send_keys(self.metabase_username)

        password_elem = driver.find_element(By.NAME, "password")
        password_elem.clear()
        password_elem.send_keys(self.metabase_password)

        driver.find_element(By.CSS_SELECTOR, ".Button").click()
        
        wait.until(EC.url_changes(driver.current_url))

        driver.get(f"{self._metabase_url}/question/{id}")

        card = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".CardVisualization")))

        location = card.location
        size = card.size
        temp_fname = self.output_dir / f'img_{id}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.png'
        driver.save_screenshot(str(temp_fname))
        x = location['x']
        y = location['y']
        width = location['x']+size['width']
        height = location['y']+size['height']
        im = Image.open(temp_fname)
        im = im.crop((int(x), int(y), int(width), int(height)))
        im = im.convert('RGB')
        im.save(self.output_dir / f'graph_{id}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.{visualization_format}')

        os.remove(temp_fname)

        driver.close()
    
    def _package_files(self):
        pass
    
    def export_question(self,
                        id,
                        with_data=True,
                        with_visualization=True,
                        data_format=XLSX,
                        visualization_format=PDF,
                        output_dir=None):
        """Export question data from Metabase in csv|xlsx|json format
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
        
        if with_data:
            if data_format not in [CSV, XLSX, JSON]:
                raise MetabaseUtilsError('Invalid data format. Supported: csv|xlsx|json')
            self._get_data(id, data_format)
        
        if with_visualization:
            if visualization_format not in [PNG, JPG, PDF]:
                raise MetabaseUtilsError('Invalid visualization format. Supported: png|jpg|pdf')
            self._get_visualization(id, visualization_format)
    
    def export_dashboard(self, id, output_dir=None):
        """TODO

        Parameters
        ----------
        TODO

        Raises
        ------
        NotImplementedError
            TODO. Coming soon.
        """
        raise NotImplementedError('TODO. Coming soon.')
