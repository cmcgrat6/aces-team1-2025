# run pip install pyqt6 SpeechRecognition pyttsx3 PyAudio pycaw screen-brightness-control
# press any button to go to its specific screen 

from PyQt6.QtWidgets import QApplication, QScrollArea, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QGridLayout, QStackedLayout
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, Qt
from PyQt6.QtGui import QPixmap

#aimport speech
import sys, time, webbrowser
from datetime import datetime

# Trip computer. Updates distance traveled every second. Currently moving at 80 km/h
class tripThread(QRunnable):
    @pyqtSlot()
    def run(self):
        tripDistance = 0
        speed = 80
        counter = 0
        while True:
            time.sleep(1)
            counter = counter + 1
            timeTracker  = datetime.fromtimestamp(counter)
            timeString = timeTracker.strftime("%H:%M:%S")
            tripDistance = tripDistance + ((speed / 60 )/ 60)
            window.tripDistanceLabel.setText("Distance travelled: " + str(round(tripDistance,2)) + "km")
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
        button1 = self.define_button("images/radio.png", 200,200,self.change_screen, 1)
        button2 = self.define_button("images/maps.png",200,200,self.change_screen,2)
        button3 = self.define_button("images/tripcomputer.png",200,200,self.change_screen,3)
        button4 = self.define_button("images/phone.png",200,200,self.change_screen,4)
        button5 = self.define_button("images/vehicleinfo.png",200,200,self.change_screen,5)
        button6 = self.define_button("images/bluetooth.png",200,200,self.change_screen,6)
        button7 = self.define_button("images/seat.png",200,200,self.change_screen,7)
        button8 = self.define_button("images/settings.png",200,200,self.change_screen,8)

        # Add the home screen buttons to the home screen with grid coordinates
        homeScreenLayout.addWidget(button1, 0, 0)
        homeScreenLayout.addWidget(button2, 0, 1)
        homeScreenLayout.addWidget(button3, 0, 2)
        homeScreenLayout.addWidget(button4, 0, 3)
        homeScreenLayout.addWidget(QLabel("Radio"),1,0)
        homeScreenLayout.addWidget(QLabel("Navigation"),1,1)
        homeScreenLayout.addWidget(QLabel("Trip Computer"),1,2)
        homeScreenLayout.addWidget(QLabel("Phone"),1,3)
        homeScreenLayout.addWidget(button5, 2, 0)
        homeScreenLayout.addWidget(button6, 2, 1)
        homeScreenLayout.addWidget(button7, 2, 2)
        homeScreenLayout.addWidget(button8, 2, 3)
        homeScreenLayout.addWidget(QLabel("Vehicle"),3,0)
        homeScreenLayout.addWidget(QLabel("Bluetooth"),3,1)
        homeScreenLayout.addWidget(QLabel("Seat"),3,2)
        homeScreenLayout.addWidget(QLabel("Settings"),3,3)

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
        # Define and add radio stations
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

        # Create the maps menu(?)
        mapContainer = QWidget()
        mapMenu = QVBoxLayout(mapContainer)
        mapMenu.addWidget(self.define_button("images/mapimage.png",450,288, self.change_screen, 2))
        end = QLineEdit()
        end.setStyleSheet("width: 200px; height:30px;")
        navButton = self.define_button("Submit", 160, 40, self.navigate, end)
        mapMenu.addWidget(end)
        mapMenu.addWidget(navButton)
        mapMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))


        # Create the trip computer menu
        tripContainer = QWidget()
        tripMenu = QVBoxLayout(tripContainer)
        # Add the text labels for speed, distance and trip time. The trip thread will update these values after initialisaion
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
        # Add contacts list and place them into scroll menu
        names = ["Amy", "Carl", "Dave work", "Home", "John", "John","Landlord", "Monica", "Morgan", "Pizza", "Tyrell"]
        for name in names:
            phoneMenu.addWidget(QLabel(name))
        phoneMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))
        # Set scroll menu rules
        phoneScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        phoneScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        phoneScroll.setWidgetResizable(True)
        phoneScroll.setWidget(phoneContainer)

        # Create the vehicle information screen
        infoContainer = QWidget()
        infoMenu = QGridLayout(infoContainer)
        # Define basic information about the car and an image of the car
        carIcon = self.define_button("images/car.png", 500,500,self.change_screen, 5)
        carIcon.setStyleSheet("background-color: rgb(250, 250, 250);")
        infoMenu.addWidget(QLabel("Doors open"),0,0)
        infoMenu.addWidget(QLabel("Temperature: 47°C"),1,0)
        infoMenu.addWidget(QLabel("No Driver Seatbelt"),2,0)
        infoMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0),3,0)
        infoMenu.addWidget(carIcon, 0,1)
        
        # Create the bluetooth screen
        bluetoothContainer = QWidget()
        bluetoothMenu = QVBoxLayout(bluetoothContainer)
        
        # 1. Bluetooth Status
        statusGroup = QVBoxLayout()
        statusGroup.addWidget(QLabel("<b>Bluetooth Status</b>"))
        self.btToggle = self.define_button("Bluetooth: On", 160, 40, self.toggle_bluetooth, None)
        statusGroup.addWidget(self.btToggle)
        self.visibilityLabel = QLabel("Visible to other devices")
        statusGroup.addWidget(self.visibilityLabel)
        bluetoothMenu.addLayout(statusGroup)
        
        # 2. Paired Devices List
        pairedGroup = QVBoxLayout()
        pairedGroup.addWidget(QLabel("<b>Paired Devices</b>"))
        self.pairedDevices = ["Amy's Phone", "Car Audio", "John's Tablet"]
        for device in self.pairedDevices:
            deviceLayout = QHBoxLayout()
            deviceLayout.addWidget(QLabel(device))
            #a deviceLayout.addWidget(self.define_button("Connect", 80, 30, self.connect_device, device))
            #a deviceLayout.addWidget(self.define_button("Remove", 80, 30, self.remove_device, device))
            pairedGroup.addLayout(deviceLayout)
        bluetoothMenu.addLayout(pairedGroup)
        
        # 3. Add New Device / Pair New Device
        pairGroup = QVBoxLayout()
        pairGroup.addWidget(QLabel("<b>Add New Device</b>"))
        pairGroup.addWidget(QLabel("Make sure your device is discoverable"))
        #a pairGroup.addWidget(self.define_button("Pair New Device", 160, 40, self.pair_new_device, None))
        bluetoothMenu.addLayout(pairGroup)
        
        
        bluetoothMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))

        # Create the seat screen
        seatContainer = QWidget()
        seatMenu = QGridLayout(seatContainer)
        seatHeight = QLabel()
        seatHeight.setStyleSheet("border-width:0px;")
        seatHeight.setPixmap(QPixmap("images/seat-height.png"))
        seatDistance = QLabel()
        seatDistance.setStyleSheet("border-width:0px;")
        seatDistance.setPixmap(QPixmap("images/seat-distance.png"))
        self.seatHeat = QLabel()
        self.seatHeat.setStyleSheet("border-width:0px;")
        self.seatHeat.setPixmap(QPixmap("images/seat-heat-off.png"))
        self.backHeat = self.define_button("Back Heat: Off", 120, 40, self.set_seat_heat, "back")
        self.bottomHeat = self.define_button("Bottom Heat: Off", 120, 40, self.set_seat_heat, "bottom")
        self.backHeatToggle = False
        self.bottomHeatToggle = False
        seatMenu.addWidget(seatHeight,0,0)
        seatMenu.addWidget(seatDistance,0,1)
        seatMenu.addWidget(self.seatHeat,0,2)
        seatMenu.addWidget(self.define_button("Back", 80, 40, self.change_screen, 0),1,0)
        seatMenu.addWidget(self.backHeat,1,1)
        seatMenu.addWidget(self.bottomHeat,1,2)
        seatMenu.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create the settings screen
        settingsContainer = QWidget()
        settingsMenu = QVBoxLayout(settingsContainer)
        # Add some basic settings and attach methods
        self.radioToggle = self.define_button("Radio: On", 160, 40, self.change_station, "")
        factorySettings = self.define_button("Factory Settings", 160, 40, self.change_screen, 0)
        systemInfo = self.define_button("System Information", 160, 40, self.change_screen, 0)
        copyrightButton = self.define_button("Copyright", 160, 40, self.change_screen, 0)
        settingsMenu.addWidget(self.radioToggle)
        settingsMenu.addWidget(factorySettings)
        settingsMenu.addWidget(systemInfo)
        settingsMenu.addWidget(copyrightButton)
        settingsMenu.addWidget(self.define_button("Back", 160, 40, self.change_screen, 0))
    
        # Add the different main screens to the stack layout (main window that will change when something happens)
        containers = [container, radioGridContainer, mapContainer, tripContainer, phoneScroll, 
                      infoContainer, bluetoothContainer, seatContainer, settingsContainer]
        for c in containers:
            self.stackLayout.addWidget(c)

        # Add the stack layout and text input to the main menu
        layout.addLayout(self.stackLayout, 0, 0)

        # Define the main widget for every visible element
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedHeight(600)
        self.setFixedWidth(900)

        # Create and start running the speech to text and trip computer threads 
        speechT = self.speechThread()
        tripT = tripThread()
        #aself.threadPool.start(speechT)
        #aself.threadPool.start(tripT)

    # Swap screens to specified index
    def change_screen(self, index):
        self.stackLayout.setCurrentIndex(index)

    # Change radio stations
    def change_station(self,station):
        self.radioLabel.setText("Now listening to: " + station)
        if (self.radioToggle.text() == "Radio: On"):
            self.radioToggle.setText("Radio: Off")
        else:
            self.radioToggle.setText("Radio: On")
    
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
    
    # --- Bluetooth screen methods ---
    def toggle_bluetooth(self, _):
        if self.btToggle.text() == "Bluetooth: On":
            self.btToggle.setText("Bluetooth: Off")
            self.visibilityLabel.setText("Not visible to other devices")
        else:
            self.btToggle.setText("Bluetooth: On")
            self.visibilityLabel.setText("Visible to other devices")

    # Change seat heat regions
    def set_seat_heat(self, region):
        # Flip value for specified heat region
        if (region == "back"):
            if (self.backHeatToggle == True):
                self.backHeatToggle = False
                self.backHeat.setText("Back Heat: Off")
            else:
                self.backHeatToggle = True
                self.backHeat.setText("Back Heat: On") 
        else:
            if (self.bottomHeatToggle == True):
                self.bottomHeatToggle = False
                self.bottomHeat.setText("Bottom Heat: Off")
            else:
                self.bottomHeatToggle = True
                self.bottomHeat.setText("Bottom Heat: On")
        # Change image icon according to previous settings
        if self.backHeatToggle == False and self.bottomHeatToggle == False:
            self.seatHeat.setPixmap(QPixmap("images/seat-heat-off.png"))
        elif self.backHeatToggle == True and self.bottomHeatToggle == False:
            self.seatHeat.setPixmap(QPixmap("images/seat-heat-back.png"))
        elif self.backHeatToggle == False and self.bottomHeatToggle == True:
            self.seatHeat.setPixmap(QPixmap("images/seat-heat-bottom.png"))
        else:
            self.seatHeat.setPixmap(QPixmap("images/seat-heat-all.png"))
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

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()