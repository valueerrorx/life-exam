"""
setup.py for life-exam
"""

__author__ = 'Thomas Michael Weissel'


import sys
import setuptools

# removing this app:
# sudo rm -r /usr/local/lib/python3.5/dist-packages/classes /usr/local/lib/python3.5/dist-packages/config /usr/local/lib/python3.5/dist-packages/twisted/plugins/examclient_plugin.py
# sudo rm -r /usr/local/lib/python3.5/dist-packages/life_exam-1.99-py3.5.egg/ 

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
        install_requires=['twisted>=18.4.0'],
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
