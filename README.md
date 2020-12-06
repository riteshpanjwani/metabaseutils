# metabaseutils
[![PyPI](https://img.shields.io/pypi/v/metabaseutils.svg)](https://pypi.python.org/pypi/metabaseutils) [![License: CC BY-SA 4.0](https://licensebuttons.net/l/by-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-sa/4.0/) [![Join the chat at https://gitter.im/metabaseutils/community](https://badges.gitter.im/metabaseutils/community.svg)](https://gitter.im/metabaseutils/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This library can be used to export 'question' and 'dashboard' from Metabase.

## Prerequisite
- Python 3.6+
- [Chromium Driver appropriate for your OS and brower version](https://chromedriver.chromium.org/downloads)

## Installation

metabaseutils can be installed using pip

```
pip install metabaseutils
```

or install it from the source

```
git clone https://github.com/riteshpanjwani/metabaseutils.git
cd metabaseutils
python setup.py install
```

## Usage

This library can be used to export 'question' and 'dashboard' in Metabase business intelligence tool (see https://www.metabase.com). Following is the example to export data/visualization from a question. Function to export dashboard is still under TODO.

```
import metabaseutils as mu


mb_utils = mu.MetabaseUtils(
    chrome_driver_path='path\\to\\chromedriver.exe',
    metabase_host='localhost',
    metabase_port=3000,
    metabase_username='metabase_username',
    metabase_password='metabase_password',
    output_dir='path\\to\\output\\directory'
)
mb_utils.export_question(1, data_format=mu.CSV, visualization_format=mu.JPG)

```

For license information, see [LICENSE.md](LICENSE.md).
