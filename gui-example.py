# run pip install pyqt6 SpeechRecognition pyttsx3 PyAudio pycaw screen-brightness-control
# press any button to go to its specific screen 

from PyQt6.QtWidgets import QApplication, QScrollArea, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, \
    QPushButton, QLineEdit, QGridLayout, QStackedLayout
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, Qt
from PyQt6.QtGui import QPixmap

import speech
import sys, time, webbrowser
from datetime import datetime

from phone_menu import create_phone_menu


# Trip computer. Updates distance traveled every second. Currently moving at 60 km/h
class TripThread(QRunnable):
    @pyqtSlot()
    def run(self):
        tripDistance = 0
        speed = 80
        counter = 0
        while True:
            time.sleep(1)
            counter = counter + 1
            timeTracker = datetime.fromtimestamp(counter)
            timeString = timeTracker.strftime("%H:%M:%S")
            tripDistance = tripDistance + ((speed / 60) / 60)
            window.tripDistanceLabel.setText("Distance travelled: " + str(round(tripDistance, 2)) + "km")
            window.speedLabel.setText("Speed: " + str(speed) + "km/h")
            window.timeLabel.setText("Trip Time: " + timeString)


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
        button1 = self.define_button("images/radio.png", 200, 200, self.change_screen, 1)
        button2 = self.define_button("images/maps.png", 200, 200, self.change_screen, 2)
        button3 = self.define_button("images/tripcomputer.png", 200, 200, self.change_screen, 3)
        button4 = self.define_button("images/phone.png", 200, 200, self.change_screen, 4)
        button5 = self.define_button("images/vehicleinfo.png", 200, 200, self.change_screen, 5)
        button6 = self.define_button("images/bluetooth.png", 200, 200, self.change_screen, 6)
        button7 = self.define_button("images/seat.png", 200, 200, self.change_screen, 7)
        button8 = self.define_button("images/settings.png", 200, 200, self.change_screen, 8)

        # Add the home screen buttons to the home screen with grid coordinates
        homeScreenLayout.addWidget(button1, 0, 0)
        homeScreenLayout.addWidget(button2, 0, 1)
        homeScreenLayout.addWidget(button3, 0, 2)
        homeScreenLayout.addWidget(button4, 0, 3)
        homeScreenLayout.addWidget(QLabel("Radio"), 1, 0)
        homeScreenLayout.addWidget(QLabel("Navigation"), 1, 1)
        homeScreenLayout.addWidget(QLabel("Trip Computer"), 1, 2)
        homeScreenLayout.addWidget(QLabel("Phone"), 1, 3)
        homeScreenLayout.addWidget(button5, 2, 0)
        homeScreenLayout.addWidget(button6, 2, 1)
        homeScreenLayout.addWidget(button7, 2, 2)
        homeScreenLayout.addWidget(button8, 2, 3)
        homeScreenLayout.addWidget(QLabel("Vehicle"), 3, 0)
        homeScreenLayout.addWidget(QLabel("Bluetooth"), 3, 1)
        homeScreenLayout.addWidget(QLabel("Seat"), 3, 2)
        homeScreenLayout.addWidget(QLabel("Settings"), 3, 3)

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
        radioButton1 = self.define_button("RTE 1", 200, 60, self.change_station, "RTE 1")
        radioButton2 = self.define_button("RTE 2", 200, 60, self.change_station, "RTE 2")
        radioButton3 = self.define_button("Newstalk", 200, 60, self.change_station, "Newstalk")
        radioButton4 = self.define_button("SPIN SW", 200, 60, self.change_station, "SPIN SW")
        radioList.addWidget(radioButton1)
        radioList.addWidget(radioButton2)
        radioList.addWidget(radioButton3)
        radioList.addWidget(radioButton4)
        radioMenu.addWidget(self.radioLabel)
        radioMenu.addWidget(radioContainer)
        radioBack = self.define_button("Back", 160, 40, self.change_screen, 0)
        radioMenu.addWidget(radioBack)

        # Create the maps menu(?)
        mapContainer = QWidget()
        mapMenu = QVBoxLayout(mapContainer)
        mapMenu.addWidget(self.define_button("images/mapimage.png", 450, 288, self.change_screen, 2))
        self.start = QLineEdit()
        self.start.setStyleSheet("width: 200px; height:30px;")
        end = QLineEdit()
        end.setStyleSheet("width: 200px; height:30px;")
        navButton = self.define_button("Submit", 200, 50, self.navigate, end)
        mapMenu.addWidget(self.start)
        mapMenu.addWidget(end)
        mapMenu.addWidget(navButton)
        mapMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the trip computer menu
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
        tripMenu.addWidget(self.tripDistanceLabel)
        tripMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the phone contacts list
        phoneContainer = QWidget()
        phoneMenu = QVBoxLayout(phoneContainer)
        phoneScroll = QScrollArea()
        names = ["Amy", "Carl", "Dave work", "Home", "John", "John", "Landlord", "Monica", "Morgan", "Pizza", "Tyrell"]
        for name in names:
            phoneMenu.addWidget(QLabel(name))
        phoneMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))
        phoneScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        phoneScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        phoneScroll.setWidgetResizable(True)
        phoneScroll.setWidget(phoneContainer)

        # Create the vehicle information screen
        infoContainer = QWidget()
        infoMenu = QGridLayout(infoContainer)
        carIcon = self.define_button("images/car.png", 500, 500, self.change_screen, 5)
        carIcon.setStyleSheet("background-color: rgb(250, 250, 250);")
        infoMenu.addWidget(QLabel("Doors open"), 0, 0)
        infoMenu.addWidget(QLabel("Temperature: 47°C"), 1, 0)
        infoMenu.addWidget(QLabel("No Driver Seatbelt"), 2, 0)
        infoMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0), 3, 0)
        infoMenu.addWidget(carIcon, 0, 1)

        # Create the bluetooth screen

        # Create the seat screen

        # Create the settings screen
        settingsContainer = QWidget()
        settingsMenu = QVBoxLayout(settingsContainer)
        self.radioToggle = self.define_button("Radio: On", 160, 40, self.change_station, "")
        factorySettings = self.define_button("Factory Settings", 160, 40, self.change_screen, 0)
        systemInfo = self.define_button("System Information", 160, 40, self.change_screen, 0)
        copyrightButton = self.define_button("Copyright", 160, 40, self.change_screen, 0)
        settingsMenu.addWidget(self.radioToggle)
        settingsMenu.addWidget(factorySettings)
        settingsMenu.addWidget(systemInfo)
        settingsMenu.addWidget(copyrightButton)
        settingsMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        phoneMenuWidget = create_phone_menu(self.change_screen, self.define_button)

        # Add the different main screens to the stack layout (main window that will change when something happens)
        self.stackLayout.addWidget(container)
        self.stackLayout.addWidget(radioGridContainer)
        self.stackLayout.addWidget(mapContainer)
        self.stackLayout.addWidget(tripContainer)
        self.stackLayout.addWidget(phoneMenuWidget)
        self.stackLayout.addWidget(infoContainer)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(settingsContainer)

        # Add the stack layout and text input to the main menu
        layout.addLayout(self.stackLayout, 0, 0)

        # Define the main widget for every visible element
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedHeight(600)
        self.setFixedWidth(900)

        # Create and start running the speech to text and trip computer threads
        speechT = self.SpeechThread()
        tripT = TripThread()
        self.threadPool.start(speechT)
        self.threadPool.start(tripT)

    # Swap screens to specified index
    def change_screen(self, index):
        self.stackLayout.setCurrentIndex(index)

    # Change radio stations
    def change_station(self, station):
        self.radioLabel.setText("Now listening to: " + station)
        if self.radioToggle.text() == "Radio: On":
            self.radioToggle.setText("Radio: Off")
        else:
            self.radioToggle.setText("Radio: On")

    # Create a button with an icon or text field, width, height and connect it to a method that needs an argument
    def define_button(self, iconOrText, w, h, method, methodArg):
        button = QPushButton()
        if ".png" in iconOrText:
            button.setIcon(QtGui.QIcon(iconOrText))
            button.setIconSize(QtCore.QSize(w, h))
        else:
            button.setText(iconOrText)
        button.setFixedSize(QtCore.QSize(w + 2, h + 2))
        button.clicked.connect(lambda: method(methodArg))
        return button

    # Open Google Maps with the specified start and end destinations (temp)
    def navigate(self, end):
        url = f"https://www.google.com/maps/dir/{self.start.text()}/{end.text()}"
        webbrowser.open(url)

    # Thread class to run the speech recognition in the background
    class SpeechThread(QRunnable):
        @pyqtSlot()
        def run(self):
            while True:
                text = speech.main()
                if type(text) is int:
                    window.change_screen(text)
                else:
                    window.change_station(text)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
