import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from tracking.tracking import start_tracking, stop_tracking,collect_feedback
import threading
import csv

def run_tracking_in_thread(task_name):
    tracking_thread = threading.Thread(target=start_tracking, args=(task_name,), daemon=True)
    tracking_thread.start()

# Helper function to save results
def save_results(task_name, user_input, correct_answer=None):
    try:
        os.makedirs(f"data/{task_name}", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
        file_path = f"data/{task_name}/U_resp_{timestamp}.txt"
        with open(file_path, "a") as f:
            f.write("=" * 50 + "\n")
            f.write(f"Task: {task_name}\n")
            f.write(f"User Input: {user_input}\n")
            
            if correct_answer:
                f.write(f"Correct Answer: {correct_answer}\n")
            f.write("=" * 50 + "\n")
        st.success(f"Results saved to `{file_path}`.")
    except Exception as e:
        st.error(f"Failed to save results: {e}")
        
# Correct Answers Array (Update based on images and task)
correct_answers = [5, 1, 4]  # Example: Different number of differences for each image

# Task: Spot the Differences
# Run 
# Generic function to handle image-based tasks
def run_image_based_task(task_name, task_description, image_paths, correct_answers):
    """
    Handles both Spot the Differences and Find Whats Missing tasks.

    Arguments:
    - task_name (str): Name of the task
    - task_description (str): Description for the user
    - image_paths (list): List of image file paths
    - correct_answers (list): List of expected answers per image
    """

    st.subheader(task_name)
    st.write(task_description)

 
    for idx, image_path in enumerate(image_paths):
        if image_path:
            # Display the images
            st.image(image_path, use_container_width=True)

            # User input for the task (text for missing object, number for differences)
            user_input = st.text_input(f"Your answer :", key=f"input_{task_name}_{idx}")

            # Get the correct answer for this image
            correct_answer = correct_answers[idx]

            # Submit button per image
            if st.button(f"Submit Answer for the task", key=f"submit_{task_name}_{idx}"):
                if user_input.strip().lower() == str(correct_answer).lower():
                    st.success(f"✅ Correct! Answer for Image {idx + 1}: `{correct_answer}`.")
                else:
                    st.error(f"❌ Incorrect. The correct answer was: `{correct_answer}`.")

                # Save the result
                # save_results(task_name, user_input, correct_answer)

   
def spot_the_differences_task():
    task_name = "Spot the Differences"
    task_description = "Find the number of differences between the 2 images."
    
    image_paths = [
        os.getcwd() + "/images/spot_1.jpg",

    ]
    
    correct_answers = [5]  # Example answers for the images

    run_image_based_task(task_name, task_description, image_paths, correct_answers)


# Find What’s Missing Task
def find_whats_missing_task():
    task_name = "Find What is Missing"
    task_description = "Can you find out what is missing?"

    image_paths = [
        os.getcwd() + "/images/spot_2.jpg",
    ]
    
    correct_answers = ["shadow"]  # Example missing objects

    run_image_based_task(task_name, task_description, image_paths, correct_answers)

def spot_the_mistake_wrapper():
    load_dotenv()
    st.title("Image-Based Tasks")
    st.write("Complete the following visual tasks.")
   # Start Task Button
    if st.button("Start"):
        run_tracking_in_thread("Task 6: Rest Task")  # Run in a background thread

    # Run both tasks
    spot_the_differences_task()
    find_whats_missing_task()
    
     # Task Finished Button
    if st.button("Task Finished"):
        stop_tracking("Task 6: Rest Task")

    # Collect feedback
    st.markdown("<hr>", unsafe_allow_html=True)  
    collect_feedback(task_name="Rest Task")
    
    
    
    
def collect_feedback_1(task_name, participantId= 'Test'):
    st.subheader("Workload & Stress Feedback")
    
    # Initialize session state for form fields
    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = False

    # TLX Factors (1-5 scale, user-friendly labels)
    st.write("Rate the following aspects of your experience (1 = Very Low, 5 = Very High):")
    
    # Assign session_state keys for each slider and text area
    mental_demand = st.slider("How mentally exhausting was the task?", 1, 5, 3, key='mental_demand')
    physical_demand = st.slider("How physically tiring was the task?", 1, 5, 3, key='physical_demand')
    temporal_demand = st.slider("How rushed did you feel?", 1, 5, 3, key='temporal_demand')
    performance = st.slider("How well do you think you performed? (Higher is better)", 1, 5, 3, key='performance')
    effort = st.slider("How hard did you have to work?", 1, 5, 3, key='effort')
    frustration = st.slider("How frustrated did you feel?", 1, 5, 3, key='frustration')

    # NASA TLX Score Calculation (now based on 1-5 scale)
    nasa_tlx = (mental_demand + physical_demand + temporal_demand + 
                (5 - performance) + effort + frustration) / 6

    # Unique follow-up questions based on the task
    if task_name == "Rest Tasks":
        most_stressful_part = st.text_area("What part of this task was the hardest?", key='most_stressful_part')
        concentration_level = st.slider("How focused did you feel?", 1, 5, 3, key='concentration_level')

    elif task_name == "TimeConstraint":
        time_pressure = st.slider("How much did the time constraint affect your performance?", 1, 5, 3, key='time_pressure')
        if time_pressure >= 4:
            st.write("It seems the timer added pressure. Any suggestions to make it fairer?")
            time_feedback = st.text_area("Your thoughts on the time limit:", key='time_feedback')
    
    elif task_name == "Interruptions Task":
        interruptions_impact = st.slider("How much did the interruptions affect you?", 1, 5, 3, key='interruptions_impact')
        if interruptions_impact >= 4:
            st.write("It looks like interruptions were a major issue. Can you describe what made it difficult?")
            interruption_feedback = st.text_area("Your experience with interruptions:", key='interruption_feedback')

    elif task_name == "Combination Task":
        multitasking_difficulty = st.slider("How difficult was it to manage both the timer and interruptions?", 1, 5, 3, key='multitasking_difficulty')
        focus_loss = st.slider("How often did you lose focus due to interruptions?", 1, 5, 3, key='focus_loss')

    # General stress-related questions
    stress_reasons = ", ".join(st.multiselect(
        "What contributed to your stress?",
        ["Lack of Experience", "Time Pressure", "Interruptions", "Unclear Instructions", "Too Many Tasks at Once", 
         "Noise/Distractions", "Lack of Breaks", "Fatigue", "Personal Life Stress"],
        key='stress_reasons'
    ))

    # Deadline experience & additional feedback
    additional_feedback = st.text_area("Any other feedback or suggestions?", key='additional_feedback')

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
        
        # Reset the form by clearing the session state
        
    