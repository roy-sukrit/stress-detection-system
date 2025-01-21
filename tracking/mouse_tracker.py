from pynput.mouse import Listener
import csv

mouse_logs = []

def on_move(x, y):
    mouse_logs.append({"event": "move", "x": x, "y": y})

with Listener(on_move=on_move) as listener:
    listener.join()

# Save logs
with open('data/mouse_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['event', 'x', 'y']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(mouse_logs)