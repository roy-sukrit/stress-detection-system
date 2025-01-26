import streamlit as st
import time
import os
from tasks.tracking import start_tracking, stop_tracking
from streamlit_ace import st_ace
import subprocess
import datetime


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

# Task 1: Word Rephrase Task
def word_rephrase_task():
    task_name = "Task 1: Word Rephrase Task"
    task_description = "Reorder the following words to form a coherent sentence:"
    words = ["stress", "analyzing", "Cognitive", "digital", "behaviors", "involves"]
    correct_sentence = "Cognitive stress involves analyzing digital behaviors."
    
    st.subheader(f"{task_name}")
    st.write(task_description)
    st.write(f"Words to reorder: `{', '.join(words)}`")
    user_input = st.text_area("Type your reordered sentence here:")

    def logic():
        st.write(f"Your input: {user_input}")
        if user_input.strip() == correct_sentence:
            st.success("Correct! Well done!")
        else:
            st.error("Incorrect. The correct sentence is:")
            st.write(f"`{correct_sentence}`")
        save_results(task_name, user_input, correct_sentence)

    run_task_with_timer(task_name, task_description, logic)

# Task 2: Report Writing Task
def report_writing_task():
    task_name = "Task 2: Report Writing Task"
    task_description = """
    Write a short report on the Mexican War of 1846. Be concise and focus on the main events.
    """
    
    st.subheader(f"{task_name}")
    st.write(task_description)

    user_input = st.text_area("Write your report here:")

    def logic():
        st.write("Your report has been recorded:")
        st.write(user_input)
        save_results(task_name, user_input)

    run_task_with_timer(task_name, task_description, logic, time_limit=10)
    
# Task 3: Python Program Task
# Task 3: Python Program Task
def python_program_task():
    task_name = "Task 3 : Write a Python Program"
    task_description = """
    Write a program to calculate the factorial of a number. Define a function named `factorial(n)` that:
    - Takes a positive integer `n` and returns its factorial.
    - The factorial of 0 is defined as 1.
    - Complete the code below.
    """
    default_code = """
def factorial(n: int) -> int:
    if n == 0:
        return 1
    # Change from here    
    return -1
    
# Example usage:
print(factorial(5))  # Expected: 120
print(factorial(0))  # Expected: 1
    """
    
    # Display the task instructions
    st.subheader(f"{task_name}")
    st.write(task_description)
    st.markdown("<h3 style='color:red;'>❗<b>Only 1 attempt is allowed!</b> ❗</h3>", unsafe_allow_html=True)

    if "code_editor" not in st.session_state:
        st.session_state.code_editor = default_code

    code = st_ace(language="python", theme="monokai", font_size=14, value=st.session_state.code_editor, key="editor")
    st.session_state.code_editor = code

    task_key = f"{task_name}_task"
    timer_key = f"{task_name}_timer"
    remaining_time_key = f"{task_name}_remaining_time"
    time_limit = 10  # Time limit in seconds

    if task_key not in st.session_state:
        st.session_state[task_key] = False
        st.session_state[timer_key] = None
        st.session_state[remaining_time_key] = time_limit
        st.session_state.timer_placeholder = None

    # Start task button
    if st.button(f"Start {task_name}") and not st.session_state[task_key]:
        st.session_state[task_key] = True
        st.session_state[timer_key] = time.time()
        st.session_state[remaining_time_key] = time_limit
        st.session_state.timer_placeholder = st.empty()

    # Run Code button
    if st.button("Run Code"):
        try:
            timestamp = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
            file_path = f"temp_code_{timestamp}.py"
            with open(file_path, "w") as f:
                f.write(code)

            # Run the code and capture the output
            result = subprocess.run(["python", file_path], capture_output=True, text=True)

            st.subheader("Output:")
            if result.stdout:
                st.text(result.stdout)
            if result.stderr:
                st.error(result.stderr)

            # Evaluate test cases
            outputs = [int(line.strip()) for line in result.stdout.strip().split("\n") if line.strip().isdigit()]
            expected_outputs = [120, 1]

            if outputs == expected_outputs:
                st.success("Test Cases Passed!")
            else:
                st.warning(f"Test Cases Failed.\nExpected: {expected_outputs}\nGot: {outputs}")

        except Exception as e:
            st.error(f"Error: {e}")

    # Timer logic
    if st.session_state[task_key]:
        if st.session_state.timer_placeholder is None:
            st.session_state.timer_placeholder = st.empty()

        current_time = time.time()
        elapsed_time = current_time - st.session_state[timer_key]
        remaining_time = max(time_limit - int(elapsed_time), 0)
        st.session_state[remaining_time_key] = remaining_time

        if remaining_time > 0:
            st.session_state.timer_placeholder.info(f"⏳ Time Remaining: {remaining_time} seconds")
            time.sleep(1)  # Delay to refresh
        else:
            st.session_state.timer_placeholder.warning("⏰ Time's up!")
            st.balloons()
            st.session_state[task_key] = False
            st.session_state.timer_placeholder = None  # Clear the placeholder

# Stress Level Feedback
def collect_feedback():
    st.subheader("Stress Level Feedback")

    st.write("How did you feel after completing the tasks?")
    stress_level = st.radio("Select your stress level:", ["Low Stress", "Medium Stress", "High Load", "Burnout"])

    st.write("Which task did you find most stressful?")
    most_stressful_task = st.selectbox("Choose the task you found most stressful:", ["Sentence Rephrasing", "Report Writing", "Python Code"])

    st.write("Which task did you find least stressful?")
    least_stressful_task = st.selectbox("Choose the task you found least stressful:", ["Sentence Rephrasing", "Report Writing", "Python Code"])

    additional_feedback = st.text_area("Additional feedback:")

    timestamp = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")

    if st.button("Submit Feedback"):
        try:
            with open(f"data/Feedback/feedback_{timestamp}.txt", "a") as f:
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Stress Level: {stress_level}\n")
                f.write(f"Most Stressful Task: {most_stressful_task}\n")
                f.write(f"Least Stressful Task: {least_stressful_task}\n")
                if additional_feedback:
                    f.write(f"Additional Feedback: {additional_feedback}\n")
                f.write("=" * 50 + "\n")
            st.success("Thank you for your feedback!")
        except Exception as e:
            st.error(f"Failed to save feedback: {e}")

# Main Function
def time_constraint_task():
    st.title("Time-Constrained Tasks")
    st.write("""
    Welcome to the time-constrained tasks! Complete the following activities within their respective time limits. 
    Your performance and stress levels will be recorded.
    """)

    word_rephrase_task()
    report_writing_task()
    python_program_task()
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)  # Adding extra space
    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal lin
    collect_feedback()