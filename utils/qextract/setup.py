from setuptools import setup

setup(name='qextract',
      version='0.0.2',
      description='Extract different types of phrases and clauses from text',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qextract'],
      scripts=['bin/extract_participle_phrases'
      ],
      install_requires=[
          'spacy'
      ],
      include_package_data=True,
      zip_safe=False)
