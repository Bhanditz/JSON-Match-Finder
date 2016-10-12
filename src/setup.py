from setuptools import setup, find_packages

setup(name='jmf',
	version='0.1.1',
	description='Match listings to unfilled openings.',
	url='',
	author='Drew Nutter',
	author_email='',
	license='GPLv3',
	packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
	zip_safe=False)
