import cv2
import os
import time
import threading
import numpy as np
import datetime
from pynput import mouse, keyboard
import dlib
import streamlit as st

import csv

# Initialize variables and a Lock
lock = threading.Lock()
session_active = threading.Event()
mouse_listener = None
keyboard_listener = None
gaze_thread = None
session_filename = None
import uuid


task_enum = {"Task 1: Word Unscramble Task":"T",
             "Task 2: Sentence Rephrase Task":"T",
             "Task 3: Report Writing Task":"T",
             "Task 4: Interruptions Task":"I",
             "Task 5: Combination Task":"C",
             "Task 6: Rest Task":"R"}

def getTaskValue(val):
    print(task_enum[val])
    return task_enum[val]
def generate_participant_id():
    """
    Generates a unique participant ID for data anonymization.
    
    Args:
        existing_ids (set): A set of already generated IDs to ensure uniqueness.
    
    Returns:
        str: A unique participant ID.
    """
   
    unique_participant_id = f"PT-{uuid.uuid4().hex[:6].upper()}"  # e.g., PT-A1B2C3
    return unique_participant_id



def log_to_csv(filename, data):
    """Helper function to log data to a CSV file."""
    csv_filename = filename.replace(".txt", ".csv")  # Store CSV alongside TXT logs
    
    # Ensure the directory exists
    directory = os.path.dirname(csv_filename)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # Check if the CSV file exists to determine if headers are needed
    file_exists = os.path.isfile(csv_filename)

    with open(csv_filename, mode="a", newline="") as f:
        writer = csv.writer(f)
        
        # Write headers if the file is new
        if not file_exists:
            writer.writerow(["Participant Id","Condition","Timestamp", "Name","Event Details"])
        
        writer.writerow(data)

# Tracking Method
def start_tracking(task_name):
    global session_filename, gaze_thread,participantId
    with lock:  # Synchronize access to shared variables
        timestamp = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
        participantId =generate_participant_id()
        session_filename = f"data/{task_name}/U_data_{timestamp}.txt"
        print(f"Starting tracking... Data will be saved to {session_filename}")

    session_active.set()
    start_new_session(session_filename,task_name)
    
     # Start listeners in separate threads
    gaze_thread = threading.Thread(target=gaze_tracking, args=(session_filename,task_name))
    mouse_listener = threading.Thread(target=mouse_tracking, args=(session_filename,task_name))
    keyboard_listener = threading.Thread(target=keyboard_tracking, args=(session_filename,task_name))
    
    gaze_thread.start()
    mouse_listener.start()
    keyboard_listener.start()

    # Wait for all threads to finish
    gaze_thread.join()
    mouse_listener.join()
    keyboard_listener.join()

def stop_tracking(task_name):

    global mouse_listener, keyboard_listener, gaze_thread, session_filename
    with lock:
        if session_active.is_set():
            print(f"Stopping tracking... Final data saved to {session_filename}")
            session_active.clear()
            end_session(session_filename,task_name)

            # Stop mouse and keyboard listeners
            if mouse_listener:
                mouse_listener.stop()
            if keyboard_listener:
                keyboard_listener.stop()

            if gaze_thread:
                gaze_thread.join()
        else:
            print("No active session to stop.")

def log_to_file(filename,name, task_name,message):
    """Helper function to log data to a file."""
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(filename, "a") as f:
        f.write(f"{participantId},{task_name},{time.strftime('%Y-%m-%d %H:%M:%S')} - {name} , {message}\n")
    log_to_csv(filename, [participantId,getTaskValue(task_name),time.strftime('%Y-%m-%d %H:%M:%S'),name, message.split(":")[1] if ":" in message else ""])        
        

