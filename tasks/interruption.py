from dotenv import load_dotenv
import streamlit as st
import time
import os
import datetime
import random
from typing import List
from streamlit_autorefresh import st_autorefresh

from tasks.time_constraint import save_results
from tracking.tracking import start_tracking, stop_tracking
from tracking.tracking import collect_feedback


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


# Function to simulate interruptions based on a random timer
def interruption_task(VIDEO_INTERRUPTIONS,INTERRUPTIONS_TIMER):
    """Handles stress detection task with interruptions."""

    # Initialize session state variables
    if "task_started" not in st.session_state:
        st.session_state.task_started = False
    if "last_interrupt_time" not in st.session_state:
        st.session_state.last_interrupt_time = time.time()
    if "interrupt_interval" not in st.session_state:
        st.session_state.interrupt_interval = random.randint(0,10)  # Random interval (5-10 sec)
    if "interrupt" not in st.session_state:
        st.session_state.interrupt = False
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    # Auto-refresh every 5 seconds to check for interruptions
    st_autorefresh(interval=5000, key="auto_refresh")

    # App Title
    st.title("Interruption-Based Task")

    # Step 1: Play Video
    
    if VIDEO_INTERRUPTIONS:
       st.video(VIDEO_INTERRUPTIONS)
    else:
     st.warning("Loading video... ")
    
    
    

    st.write("**Watch the video and answer the questions. Interruptions will occur!**")

    # Step 2: Define questions
    questions = [
        "What was the main topic of the video?",
        "What are some scientifically proven ways to improve memory and focus, as mentioned in the talk?",
        "Why is physical activity considered beneficial for brain health, and how does it help in counteracting the effects of stress?",
    ]
    
    interruption_files = [
    os.getcwd() + "/music/1.mp3",
    os.getcwd() + "/music/3.mp3",
    os.getcwd() + "/music/4.mp3",
    os.getcwd() + "/music/5.mp3",
    os.getcwd() + "/music/6.mp3",
    os.getcwd() + "/music/7.mp3",
    os.getcwd() + "/music/8.mp3"
     ]

    # Step 3: Start Task Button
    if not st.session_state.task_started:
        if st.button("Start Task"):

            st.session_state.task_started = True
            st.session_state.last_interrupt_time = time.time()
            st.session_state.interrupt = False
            st.session_state.answers = {f"question_{idx}": "" for idx in range(1, len(questions) + 1)}
            st.write("**Task started! Answer the questions below. Interruptions will occur!**")
            start_tracking("Task 4: Interruptions Task")


    # Step 4: Display Questions
    if st.session_state.task_started:
        for idx, question in enumerate(questions, start=1):
            answer_key = f"question_{idx}"
            st.session_state.answers[answer_key] = st.text_input(
                f"Q{idx}: {question}",
                value=st.session_state.answers[answer_key],
                key=answer_key,
            )

    # Step 5: Handle interruptions
    if st.session_state.task_started:
        current_time = time.time()
        if current_time - st.session_state.last_interrupt_time >= st.session_state.interrupt_interval:
            st.session_state.interrupt = True
            st.session_state.last_interrupt_time = current_time
            st.session_state.interrupt_interval = random.randint(20, 120)  # Set new random interval

        # Play interruption audio if triggered
        if st.session_state.interrupt:
            st.warning("🔊 **Interruption! Stay focused!**")
            st.audio(random.choice(interruption_files), format="audio/mp3",autoplay=True)
            st.session_state.interrupt = False  # Reset interrupt flag

    # Step 6: Submit Button (End Task)
    if st.session_state.task_started:
        if st.button("Submit Answers"):
            st.success("✅ Responses submitted successfully!")
            st.write("**Your Answers:**")
            st.balloons()

            for idx, question in enumerate(questions, start=1):
                st.write(f"Q{idx}: {st.session_state.answers[f'question_{idx}']}")
            st.session_state.task_started = False  # Stop task
            stop_tracking("Task 4: Interruptions Task")
            formatted_answers = "\n".join([f"{key}: {value}" for key, value in st.session_state.answers.items()])
            save_results("Task 4: Interruptions Task",formatted_answers)



def run_all_tasks(VIDEO_INTERRUPTIONS):
    load_dotenv()

    # INTERRUPTIONS_TIMER = os.getenv("INTERRUPTIONS_TIMER")
    INTERRUPTIONS_TIMER = 720

    # print("INTERRUPTIONS_TIMER==>",INTERRUPTIONS_TIMER)
    interruption_task(VIDEO_INTERRUPTIONS,INTERRUPTIONS_TIMER)
     
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)  # Adding extra space
    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal lin
    collect_feedback("Interruptions Task")