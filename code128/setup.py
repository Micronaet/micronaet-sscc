
from setuptools import setup, find_packages 
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_descr = f.read()

setup(
    name        = "code128",
    version     = "0.2",
    description = "Create code128 barcodes",
    long_description = long_descr,
    url         = "https://bitbucket.org/01100101/code128",
    author      = "Felix Knopf",
    author_email = "felix.knopf@arcor.de",
    license     = "LGPLv2+",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: "
            "GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
    keywords    = "barcode code128",
    packages=find_packages(exclude=[]),
    #install_requires = []
    extras_require = { "PIL" : ["Pillow>=2.7.0"] },
    entry_points={
        "console_scripts": [
            "code128 = code128.tool:main",
        ]
    }
)

