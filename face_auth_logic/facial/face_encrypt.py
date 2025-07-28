import numpy as np 
import face_recognition as fc 
import hashlib
import cv2 
import os 
import time


ENCODING_FILE = 'mean_encoding.npy'
KEY_FILE = 'face_key.bin'
DISTANCE_THRESHOLD = 0.6
didBlink = True




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
    im = cv2.VideoCapture(0)
    print("Camera On.")

    while True:
        ret, frame = im.read()
        if not ret:
            continue
        cv2.imshow("Camera",frame)
        
        key = cv2.waitKey(1) & 0xFF
        cv2.imwrite(filename, frame)
        if key == ord('q'):
            break
    im.release()
    cv2.destroyAllWindows()
    return filename


def capture_and_save_face(filename="live_check.jpg", seconds=2):
    cam = cv2.VideoCapture(0)

    print("[📸] Capturing frame from Cam...")

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



# AVERAGING FACE ENCODINGS
def enroll_face(n_samples = 5, delay = 2):
    print(f"Capturing {n_samples} of face to generate average encoding key...")

    encodings=[]
    for i in range(n_samples):
        filename=f"enroll_{i}.jpg"
        capture_and_save_face(filename=filename,seconds=delay)
        encoding=face_to_encoding(f'enroll_{i}.jpg')
        if encoding is not None:
            encodings.append(encoding)
    
    average_encoding = np.mean(encodings,0)
    key=encoding_to_key(average_encoding)
    save_key(key,KEY_FILE)

def authenticate_face():
    try:
        saved_encoding = np.load(ENCODING_FILE)
    except FileNotFoundError:
        print("❌ Saved Encoding file not found")
        return
    capture_and_save_face("auth_check.jpg")
    current_encoding = face_to_encoding("auth_check.jpg")

    if current_encoding is None:
        print("❌ Failed to get current encoding")
        return
    
    distance = np.linalg.norm(current_encoding-saved_encoding)
    if(distance<=DISTANCE_THRESHOLD):
        print("✅ Face matched. Generating blended key...")
        blended_encoding = (current_encoding+saved_encoding)/2
        key = encoding_to_key(blended_encoding)
        return key
    else:
        print("❌ Face Mismatch!")
        return None
        