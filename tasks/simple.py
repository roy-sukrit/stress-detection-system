from gaze_tracking import GazeTracking
import cv2

# Initialize the GazeTracking object
gaze = GazeTracking()

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Send the frame to the GazeTracking object
    gaze.refresh(frame)

    # Get the gaze status
    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_up():
        text = "Looking up"
    elif gaze.is_down():
        text = "Looking down"
    else:
        text = "Looking center"

    # Display the gaze status on the frame
    cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Gaze Tracking", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()