def start_new_session(filename,task_name):
    """Log the start of a new session."""
    
    log_to_file(filename,"Session", task_name, f"====== {task_name}======")

    log_to_file(filename,"Session", task_name, "====== New Session Start ======")
    log_to_file(filename, "Session", task_name,f"Session Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def end_session(filename,task_name):
    """Log the end of a session."""
    log_to_file(filename,"Session",task_name, f"====== Session End ======")
    log_to_file(filename, "Session",task_name, f"Session End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def mouse_tracking(filename,task_name):
    def on_move(x, y):
        if session_active.is_set():
            log_to_file(filename, "Mouse",f"Mouse Move - ({x}, {y})")

    def on_click(x, y, button, pressed):
        if session_active.is_set():
            log_to_file(filename,"Mouse", task_name,f"Mouse {'Press' if pressed else 'Release'} - ({x}, {y})")

    def on_scroll(x, y, dx, dy):
        if session_active.is_set():
            log_to_file(filename,"Mouse", f"Mouse Scroll -({x}, {y}) : Delta ({dx}, {dy})")

    global mouse_listener
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()
    mouse_listener.join()

def keyboard_tracking(filename):
    def on_press(key):
        if session_active.is_set():
            log_to_file(filename,"Keyboard", f"Key Press: {key}")

    def on_release(key):
        if session_active.is_set():
            log_to_file(filename,"Keyboard",  f"Key Release: {key}")
        if key == keyboard.Key.esc:  # Stop listener on Esc key
            return False

    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    keyboard_listener.join()


#Approach 1
def gaze_tracking_1(filename):
    """Tracks gaze direction using OpenCV and logs gaze as left, right, or forward."""
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
                log_to_file(filename,"Gaze Direction",  "Error: Failed to grab frame")
                print("Failed to grab frame")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=6, minSize=(50, 50))

            if len(faces) == 0:
                log_to_file(filename, "Gaze Direction","No face detected")
                print("No face detected")
                continue

            for (x, y, w, h) in faces:
                roi_gray = gray_frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.05, minNeighbors=5, minSize=(20, 20))

                if len(eyes) >= 2:
                    gaze_direction = analyze_gaze_direction(eyes, roi_gray, w)
                    log_to_file(filename,"Gaze Direction", f":{gaze_direction}")
                    print(f"Gaze Direction: {gaze_direction}")
                else:
                    log_to_file(filename, "Not enough eyes detected")
                    print("Not enough eyes detected")

            time.sleep(0.5)  # Slight delay to prevent high CPU usage

    except Exception as e:
        log_to_file(filename,"Gaze Direction", f"Error during gaze tracking: {str(e)}")
        print(f"Error during gaze tracking: {str(e)}")

    finally:
        webcam.release()
        cv2.destroyAllWindows()
        log_to_file(filename,"Gaze Direction", "Gaze tracking session ended")

