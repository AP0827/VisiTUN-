import cv2
import dlib
from hashlib import sha256
import numpy as np
from .face_encrypt import save_key

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)

def quantize(feature:float, max_val:float, min_val:float, num_bins:int) -> int:
    bin_size = (max_val - min_val) / num_bins
    bin_index = int((feature - min_val) / bin_size)
    # Clamp to valid bin range
    return max(0, min(bin_index, num_bins - 1))


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

def bin_key(*bins: int, password="1994", filename: str) -> bytes:
    bin_pass_str = '-'.join(str(b) for b in bins) + password
    key = sha256(bin_pass_str.encode()).digest()
    save_key(key=key, filename=filename)
    return key