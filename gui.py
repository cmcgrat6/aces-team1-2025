# run pip install pyqt6 SpeechRecognition pyttsx3 PyAudio pycaw screen-brightness-control
# press any button to go to its specific screen 

from PyQt6.QtWidgets import QApplication, QScrollArea, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QGridLayout, QStackedLayout
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, Qt
from PyQt6.QtGui import QPixmap

import speech
from screendimmer import ListenerThread
import sys, time, webbrowser
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Define the stylesheet for the windows
        with open("styles.css", "r") as file:
            self.setStyleSheet(file.read())

        self.setWindowTitle("Speed Sensitive Screen")
    
        # Define each different layout 
        container = QWidget()
        layout = QGridLayout()
        homeScreenLayout = QGridLayout(container)
        self.stackLayout = QStackedLayout()

        # Create button, label and scrollArea list so we can enable / disable all of them at once later
        self.buttons = []
        # Create labels list so we can dim them all at once later
        self.labels = []
        
        # Add the home screen buttons to the home screen with grid coordinates
        homeScreenLayout.addWidget(self.define_button("images/radio.png", 200,200,self.change_screen, 1), 0, 0)
        homeScreenLayout.addWidget(self.define_button("images/maps.png",200,200,self.change_screen,2), 0, 1)
        homeScreenLayout.addWidget(self.define_button("images/tripcomputer.png",200,200,self.change_screen,3), 0, 2)
        homeScreenLayout.addWidget(self.define_button("images/phone.png",200,200,self.change_screen,4), 0, 3)
        homeScreenLayout.addWidget(self.define_label("Radio"),1,0)
        homeScreenLayout.addWidget(self.define_label("Navigation"),1,1)
        homeScreenLayout.addWidget(self.define_label("Trip Computer"),1,2)
        homeScreenLayout.addWidget(self.define_label("Phone"),1,3)
        homeScreenLayout.addWidget(self.define_button("images/vehicleinfo.png",200,200,self.change_screen,5), 2, 0)
        homeScreenLayout.addWidget(self.define_button("images/bluetooth.png",200,200,self.change_screen,6), 2, 1)
        homeScreenLayout.addWidget(self.define_button("images/messages.png",200,200,self.change_screen,7), 2, 2)
        homeScreenLayout.addWidget(self.define_button("images/settings.png",200,200,self.change_screen,8), 2, 3)
        homeScreenLayout.addWidget(self.define_label("Vehicle"),3,0)
        homeScreenLayout.addWidget(self.define_label("Bluetooth"),3,1)
        homeScreenLayout.addWidget(self.define_label("Messages"),3,2)
        homeScreenLayout.addWidget(self.define_label("Settings"),3,3)

        # Create the radio menu and associated buttons
        radioContainer = QWidget()
        radioGridContainer = QWidget()
        radioList = QHBoxLayout(radioContainer)
        radioMenu = QGridLayout(radioGridContainer)
        self.radioLabel = self.define_label("Radio Off")
        self.radioLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Define and add radio stations
        radioList.addWidget(self.define_button("RTE 1", 200,60,self.change_station, "Now listening to: RTE 1"))
        radioList.addWidget(self.define_button("RTE 2", 200,60,self.change_station, "Now listening to: RTE 2"))
        radioList.addWidget(self.define_button("Newstalk", 200,60,self.change_station, "Now listening to: Newstalk"))
        radioList.addWidget(self.define_button("SPIN SW", 200,60,self.change_station, "Now listening to: SPIN SW"))
        radioMenu.addWidget(self.radioLabel)
        radioMenu.addWidget(radioContainer)
        radioMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the maps menu
        mapContainer = QWidget()
        mapMenu = QVBoxLayout(mapContainer)
        mapImage = QLabel()
        mapImage.setStyleSheet("border-width:1px;")
        mapImage.setPixmap(QPixmap("images/mapimage.png"))
        mapMenu.addWidget(mapImage)
        end = QLineEdit()
        end.setMaximumSize(300,40)
        end.setStyleSheet("width:200px;height:30px;background-color:white;color:black;")
        mapMenu.addWidget(end)
        mapMenu.addWidget(self.define_button("Submit", 160, 40, self.navigate, end))
        mapMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the trip computer menu
        tripContainer = QWidget()
        tripMenu = QVBoxLayout(tripContainer)
        # Add the text labels for speed, distance and trip time. The trip computer thread will update these values after initialisaion
        self.tripDistanceLabel = self.define_label("")
        self.speedLabel = self.define_label("")
        self.timeLabel = self.define_label("")
        self.rangeLabel = self.define_label("")
        self.tripDistanceLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rangeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tripMenu.addWidget(self.timeLabel)
        tripMenu.addWidget(self.speedLabel)
        tripMenu.addWidget(self.tripDistanceLabel)
        tripMenu.addWidget(self.rangeLabel)
        tripMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the phone contacts list
        phoneContainer = QWidget()
        phoneMenu = QVBoxLayout(phoneContainer)
        phoneScroll = QScrollArea()
        # Add contacts list and place them into scroll menu
        self.contacts = ["Amy", "Caitlin", "Dave work", "Home", "John", "John", "Landlord", "Lisa", "Monica", "Morgan", 
                         "Paul", "Pizza", "Sean", "Sylvester do not answer", "Tyrell"]
        for name in self.contacts:
            phoneMenu.addWidget(self.define_label(name))
        phoneMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))
        # Set scroll menu rules
        phoneScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        phoneScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        phoneScroll.setWidgetResizable(True)
        phoneScroll.setWidget(phoneContainer)

        # Create the vehicle information screen
        infoContainer = QWidget()
        infoMenu = QGridLayout(infoContainer)
        infoSidebarContainer = QWidget()
        infoSidebar = QVBoxLayout(infoSidebarContainer)
        # Define basic information about the car and add an image of the car
        infoSidebar.addWidget(self.define_label("Driver door open"))
        infoSidebar.addWidget(self.define_label("Temperature: 47°C"))
        infoSidebar.addWidget(self.define_label("No driver seatbelt"))
        infoSidebar.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))
        carImage = self.define_label("")
        carImage.setStyleSheet("border-width:0px;")
        carImage.setPixmap(QPixmap("images/car.png"))
        infoMenu.addWidget(infoSidebarContainer,0,0)
        infoMenu.addWidget(carImage, 0,1)
        
        # Create the bluetooth screen
        bluetoothContainer = QWidget()
        bluetoothMenu = QVBoxLayout(bluetoothContainer)
        
        # 1. Bluetooth Status
        statusGroup = QVBoxLayout()
        statusGroup.addWidget(self.define_label("<b>Bluetooth Status</b>"))
        self.btToggle = self.define_button("Bluetooth: On", 160, 40, self.toggle_bluetooth, None)
        statusGroup.addWidget(self.btToggle)
        self.visibilityLabel = self.define_label("Visible to other devices")
        statusGroup.addWidget(self.visibilityLabel)
        bluetoothMenu.addLayout(statusGroup)
        
        # 2. Paired Devices List
        pairedGroup = QVBoxLayout()
        pairedGroup.addWidget(self.define_label("<b>Paired Devices</b>"))
        self.pairedDevices = ["Amy's Phone", "Car Audio", "John's Tablet"]
        for device in self.pairedDevices:
            deviceLayout = QHBoxLayout()
            deviceLayout.addWidget(self.define_label(device))
            deviceLayout.addWidget(self.define_button("Connect", 80, 30, self.connect_device, device))
            deviceLayout.addWidget(self.define_button("Remove", 80, 30, self.remove_device, device))
            pairedGroup.addLayout(deviceLayout)
        bluetoothMenu.addLayout(pairedGroup)
        
        # 3. Add New Device / Pair New Device
        pairGroup = QVBoxLayout()
        pairGroup.addWidget(self.define_label("<b>Add New Device</b>"))
        pairGroup.addWidget(self.define_label("Make sure your device is discoverable"))
        pairGroup.addWidget(self.define_button("Pair New Device", 160, 40, self.pair_new_device, None))
        bluetoothMenu.addLayout(pairGroup)
        bluetoothMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the messages screen
        # Create the widgets and layouts needed for the screen
        messageContainer = QWidget()
        messageLayout = QVBoxLayout(messageContainer)
        messageMenuContainer = QWidget()
        messagesMenu = QVBoxLayout(messageMenuContainer)
        messageScrollContainer = QWidget()
        messagesScroll = QScrollArea(messageScrollContainer)
        # Add all of the contacts to the scroll area
        for name in self.contacts:
            messagesMenu.addWidget(self.define_button(name, 800, 50, self.open_messages, name))
        # Set the scroll area rules and add each widget to the correct place
        messagesScroll.setMinimumSize(850,500)
        messagesScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        messagesScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        messagesScroll.setWidgetResizable(True)
        messagesScroll.setWidget(messageMenuContainer)
        messageLayout.addWidget(messageScrollContainer)
        messageLayout.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))
        # Create a texts container with associated widgets to be used later by open_messages
        self.textsContainer = QWidget()
        self.textsMenu = QVBoxLayout(self.textsContainer)
        self.message = self.define_label("")
        self.messageWidgets = []

        # Create the settings screen
        settingsContainer = QWidget()
        settingsMenu = QVBoxLayout(settingsContainer)
        # Add some basic settings and attach methods
        self.radioToggle = self.define_button("Radio: On", 160, 40, self.change_station, "Radio Off")
        factorySettings = self.define_button("Language", 160, 40, self.change_screen, 10)
        systemInfo = self.define_button("System Information", 160, 40, self.change_screen, 11)
        copyrightButton = self.define_button("Copyright", 160, 40, self.change_screen, 12)
        settingsMenu.addWidget(self.radioToggle)
        settingsMenu.addWidget(factorySettings)
        settingsMenu.addWidget(systemInfo)
        settingsMenu.addWidget(copyrightButton)
        settingsMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the languages screen
        languageContainer = QWidget()
        langaugeVBox = QVBoxLayout(languageContainer)
        for name in ["English (UK)","English (US)","English (Ireland)"]:
            newLayout = QHBoxLayout()
            newLayout.addWidget(self.define_button(name,300,150,self.change_screen,8))
            newLayout.addWidget(self.define_button("images/"+name+".png",300,150,self.change_screen,8))
            langaugeVBox.addLayout(newLayout)
        langaugeVBox.addWidget(self.define_button("Back", 160, 40, self.change_screen, 8))

        # Create the information menu
        informationContainer = QWidget()
        informationMenu = QVBoxLayout(informationContainer)
        informationText = self.define_label("How to use:\nAfter running this program, run speedtest.py.\nInteract with this menu" \
        ", ideally with the touchscreen.\nYou may also say 'Hey Jaguar' to use the voice control system.\nUse the slider included in speedtest.py" \
        "to adjust the simulated speed.\nFor safety, the GUI will not be interactable past 60km/h." \
        "\nUse the voice control system past this point.")
        informationMenu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        informationMenu.addWidget(informationText)
        informationMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 8))

        # Create the copyright menu with credits
        copyrightContainer = QWidget()
        copyrightScreen = QVBoxLayout(copyrightContainer)
        copyrightText = self.define_label("By Conor McGrath, Nasrin Shamaeian, Jie Song Tan, \nShaun Purcell and Shane Easo." \
        "\nCreated for the JLR Shannon Undergraduates ACES Challenge 2025. \nSpecial thanks to John Lawless and Lee Skrypchuk " \
        "\nfor their guidance on the project's direction.")
        copyrightText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyrightScreen.addWidget(copyrightText)
        copyrightScreen.addWidget(self.define_button("Back", 160, 40, self.change_screen, 8))
    
        # Add the different main screens to the stack layout (main window that will change when something happens)
        self.containers = [container, radioGridContainer, mapContainer, tripContainer, phoneScroll, 
                      infoContainer, bluetoothContainer, messageContainer, settingsContainer, self.textsContainer, 
                      languageContainer, informationContainer, copyrightContainer]
        for c in self.containers:
            self.stackLayout.addWidget(c)

        # Add the stack layout and text input to the main menu
        layout.addLayout(self.stackLayout, 0, 0)

        # Define the main widget for every visible element
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedHeight(600)
        self.setFixedWidth(900)

        # Define thread pool to run background threads
        self.threadPool = QThreadPool()
        # Create and start running the speech to text and trip computer threads 
        speechT = self.speechThread()
        self.tripT = self.tripThread()
        # Instantiate the listener thread and connect its signal
        self.listener = ListenerThread()
        self.listener.speed_received.connect(self.adjust_dimming)
        self.listener.start()  # Begin background listening
        self.threadPool.start(speechT)
        self.threadPool.start(self.tripT)

    # Swap screens to specified index
    def change_screen(self, index):
        self.stackLayout.setCurrentIndex(index)

    # Change radio stations
    def change_station(self,station):
        self.radioLabel.setText(station)
        if (self.radioToggle.text() == "Radio: On"):
            self.radioToggle.setText("Radio: Off")
        else:
            self.radioToggle.setText("Radio: On")

    # Adjust the brightness of the screen and enable / disable buttons
    def adjust_dimming(self, speed:int):
        self.tripT.speed = speed
        if speed < 40:
            alpha = 0
            disable = False
        elif speed < 60:
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
        for b in self.buttons:
            b.setEnabled(not disable)
        if disable == True: textColour = "rgb(93,93,93)"
        else: textColour = "rgb(0,0,0)"

        # Apply a semi-transparent black overlay
        for container in self.containers:
            container.setStyleSheet(
                f"background-color: rgba(0, 0, 0, {alpha});"
            )
        for button in self.buttons:
            button.setStyleSheet(
                f"background-color: rgba(255,255,255, {alpha}); color:{textColour};"
            )
        for label in self.labels:
            label.setStyleSheet(
                f"background-color: rgba(255, 255, 255, {alpha});" 
            )

    # Get messages from the messages file for the specific contact and display them
    def open_messages(self, name):
        for widget in self.messageWidgets:
            self.textsMenu.removeWidget(widget)
        self.messageWidgets = []
        length = len(name)
        messagesExist = False
        messagesFile = open("messages.txt", "r")
        for line in messagesFile:
            if name in line[:length]:
                messagesExist = True
                widget = self.define_label(line)
                widget.setMinimumHeight(60)
                if "From" in line[length:length+5]: 
                    widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    widget.setText(line[length + 6:])
                else: 
                    widget.setAlignment(Qt.AlignmentFlag.AlignRight)
                    widget.setText(line[length + 4:])
                self.messageWidgets.append(widget)
                self.textsMenu.addWidget(widget)
        if (not messagesExist): 
            widget = self.define_label("No messages available.")
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.messageWidgets.append(widget)
            self.textsMenu.addWidget(widget)
        backButton = self.define_button("Back", 160, 40, self.change_screen, 7)
        self.textsMenu.addWidget(backButton)
        self.messageWidgets.append(backButton)
        self.change_screen(9)

    # Create a button with an icon or text field, width, height and connect it to a method 
    def define_button(self, iconOrText, w, h, method, methodArg):
        button = QPushButton()
        if ".png" in iconOrText: 
            button.setIcon(QtGui.QIcon(iconOrText))
            button.setIconSize(QtCore.QSize(w,h))
        else:
            button.setText(iconOrText)
        button.setFixedSize(QtCore.QSize(w+2,h+2))
        button.clicked.connect(lambda: method(methodArg))
        self.buttons.append(button)
        button.setStyleSheet("background-color: rgb(255, 255, 255);")
        return button
    
    # Create a label with a text field. Exists because dimming the screen without redefining background colour for each label will dim them until they are unreadable
    def define_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("background-color: white;")
        self.labels.append(label)
        return label

    # --- Bluetooth screen methods ---
    def toggle_bluetooth(self, _):
        if self.btToggle.text() == "Bluetooth: On":
            self.btToggle.setText("Bluetooth: Off")
            self.visibilityLabel.setText("Not visible to other devices")
        else:
            self.btToggle.setText("Bluetooth: On")
            self.visibilityLabel.setText("Visible to other devices")

    def connect_device(self, device):
        self.activeDeviceLabel.setText(f"Connected to: {device}")
        self.signalLabel.setText("Signal: Good")
        self.batteryLabel.setText("Battery: 85%")
        self.errorLabel.setText("")

    def remove_device(self, device):
        self.errorLabel.setText(f"{device} removed from paired devices.")
        
    def pair_new_device(self, _):
        self.errorLabel.setText("Pairing failed: Device not found.")

    # Open Google Maps with the specified start and end destinations (temp)
    def navigate(self, end):
        url = f"https://www.google.com/maps/dir/{"V14 T863"}/{end.text()}"
        webbrowser.open(url)

    # Thread class to run the speech recognition in the background
    class speechThread(QRunnable):
        @pyqtSlot()
        def run(self):
            while True:
                text = speech.main()
                # Voice commands to change screen will be denoted by an index, otherwise (for now) it changes radio station
                # Any other methods like telegram messaging are not handled by this program, so they are not returned
                if (type(text) is int):
                    window.change_screen(text)
                else:
                    window.change_station(text)

    # Trip computer. Updates distance traveled every second.
    class tripThread(QRunnable):
        @pyqtSlot()
        def run(self):
            tripDistance = 0
            self.speed = 0
            counter = 0
            range = 500
            while True:
                time.sleep(1)
                counter = counter + 1
                timeTracker  = datetime.fromtimestamp(counter)
                timeString = timeTracker.strftime("%H:%M:%S")
                tripDistance = tripDistance + ((self.speed / 60 )/ 60)
                range = range - ((self.speed / 60 )/ 60)
                window.tripDistanceLabel.setText("Distance travelled: " + str(round(tripDistance,2)) + "km")
                window.speedLabel.setText("Speed: " + str(self.speed) + "km/h")
                window.timeLabel.setText("Trip Time: " + timeString)
                window.rangeLabel.setText("Range: " + str(round(range,2)) + "km")

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()