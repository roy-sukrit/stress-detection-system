import random
import streamlit as st
from tasks.time_constraint import gifPaths, time_constraint_task
from tasks.interruption import run_all_tasks
from tasks.combination import run_combination_tasks
from tasks.rest import spot_the_mistake_wrapper
from dotenv import load_dotenv
import os
from streamlit_scroll_to_top import scroll_to_here  # Import the library
from streamlit_option_menu import option_menu  # Import the option menu

load_dotenv()

GOOGLE_FORM_LINK = os.getenv("GOOGLE_FORM")
VIDEO_INTERRUPTIONS = os.getenv("VIDEO_INTERRUPTIONS")
VIDEO_COMBINATION = os.getenv("VIDEO_COMBINATION")

# Step 1: Initialize scroll state in session_state
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False

# Step 2: Define a scroll function to trigger the state change
def scroll():
    st.session_state.scroll_to_top = True

st.title("Cognitive Stress Experiment")

# Only show the message if the form is not completed
form_completed = st.checkbox("I have completed the questionnaire ✅")

if not form_completed:
    st.warning(f"🚨 Please complete the [questionnaire]({GOOGLE_FORM_LINK}) before proceeding! 📝")
    st.image(random.choice(gifPaths()), caption="Keep Going! 😂")

else:
    # Store the selected task type in session state
    if "task_type" not in st.session_state:
        st.session_state["task_type"] = "Time Constraint"  # Default task type

    # Use streamlit-option-menu for task selection in the sidebar
    with st.sidebar:
        task_type = option_menu(
            menu_title="Select Task",  # Menu title
            options=["Time Constraint", "Interruption", "No Stressor", "Combination"],  # Task options
            icons=["clock", "play", "pause", "gear"],  # Icons for each option
            default_index=["Time Constraint", "Interruption", "No Stressor", "Combination"].index(st.session_state["task_type"]),  # Default selected index
            orientation="vertical",  # Vertical menu
            key="selected_task_type"
        )

    # Check if the task type has changed
    if task_type != st.session_state["task_type"]:
        st.session_state["task_type"] = task_type  # Update the task type in session state
        scroll_to_here(0, key='top')
    # Run the selected task
    if st.session_state["task_type"] == "Time Constraint":
        time_constraint_task()
    elif st.session_state["task_type"] == "Interruption":
        run_all_tasks(VIDEO_INTERRUPTIONS)
    elif st.session_state["task_type"] == "Combination":
        st.sidebar.image(random.choice(gifPaths()), caption="Keep Going! 😂")
        run_combination_tasks(VIDEO_COMBINATION)
        st.sidebar.image(random.choice(gifPaths()), caption="Keep Going! 😂")
    elif st.session_state["task_type"] == "No Stressor":
        spot_the_mistake_wrapper()

    # Scroll to the top if scroll_to_top is True
    if st.session_state.scroll_to_top:
        scroll_to_here(0, key='top')  # Use scroll_to_here to scroll to the top
        st.session_state.scroll_to_top = False  # Reset the state after scrolling