# #Approach 1 
def analyze_gaze_direction_1(eyes, roi_gray, face_width):
    """Analyze the gaze direction based on the eye region and face width."""
    eye_positions = []
    for (ex, ey, ew, eh) in eyes:
        eye_center = (ex + ew // 2, ey + eh // 2)
        eye_positions.append(eye_center)

    eye_positions = sorted(eye_positions, key=lambda pos: pos[0])

    left_eye_x, _ = eye_positions[0]
    right_eye_x, _ = eye_positions[1]
    face_center_x = face_width // 2

    gaze_direction = "Looking Forward"
    
    if left_eye_x < face_center_x - 10 and right_eye_x < face_center_x - 10:  # Both eyes on the left
        gaze_direction = "Looking Left"
    elif right_eye_x > face_center_x + 10 and left_eye_x > face_center_x + 10:  # Both eyes on the right
        gaze_direction = "Looking Right"

    return gaze_direction
#Approach 1


#Approach 2 
def analyze_gaze_direction_2(eyes, roi_gray, face_width):
    """Analyze the gaze direction based on the eye region and face width."""
    try:
        # Sorting eyes by their x-coordinates to differentiate left and right eyes
        eye_positions = sorted(eyes, key=lambda pos: pos[0])
        
        '''
        Here, lambda pos: pos[0] extracts the x coordinate (pos[0]) from each bounding box tuple.
	    This ensures the sorting is based on the horizontal position of the detected eyes.
        '''
        if len(eye_positions) < 2:
            return "Not enough eyes detected"
        
        # Calculate positions of the eyes
        # Center of the left eye
        left_eye_x = eye_positions[0][0] + eye_positions[0][2] // 2  
        '''
        eye_positions[0][0]: x-coordinate of the top-left corner of the left eye.
	    eye_positions[0][2] // 2: Half of the width of the left eye bounding box. 
        Adding this to the x-coordinate gives the x-coordinate of the center of the left eye.
        '''

        # Center of the right eye
        right_eye_x = eye_positions[1][0] + eye_positions[1][2] // 2 
        
        face_center_x = face_width // 2
        print(f"Left Eye X: {left_eye_x}, Right Eye X: {right_eye_x}, Face Center: {face_center_x}")
        
        # Determine gaze direction
        '''
        . left_eye_x < face_center_x - 20 and right_eye_x < face_center_x - 20
	    •	Condition: Both the left and right eyes are horizontally positioned significantly to the left of the face center.
	    •	Threshold: 20 is the tolerance value used to determine if the eyes are sufficiently far from the center to consider
         the gaze as “Looking Left.”
	    •	Interpretation:
	    •	If the centers of both eyes are located at x-coordinates less than face_center_x - 20, 
            it means the user is looking towards the left.
        '''
        if left_eye_x < face_center_x - 10 and right_eye_x < face_center_x - 10:  # Looking Left
            return "Looking Left"
        
        elif left_eye_x > face_center_x + 10 and right_eye_x > face_center_x + 10:  # Looking Right
            return "Looking Right"
        else:
            return "Looking Forward"
    except Exception as e:
        print(f"Error in analyze_gaze_direction: {e}")
        return "Error in gaze direction analysis"
# Approach 2 

def gaze_tracking(filename,task_name):
    """Tracks gaze direction and head pose using OpenCV, logs results to the file."""
    webcam = cv2.VideoCapture(0)
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_landmark_model = os.getcwd()+"/tasks/shape_predictor_68_face_landmarks.dat"  # Path to dlib's landmark model
    predictor = dlib.shape_predictor(face_landmark_model)
    detector = dlib.get_frontal_face_detector()

    if not webcam.isOpened():
        log_to_file(filename, "Error",task_name,"Error: Webcam not found!")
        print("Error: Webcam not found!")
        return

    try:
        while session_active.is_set():
            ret, frame = webcam.read()
            if not ret:
                log_to_file(filename, "Error", "Error: Failed to grab frame")
                print("Failed to grab frame")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray_frame)
            # print("faces ---->",faces)

            if len(faces) == 0:
                log_to_file(filename, "Error",task_name, "No face detected")
                print("No face detected")
                continue

            for face in faces:
                #Predicts 68 Landmarks for each face
                landmarks = predictor(gray_frame, face)
                # print("landmarks ---->",landmarks)

                
                face_width = face.right() - face.left()  
                # print("face_width ---->",face_width)

                # Extract eye regions
                left_eye = get_eye_region(landmarks, left=True)
                right_eye = get_eye_region(landmarks, left=False)

                # Left and Right into a single list
                eyes = [left_eye, right_eye]
                # print("eyes ---->",eyes)

                # Analyze gaze direction
                gaze_direction = analyze_gaze_direction(eyes, gray_frame, face_width)
                
                log_to_file(filename,  "Gaze",task_name,f": {gaze_direction}")
                print(f"Gaze Direction: {gaze_direction}")

                # Head pose estimation
                image_points = get_image_points(landmarks)
                head_pose = calculate_head_pose(image_points, frame)
                log_to_file(filename, "Head Pose",task_name, f": {head_pose}")
                print(f"Head Pose: {head_pose}")

            time.sleep(0.5)  # Prevent high CPU usage

    except Exception as e:
        log_to_file(filename, "Error", f"Error during gaze tracking: {str(e)}")
        print(f"Error during gaze tracking: {str(e)}")

    finally:
        webcam.release()
        cv2.destroyAllWindows()
        log_to_file(filename,  "Gaze",task_name,"Gaze tracking session ended")


# Helper Functions
def get_eye_region(landmarks, left=True):
    """Extracts the eye region from the landmarks."""
      # Left eye
    if left:
        points = [36, 37, 38, 39, 40, 41]
    else:
        points = [42, 43, 44, 45, 46, 47] 
        
    return [(landmarks.part(p).x, landmarks.part(p).y) for p in points]

