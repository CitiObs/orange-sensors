from setuptools import setup, find_packages
import os

NAME = "Orange3-Sensors"
DOCUMENTATION_NAME = 'Orange Sensors'

VERSION = "0.0.1"

AUTHOR = "Óscar González, Fab Lab Barcelona - IAAC"
URL = 'https://github.com/fablabbcn/orange-sensors'

DESCRIPTION = "Add-on containing Orange Sensors widgets to analyse sensor data"
LONG_DESCRIPTION = open(os.path.join(
    os.path.dirname(__file__), 'README.md')).read()
LICENSE = "GNU General Public License v3"

KEYWORDS = [
    'orange3 add-on',
    'orange',
    'data mining',
    'sensors',
    'Smart Citizen',
    'Sensor Things API'
]

setup(
    name="Orange Sensors",
    version=VERSION,
    author=AUTHOR,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license=LICENSE,
    packages=["orange_sensors"],
    package_data={
        "orange_sensors": ["icons/*"],
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        'Environment :: X11 Applications :: Qt',
        'Environment :: Console',
        'Environment :: Plugins',
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
    ],
    entry_points={
        "orange.widgets": "Sensors = orange_sensors",
        "orange.addons": "Sensors = orange_sensors"
    },
    install_requires=[
        "flat_table >= 1.1.1",
        "pandas >= 1.4.1",
        "pandas != 1.5.1",
        "Orange3 >= 3.31.1",
        "PyQt5",
        # TODO Add secd_staplus_client when it's ready
        "smartcitizen-connector == 1.0.4", #Smart Citizen connector should be fixed at a version
        "nest_asyncio",
        "git+https://github.com/securedimensions/STAplus-Python-Client.git"
    ],
    keywords=KEYWORDS,
    include_package_data=True,
    zip_safe=False,
)
