from pynput.keyboard import Listener
import csv

keystroke_logs = []

def on_press(key):
    keystroke_logs.append({"key": key, "event": "press"})

with Listener(on_press=on_press) as listener:
    listener.join()

# Save logs
with open('data/keystroke_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['key', 'event']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(keystroke_logs)