import contextlib
import pyvirtualcam
import cv2
from frame_generator import FrameGen
import os
import threading
# from ui import get_camera_index

def main(mode, camera_index):
    t = threading.current_thread()
    
    global continue_run

    # Keep track of current camera used
    cap = cv2.VideoCapture(camera_index)

    success, frame1 = cap.read() # grab initial frame to size matching virtual cam
    if not success:
        print('Camera read unsuccessful')
    
    frame_generator = FrameGen(frame1, mode)

    try:
        with pyvirtualcam.Camera(width=frame1.shape[1], height=frame1.shape[0], fps=20) as cam:
            print(f'Using virtual camera: {cam.device}')
            while cap.isOpened() and getattr(t, 'continue_run', True):
                success, image = cap.read()
                if not success: 
                    break

                # If current camera fails do not do anything
                # with contextlib.suppress(Exception):
                image = frame_generator.process(image)
                cam.send(image)
                cam.sleep_until_next_frame()
                    
    except KeyboardInterrupt:
        print('\nThank You!')
        print('Releasing Camera')
    except Exception as e:
        print(e)

    cap.release()
    
    

# main(2, get_camera_index())