def analyze_gaze_direction(eyes, gray_frame, face_width):
    """Analyzes gaze direction based on eye regions."""
    gaze_directions = []
    for eye in eyes:
        # Geting the bounding box of the eye
        x_coords = [point[0] for point in eye]
        y_coords = [point[1] for point in eye]

        # Croping the eye region
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        eye_region = gray_frame[min_y:max_y, min_x:max_x]

        # Threshold the eye region for binary mask
        _, threshold_eye = cv2.threshold(eye_region, 70, 255, cv2.THRESH_BINARY)

        # Finding contours to locate the pupil
        contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # print("contours ---->",contours)
        
        if contours:
            # Finding the largest contour assuming it's the pupil
            largest_contour = max(contours, key=cv2.contourArea)
            # print("largest_contour ---->",largest_contour)

            moments = cv2.moments(largest_contour)
            # print("moments ---->",moments)

            

            if moments['m00'] != 0:
                cx = int(moments['m10'] / moments['m00'])  # x-coordinate of pupil
                # print("cx ---->",cx)

                relative_position = cx / (max_x - min_x)  # Normalizing position
                # print("relative_position --->",relative_position)
                # Classify gaze direction
                if relative_position < 0.4:
                    gaze_directions.append("Left")
                elif 0.4 <= relative_position <= 0.6:
                    gaze_directions.append("Center")
                else:
                    gaze_directions.append("Right")
            else:
                gaze_directions.append("Unknown")
        else:
            gaze_directions.append("Unknown")

    # Combine gaze directions
    if "Left" in gaze_directions and "Right" in gaze_directions:
        return "Mixed"
    elif "Left" in gaze_directions:
        return "Left"
    elif "Right" in gaze_directions:
        return "Right"
    else:
        return "Center"


def get_image_points(landmarks):
    """Maps dlib landmarks to 2D image points for head pose calculation."""
    points = [30, 8, 36, 45, 48, 54]  # Nose tip, chin, eyes, and mouth corners
    return np.array([(landmarks.part(p).x, landmarks.part(p).y) for p in points], dtype="double")


import cv2
import numpy as np

def calculate_head_pose(image_points, frame):
    """Calculates the head pose using the 2D image points and frame."""
    # 3D model points of the face (in the 3D space)
    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corner
        (-150.0, -150.0, -125.0),  # Left mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner
    ], dtype="double")
    
    # Camera matrix (intrinsic parameters)
    focal_length = frame.shape[1]  # Focal length is typically the width of the image
    center = (frame.shape[1] / 2, frame.shape[0] / 2)  # Optical center is the center of the image
    
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    # Distortion coefficients (assuming no lens distortion)
    dist_coeffs = np.zeros((4, 1))  # No distortion
    
    # Solve for the rotation and translation vectors
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs
    )
    
    if not success:
        print("Could not solve PnP")
        return None
    
    # Get the rotation matrix from the rotation vector
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    
    # Get the Euler angles (yaw, pitch, roll)
    angles = cv2.decomposeProjectionMatrix(np.hstack([rotation_matrix, translation_vector]))[6]
    yaw, pitch, roll = angles

    # Determine head direction
    if pitch < -10:
        head_direction = "Looking Down"
    elif pitch > 10:
        head_direction = "Looking Up"
    else:
        head_direction = "Neutral"

    if yaw < -10:
        head_direction += " and Looking Left"
    elif yaw > 10:
        head_direction += " and Looking Right"
    else:
        head_direction += " and Centered"

    # Project 3D points to 2D image plane to visualize the pose
    nose_end_point_3D = np.array([(0.0, 0.0, 1000.0)])  # Point far along the z-axis (outwards)
    nose_end_point_2D, _ = cv2.projectPoints(nose_end_point_3D, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
    
    # Draw the head pose on the image
    p1 = (int(image_points[0][0]), int(image_points[0][1]))  # Nose tip (2D point)
    p2 = (int(nose_end_point_2D[0][0][0]), int(nose_end_point_2D[0][0][1]))  # Nose tip projected in 2D

    # Draw line on the image indicating the direction of the nose
    cv2.line(frame, p1, p2, (0, 0, 255), 2)  # Red line

    # Return the head pose direction (Up/Down/Left/Right)
    return head_direction



def calculate_head_pose_old(image_points, frame):
    
    """Calculates the head pose using image points and returns pitch, yaw, and roll."""
    # 3D model points
    model_points = np.array([
        (0.0, 0.0, 0.0),        # Nose tip
        (0.0, -330.0, -65.0),   # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corner
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)   # Right mouth corner
    ])

    # Camera internals
    size = frame.shape
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    dist_coeffs = np.zeros((4, 1))  # Assume no lens distortion

    # SolvePnP
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs
    )
    if success:
        return rotation_vector.flatten()  # Pitch, yaw, roll
    return "Pose estimation failed"


