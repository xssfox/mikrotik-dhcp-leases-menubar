from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'plist': {
    },
    'packages': [
        'rumps',
        'routeros_api',
        'py2app',
        'pypref',
        'appdirs',
        'pytimeparse',
        'clipboard'
        ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)