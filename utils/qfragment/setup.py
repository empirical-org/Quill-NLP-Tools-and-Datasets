from setuptools import setup

setup(name='qfragment',
      version='0.0.26',
      description='Sentence fragment detection and feedback',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qfragment'],
      install_requires=[
        'Flask==0.12.2',
        'SQLAlchemy==1.2.6',
        'en_core_web_lg==2.0.0',
        'nltk==3.2.5',
        'numpy==1.14.2',
        'pandas==0.19.2',
        'pathlib==1.0.1',
        'psycopg2==2.7.3.2',
        'requests==2.18.4',
        'spacy==2.0.10',
        'spacy==2.0.10',
        'tensorflow==2.7.2',
        'tensorflow==2.7.2',
        'textacy==0.6.1',
        'tflearn',
        'tflearn==0.3.2',
        'thinc==6.10.2',
      ],
      dependency_links = [
        'https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.0.0/en_core_web_lg-2.0.0.tar.gz#egg=en_core_web_lg==2.0.0'
      ],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
