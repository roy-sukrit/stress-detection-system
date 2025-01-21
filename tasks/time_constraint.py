import streamlit as st
import time
import os
from tasks.tracking import start_tracking, stop_tracking

def time_constraint_task():
    st.header("Time-Constrained Task")
    st.write("""
    In this task, you will have a limited amount of time to complete the activity.
    Try to perform as efficiently as possible within the time constraint.
    """)

    task_description = "Reorder the following words to form a coherent sentence:"
    words = ["stress", "analyzing", "Cognitive", "digital", "behaviors", "involves"]
    correct_sentence = "Cognitive stress involves analyzing digital behaviors."
    st.write(f"Task: {task_description}")
    st.write(f"Words to reorder: `{', '.join(words)}`")

    user_input = st.text_area("Type your reordered sentence here:")

    time_limit = 10
    timer_placeholder = st.empty()

    if "task_started" not in st.session_state:
        st.session_state["task_started"] = False
        st.session_state["start_time"] = None
        st.session_state["remaining_time"] = time_limit

    if "start_button_clicked" not in st.session_state:
        st.session_state["start_button_clicked"] = False

    if st.button("Start Task") and not st.session_state["task_started"]:
        st.session_state["start_button_clicked"] = True
        st.session_state["task_started"] = True
        st.session_state["start_time"] = time.time()
        start_tracking()  

    if st.session_state["start_button_clicked"]:
        if st.session_state["task_started"]:
            current_time = time.time()
            elapsed_time = current_time - st.session_state["start_time"]
            remaining_time = max(time_limit - int(elapsed_time), 0)
            st.session_state["remaining_time"] = remaining_time

            if remaining_time > 0:
                timer_placeholder.info(f"⏳ Time Remaining: {remaining_time} seconds")
                time.sleep(1)
                st.rerun()
            else:
                timer_placeholder.warning("⏰ Time's up!")
                st.balloons()

                st.write(f"Your input: {user_input}")
                if user_input.strip() == correct_sentence:
                    st.success("Correct! Well done!")
                else:
                    st.error("Incorrect. The correct sentence is:")
                    st.write(f"`{correct_sentence}`")

                try:
                    os.makedirs("data", exist_ok=True)
                    file_path = "data/time_constraint_results.txt"
                    with open(file_path, "a") as f:
                        f.write(f"User Input: {user_input}\n")
                        f.write(f"Correct Sentence: {correct_sentence}\n")
                        f.write("=" * 50 + "\n")
                    st.success(f"Results saved to `{file_path}`.")
                except Exception as e:
                    st.error(f"Failed to write results: {e}")

                stop_tracking()

                #Collect user feedback on stress level
                st.subheader("Stress Level Feedback")
                st.write("On a scale of 1 to 10, how stressed did you feel during the task?")
                stress_level = st.slider("Rate your stress level:", 1, 10, 5)

                # Save stress level feedback to file
                if st.button("Submit Feedback"):
                    try:
                        with open(file_path, "a") as f:
                            f.write(f"Stress Level: {stress_level}/10\n")
                            f.write("=" * 50 + "\n")
                        st.success("Thank you for your feedback!")
                    except Exception as e:
                        st.error(f"Failed to save feedback: {e}")

