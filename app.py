import streamlit as st
from tasks.time_constraint import time_constraint_task
from tasks.interruption import run_all_tasks
from tasks.combination import run_combination_tasks
from tasks.tracking import start_tracking
    
st.title("Cognitive Stress Experiment ")

task_type = st.sidebar.selectbox(
    "Select Task Type", 
    ["Time Constraint", "Interruption", "Combination"]
)

if task_type == "Time Constraint":
    time_constraint_task()
elif task_type == "Interruption":
    # interruption_task()
    run_all_tasks()
elif task_type == "Combination":
    run_combination_tasks()