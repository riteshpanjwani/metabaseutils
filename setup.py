from setuptools import setup


setup(name='metabaseutils',
      version='0.0.1',
      url='https://github.com/riteshpanjwani/metabaseutils',
      author='Ritesh Panjwani',
      author_email='riteshpanjwani@gmail.com',
      license='CC BY-SA',
      packages=['metabaseutils'],
      description='This library can be used to export \'question\' and \'dashboard\' from Metabase',
      long_description='This library can be used to export \'question\' and \'dashboard\' from Metabase',
      zip_safe=False,
      keywords = ['metabase', 'python'],
      install_requires=[line.replace('\n', '') for line in open('requirements.txt').readlines()],
      python_requires='>=3.6',
      )
