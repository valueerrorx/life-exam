"""
setup.py for life-exam
Usage: sudo pip3 install .
"""
__author__ = 'Thomas Michael Weissel'

from distutils.core import setup
from version import __version__


def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


if __name__ == '__main__':

    setup(
        name="life-exam",
        version=__version__,
        description="LiFE Exam",
        author=__author__,
        maintainer=__author__,
        license="GPLv3",
        author_email="valueerror@gmail.com",
        url="http://life-edu.eu",
        install_requires=[
            'Twisted>20.0.0',
            'PyYAML',
            'regex',
            'numpy',
            'matplotlib',
            'opencv-python-headless',
            'pathlib',
            'datetime',
            'psutil',
            'pillow',
            'pyqt5',
            'qt5reactor',
            'ConfigObj',
            'argparse'
        ],
        python_requires='>=3.8',
    )

    refresh_plugin_cache()
