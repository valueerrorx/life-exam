"""
setup.py for life-exam
"""

__author__ = 'Thomas Michael Weissel'


import sys

try:
    import twisted
except ImportError:
    raise SystemExit("twisted not found.  Make sure you "
                     "have installed the Twisted core package.")

from distutils.core import setup

def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


if __name__ == '__main__':
    
    setup(
        name="life-exam",
        version='1.99',
        description="LiFE Exam Client",
        author=__author__,
        maintainer=__author__,
        license="GPLv3",
        author_email="valueerror@gmail.com",
        url="http://life-edu.eu",
        packages=[
            "config",
            "classes",
            "twisted.plugins",
        ],
        package_data={
            'twisted': ['plugins/examclient_plugin.py'],
        }
        )
    
    refresh_plugin_cache()
