import streamlit as st
import time
import os
from tracking.tracking import start_tracking, stop_tracking
from streamlit_ace import st_ace
import datetime
from streamlit_sortables import sort_items
import random
from streamlit_autorefresh import st_autorefresh
import csv
import datetime
from tracking.tracking import collect_feedback
from dotenv import load_dotenv

import os



# Helper function to clear old results
def clear_old_results():
    for key in list(st.session_state.keys()):
        if "task" in key or "timer" in key or "user_order" in key:
            del st.session_state[key]

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

# Helper function for task timer
def run_task_with_timer(task_name, task_description, task_logic, time_limit=10):
    # Use task-specific keys for the session state
    task_key = f"{task_name}_task"
    timer_key = f"{task_name}_timer"
    remaining_time_key = f"{task_name}_remaining_time"

    # Initialize state variables
    if task_key not in st.session_state:
        st.session_state[task_key] = False
        st.session_state[timer_key] = None
        st.session_state[remaining_time_key] = time_limit

    if st.button(f"Start {task_name}") and not st.session_state[task_key]:
        clear_old_results()  # Fix Issue 1: Clear previous task results

        st.session_state[task_key] = True
        st.session_state[timer_key] = time.time()
        start_tracking(task_name)

    # Only show the timer and logic after the task has started
    if st.session_state[task_key]:
        # Placeholder for timer
        timer_placeholder = st.empty()  

        current_time = time.time()
        elapsed_time = current_time - st.session_state[timer_key]
        remaining_time = max(time_limit - int(elapsed_time), 0)
        st.session_state[remaining_time_key] = remaining_time

        if remaining_time > 0:
            # Update the timer
            timer_placeholder.info(f"⏳ Time Remaining: {remaining_time} seconds")
            time.sleep(1)
            st.rerun()  # Re-run to update the timer display
        else:
            timer_placeholder.warning("⏰ Time's up!")
            st.balloons()
            stop_tracking(task_name)
            task_logic()
            st.session_state[task_key] = False

def word_rephrase_task(TIME_CONSTRAINT_TIMER):
    task_name = "Task 1: Word Unscramble Task"
    task_description = "Unscramble the following words to form correct words:"
    
    word_pairs = {
        "stsers": "stress",
        "gnirotinom": "monitoring",
        "erhavoib": "behavior",
        "gilatid": "digital",
        "siyslana": "analysis"
    }

    st.subheader(task_name)
    st.write(task_description)
    st.image(random.choice(gifPaths()), caption="Keep Going! 😂")

    user_answers = {}
    
    # User input for unscrambling words
    for scrambled_word in word_pairs.keys():
        st.markdown(
        f"<p style='font-size:18px; font-weight:bold; color:#333;'>Unscramble: "
        f"<span style='color:#d63384; border: 2px solid #d63384; padding: 2px 6px; border-radius: 5px;'>{scrambled_word}</span></p>", 
        unsafe_allow_html=True
    )
        user_answers[scrambled_word] = st.text_input("", key=scrambled_word)
        
    def logic():
        correct_count = 0
        st.write("### Results:")
        
        # Compare user's input with correct words
        for scrambled, correct in word_pairs.items():
            user_input = user_answers[scrambled].strip().lower()
            if user_input == correct:
                st.success(f"✅ `{scrambled}` → `{user_input}` (Correct)")
                correct_count += 1
            else:
                st.error(f"❌ `{scrambled}` → `{user_input}` (Incorrect, Correct Answer: `{correct}`)")

        st.write(f"### Final Score: {correct_count} / {len(word_pairs)}")

        # Save results (you can implement the save logic as needed)
        save_results(task_name, user_answers, word_pairs)

    # Start the task and run with a timer
    run_task_with_timer(task_name, task_description, logic,TIME_CONSTRAINT_TIMER)


# Task 3: Report Writing Task
def report_writing_task(TIME_CONSTRAINT_TIMER):
    task_name = "Task 3: Report Writing Task"
    task_description = """
    Write a short report on Irish War of Independence. Be concise and highlight the timeline.
    """
    
    st.subheader(f"{task_name}")
    st.write(task_description)
    st.write('Max words - 150.')
    st.image(random.choice(gifPaths()), caption="Keep Going! 😂")

    user_input = st.text_area("Write your report here:")

    def logic():
        st.write("Your report has been recorded:")
        st.write(user_input)
        save_results(task_name, user_input)

    run_task_with_timer(task_name, task_description, logic, TIME_CONSTRAINT_TIMER)
    
 
