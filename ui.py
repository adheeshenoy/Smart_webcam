import mediapipe as mp
import cv2
import numpy as np
import contextlib
import pyvirtualcam

# UI functions


def get_camera_index():
    camera_index = 0
    total_cameras = get_camera_count()
    
    cap = cv2.VideoCapture(camera_index)
    print(help(cap))
    success, frame1 = cap.read()
    if not success:
        return False, None
    
    with pyvirtualcam.Camera(width=frame1.shape[1], height=frame1.shape[0], fps=20) as cam:
        i = 0
        while i < 50:
            
            success, frame1 = cap.read()
            if not success:
                camera_index += 1
                
                if camera_index > total_cameras:
                    return False, None
                
                cap = cv2.VideoCapture(camera_index)
                print(cap.getBackendName())
                i = 0
                success, frame1 = cap.read()
                
            cam.send(frame1)
            cam.sleep_until_next_frame()
            i+=1
        return True, camera_index
    
# print(get_camera_index())

# UI Classes
class CoordinatesState():
    '''
    Performs calibration for the top down video
    '''
    def __init__(self, coords = [], image_size = None):  # sourcery skip: default-mutable-arg
        self.coords = coords
        self.temp = None
        self.steps = 0
        self.pts = None
        self.image_size = image_size
        
    def set_image_size(self, image_size):
        self.image_size = image_size
    
    def _order_coords(self):
        '''get correct order of coordinates'''
        sums = np.sum(self.coords, axis = 1)
        tl = self.coords[np.argmin(sums)]
        br = self.coords[np.argmax(sums)]
        
        diff = np.diff(self.coords, axis = 1)
        tr = self.coords[np.argmin(diff)]
        bl = self.coords[np.argmax(diff)]
        return np.array([tl, tr, bl, br])
    
    def draw_circles(self, image, radius = 20, color = (255, 255, 255), thickness = -1):
        for coord in self.coords:
            image = cv2.circle(image, coord, radius, color, thickness)
        return image
    
    def __len__(self):
        return len(self.coords)
    
    def _write_image(self, image, text, org, thickness = 2, fontScale = 1, font = cv2.FONT_HERSHEY_SIMPLEX, color = (255, 0, 0)):
        return cv2.putText(image, text, org, font, 
                        fontScale, color, thickness, cv2.LINE_AA)
    
    def get_pts(self):
        if self.pts:
            return self.pts
        self.coords = self._order_coords()
        pts1 = np.float32(self.coords)
        pts2 = np.float32([[0, 0], [self.image_size[1], 0], [0, self.image_size[0]], [self.image_size[1], self.image_size[0]]])
        return {'pts1': pts1, 'pts2': pts2}

    def get_coordinates(self, image, hand_landmarks, mp_hands, threshold = 10, max_steps = 20):
        if self.temp:
            x = round(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * self.image_size[1],3)
            y = round(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * self.image_size[0], 3)
            diff_x = abs(self.temp[0]- x) < threshold
            diff_y = abs(self.temp[1] - y) < threshold
            s = max_steps - self.steps
            image = self._write_image(image, f'Hold still for {s} more frames.', (50, 100))
                            
            if diff_x and diff_y:
                self.steps += 1
            else:
                self.temp = (x, y)
                self.steps = 0
                
            if self.steps > max_steps:
                x, y = int(x), int(y)
                self.coords.append((x, y))
                image = self._write_image(image, f'Coordinate ({x}, {y}) selected', (50, 200))
                self.temp = None
                self.steps = 0
        else:
            self.temp = [round(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * self.image_size[1],3), round(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * self.image_size[0], 3)]
        return image


class UserInput():
    def __init__(self, frame, mode):
        self.frame = frame
        # self.mode = self.get_mode()
        self.mode = mode
        self.kwargs = self.get_kwargs()

    # def get_mode(self):
    #     while True:
    #         try:
    #             mode = int(input('''What mode do you want to run:
    #             1. Normal
    #             2. BGR
    #             3. Blur
    #             4. Extreme Blur
    #             5. GrayScale
    #             6. Hist equalization
    #             7. Adaptive Thresholding
    #             8. Smart Blur
    #             9. Top-down camera (COLOR)
    #             10. Top-down camera (DOCUMENT)
    #             11. Smart Face Blur
    #             option: '''))
    #             if mode > 0 and mode < 12:
    #                 return mode
    #             raise Exception('Incorrect Input')
    #         except Exception:
    #             print('Please choose one of the options from the list.')
    #             continue
        
    def get_kwargs(self):
        kwargs = {}

        if self.mode == 8:
            kwargs['face_detection'] = mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        elif self.mode in [9, 10]:
            kwargs['mp_hands'] = mp.solutions.hands
            kwargs['hand_detection'] = kwargs['mp_hands'].Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
            kwargs['coordinates_state'] = CoordinatesState(image_size=self.frame.shape)
            kwargs['mp_drawing'] = mp.solutions.drawing_utils
            kwargs['mp_drawing_styles'] = mp.solutions.drawing_styles
            kwargs['image_size'] = self.frame.shape
        elif self.mode == 11:
            kwargs['face_detection'] = mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
            kwargs['image_size'] = self.frame.shape
        return kwargs

