import os
from dotenv import load_dotenv
import streamlit as st
import random
import time
import uuid
from streamlit_autorefresh import st_autorefresh
from tracking.tracking import start_tracking, stop_tracking
from tasks.time_constraint import gifPaths, save_results
from tracking.tracking import collect_feedback

def combination_task(VIDEO_COMBINATION,COMBINATION_TIMER):
    """Task combining a timer and interruptions while writing an email based on a video."""

    # Initialize session state variables
    if "task_started" not in st.session_state:
        st.session_state.task_started = False
    if "last_interrupt_time" not in st.session_state:
        st.session_state.last_interrupt_time = time.time()
    if "interrupt_interval" not in st.session_state:
        st.session_state.interrupt_interval = random.randint(0,int(COMBINATION_TIMER))  # Random interval (5-10 sec)
    if "interrupt" not in st.session_state:
        st.session_state.interrupt = False
    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None  # Store the selected audio file
    if "time_remaining" not in st.session_state:
        st.session_state.time_remaining = 180  # Timer set to 3 minutes (180 seconds)
    if "email_draft" not in st.session_state:
        st.session_state.email_draft = ""  # Initialize only if not set

    # Auto-refresh every second to update the timer
    st_autorefresh(interval=1000, key="auto_refresh")

    # App Title
    st.title("Timed Email Writing Task with Interruptions")

    # Step 1: Play Video
    
     
    if VIDEO_COMBINATION:
     st.video(f"{VIDEO_COMBINATION}")  
    else:
     st.warning("Loading video... ")
    
    
    
   
    st.write("**Watch the video and write a professional email about how Duolingo uses methods like gamification, streaks, notifications, etc., which can be used in your company.**")
    st.write("🔔 **You will face random interruptions while writing!**")

    # Step 2: Define multiple audio interruptions
    interruption_files = [
        "music/crowd-clapping.mp3",
        "music/crowd-murmuring.mp3",
        "music/crowd-noise.mp3",    ]

    # Step 3: Start Task Button
    if not st.session_state.task_started:

        if st.button("Start Task"):
            st.session_state.task_started = True
            st.session_state.last_interrupt_time = time.time()
            st.session_state.interrupt = False
            st.session_state.audio_file = None
            st.session_state.time_remaining = 180  # Reset timer to 3 minutes
            st.session_state.email_draft = ""  # Reset email draft
            start_tracking("Task 5: Combination Task")


    # Step 4: Timer Logic
    if st.session_state.task_started:
        if st.session_state.time_remaining > 0:
            st.session_state.time_remaining -= 1
        else:
            st.warning("⏳ **Time's up! Please submit your email.**")

        # Display the countdown timer
        st.write(f"⏰ **Time Remaining:** {st.session_state.time_remaining} seconds")

    # Step 5: Email Writing Input Box (Improved UI with Subject and To)
    st.write("**To:** stephen.johnson@gmail.com")  # Static email recipient
    st.write("**Subject:** How Duolingo's Methods Can Enhance Your Company")
    
    email_draft = st.text_area(
        "📧 Write your email based on the video:",
        value=st.session_state.email_draft,
        key="email_draft",
        height=250,
        help="Make sure to include a professional greeting, the body, and a conclusion.",
            label_visibility="hidden"  # ✅ Proper way to hide labels

    )

    st.write("**Structure Suggestions**:")
    st.write("1. **Greeting:** Start with a formal greeting like 'Dear [Recipient's Name],'")
    st.write("2. **Body:** Discuss how Duolingo uses gamification, streaks, notifications, etc.")
    st.write("3. **Closing:** End with a formal closing like 'Sincerely,' followed by your name.")
    st.write("🔑 **Remember:** The email should have a clear flow from greeting to body to closing.")


    # Step 6: Handle Interruptions
    if st.session_state.task_started and st.session_state.time_remaining > 0:
        current_time = time.time()
        if current_time - st.session_state.last_interrupt_time >= st.session_state.interrupt_interval:
            st.session_state.interrupt = True
            st.session_state.last_interrupt_time = current_time
            st.session_state.interrupt_interval = random.randint(8, 12)  # Set new random interval
            st.session_state.audio_file = random.choice(interruption_files)  # Select a random audio file

        # Play interruption audio if triggered
        if st.session_state.interrupt and st.session_state.audio_file:
            st.warning("🔊 **Interruption! Stay focused!**")
            st.audio(st.session_state.audio_file, format="audio/mp3", autoplay=True)
            st.session_state.interrupt = False  # Reset interrupt flag

    # Step 7: Submit Button (End Task)
    if st.session_state.task_started:
        if st.button("Submit Email") or st.session_state.time_remaining <= 0:
            st.success("✅ Email submitted successfully!")
            st.balloons()

            st.write("📨 **Your Email Draft:**")
            st.write(email_draft)  # Display user's draft
            st.session_state.task_started = False  # Stop task
            stop_tracking("Task 5: Combination Task")
            save_results("Task 5: Combination Task",email_draft)



def run_combination_tasks(VIDEO_COMBINATION):
    load_dotenv()

    COMBINATION_TIMER = os.getenv("COMBINATION_TIMER")

    combination_task(VIDEO_COMBINATION,COMBINATION_TIMER)

    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)  # Adding extra space
    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal lin

    collect_feedback("Combination Task")


