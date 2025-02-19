import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from tracking.tracking import start_tracking, stop_tracking, collect_feedback
import threading

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
                save_results(task_name, user_input, correct_answer)

   
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
        run_tracking_in_thread("Rest Task")  # Run in a background thread

    # Run both tasks
    spot_the_differences_task()
    find_whats_missing_task()
    
     # Task Finished Button
    if st.button("Task Finished"):
        stop_tracking("Rest Task")

    # Collect feedback
    st.markdown("<hr>", unsafe_allow_html=True)  
    collect_feedback(task_name="Rest Tasks")