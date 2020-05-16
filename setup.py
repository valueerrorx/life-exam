"""
setup.py for life-exam
Usage: pip3 install .
"""
__author__ = 'Thomas Michael Weissel'


from distutils.core import setup


def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


if __name__ == '__main__':

    setup(
        name="life-exam",
        version='3.2',
        description="LiFE Exam Client",
        author=__author__,
        maintainer=__author__,
        license="GPLv3",
        author_email="valueerror@gmail.com",
        url="http://life-edu.eu",
        install_requires=[
            'Twisted>20.0.0',
            'PyYAML',
            'regex',
        ],
        packages=[
            "config",
            "classes",
            "twisted.plugins",
        ],
        package_data={
            'twisted': ['plugins/examclient_plugin.py'],
        },
        python_requires='>=3.6',
    )

    refresh_plugin_cache()
