# metabaseutils
[![PyPI](https://img.shields.io/pypi/v/metabaseutils.svg)](https://pypi.python.org/pypi/metabaseutils)

This library can be used to export 'question' and 'dashboard' from [Metabase](https://www.metabase.com) business intelligence tool.

## Prerequisite
- Python 3.6+
- [Chromium Driver appropriate for your OS and brower version](https://chromedriver.chromium.org/downloads)

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

This library can be used to export 'question' and 'dashboard' in [Metabase](https://www.metabase.com) business intelligence tool.

Initialize MetabaseUtils object

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