# Task 2: Sentence Reorder Task
def sentence_rephrase_task(TIME_CONSTRAINT_TIMER):
    task_name = "Task 2: Sentence Rephrase Task"
    task_description = "Drag and drop the sentences to arrange them in the correct order."

    correct_order = [
        "Many people spend hours on digital devices daily.",
        "Digital behavior analysis helps in understanding user stress patterns.",
        "AI models can predict stress levels based on user interactions.",
        "Identifying stress early can lead to better mental well-being.",
        "This results in prevention of cognitive overload and stress."
    ]

    # Initialize session state for user order if it's the first time
    if "user_order" not in st.session_state:
        shuffled_sentences = correct_order.copy()
        random.shuffle(shuffled_sentences)
        st.session_state["user_order"] = shuffled_sentences

    # Task description and instructions
    st.subheader(task_name)
    st.write(task_description)
    st.image(random.choice(gifPaths()), caption="Keep Going! 😂")

    # Display sentences with selectable options for reordering
    st.write("### Arrange the sentences in the correct order:")
    new_order = []
    available_sentences = st.session_state["user_order"].copy()  # Copy of sentences to avoid modifying the original list

    for i in range(len(st.session_state["user_order"])):
        # Use a selectbox to allow the user to reorder sentences
        selected_sentence = st.selectbox(
            f"Sentence {i + 1}",
            options=available_sentences,
            key=f"sentence_{i}"
        )
        new_order.append(selected_sentence)
        available_sentences.remove(selected_sentence)  # Remove the selected sentence from available options

    # Update the session state with the new order
    if new_order != st.session_state["user_order"]:
        st.session_state["user_order"] = new_order

    # Result and Logic
    def logic():
        correct_count = sum(1 for u, c in zip(st.session_state["user_order"], correct_order) if u == c)
        st.write("### Results:")
        for i, (user_sentence, correct_sentence) in enumerate(zip(st.session_state["user_order"], correct_order), 1):
            if user_sentence == correct_sentence:
                st.success(f"✅ Position {i} is correct.")
            else:
                st.error(f"❌ Position {i} is incorrect. Correct sentence: `{correct_sentence}`")

        st.write(f"### Final Score: {correct_count} / {len(correct_order)}")

    # Trigger the timer and handle task completion logic
    run_task_with_timer(task_name, task_description, logic, TIME_CONSTRAINT_TIMER)


def gifPaths():
    # Get the current working directory
    filePath = os.getcwd()
    
    # Define the path to the 'gifs' directory
    gifs_dir = os.path.join(filePath, 'gifs')
    
    # Check if the 'gifs' directory exists
    if not os.path.exists(gifs_dir):
        raise FileNotFoundError(f"The directory '{gifs_dir}' does not exist.")
    
    # Get a list of files in the 'gifs' directory
    files = os.listdir(gifs_dir)
    
    # Filter out non-image files (e.g., only allow .gif, .png, .jpg, etc.)
    valid_extensions = ['.gif', '.png', '.jpg', '.jpeg']
    image_files = [file for file in files if os.path.splitext(file)[1].lower() in valid_extensions]
    
    # Construct full paths for the image files
    image_paths = [os.path.join(gifs_dir, file) for file in image_files]
    
    # Debugging: Print the list of valid image paths
    # print("Valid image files:", image_paths)
    
    return image_paths




def distractorGifPaths():
    # Get the current working directory
    filePath = os.getcwd()
    
    # Define the path to the 'gifs' directory
    gifs_dir = os.path.join(filePath, 'distractors')
    
    # Check if the 'gifs' directory exists
    if not os.path.exists(gifs_dir):
        raise FileNotFoundError(f"The directory '{gifs_dir}' does not exist.")
    
    # Get a list of files in the 'gifs' directory
    files = os.listdir(gifs_dir)
    
    # Filter out non-image files (e.g., only allow .gif, .png, .jpg, etc.)
    valid_extensions = ['.gif', '.png', '.jpg', '.jpeg']
    image_files = [file for file in files if os.path.splitext(file)[1].lower() in valid_extensions]
    
    # Construct full paths for the image files
    image_paths = [os.path.join(gifs_dir, file) for file in image_files]
    
    # Debugging: Print the list of valid image paths
    # print("Valid image files:", image_paths)
    
    return image_paths

def time_constraint_task():
    load_dotenv()

    TIME_CONSTRAINT_TIMER = os.getenv("TIME_CONSTRAINT_TIMER")
    st.title("Time-Constrained Tasks")
    st.write("""
    Welcome to the time-constrained tasks! Complete the following activities within their respective time limits. 
    Your performance and stress levels will be recorded.
    """)

    word_rephrase_task(10)
    sentence_rephrase_task(10)
    report_writing_task(10)
    
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)  # Adding extra space
    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal lin
    collect_feedback(task_name="TimeConstraint")
    
    