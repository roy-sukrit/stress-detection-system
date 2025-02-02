import streamlit as st
import time
import os
import datetime
import random
import threading
from typing import List
from PIL import Image


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

# Task 1: Click Accuracy Test
def click_accuracy_task(time_limit=10):
    task_name = "Click Accuracy Task"
    task_description = """
    In this task, you'll be presented with buttons that appear randomly on the screen. 
    You need to click as many buttons as possible before the time runs out!
    """
    
    st.subheader(f"{task_name}")
    st.write(task_description)

    # Time and click count tracking
    start_time = time.time()
    click_count = 0
    button_positions = []

    def generate_button():
        # Generate random button position
        x_pos = random.randint(0, 80)
        y_pos = random.randint(0, 80)
        button_positions.append((x_pos, y_pos))
        return st.button("Click me!", key=f"button_{len(button_positions)}", on_click=lambda: increment_click_count())

    def increment_click_count():
        nonlocal click_count
        click_count += 1

    timer_placeholder = st.empty()

    while time.time() - start_time < time_limit:
        # Show a button at a random location each second
        button = generate_button()
        time.sleep(1)
        timer_placeholder.info(f"⏳ Time Remaining: {time_limit - int(time.time() - start_time)} seconds")
        if time.time() - start_time > time_limit:
            break
    
    st.write(f"You clicked {click_count} times.")
    save_results(task_name, user_input=str(click_count))

# Task 2: Math Problem Solver
def math_problem_task(time_limit=15):
    task_name = "Math Problem Solver"
    task_description = """
    Solve as many math problems as you can within the time limit. 
    You will be presented with simple arithmetic problems.
    """

    st.subheader(f"{task_name}")
    st.write(task_description)

    problems = [("2 + 3", 5), ("7 * 3", 21), ("12 / 4", 3), ("15 - 6", 9)]
    random.shuffle(problems)

    start_time = time.time()
    user_answers = []

    for problem, correct_answer in problems:
        if time.time() - start_time > time_limit:
            break
        user_input = st.text_input(f"Solve: {problem}")
        if user_input:
            user_answers.append((problem, user_input, correct_answer))
            time.sleep(1)  # Delay for the user to see the problem

    st.write("Time's up!")
    for problem, user_input, correct_answer in user_answers:
        if str(user_input) == str(correct_answer):
            st.success(f"Correct: {problem} = {correct_answer}")
        else:
            st.error(f"Incorrect: {problem} = {correct_answer}")

    save_results(task_name, user_input=str(user_answers))

# Task 3: Image Recognition Task
def image_recognition_task(time_limit=10):
    task_name = "Image Recognition Task"
    task_description = """
    In this task, you need to identify specific objects from images within the time limit.
    Click on the image that contains the object you're looking for.
    """

    st.subheader(f"{task_name}")
    st.write(task_description)

    # Loading some example images
    image_1 = Image.open("path/to/image1.jpg")
    image_2 = Image.open("path/to/image2.jpg")
    correct_image = image_1

    start_time = time.time()

    # Display images to choose from
    st.image([image_1, image_2], caption=["Image 1", "Image 2"], use_column_width=True)

    if time.time() - start_time < time_limit:
        user_input = st.selectbox("Select the image with the object", ["Image 1", "Image 2"])
        
        if user_input == "Image 1":
            st.success("Correct!")
            save_results(task_name, user_input=user_input, correct_answer="Image 1")
        else:
            st.error("Incorrect! The correct image was Image 1.")

# Task 4: Typing Speed Test
def typing_speed_test(time_limit=30):
    task_name = "Typing Speed Test"
    task_description = """
    In this task, you need to type the sentence below as fast as possible. 
    The test will end after the time runs out.
    """

    sentence_to_type = "The quick brown fox jumps over the lazy dog."

    st.subheader(f"{task_name}")
    st.write(task_description)
    st.write(f"Type the following sentence as fast as you can: **{sentence_to_type}**")

    start_time = time.time()
    user_input = st.text_area("Start typing here:")

    while time.time() - start_time < time_limit:
        time.sleep(1)  # Give the user time to type
        if user_input.strip() == sentence_to_type:
            st.success("You typed it correctly!")
            break

    st.write("Time's up!")
    save_results(task_name, user_input=user_input)

# Task 5: Memory Recall Game
def memory_recall_game(time_limit=10):
    task_name = "Memory Recall Game"
    task_description = """
    In this task, you will see a sequence of numbers. 
    After the sequence is shown, type the numbers in the same order.
    The sequence will disappear after a short period.
    """

    sequence = [random.randint(1, 9) for _ in range(5)]  # Generate a sequence of 5 numbers
    sequence_shown = False

    st.subheader(f"{task_name}")
    st.write(task_description)

    start_time = time.time()

    # Show sequence for a brief time
    if time.time() - start_time < 3:
        st.write(f"Remember this sequence: {sequence}")
        time.sleep(3)  # Wait for 3 seconds to show the sequence
        st.write("Sequence hidden!")
        sequence_shown = True

    # Allow the user to input the sequence
    if sequence_shown and time.time() - start_time < time_limit:
        user_input = st.text_input("Enter the sequence of numbers:")

        if user_input == "".join(map(str, sequence)):
            st.success("Correct!")
        else:
            st.error(f"Incorrect! The correct sequence was: {''.join(map(str, sequence))}")
    save_results(task_name, user_input=user_input)


