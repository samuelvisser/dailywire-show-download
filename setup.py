"""
Setup script for DailyWire Downloader.
"""

from setuptools import setup, find_packages

# Read version from package
with open('dailywire_downloader/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

# Read long description from README
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='dailywire-downloader',
    version=version,
    description='A Python package for downloading DailyWire shows',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='DailyWire Downloader Team',
    author_email='example@example.com',
    url='https://github.com/example/dailywire-downloader',
    packages=find_packages(),
    install_requires=[
        'pyyaml>=6.0',
    ],
    python_requires='>=3.13',
    entry_points={
        'console_scripts': [
            'dailywire-downloader=dailywire_downloader.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
        'Topic :: Multimedia :: Video',
    ],
)