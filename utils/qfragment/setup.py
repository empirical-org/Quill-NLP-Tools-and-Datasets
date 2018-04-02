from setuptools import setup

setup(name='qfragment',
      version='0.0.15',
      description='Sentence fragment detection and feedback',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qfragment'],
      install_requires=[
          'nltk',
          'numpy',
          'spacy==1.10.1',
          'tensorflow==1.7.0',
          'tflearn==0.3.2'
      ],
      include_package_data=True,
      zip_safe=False)
