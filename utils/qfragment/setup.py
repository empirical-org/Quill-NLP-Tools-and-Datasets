from setuptools import setup

setup(name='qfragment',
      version='0.0.6',
      description='Sentence fragment detection and feedback',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qfragment'],
      scripts=['bin/qfragment'],
      install_requires=[
          'nltk',
          'numpy',
          'spacy',
          'tensorflow',
          'tflearn'
      ],
      include_package_data=True,
      zip_safe=False)
