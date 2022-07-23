from setuptools import setup
import os

APP = ['status_bar_app.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': os.path.abspath('./media/webcam-round.icns'),
    'plist': {
        'LSUIElement': True,
    },
}

setup(
    name='SmartCam',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    
)
