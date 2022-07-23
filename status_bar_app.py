import rumps
from main import main
from threading import Thread
# from ui import get_camera_index, get_camera_count
import pkg_resources.py2_warn
import time
import os

class SmartCam(rumps.App):
    def __init__(self):
        super(SmartCam, self).__init__("Smart Cam", icon = 'webcam-round.icns')
        self.menu = [
        'No Filter',
        'Smart Blur',
        'Smart Face Blur',
        'Top-Down Camera (COLOR)',
        'Top-Down Camera (DOCUMENT)',
        'Sketch Filter',
        'High Contrast',
        'GreyScale',
        'Blur',
        'Extreme Blur',
        'RGB2BGR',
        'Switch Mode',
        'Quit'
        ]
        
        self.callback_mapping = {
            'No Filter':self.rgb,
            'Smart Blur': self.smart_blur,
            'Smart Face Blur': self.smart_face_blur,
            'Top-Down Camera (COLOR)': self.top_down_color,
            'Top-Down Camera (DOCUMENT)': self.top_down_doc,
            'Sketch Filter': self.sketch_filter,
            'High Contrast': self.high_contrast,
            'GreyScale': self.greyscale,
            'Blur': self.blur,
            'Extreme Blur': self.extreme_blur,
            'RGB2BGR': self.rgb2bgr,
            'Switch Mode': self.switch,
            'Quit': self.clean_up_and_quit
        }
        
        
        self.mode_mapping = {
            'No Filter': 1,
            'Smart Blur': 8,
            'Smart Face Blur': 11,
            'Top-Down Camera (COLOR)': 9,
            'Top-Down Camera (DOCUMENT)': 10,
            'Sketch Filter': 7,
            'High Contrast': 6,
            'GreyScale': 5,
            'Blur': 3,
            'Extreme Blur': 4,
            'RGB2BGR': 2,
        }
        
        self.quit_button = None
        self.filter_thread = None
        
        self.camera_index = 1
        # self.max_camera = get_camera_count()
        
        # self.configured = False

    def turn_off_buttons(self):
        for k, menuItem in self.menu.items():
            if k not in ['Quit', 'Switch Mode']:
                menuItem.set_callback(None)
                
    # @rumps.clicked('Configure Camera')
    # def configure(self, _):
    #     try:
    #         self.configured, self.camera_index = get_camera_index()
    #         if not success:
    #             rumps.notification('Camera Failure!', 'Could not find virtual camera.')         
    #         else:
    #             rumps.notification('Camera Found!')
    #         print(self.configured, self.camera_index)
    #     except:
    #         rumps.notification('Failure!')
            
        # self.menu['Configure Camera'].set_callback(None)
            
    
    @rumps.clicked('No Filter')
    def rgb(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['No Filter'], self.camera_index])
        self.filter_thread.start()

    @rumps.clicked('Smart Blur')
    def smart_blur(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Smart Blur'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('Smart Face Blur')
    def smart_face_blur(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Smart Face Blur'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('Top-Down Camera (COLOR)')
    def top_down_color(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Top-Down Camera (COLOR)'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('Top-Down Camera (DOCUMENT)')
    def top_down_doc(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Top-Down Camera (DOCUMENT)'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('Sketch Filter')
    def sketch_filter(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Sketch Filter'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('High Contrast')
    def high_contrast(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['High Contrast'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('GreyScale')
    def greyscale(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['GreyScale'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('Blur')
    def blur(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Blur'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('Extreme Blur')
    def extreme_blur(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['Extreme Blur'], self.camera_index])
        self.filter_thread.start()
        
    @rumps.clicked('RGB2BGR')
    def rgb2bgr(self, _):
        self.turn_off_buttons()
        self.filter_thread = Thread(target = main, args = [self.mode_mapping['RGB2BGR'], self.camera_index])
        self.filter_thread.start()

    @rumps.clicked('Switch Mode')
    def switch(self, _):
        if self.filter_thread:
            self.filter_thread.continue_run = False
            self.filter_thread.join()
            self.filter_thread = None
            for k, menu_item in self.menu.items():
                if k not in ['Quit', 'Switch Mode']:
                    menu_item.set_callback(self.callback_mapping[k])
        else:
            rumps.notification("Select a mode!", "", "It seems as if you have not selected a mode")
    
    @rumps.clicked('Quit')
    def clean_up_and_quit(self, _):
        if self.filter_thread:
            self.filter_thread.continue_run = False
            self.filter_thread.join()
        rumps.quit_application()
    

if __name__ == "__main__":
    SmartCam().run()

