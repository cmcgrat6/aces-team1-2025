"""
run with screendimmer.py
"""

import sys                   
import socket                
import threading            
from PyQt6.QtWidgets import (
    QApplication,            # Main Qt application
    QWidget,                 # Base class for all UI objects
    QVBoxLayout,             # Vertical layout manager
    QSlider,                 # Slider widget
    QLabel,                  # Display text or image
    QHBoxLayout,             # Horizontal layout manager
    QPushButton              # Button widget
)
from PyQt6.QtCore import Qt

# Network configuration for sending speed values
HOST = 'localhost'
PORT = 65432

def send_speed(speed):
    """
    Connect to the receiver service and send the current speed.
    Runs in a separate thread to avoid blocking the UI.
    """
    try:
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            # Send the speed as a UTF-8 encoded string
            s.sendall(str(speed).encode())
    except ConnectionRefusedError:
        # If the server isn't listening, print a warning
        print("Receiver not running.")

class SpeedControl(QWidget):
    """
    Main widget containing a label, a slider, and +/- buttons
    to control and display speed in km/h.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speed Control")
        self.setFixedSize(400, 150)

        # Label to show the current speed
        self.label = QLabel("Speed: 0 km/h", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 16px;")

        # Horizontal slider ranging from 0 to 200
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 200)
        self.slider.setTickInterval(20)
        # Connect slider movement to handler
        self.slider.valueChanged.connect(self.on_speed_change)

        # Layout for the '+' and '–' buttons
        btn_layout = QHBoxLayout()
        for text, difference in [("–", -5), ("+", 5)]:
            btn = QPushButton(text)
            btn.setFixedWidth(50)
            # Pass the difference (+5 or -5) when the button is clicked
            btn.clicked.connect(lambda _, d=difference: self.adjust_speed(d))
            btn_layout.addWidget(btn)

        # Combine all widgets into the main vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def on_speed_change(self, val):
        """
        Slot called whenever the slider value changes.
        Updates the label and sends the new speed.
        """
        # Update the label text
        self.label.setText(f"Speed: {val} km/h")
        # Send speed in a daemon thread so the UI remains responsive
        threading.Thread(target=send_speed, args=(val,), daemon=True).start()

    def adjust_speed(self, difference):
        """
        Adjusts the slider by a fixed difference,
        ensuring the value stays within [0, 200].
        """
        new_val = max(0, min(200, self.slider.value() + difference))
        # This will trigger on_speed_change via the valueChanged signal
        self.slider.setValue(new_val)

if __name__ == "__main__":
    # Standard boilerplate to launch the Qt application
    app = QApplication(sys.argv)
    w = SpeedControl()
    w.show()
    sys.exit(app.exec())
