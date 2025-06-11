import numpy as np 
import face_recognition as fc 
import hashlib
import cv2 
import os 
import time

droid_cam_url = "http://192.168.198.202:4747/video"


def face_to_encoding(img_path: str) -> np.ndarray:
    # Extract face encoding from image file
    face = fc.load_image_file(img_path)
    encodings = fc.face_encodings(face)

    if(len(encodings)==0):
        print("❌ No face found!")
    else:
        print("✅ Face found!")
        return encodings[0]
    
def encoding_to_key(encodings: np.ndarray) -> bytes:
    # convert array into bytes of data
    encodings_bytes = encodings.tobytes()

    # convert the encodings into 256 bit format for the key
    return hashlib.sha256(encodings_bytes).digest()

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
def droid_cam_video(filename="captured_image.jpg"):
    im = cv2.VideoCapture(droid_cam_url)
    print("Press 's' to capture 📷")

    while True:
        ret, frame = im.read()
        if not ret:
            continue
        cv2.imshow("Camera",frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            print(f"✅ Image captured to file : {filename}")
            cv2.imwrite(filename, frame)
        elif key == ord('q'):
            break

    im.release()
    cv2.destroyAllWindows()
    return filename

def capture_and_save_face(filename="live_check.jpg", seconds=2):
    cam = cv2.VideoCapture(droid_cam_url)
    if not cam.isOpened():
        raise RuntimeError("❌ Could not access DroidCam stream.")

    print("[📸] Capturing frame from DroidCam...")

    start_time = time.time()
    while time.time() - start_time < seconds:
        ret, frame = cam.read()
        if not ret:
            continue
        # Save first valid frame
        cv2.imwrite(filename, frame)
        print(f"[💾] Frame saved to {filename}")
        break

    cam.release()
    cv2.destroyAllWindows()



def face_cap_ret_key() -> bytes:
    img_path = droid_cam_video()
    encoding = face_to_encoding(img_path)
    key = encoding_to_key(encoding)
    save_key(key)
    key = load_key()
    print(f"🔐 AES Key (hex): {key.hex()}")

    return key
