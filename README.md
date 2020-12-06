# metabaseutils
[![PyPI](https://img.shields.io/pypi/v/metabaseutils.svg)](https://pypi.python.org/pypi/metabaseutils) [![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgreen.svg)](https://creativecommons.org/licenses/by-sa/4.0/) [![Join the chat at https://gitter.im/metabaseutils/community](https://badges.gitter.im/metabaseutils/community.svg)](https://gitter.im/metabaseutils/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This library can be used to export 'question' and 'dashboard' from [Metabase](https://www.metabase.com) business intelligence tool.

## Prerequisite
- Python >=3.6
- [Google Chrome](https://www.google.com/intl/en_in/chrome/)
- [Chromium Driver](https://chromedriver.chromium.org/downloads)

## Installation

metabaseutils can be installed using pip (TODO)

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

Initialize MetabaseUtils object

```
import metabaseutils as mu


mb_utils = mu.MetabaseUtils(
    chrome_driver_path='path/to/chromedriver',
    metabase_host='localhost',
    metabase_port=3000,
    metabase_username='metabase_username',
    metabase_password='metabase_password',
    output_dir='path/to/output/directory'
)

```

Example to export data/visualization from a question:

```
question_id=1
mb_utils.export(question_id, visualization_format=mu.PNG)

```

Example to export data/visualization from a question:

```
dashboard_id=1
mb_utils.export(dashboard_id, what=mu.DASHBOARD)

```

## Limitations

TODO

## TODO

TODO

## License
For license information, see [LICENSE.md](LICENSE.md).
