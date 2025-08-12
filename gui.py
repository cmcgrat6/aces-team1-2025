# run pip install pyqt6 SpeechRecognition pyttsx3 PyAudio pycaw screen-brightness-control PyQt6-WebEngine requests
# press any button to go to its specific screen

from PyQt6.QtWidgets import QApplication, QScrollArea, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QGridLayout, QStackedLayout
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, Qt, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from urllib.parse import quote


import speech, phone_menu
from screendimmer import ListenerThread
import sys, time, webbrowser
from datetime import datetime
import pyttsx3
from speech import speechThread

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

        # map screen
        mapContainer = QWidget()
        mapMenu = QVBoxLayout(mapContainer)
        
        self.mapWebView = QWebEngineView()
        default_start = "Jaguar Land Rover Shannon"
        default_dest = ""
        url = f"https://www.google.com/maps/dir/{default_start}/{default_dest}"
        self.mapWebView.load(QUrl(url))
        mapMenu.addWidget(self.mapWebView)
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

        # Create the phone menu
        self.phoneScroll = phone_menu.create_phone_menu(self.change_screen, self.define_button)

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
        self.carImage = self.define_label("")
        self.carImage.setStyleSheet("border-width:0px;")
        self.carImage.setPixmap(QPixmap("images/car.png"))
        infoMenu.addWidget(infoSidebarContainer,0,0)
        infoMenu.addWidget(self.carImage, 0,1)

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
        self.amyPhone = self.define_label("Amy's Phone")
        self.carAudio = self.define_label("Car Audio")
        self.johnTablet = self.define_label("John's Tablet")
        pairedDevices = [self.amyPhone, self.carAudio, self.johnTablet]
        for device in pairedDevices:
            deviceLayout = QHBoxLayout()
            deviceLayout.addWidget(device)
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
        
        #for speech 
        self.messagesScroll = messagesScroll
        
        # Add all of the contacts to the scroll area
        self.contacts = ["Amy", "Caitlin", "Dave work", "Home", "John", "Landlord", "Lisa", "Monica", "Morgan", 
                         "Paul", "Pizza", "Sean", "Sylvester do not answer", "Tyrell"]
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
        copyrightButton = self.define_button("Credits", 160, 40, self.change_screen, 12)
        settingsMenu.addWidget(self.radioToggle)
        settingsMenu.addWidget(factorySettings)
        settingsMenu.addWidget(systemInfo)
        settingsMenu.addWidget(copyrightButton)
        settingsMenu.addWidget(self.define_button("Close program", 160, 40, self.exit_program, 0))
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
        " to adjust the simulated speed.\nFor safety, the GUI will not be interactable past 60km/h." \
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
        self.containers = [container, radioGridContainer, mapContainer, tripContainer, self.phoneScroll,
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

        self.current_screen = 0  # Main screen by default


        # Define thread pool to run background threads
        self.threadPool = QThreadPool()
        
        # speech to text signals and threads
        self.speechT = speechThread()
        self.speechT.signals.change_screen.connect(self.change_screen_voice)
        self.speechT.signals.change_station.connect(self.change_station_voice)
        self.speechT.signals.load_map.connect(self.load_map)
        self.speechT.signals.scroll.connect(self.scrollContent)
        self.speechT.signals.open_chat.connect(self.voice_open_chat)
        self.speechT.signals.toggle_bluetooth.connect(self.toggle_bluetooth_voice)
        self.speechT.signals.toggle_radio.connect(self.toggle_radio_voice)
        self.threadPool.start(self.speechT)
        
        # trip threads
        self.tripT = self.tripThread()
        # Instantiate the listener thread and connect its signal
        self.listener = ListenerThread()
        self.listener.speed_received.connect(self.adjust_dimming)
        self.listener.start()  # Begin background listening
        self.threadPool.start(self.tripT)

    # Exits the program. Crashes it at the moment, using exit() just freezes it
    def exit_program(self, device):
        self.exitProgramLabel.setText(f"Connected to: {device}")
    # Swap screens to specified index
    def change_screen(self, index):
        self.current_screen = index
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
            alpha = 30
            disable = False
        elif speed < 80:
            alpha = 50
            disable = True
        elif speed < 100:
            alpha = 70
            disable = True
        elif speed < 120:
            alpha = 90
            disable = True
        else:
            alpha = 110
            disable = True
        for b in self.buttons:
            b.setEnabled(not disable)
        if disable == True: textColour = 93
        else: textColour = 255

        if speed > 39:
            self.carImage.setPixmap(QPixmap("images/darkcar.png"))
        else:
            self.carImage.setPixmap(QPixmap("images/car.png"))
        # Apply a semi-transparent black overlay
        for container in self.containers:
            container.setStyleSheet(
                f"background-color: rgba(0, 0, 0, {alpha});"
            )
        for button in self.buttons:
            button.setStyleSheet(
                f"background-color: rgba({textColour}, {textColour}, {textColour}, {alpha});"
            )
        for label in self.labels:
            label.setStyleSheet(
                f"background-color: rgba(0, 0, 0, {alpha});" 
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
        
    def voice_open_chat(self, contact_name):
        self.open_messages(contact_name)
        
        # read message content
        messages = []
        with open("messages.txt", "r") as file:
            for line in file:
                if line.startswith(contact_name):
                    msg_start = line.find("From: ")
                    if msg_start != -1:
                        messages.append(line[msg_start + 6:].strip())
                    else:
                        msg_start = line.find("To: ")
                        if msg_start != -1:
                            messages.append(line[msg_start + 4:].strip())
    
        self.speechT.read_messages = messages


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
        text = device.text()
        if (not text.endswith(": Connected")):
            device.setText(text + ": Connected")

    def remove_device(self, device):
        text = device.text()
        if (text.endswith(": Connected")):
            device.setText(text[:-11])

    def pair_new_device(self, _):
        b = 5

    # open maps
    def load_map(self, url: str):
        self.mapWebView.load(QtCore.QUrl(url))

    def scrollContent(self, delta):
        current_screen = self.current_screen
        if current_screen == 4:  # phone screen
            scroll = self.phoneScroll
        elif current_screen == 7:  # messages screen
            scroll = self.messagesScroll
        else:
            print("Scroll not available on this screen.")
            return

        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().value() + delta)

    # change screen, station with voice commands
    def change_screen_voice(self, screen_num):
        self.change_screen(screen_num)

    def change_station_voice(self, station):
        print(f"Changing to station {station}")
        self.radioLabel.setText(station)
        if (self.radioToggle.text() == "Radio: On"):
            self.radioToggle.setText("Radio: Off")
        else:
            self.radioToggle.setText("Radio: On")

    def toggle_bluetooth_voice(self, turn_on):
        current_state = self.btToggle.text() == "Bluetooth: On"
        if turn_on != current_state:
            self.btToggle.click()  # click button (on/off)
    
    def toggle_radio_voice(self, turn_on):
        current_state = self.radioToggle.text() == "Radio: On"
        if turn_on != current_state:
            self.radioToggle.click()  # click button (on/off)

    def closeEvent(self, event):
        print("GUI closing, stopping speech and exiting...")
        if hasattr(self, 'speechT'):
            self.speechT.stop()   # stop speechThread
        event.accept()                 # close event
        QApplication.quit()            # quit application

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

sys.exit(app.exec())
