import streamlit as st
import time
import random
from datetime import datetime
import os

# Import your task tracking functions
from tasks.tracking import start_tracking, stop_tracking  # Assuming tasks.tracking is available

def essay_writing_with_interruptions():
    st.title("Essay Writing with Interruptions")
    st.write("""
    This task requires you to write a short essay based on the provided topic and clues. 
    While you are writing, simulated email interruptions will distract you. 
    You must handle the interruptions and complete your essay within the time limit.
    """)

    # --- Essay Topic & Clues ---
    essay_topic = "The impact of technology on modern society"
    clues = [
        "Social media", 
        "Artificial intelligence", 
        "Automation", 
        "Digital divide", 
        "Cybersecurity", 
        "Remote work", 
        "E-commerce", 
        "Climate change"  # Irrelevant clue
    ]
    st.write(f"**Essay Topic:** {essay_topic}")
    st.write("**Clues:**", ", ".join(clues))

    # --- Time Constraint (e.g., 5 minutes) ---
    time_limit = 300  # 5 minutes in seconds

    # --- Timer Placeholder ---
    timer_placeholder = st.empty()

    # --- Session State Initialization ---
    if "task_started" not in st.session_state:
        st.session_state["task_started"] = False
        st.session_state["start_time"] = None
        st.session_state["remaining_time"] = time_limit
        st.session_state["user_input"] = ""

    # --- Start Task Button ---
    if "start_button_clicked" not in st.session_state:
        st.session_state["start_button_clicked"] = False

    if st.button("Start Task") and not st.session_state["task_started"]:
        st.session_state["start_button_clicked"] = True
        st.session_state["start_time"] = time.time()
        start_tracking()  # Begin tracking user interaction

    # --- Timer Logic ---
    if st.session_state["start_button_clicked"]:
        if st.session_state["task_started"]:
            current_time = time.time()
            elapsed_time = current_time - st.session_state["start_time"]
            remaining_time = max(time_limit - int(elapsed_time), 0)
            st.session_state["remaining_time"] = remaining_time

            # Display Timer
            if remaining_time > 0:
                timer_placeholder.info(f"⏳ Time Remaining: {remaining_time} seconds")
                time.sleep(1)  # Wait for 1 second

                # Simulate Email Arrival (every 2 seconds)
                if random.random() < 0.5:  # 50% chance per second
                    email_type = random.choice(
                        ["Task-Relevant", "Project-Related", "Irrelevant"]
                    )
                    message = random.choice(
                        {
                            "Task-Relevant": [
                                "Hint: Consider the ethical implications of AI.",
                                "Research suggests a correlation between social media use and mental health."
                            ],
                            "Project-Related": [
                                "Meeting scheduled for tomorrow to discuss project progress."
                            ],
                            "Irrelevant": [
                                "Company social event next week!",
                            ],
                        }[email_type]
                    )
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    st.sidebar.write(
                        f"**{timestamp}** - **{email_type}** - {message}"
                    )

                # Track user input for the essay
                user_input = st.text_area("Write your essay:", height=200)
                st.session_state["user_input"] = user_input

                st.rerun()  # Rerun to update timer and potentially display emails
            else:
                timer_placeholder.warning("⏰ Time's up!")
                st.balloons()

                # Display Results
                st.write("Your Essay:")
                st.write(user_input)

                # Save results to file
                try:
                    os.makedirs("data", exist_ok=True)
                    file_path = "data/essay_writing_interrupt_results.txt"

                    with open(file_path, "a") as f:
                        f.write(f"Essay Topic: {essay_topic}\n")
                        f.write("Clues: " + ", ".join(clues) + "\n")
                        f.write("User Essay:\n")
                        f.write(user_input + "\n")
                        f.write("=" * 50 + "\n")
                    st.success(f"Results saved to `{file_path}`.")
                except Exception as e:
                    st.error(f"Failed to write results: {e}")

                stop_tracking()

                # --- Multiple Choice Questions ---
                st.write("Time to answer some multiple choice questions based on your essay.")

                questions = [
                    {"question": "What was the main topic of your essay?", "options": ["Technology", "Sports", "Health", "Education"], "answer": "Technology"},
                    {"question": "Which of these was NOT a clue provided for your essay?", "options": ["E-commerce", "Cybersecurity", "Global warming", "Remote work"], "answer": "Global warming"}
                ]

                for q in questions:
                    answer = st.radio(q["question"], q["options"], key=q["question"])
                    if answer == q["answer"]:
                        st.success("Correct!")
                    else:
                        st.error("Wrong answer. The correct answer was: " + q["answer"])

if __name__ == "__main__":
    essay_writing_with_interruptions()