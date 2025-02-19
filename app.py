import random
import streamlit as st
from tasks.time_constraint import gifPaths, time_constraint_task
from tasks.interruption import run_all_tasks
from tasks.combination import run_combination_tasks
from tasks.rest import spot_the_mistake_wrapper
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_FORM_LINK = os.getenv("GOOGLE_FORM")

VIDEO_INTERRUPTIONS = os.getenv("VIDEO_INTERRUPTIONS")
VIDEO_COMBINATION = os.getenv("VIDEO_COMBINATION")

st.title("Cognitive Stress Experiment")

# Only show the message if the form is not completed
form_completed = st.checkbox("I have completed the questionnaire ✅")

if not form_completed:
    st.warning(f"🚨 Please complete the [questionnaire]({GOOGLE_FORM_LINK}) before proceeding! 📝")
    st.image(random.choice(gifPaths()), caption="Keep Going! 😂")

else:
    task_type = st.sidebar.selectbox(
        "Select Task Type", 
        ["Time Constraint", "Interruption", "Combination","No Stressor"]
    )

  
   
    if task_type == "Time Constraint":
        time_constraint_task()
    elif task_type == "Interruption":
        run_all_tasks(VIDEO_INTERRUPTIONS)
    elif task_type == "Combination":
        st.sidebar.image(random.choice(gifPaths()), caption="Keep Going! 😂")
        run_combination_tasks(VIDEO_COMBINATION)
        st.sidebar.image(random.choice(gifPaths()), caption="Keep Going! 😂")
        
    elif task_type =="No Stressor":
        spot_the_mistake_wrapper()    