import cv2
from ui import UserInput

class FrameGen():
    '''Used to process the images accordingly.'''
    
    def __init__(self, frame, mode):
        self.user_input = UserInput(frame, mode)
        
        # List of all available functions and their respective arguments excluding the image
        self.functions = {
            1: None,
            2: {
                'function': self.cvt_BGR,
                'args': {}
                },
            3: {
                'function': self.blur_image,
                'args': {'kernel_size': 10}
                },
            4: {
                'function': self.blur_image,
                'args': {'kernel_size': 100}
                },
            5: {
                'function': self.cvt_grey,
                'args': {}
                },
            6: {
                'function': self.hist_eq,
                'args': {}
                },
            7: {
                'function': self.adaptive_threshold,
                'args': {}
                },
            8: {
                'function': self.smart_blur, 
                'args': {'model': self.user_input.kwargs, 'kernel_size' : 500}
                },
            9: {
                'function': self.top_down, 
                'args': {'model': self.user_input.kwargs, 'mode': 'color'}
                },
            10: {
                'function': self.top_down, 
                'args': {'model': self.user_input.kwargs, 'mode': 'doc'}
                },
            11: {
                'function': self.smart_face_blur, 
                'args': {'model': self.user_input.kwargs}
                }
        }
        
        # Getting the relevant function and arguments
        self.function = self.functions[self.user_input.mode]['function'] if self.user_input.mode > 1 else None
        self.args = self.functions[self.user_input.mode]['args'] if self.user_input.mode > 1 else None
        
    # Main function
    def process(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.function(image) if self.function else image

    # IMAGE PROCESSING FUNCTIONS
    def cvt_BGR(self, image):
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    def blur_image(self, image, kernel_size = None):
        '''args = [kernel_size]'''
        if kernel_size:
            return cv2.blur(image, (kernel_size, kernel_size))
        return cv2.blur(image, (self.args['kernel_size'], self.args['kernel_size']))

    def cvt_grey(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return image

    def hist_eq(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        H, S, V = cv2.split(image)
        V = cv2.equalizeHist(V)
        image = cv2.merge((H,S,V))
        image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
        return image

    def adaptive_threshold(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return image

    def hsv_adaptive_threshold(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        H, S, V = cv2.split(image)
        V = cv2.adaptiveThreshold(V,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        image = cv2.merge((H,S,V))
        image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
        return image

    def smart_blur(self, image):
        '''args = [kwargs, kernel_size]'''
        # pass by reference.
        image.flags.writeable = False
        if not self.args['model']['face_detection'].process(image).detections:
            return self.blur_image(image, self.args['kernel_size'])
        return image

    def smart_face_blur(self, image):
        '''args = [kwargs]'''
        # pass by reference.
        image.flags.writeable = False
        result = self.args['model']['face_detection'].process(image).detections
        image.flags.writeable = True       
        if result:
            try:
                for detection in result:
                    size = detection.location_data.relative_bounding_box
                    x = int(size.xmin * self.args['model']['image_size'][1]) 
                    y = int(size.ymin * self.args['model']['image_size'][0]) 
                    sx = int(size.width * self.args['model']['image_size'][1])
                    sy = int(size.height * self.args['model']['image_size'][0])
                    image[y:y + sy, x:x + sx, :] = self.blur_image(image[y:y + sy, x:x + sx, :], 100)
                return image
            except Exception as e:
                print('exception:')
                print(e)
        return self.blur_image(image, 500)

    def flip_image(self, image, mode):
        if mode == 2:
            image = cv2.flip(image, 0)
            return cv2.flip(image, 1)
        return cv2.flip(image, mode)

    def top_down(self, image):
        '''args = [kwargs, output mode]'''
        
        image.flags.writeable = False
        results = self.args['model']['hand_detection'].process(image)
        image.flags.writeable = True
    
        # Draw the hand annotations on the image and finish calibration
        if results.multi_hand_landmarks and len(self.args['model']['coordinates_state']) < 4:
            for hand_landmarks in results.multi_hand_landmarks:
                self.args['model']['mp_drawing'].draw_landmarks(
                    image,
                    hand_landmarks,
                    self.args['model']['mp_hands'].HAND_CONNECTIONS,
                    self.args['model']['mp_drawing_styles'].get_default_hand_landmarks_style(),
                    self.args['model']['mp_drawing_styles'].get_default_hand_connections_style())
                image = self.args['model']['coordinates_state'].get_coordinates(image, hand_landmarks, self.args['model']['mp_hands'])
            image = self.args['model']['coordinates_state'].draw_circles(image)
            image = self.flip_image(image, 1)
        elif len(self.args['model']['coordinates_state']) == 4:
            pts = self.args['model']['coordinates_state'].get_pts()
            # Apply Perspective Transform Algorithm
            matrix = cv2.getPerspectiveTransform(pts['pts1'], pts['pts2'])
            image = cv2.warpPerspective(image, matrix, (self.args['model']['image_size'][1], self.args['model']['image_size'][0]))
            
            # image = self.flip_image(image, 0)
            image = flip_image(image, 2)
            
            image = self.hsv_adaptive_threshold(image) if self.args['mode'] == 'color' else self.adaptive_threshold(image)
                
        else:
            image = self.flip_image(image, 1)
        
        return image