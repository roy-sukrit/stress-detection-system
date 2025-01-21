import streamlit as st
import random
import time
import uuid

def combination_task():
    st.header("Combination Task: Time Constraints and Interruptions")
    st.write("""
    This task combines time constraints and random interruptions. 
    You need to complete the main task within the given time while handling interruptions effectively.
    """)

    # Main Task: Typing a paragraph under a time constraint
    paragraph = "Stress levels can significantly impact productivity and mental health. Analyzing digital behavior offers valuable insights."
    st.write(f"Main Task: Type the following paragraph within the given time:\n`{paragraph}`")
    user_input = st.text_area("Start typing here:", key="combination_task")

    # Timer setup for the task (e.g., 90 seconds)
    task_duration = 90  # seconds
    st.info(f"You have {task_duration} seconds to complete the task.")

    # Interruptions setup
    interruptions = [
        {"type": "popup", "message": "Click this button to dismiss the interruption."},
        {"type": "alert", "message": "Read and acknowledge this alert."},
        {"type": "question", "message": "Answer this question: What's 7 + 4?"}
    ]

    # Initialize logging
    interruption_responses = []
    task_start_time = time.time()
    time_remaining = task_duration

    # Counter for unique keys
    interruption_count = 0

    while time_remaining > 0:
        # Display remaining time
        time_elapsed = time.time() - task_start_time
        time_remaining = task_duration - time_elapsed
        st.info(f"Time Remaining: {int(time_remaining)} seconds")

        # Simulate random interruptions
        if random.random() < 0.3:  # 30% chance of an interruption every second
            interruption = random.choice(interruptions)
            unique_key = f"interruption_{interruption_count}"  # Ensure unique key for every interruption
            if interruption["type"] == "popup":
                if st.button(interruption["message"], key=unique_key):
                    interruption_responses.append({"type": "popup", "response": "Handled", "time": time_elapsed})
                    st.success("You dismissed the popup!")
            elif interruption["type"] == "alert":
                st.warning(interruption["message"])
                if st.button("Acknowledge", key=unique_key):
                    interruption_responses.append({"type": "alert", "response": "Acknowledged", "time": time_elapsed})
                    st.success("You acknowledged the alert!")
            elif interruption["type"] == "question":
                # user_answer = st.text_input(interruption["message"], key=unique_key)
                user_answer = st.text_input(interruption["message"], key=f"question_{len(interruption_responses)}_{uuid.uuid4()}"
)
                if user_answer:
                    interruption_responses.append({"type": "question", "response": user_answer, "time": time_elapsed})
                    st.success("You answered the question!")
            interruption_count += 1  # Increment counter for unique keys

        # Break if time runs out
        if time_remaining <= 0:
            break

        # Small delay to avoid overwhelming the user with interruptions
        time.sleep(1)

    # Task end
    st.success("Task complete! Thank you for your participation.")

    # Log results
    st.write("**Interruption Responses**:")
    for idx, response in enumerate(interruption_responses, start=1):
        st.write(f"Interruption {idx}: {response}")

    # Save results
    with open("data/combination_task_results.txt", "a") as f:
        f.write(f"User Input: {user_input}\n")
        f.write(f"Interruption Responses: {interruption_responses}\n")
        f.write("=" * 50 + "\n")