def collect_feedback_(task_name, participantId='Test'):
    st.subheader("Workload & Stress Feedback")

    # Slider range and default
    s_min, s_max, default_value = 1, 5, 3

    # Use a versioning system to reset sliders dynamically
    if "slider_version" not in st.session_state:
        st.session_state["slider_version"] = 1

    def reset_sliders():
        """Increments slider version to force Streamlit to reset values."""
        st.session_state["slider_version"] = 3

    # Sliders (force reset using unique keys)
    mental_demand = st.slider("How mentally exhausting was the task?", s_min, s_max, default_value, key=f"mental_demand_{st.session_state['slider_version']}")
    physical_demand = st.slider("How physically tiring was the task?", s_min, s_max, default_value, key=f"physical_demand_{st.session_state['slider_version']}")
    temporal_demand = st.slider("How rushed did you feel?", s_min, s_max, default_value, key=f"temporal_demand_{st.session_state['slider_version']}")
    performance = st.slider("How well do you think you performed? (Higher is better)", s_min, s_max, default_value, key=f"performance_{st.session_state['slider_version']}")
    effort = st.slider("How hard did you have to work?", s_min, s_max, default_value, key=f"effort_{st.session_state['slider_version']}")
    frustration = st.slider("How frustrated did you feel?", s_min, s_max, default_value, key=f"frustration_{st.session_state['slider_version']}")

    # Calculate NASA TLX Score
    nasa_tlx = (mental_demand + physical_demand + temporal_demand + 
                (5 - performance) + effort + frustration) / 6

    # Submit feedback button
    if st.button("Submit Feedback"):
        # Store feedback (Replace with actual storage logic)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = f"data/Feedback/{task_name}/feedback_data_{timestamp}.csv"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Participant Id", "Timestamp", "Mental Demand", "Physical Demand", "Temporal Demand", 
                                 "Performance", "Effort", "Frustration", "NASA TLX Score"])
            writer.writerow([participantId, timestamp, mental_demand, physical_demand, temporal_demand, 
                             performance, effort, frustration, round(nasa_tlx, 2)])

        st.success(f"Thank you for your feedback! NASA TLX Score: {nasa_tlx:.2f}")

        # Reset sliders after submission
        reset_sliders()

    # Manual Reset Button (optional)
    st.button("Reset Form", on_click=reset_sliders)

# Call the function

