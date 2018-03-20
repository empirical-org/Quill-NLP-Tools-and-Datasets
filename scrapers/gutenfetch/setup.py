from setuptools import setup

setup(name='gutenfetch',
      version='0.0.2',
      description='Bulk downloads from project gutenberg.',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['gutenfetch'],
      scripts=['bin/gutenfetch'],
      zip_safe=False)
