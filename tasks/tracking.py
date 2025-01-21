import cv2
import os
import time
import threading
import numpy as np
import datetime
import tempfile
from pynput import mouse, keyboard
import dlib
from threading import Event
# import sys
# sys.path.append('/Users/src/Sukrit_Development/stress-analysis/tasks')

# try:
#     from gaze_tracking import GazeTracking
#     print("gaze_tracking imported successfully! tracking.py")
# except ModuleNotFoundError as e:
#     print(f"ModuleNotFoundError tracking.py: {e}")


# Trying with Dlib
# Initialize dlib face detector and landmark predictor
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
# session_active = Event()  # A flag for controlling session flow


# Initialize variables and a Lock
lock = threading.Lock()
session_active = threading.Event()
mouse_listener = None
keyboard_listener = None
gaze_thread = None
session_filename = None

def log_to_file(filename, message):
    """Helper function to log data to a file."""
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(filename, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def start_new_session(filename):
    """Log the start of a new session."""
    log_to_file(filename, "====== New Session Start ======")
    log_to_file(filename, f"Session Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def end_session(filename):
    """Log the end of a session."""
    log_to_file(filename, f"====== Session End ======")
    log_to_file(filename, f"Session End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Mouse tracking
def mouse_tracking(filename):
    def on_move(x, y):
        if session_active.is_set():
            log_to_file(filename, f"Mouse moved to ({x}, {y})")

    def on_click(x, y, button, pressed):
        if session_active.is_set():
            log_to_file(filename, f"Mouse {'pressed' if pressed else 'released'} at ({x}, {y})")

    def on_scroll(x, y, dx, dy):
        if session_active.is_set():
            log_to_file(filename, f"Scrolled at ({x}, {y}) with delta ({dx}, {dy})")

    global mouse_listener
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()
    mouse_listener.join()

# Keyboard tracking
def keyboard_tracking(filename):
    def on_press(key):
        if session_active.is_set():
            log_to_file(filename, f"Key pressed: {key}")

    def on_release(key):
        if session_active.is_set():
            log_to_file(filename, f"Key released: {key}")
        if key == keyboard.Key.esc:  # Stop listener on Esc key
            return False

    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    keyboard_listener.join()



#Approach 1
def gaze_tracking(filename):
    """Tracking gaze direction using OpenCV and logs gaze as left, right, or forward."""
    webcam = cv2.VideoCapture(0)
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    if not webcam.isOpened():
        log_to_file(filename, "Error: Webcam not found!")
        print("Error: Webcam not found!")
        return

    try:
        while session_active.is_set():
            ret, frame = webcam.read()
            if not ret:
                log_to_file(filename, "Error: Failed to grab frame")
                print("Failed to grab frame")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Gray Frame", gray_frame)

            #Display the gray frame !!!
            print("gray_frame",gray_frame)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=6, minSize=(50, 50))

            if len(faces) == 0:
                log_to_file(filename, "No face detected")
                print("No face detected")
                continue

            for (x, y, w, h) in faces:
                roi_gray = gray_frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.05, minNeighbors=5, minSize=(20, 20))
                print("Eyes ====>",eyes)
                if len(eyes) >= 2:
                    gaze_direction = analyze_gaze_direction(eyes, roi_gray, w)
                    log_to_file(filename, f"Gaze Direction: {gaze_direction}")
                    print(f"Gaze Direction: {gaze_direction}")
                else:
                    log_to_file(filename, "Not enough eyes detected")
                    print("Not enough eyes detected")

            time.sleep(0.5)  # Slight delay to prevent high CPU usage

    except Exception as e:
        log_to_file(filename, f"Error during gaze tracking: {str(e)}")
        print(f"Error during gaze tracking: {str(e)}")

    finally:
        webcam.release()
        cv2.destroyAllWindows()
        log_to_file(filename, "Gaze tracking session ended")

# #Approach 1 
# # def analyze_gaze_direction(eyes, roi_gray, face_width):
#     """Analyze the gaze direction based on the eye region and face width."""
#     eye_positions = []
#     for (ex, ey, ew, eh) in eyes:
#         eye_center = (ex + ew // 2, ey + eh // 2)
#         eye_positions.append(eye_center)

#     eye_positions = sorted(eye_positions, key=lambda pos: pos[0])

#     left_eye_x, _ = eye_positions[0]
#     right_eye_x, _ = eye_positions[1]
#     face_center_x = face_width // 2

#     gaze_direction = "Looking Forward"
    
#     if left_eye_x < face_center_x - 20 and right_eye_x < face_center_x - 20:  # Both eyes on the left
#         gaze_direction = "Looking Left"
#     elif right_eye_x > face_center_x + 20 and left_eye_x > face_center_x + 20:  # Both eyes on the right
#         gaze_direction = "Looking Right"

#     return gaze_direction
# #Approach 1

#Approach 2 
def analyze_gaze_direction(eyes, roi_gray, face_width):
    """Analyze the gaze direction based on the eye region and face width."""
    try:
        # Sorting eyes by their x-coordinates to differentiate left and right eyes
        eye_positions = sorted(eyes, key=lambda pos: pos[0])
        
        if len(eye_positions) < 2:
            return "Not enough eyes detected"
        
        # Calculate positions of the eyes
        left_eye_x = eye_positions[0][0] + eye_positions[0][2] // 2  # Center of the left eye
        right_eye_x = eye_positions[1][0] + eye_positions[1][2] // 2  # Center of the right eye
        
        face_center_x = face_width // 2
        
        # Debuggingr
        print(f"Left Eye X: {left_eye_x}, Right Eye X: {right_eye_x}, Face Center: {face_center_x}")
        
        # Determine gaze direction
        if left_eye_x < face_center_x - 20 and right_eye_x < face_center_x - 20:  # Looking Left
            return "Looking Left"
        elif left_eye_x > face_center_x + 20 and right_eye_x > face_center_x + 20:  # Looking Right
            return "Looking Right"
        else:
            return "Looking Forward"
    except Exception as e:
        print(f"Error in analyze_gaze_direction: {e}")
        return "Error in gaze direction analysis"

# Approach 2 

# Tracking Method
def start_tracking():
    global session_filename, gaze_thread
    with lock:  # Synchronize access to shared variables
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_filename = f"data/computer_interaction_{timestamp}.txt"
        print(f"Starting tracking... Data will be saved to {session_filename}")

    session_active.set()
    start_new_session(session_filename)
    
     # Start listeners in separate threads
    gaze_thread = threading.Thread(target=gaze_tracking, args=(session_filename,))
    mouse_listener = threading.Thread(target=mouse_tracking, args=(session_filename,))
    keyboard_listener = threading.Thread(target=keyboard_tracking, args=(session_filename,))
    
    gaze_thread.start()
    # mouse_listener.start()
    # keyboard_listener.start()

    # Wait for all threads to finish
    gaze_thread.join()
    # mouse_listener.join()
    # keyboard_listener.join()

def stop_tracking():

    global mouse_listener, keyboard_listener, gaze_thread, session_filename
    with lock:
        if session_active.is_set():
            print(f"Stopping tracking... Final data saved to {session_filename}")
            session_active.clear()
            end_session(session_filename)

            # Stop mouse and keyboard listeners
            if mouse_listener:
                mouse_listener.stop()
            if keyboard_listener:
                keyboard_listener.stop()

            if gaze_thread:
                gaze_thread.join()
        else:
            print("No active session to stop.")
