import sys                     
import socket                  
from PyQt6.QtWidgets import (
    QApplication,              # Core application object for Qt
    QWidget,                   # Base class for all UI widgets
    QLabel,                    # Widget to display text or images
    QPushButton,               # Clickable button widget
    QGridLayout                # Grid layout manager for arranging widgets
)
from PyQt6.QtCore import (
    pyqtSignal,                 
    QThread,            
    Qt                          
)

# Network configuration for incoming speed values
HOST = 'localhost'
PORT = 65432

class ListenerThread(QThread):
    """
    Worker thread that listens on a TCP socket for incoming speed values.
    Emits a Qt signal with the received speed so the UI can react safely.
    """
    # Define a signal carrying an integer (the new speed)
    speed_received = pyqtSignal(int)
    def run(self):
        """
        Thread entry point.
        Binds to HOST:PORT, listens for connections, reads speed data,
        and emits speed_received whenever valid data arrives.
        """
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Allow re-binding quickly after restarting the app
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))    # Bind to the specified host and port
            s.listen()              # Start listening for incoming connections

            # Continuously accept new connections
            while True:
                conn, _addr = s.accept()   # Block until a client connects
                with conn:
                    data = conn.recv(1024)  
                    if data:
                        # Decode bytes to string, convert to int, emit signal
                        speed = int(data.decode())
                        self.speed_received.emit(speed)

class ScreenDimmer(QWidget):
    """
    Main application window that dims its contents based on incoming speed.
    Displays six buttons in a 2×3 grid and overlays a semi-transparent
    black layer when speed crosses certain thresholds.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Dimmer")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background: white;")  # Default background

        # Overlay label covering the entire window, used for dimming effect
        self.overlay = QLabel(self)
        self.overlay.setGeometry(0, 0, 400, 250)
        # Start hidden—will be shown/hidden in adjust_dimming()
        self.overlay.hide()

        # Create a grid layout for six action buttons
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.buttons = []
        for i in range(6):
            # Create each button labeled Action 1 … Action 6
            btn = QPushButton(f"Action {i+1}")
            btn.setStyleSheet("font-size: 14px; padding: 8px;")
            self.buttons.append(btn)

            # Place first three in column 0, next three in column 1
            col = 0 if i < 3 else 1
            row = i % 3
            layout.addWidget(btn, row, col)

        self.setLayout(layout)

        # Instantiate the listener thread and connect its signal
        self.listener = ListenerThread()
        self.listener.speed_received.connect(self.adjust_dimming)
        self.listener.start()  # Begin background listening

    def adjust_dimming(self, speed: int):
        """
        Slot that adjusts the overlay opacity and button states
        in response to a new speed value.
        """
        # Below 40 km/h: full brightness, no overlay, all buttons enabled
        if speed < 40:
            self.overlay.hide()
            for btn in self.buttons:
                btn.setEnabled(True)
            return

        # Determine overlay alpha and button-disable flag by speed range
        if speed < 60:
            alpha = 60
            disable = False
        elif speed < 80:
            alpha = 100
            disable = True
        elif speed < 100:
            alpha = 140
            disable = True
        elif speed < 120:
            alpha = 180
            disable = True
        else:
            alpha = 215
            disable = True

        # Apply a semi-transparent black overlay
        self.overlay.setStyleSheet(
            f"background-color: rgba(0, 0, 0, {alpha});"
        )
        self.overlay.show()
        # Ensure overlay sits below buttons so they remain clickable/visible
        self.overlay.lower()

        # Enable or disable buttons based on the disable flag
        for btn in self.buttons:
            btn.setEnabled(not disable)

if __name__ == "__main__":
    # Qt application boilerplate
    app = QApplication(sys.argv)
    w = ScreenDimmer()
    w.show()
    sys.exit(app.exec())
