import cv2

def get_camera_count():
    camera_detected = 0
    while True:
        cap = cv2.VideoCapture(camera_detected)
        if not cap.isOpened():
            break
        camera_detected += 1
        cap.release()
    return camera_detected


if __name__ == '__main__':
    get_camera_count()