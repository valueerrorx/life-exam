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
            'opencv-python',
            'pathlib',
            'datetime'
        ],
        python_requires='>=3.8',
    )

    refresh_plugin_cache()
