from setuptools import setup

setup(name='qmangle',
      version='0.0.0',
      description='Generate problematic sentences from correct sentences',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qmangle'],
      scripts=['bin/mangle',
      ],
      install_requires=[
          'spacy',
          'Pattern==2.6'
      ],
      include_package_data=True,
      zip_safe=False)
