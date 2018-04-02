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
          'spacy==2.0.10',
          'tensorflow==1.5.1',
          'tflearn'
      ],
      include_package_data=True,
      zip_safe=False)