def ethical_dilemma_game():
    """
    Presents ethical dilemmas to the user with optional interruptions. 
    Users choose an action and rate their confidence.
    """

    st.title("Ethical Dilemma Game")

    dilemmas = [
        """A runaway trolley is headed towards five people tied to the tracks. 
        You have the option to switch the trolley to a different track, but there is one person tied to that track. 
        Do you switch the tracks?""",
        """A doctor has five patients, each in need of a different organ to survive. 
        A healthy traveler arrives at the hospital for a routine check-up. 
        Would it be ethically justifiable to kill the traveler and harvest their organs to save the five patients?""",
        """You witness your boss engaging in unethical behavior that could harm the company. 
        Do you report them, even if it could jeopardize your job and potentially damage your reputation?"""
    ]

    # List of image paths
    current_dir = os.path.dirname(__file__)  # Get the current directory

    image_paths = [
        os.path.join(current_dir, "images/image1.jpeg"), 
        os.path.join(current_dir, "images/image2.jpeg"),
        os.path.join(current_dir, "images/image3.jpeg") 
    ]

    # Select a random dilemma and image
    dilemma_index = random.randint(0, len(dilemmas) - 1)
    dilemma = dilemmas[dilemma_index]
    image_path = image_paths[dilemma_index]

    st.write(dilemma)

    # Decision options
    options = ["Yes", "No"]
    choice = st.radio("Choose an option:", options)

    # Confidence level
    confidence = st.slider("How confident are you in your decision?", 0, 100, 50)

    # Interruption settings
    st.sidebar.header("Interruption Settings")
    enable_interruptions = st.sidebar.checkbox("Enable Interruptions")
    interruption_type = st.sidebar.selectbox("Interruption Type", ["Auditory", "Visual", "None"])

    if st.button("Submit"):
        if enable_interruptions and interruption_type == "Visual":
            print("image_path ==>",image_path)
            st.image(image_path)
            # time.sleep(2)  # Short delay after visual interruption

        # Store data (replace with actual data storage logic)
        if choice and confidence:
            st.success("Response Submitted!")
            st.write(f"Choice: {choice}")
            st.write(f"Confidence Level: {confidence}%")

# Function to initialize session state variables

def interruption_task():
    """Handles stress detection task with interruptions."""

    # Initialize session state
    if "task_started" not in st.session_state:
        st.session_state.task_started = False
    if "last_interrupt_time" not in st.session_state:
        st.session_state.last_interrupt_time = time.time()
    if "interrupt_interval" not in st.session_state:
        st.session_state.interrupt_interval = random.randint(5, 10)  # Random interval (5-10 sec)
    if "interrupt" not in st.session_state:
        st.session_state.interrupt = False
    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    # App title
    st.title("Interruption-Based Task")

    # Step 1: Play Video
    st.video("https://www.youtube.com/watch?v=Nz9eAaXRzGg")
    st.write("**Watch the video and answer the questions. Interruptions will occur!**")

    # Step 2: Define questions
    questions = [
        "What was the main topic of the video?",
        "What key point did the speaker make about real-world applications?",
        "Summarize the conclusion in one sentence.",
    ]

    # Step 3: Define interruption sounds
    interruption_files = ["tasks/crowd-clapping-and-cheering-effect-272056.mp3"]

    # Step 4: Start Task Button
    if not st.session_state.task_started:
        if st.button("Start Task"):
            st.session_state.task_started = True
            st.session_state.last_interrupt_time = time.time()
            st.session_state.interrupt = False
            st.session_state.audio_file = None
            st.session_state.answers = {f"question_{idx}": "" for idx in range(1, len(questions) + 1)}
            st.write("**Task started! Answer the questions below. Interruptions will occur!**")

    # Step 5: Display Questions
    if st.session_state.task_started:
        for idx, question in enumerate(questions, start=1):
            answer_key = f"question_{idx}"
            st.session_state.answers[answer_key] = st.text_input(
                f"Q{idx}: {question}",
                value=st.session_state.answers[answer_key],
                key=answer_key,
            )

    # Step 6: Handle interruptions
    if st.session_state.task_started:
        interrupt_container = st.empty()  # Allows UI updates

        # Check if it's time for an interruption
        if time.time() - st.session_state.last_interrupt_time >= st.session_state.interrupt_interval:
            st.session_state.interrupt = True
            st.session_state.last_interrupt_time = time.time()
            st.session_state.interrupt_interval = random.randint(8, 12)  # Set new random interval
            st.session_state.audio_file = random.choice(interruption_files)

        # Play interruption audio if triggered
        if st.session_state.interrupt and st.session_state.audio_file:
            if os.path.exists(st.session_state.audio_file):
                with interrupt_container:
                    st.warning("🔊 Interruption! Stay focused!")
                    audio_placeholder = st.empty()  # Creates a temporary space for audio
                    audio_placeholder.audio(st.session_state.audio_file, format="audio/mp3",autoplay=True)
                    time.sleep(8)
                    audio_placeholder.empty()  # Clears the audio element

            else:
                st.error(f"Interruption file '{st.session_state.audio_file}' not found!")

            st.session_state.interrupt = False  # Reset interrupt flag

    # Step 7: Submit Button (End Task)
    if st.session_state.task_started:
        if st.button("Submit Answers"):
            st.success("✅ Responses submitted successfully!")
            st.write("**Your Answers:**")
            for idx, question in enumerate(questions, start=1):
                st.write(f"Q{idx}: {st.session_state.answers[f'question_{idx}']}")
            st.session_state.task_started = False  # Stop task

def run_all_tasks():
    st.title("Interactive Tasks with Time Constraints")
    interruption_task()
    # click_accuracy_task(time_limit=10)
    # math_problem_task(time_limit=15)
    # image_recognition_task(time_limit=10)
    # typing_speed_test(time_limit=30)
    # memory_recall_game(time_limit=10)
