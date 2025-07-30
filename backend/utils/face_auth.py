# save_key(key: bytes, filename='face_key.bin')
# load_key(filename='face_key.bin') -> bytes
# cam_video(filename="captured_image.jpg")
# quantize(feature:float, max_val:float, min_val:float, num_bins:int) -> int
# get_landmarks(filename:str)
# get_features(landmarks:np.ndarray) -> np.ndarray
# bin_key(*bins: int, password, filename: str) -> bytes
# hybrid_key(features:np.ndarray, filename:str, password="1994")


import numpy as np
import cv2
import os 
import time
import cv2
import dlib
from hashlib import sha256
import os
import numpy as np
from threading import Lock, Thread
from flask_socketio import SocketIO
import getpass

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
KEY_FILE = 'face_key.bin'
img_filename = 'live_captured_face.jpg'
key_filename = 'live_key.bin'


# SAVE AND LOAD KEY
def save_key(key: bytes, filename='face_key.bin'):
    try:
        with open(filename, 'wb') as f:
            f.write(key)
        print(f"✅ File saved at {filename} !")
    except Exception as e:
        print(f"❌ Error saving the key : {e}")

def load_key(filename='face_key.bin') -> bytes:
    # Load the cryptographic key from file
    try:
        with open(filename, 'rb') as f: 
            return f.read()
    except FileNotFoundError:
        print(f"❌ Key file '{filename}' not found")
        return None
    except Exception as e:
        print(f"❌ Error loading key: {e}")
        return None
    
# CAMERA
def cam_video(filename="captured_image.jpg"):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
    cap.release()
    return filename

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
    if len(faces) != 1:
        return None  # <- Add this line

    shapes = predictor(gray, faces[0])
    landmarks = np.array([[p.x, p.y] for p in shapes.parts()])
    return landmarks

def get_features(landmarks:np.ndarray) -> np.ndarray:
    # EYE DISTANCE
    left_eye = landmarks[39]
    right_eye = landmarks[42]
    eye_dist = np.linalg.norm(left_eye-right_eye)

    # NOSE LENGTH
    nose_ridge = landmarks[27]
    nose_bottom = landmarks[33]
    nose_len = np.linalg.norm(nose_ridge-nose_bottom)

    # NOSE WIDTH
    nose_wid = np.linalg.norm(landmarks[31] - landmarks[35])

    #LEFT TO CHIN & RIGHT TO CHIN
    L2Chin = np.linalg.norm(landmarks[0] - landmarks[8])
    R2Chin = np.linalg.norm(landmarks[16] - landmarks[8])

    V_shape = L2Chin+R2Chin

    # FACE WIDTH FOR SCALING
    face_width = np.linalg.norm(landmarks[0]-landmarks[16])

    features=np.array([
        eye_dist/face_width,
        nose_len/face_width,
        nose_wid/face_width,
        V_shape/face_width

    ])
    return features

def bin_key(*bins: int, password, filename: str) -> bytes:
    bin_pass_str = '-'.join(str(b) for b in bins) + password
    key = sha256(bin_pass_str.encode()).digest()
    save_key(key=key, filename=filename)
    return key

def hybrid_key(features:np.ndarray, filename:str, password="1994") -> bytes:
    combined = password.encode()+features.tobytes()
    key = sha256(combined).digest()
    save_key(key=key,filename=filename)
    return key

auth_lock = Lock()
shared_state = {
    "aes_key": None,
    "authenticated": False,
    "terminate": False
}
socketio = None

def authenticate_face(shared_state, password, user_id, interval=5.0):
    while not shared_state["terminate"]:
        time.sleep(interval)

        cam_video(img_filename)
        landmarks = get_landmarks(img_filename)

        if landmarks is None:
            print("❌ Either No face or Multiple people. GET OUT OR GET BACK HERE.")
            continue

        try:
            features = get_features(landmarks=landmarks)

            eye_bin = quantize(features[0], min_val=0.30, max_val=0.52, num_bins=5)
            nose_len_bin = quantize(features[1], min_val=0.45, max_val=0.70, num_bins=5)
            nose_wid_bin = quantize(features[2], min_val=0.25, max_val=0.45, num_bins=5)
            v_shape_bin = quantize(features[3], min_val=1.5, max_val=2.3, num_bins=5)

            _ = bin_key(eye_bin, nose_len_bin, nose_wid_bin, v_shape_bin, password=password, filename=key_filename)
            new_key = load_key(key_filename)
            with auth_lock:
                shared_state["aes_key"] = new_key
                shared_state["authenticated"] = True
            socketio.emit("auth_status", {"user_id":user_id, "authenticated":True},room=user_id)


        except Exception as e:
            print(f"[Auth Error] {e}")
            with auth_lock:
                shared_state["authenticated"] = False
            socketio.emit("auth_status", {"user_id":user_id, "authenticated":False}, room=user_id)
    print(f"🛑 Stopped auth thread for {user_id}")
    socketio.emit("auth_terminated", {"user_id": user_id}, room=user_id)


def continuous_reauth():
    print("📷 Adjust your camera, then press 'q' to capture.")
    cam_video(img_filename)

    password = getpass("🔑 Enter your AES password: ")
    print("🔁 Starting background face authentication...")

    auth_thread = Thread(target=authenticate_face, args=(shared_state, password), daemon=True)
    auth_thread.start()

    input("[⏳] Press Enter when ready to start packet reception...")

    try:
        while True:
            with auth_lock:
                if not shared_state["authenticated"]:
                    print("[🔒] Skipping packet — not authenticated.")
                    continue
                current_key = shared_state["aes_key"]

            decrypted_data = decrypt(ciphertext, nonce, current_key)
            if not decrypted_data:
                print("[❌] Packet decryption failed.")
                continue

            payload = extract_payload(decrypted_data)
            print(f"[📥] Decrypted packet ({len(decrypted_data)} bytes): {payload}")

    except KeyboardInterrupt:
        print("\n[🔴] Receiver terminated by user.")

    finally:
        shared_state["terminate"] = True
        print("💤 Shutting down cleanly...")
