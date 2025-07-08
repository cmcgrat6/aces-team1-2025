# run pip install pyqt6 SpeechRecognition pyttsx3 PyAudio pycaw screen-brightness-control
# press any button to go to its specific screen 

from PyQt6.QtWidgets import QApplication, QSlider, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QGridLayout, QStackedLayout
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, Qt

import speech
import sys, time
from datetime import datetime

# Trip computer. Updates distance traveled every second. Currently moving at 60 km/h
class tripThread(QRunnable):
    @pyqtSlot()
    def run(self):
        tripDistance = 0
        speed = 60
        timeCount = 0
        while True:
            time.sleep(1)
            timeCount = datetime.now()
            tripDistance = tripDistance + ((speed / 60 )/ 60)
            window.tripDistanceLabel.setText("Distance travelled: " + str(round(tripDistance,2)) + "km")
            window.speedLabel.setText("Speed: " + str(speed) + "km/h")
            window.timeLabel.setText("Trip Time: " + str(timeCount.hour) + ":" + str(timeCount.minute) + ":" + str(timeCount.second))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Define the stylesheet for the windows
        with open("styles.css", "r") as file:
            self.setStyleSheet(file.read())
        self.threadPool = QThreadPool()

        self.setWindowTitle("Really early version")
    
        # Define each different layout 
        container = QWidget()
        layout = QGridLayout()
        homeScreenLayout = QGridLayout(container)
        self.stackLayout = QStackedLayout()

        # Define each button for the home screen
        button1 = self.define_button("images/radio.png", 200,200,self.change_screen, 1)
        button2 = self.define_button("images/maps.png",200,200,self.change_screen,2)
        button3 = self.define_button("images/tripcomputer.png",200,200,self.change_screen,3)
        button4 = self.define_button("images/phone.png",200,200,self.change_screen,4)
        button5 = self.define_button("images/messages.png",200,200,self.change_screen,5)
        button6 = self.define_button("images/bluetooth.png",200,200,self.change_screen,6)
        button7 = self.define_button("images/seat.png",200,200,self.change_screen,7)
        button8 = self.define_button("images/settings.png",200,200,self.change_screen,8)

        # Add the home screen buttons to the home screen with grid coordinates
        homeScreenLayout.addWidget(button1, 0, 0)
        homeScreenLayout.addWidget(button2, 0, 1)
        homeScreenLayout.addWidget(button3, 0, 2)
        homeScreenLayout.addWidget(button4, 0, 3)
        homeScreenLayout.addWidget(button5, 1, 0)
        homeScreenLayout.addWidget(button6, 1, 1)
        homeScreenLayout.addWidget(button7, 1, 2)
        homeScreenLayout.addWidget(button8, 1, 3)

        # Create the "go home" button
        homeButton = QPushButton("Back to main screen")
        homeButton.clicked.connect(lambda: self.change_screen(0))

        # Create the radio menu and associated buttons
        radioContainer = QWidget()
        radioGridContainer = QWidget()
        radioList = QHBoxLayout(radioContainer)
        radioMenu = QGridLayout(radioGridContainer)
        self.radioLabel = QLabel("Now listening to:")
        self.radioLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        radioButton1 = self.define_button("RTE 1", 200,60,self.change_station, "RTE 1")
        radioButton2 = self.define_button("RTE 2", 200,60,self.change_station, "RTE 2")
        radioButton3 = self.define_button("Newstalk", 200,60,self.change_station, "Newstalk")
        radioButton4 = self.define_button("SPIN SW", 200,60,self.change_station, "SPIN SW")
        radioList.addWidget(radioButton1)
        radioList.addWidget(radioButton2)
        radioList.addWidget(radioButton3)
        radioList.addWidget(radioButton4)
        radioMenu.addWidget(self.radioLabel)
        radioMenu.addWidget(radioContainer)
        radioBack = self.define_button("Back", 160, 40, self.change_screen, 0)
        radioMenu.addWidget(radioBack)

        #Create the trip computer menu
        tripContainer = QWidget()
        tripMenu = QVBoxLayout(tripContainer)
        self.tripDistanceLabel = QLabel("")
        self.speedLabel = QLabel("")
        self.timeLabel = QLabel("")
        self.tripDistanceLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tripMenu.addWidget(self.timeLabel)
        tripMenu.addWidget(self.speedLabel)
        # tripMenu.addWidget(self.tripDistanceLabel)
        tripBack = self.define_button("Back", 160, 40, self.change_screen, 0) # Cannot copy a button, have to create a new one for each menu. I know.
        tripMenu.addWidget(tripBack)

        # Add the different main screens to the stack layout (main window that will change when something happens)
        self.stackLayout.addWidget(container)
        self.stackLayout.addWidget(radioGridContainer)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(tripContainer)
        # The next 5 are just for testing purposes, so each button does something.
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)

        # Add the stack layout and text input to the main menu
        layout.addLayout(self.stackLayout, 0, 0)

        # Define the main widget for every visible element
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedHeight(450)
        self.setFixedWidth(900)

        # Create and start running the speech to text and trip computer threads 
        speechT = self.speechThread()
        tripT = tripThread()
        self.threadPool.start(speechT)
        self.threadPool.start(tripT)

    # Swap screens to specified index
    def change_screen(self, index):
        self.stackLayout.setCurrentIndex(index)

    # Change radio stations
    def change_station(self,station):
        self.radioLabel.setText("Now listening to: " + station)
    
    # Create a button with an icon or text field, width, height and connect it to a method that needs an argument
    def define_button(self, iconOrText, w, h, method, methodArg):
        button = QPushButton()
        if ".png" in iconOrText: 
            button.setIcon(QtGui.QIcon(iconOrText))
            button.setIconSize(QtCore.QSize(w,h))
        else:
            button.setText(iconOrText)
        button.setFixedSize(QtCore.QSize(w+2,h+2))
        button.clicked.connect(lambda: method(methodArg))
        return button
      
    # Thread class to run the speech recognition in the background
    class speechThread(QRunnable):
        @pyqtSlot()
        def run(self):
            while True:
                text = speech.main()
                if (type(text) is int):
                    window.change_screen(text)
                else:
                    window.change_station(text)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()



