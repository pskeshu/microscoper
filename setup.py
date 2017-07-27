from setuptools import setup

setup(name='microscoper',
      version='0.2.3',
      description=' A simple wrapper for python-bioformats to convert .vsi CellSense format to TIFF.',
      url='https://www.github.com/pskeshu/microscoper',
      author='Kesavan Subburam',
      author_email='pskesavan@tifrh.res.in',
      packages=['microscoper'],
      install_requires=['numpy>=1.13.1',
                        'tifffile>=0.12.1',
                        'tqdm>=4.11.2',
                        'python-bioformats>=1.1.0'],
      license='MIT',
      zip_safe=False)
