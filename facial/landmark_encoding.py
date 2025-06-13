import cv2
import dlib
from hashlib import sha256
import numpy as np
from .face_encrypt import droid_cam_video, save_key

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
droid_cam_url = "http://192.168.198.202:4747/video"

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)


def get_landmarks(filename:str):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        print("❌ No Face detected!")
        return None  # <- Add this line

    shapes = predictor(gray, faces[0])
    landmarks = np.array([[p.x, p.y] for p in shapes.parts()])
    return landmarks

def get_features(landmarks:np.ndarray) -> np.ndarray:
    # EYE DISTANCE
    left_eye = np.mean(landmarks[32:42], axis=0)
    right_eye = np.mean(landmarks[42:48], axis=0)
    eye_dist = np.linalg.norm(left_eye-right_eye)

    # NOSE TO CHIN
    nose = landmarks[30]
    chin = landmarks[8]
    nose_to_chin = np.linalg.norm(nose-chin)

    # FACE WIDTH FOR SCALING
    face_width = np.linalg.norm(landmarks[0]-landmarks[16])

    features=np.array([
        eye_dist/face_width,
        nose_to_chin/face_width
    ])
    return features

def hybrid_key(features:np.ndarray, filename:str, password="1994" ) -> bytes:
    combined = password.encode()+features.tobytes()
    key = sha256(combined).digest()
    save_key(key=key,filename=filename)
    return key