def collect_feedback(task_name, participantId='Test'):
    st.subheader("Workload & Stress Feedback")

    # Initialize session state for form reset
    if "slider_version" not in st.session_state:
        st.session_state["slider_version"] = 3

    def reset_sliders():
        """Forces slider reset by incrementing version key."""
        st.session_state["slider_version"] = 3

    # TLX Factors (1-5 scale, user-friendly labels)
    st.write("Rate the following aspects of your experience (1 = Very Low, 5 = Very High):")

    # Sliders with forced reset
    mental_demand = st.slider("How mentally exhausting was the task?", 1, 5, 3, key=f"mental_demand_{st.session_state['slider_version']}")
    physical_demand = st.slider("How physically tiring was the task?", 1, 5, 3, key=f"physical_demand_{st.session_state['slider_version']}")
    temporal_demand = st.slider("How rushed did you feel?", 1, 5, 3, key=f"temporal_demand_{st.session_state['slider_version']}")
    performance = st.slider("How well do you think you performed? (Higher is better)", 1, 5, 3, key=f"performance_{st.session_state['slider_version']}")
    effort = st.slider("How hard did you have to work?", 1, 5, 3, key=f"effort_{st.session_state['slider_version']}")
    frustration = st.slider("How frustrated did you feel?", 1, 5, 3, key=f"frustration_{st.session_state['slider_version']}")

    # NASA TLX Score Calculation
    nasa_tlx = (mental_demand + physical_demand + temporal_demand + 
                (5 - performance) + effort + frustration) / 6

    # Task-Specific Questions
    if task_name == "Rest Tasks":
        most_stressful_part = st.text_area("What part of this task was the hardest?", key="most_stressful_part")
        concentration_level = st.slider("How focused did you feel?", 1, 5, 3, key=f"concentration_level_{st.session_state['slider_version']}")

    elif task_name == "TimeConstraint":
        time_pressure = st.slider("How much did the time constraint affect your performance?", 1, 5, 3, key=f"time_pressure_{st.session_state['slider_version']}")
        if time_pressure >= 4:
            st.write("It seems the timer added pressure. Any suggestions to make it fairer?")
            time_feedback = st.text_area("Your thoughts on the time limit:", key="time_feedback")

    elif task_name == "Interruptions Task":
        interruptions_impact = st.slider("How much did the interruptions affect you?", 1, 5, 3, key=f"interruptions_impact_{st.session_state['slider_version']}")
        if interruptions_impact >= 4:
            st.write("It looks like interruptions were a major issue. Can you describe what made it difficult?")
            interruption_feedback = st.text_area("Your experience with interruptions:", key="interruption_feedback")

    elif task_name == "Combination Task":
        multitasking_difficulty = st.slider("How difficult was it to manage both the timer and interruptions?", 1, 5, 3, key=f"multitasking_difficulty_{st.session_state['slider_version']}")
        focus_loss = st.slider("How often did you lose focus due to interruptions?", 1, 5, 3, key=f"focus_loss_{st.session_state['slider_version']}")

    # General Stress Contributors
    stress_reasons = ", ".join(st.multiselect(
        "What contributed to your stress?",
        ["Lack of Experience", "Time Pressure", "Interruptions", "Unclear Instructions", "Too Many Tasks at Once", 
         "Noise/Distractions", "Lack of Breaks", "Fatigue", "Personal Life Stress"],
        key="stress_reasons"
    ))

    # Additional Feedback
    additional_feedback = st.text_area("Any other feedback or suggestions?", key="additional_feedback")

    # Timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Submit feedback button
    if st.button("Submit Feedback"):
        file_path = f"data/Feedback/{task_name}/feedback_data_{participantId}.csv"

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Check if file exists (to add headers if needed)
        file_exists = os.path.isfile(file_path)

        # Open CSV file and append data
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)

            # Write headers if the file is new
            if not file_exists:
                writer.writerow(["Participant Id", "Timestamp",
                                 "Mental Demand", "Physical Demand", "Temporal Demand", 
                                 "Performance", "Effort", "Frustration", "NASA TLX Score",
                                 "Stress Reasons", "Additional Feedback"])

            # Store common data
            feedback_data = [participantId, timestamp, 
                             mental_demand, physical_demand, temporal_demand, 
                             performance, effort, frustration, round(nasa_tlx, 2), 
                             stress_reasons, additional_feedback]

            # Add task-specific data
            if task_name == "Rest Tasks":
                feedback_data.append(most_stressful_part)
                feedback_data.append(concentration_level)

            elif task_name == "TimeConstraint":
                feedback_data.append(time_pressure)
                if time_pressure >= 4:
                    feedback_data.append(time_feedback)

            elif task_name == "Interruptions Task":
                feedback_data.append(interruptions_impact)
                if interruptions_impact >= 4:
                    feedback_data.append(interruption_feedback)

            elif task_name == "Combination Task":
                feedback_data.append(multitasking_difficulty)
                feedback_data.append(focus_loss)

            # Write the feedback data row
            writer.writerow(feedback_data)

        st.success(f"Thank you for your feedback! NASA TLX Score: {nasa_tlx:.2f}")

        # Reset sliders after submission
        reset_sliders()
 
    