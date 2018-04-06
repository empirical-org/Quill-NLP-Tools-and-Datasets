from setuptools import setup

setup(name='qfragment',
      version='0.0.22',
      description='Sentence fragment detection and feedback',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qfragment'],
      install_requires=[
          'en_core_web_lg==2.0.0',
          'nltk',
          'numpy',
          'spacy==2.0.10',
          'tensorflow==1.5.1',
          'tflearn',
      ],
      dependency_links = [
          'https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.0.0/en_core_web_lg-2.0.0.tar.gz#egg=en_core_web_lg==2.0.0'
      ],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
