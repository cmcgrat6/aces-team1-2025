# a 4x2 grid with buttons in it placed in a hbox next to a slider.

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QGridLayout, QStackedLayout
from PyQt6.QtWidgets import QSlider
from PyQt6 import QtGui, QtCore

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Really early version")
    
        # Define each different layout 
        container = QWidget()
        layout = QGridLayout()
        homeScreenLayout = QGridLayout(container)
        self.stackLayout = QStackedLayout()

        # Define each button for the home screen
        button1 = self.define_button("images/radio.png", 100,100,self.change_screen, 1)
        button2 = self.define_button("images/maps.png",100,100,self.change_screen,2)
        button3 = self.define_button("images/tripcomputer.png",100,100,self.change_screen,3)
        button4 = self.define_button("images/phone.png",100,100,self.change_screen,4)
        button5 = self.define_button("images/messages.png",100,100,self.change_screen,5)
        button6 = self.define_button("images/bluetooth.png",100,100,self.change_screen,6)
        button7 = self.define_button("images/seat.png",100,100,self.change_screen,7)
        button8 = self.define_button("images/settings.png",100,100,self.change_screen,8)

        # Create the textField for "voice" input. Jie probably has something better than this already.
        self.textField = QLineEdit()
        self.textField.setText("A surrogate for voice input. Try deleting this and replacing with 'radio' or 'phone'")
        self.textField.textChanged.connect(self.commandSearch)

        # Add the home screen buttons to the home screen with grid coordinates
        homeScreenLayout.addWidget(button1, 0, 0)
        homeScreenLayout.addWidget(button2, 0, 1)
        homeScreenLayout.addWidget(button3, 0, 2)
        homeScreenLayout.addWidget(button4, 0, 3)
        homeScreenLayout.addWidget(button5, 1, 0)
        homeScreenLayout.addWidget(button6, 1, 1)
        homeScreenLayout.addWidget(button7, 1, 2)
        homeScreenLayout.addWidget(button8, 1, 3)
        homeScreenLayout.addWidget(self.textField, 2, 0)

        # Create the "go home" button
        homeButton = QPushButton("Back to main screen")
        homeButton.clicked.connect(lambda: self.change_screen(0))

        # Add the different main screens to the stack layout (main window that will change when something happens)
        self.stackLayout.addWidget(container)
        self.stackLayout.addWidget(homeButton)
        # The next 7 are just for testing purposes, so each button does something.
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)
        self.stackLayout.addWidget(homeButton)

        # Add the stack layout and text input to the main menu
        layout.addLayout(self.stackLayout, 0, 0)
        #layout.addLayout(sliderLayout,0,1 )
        layout.addWidget(self.textField,1,0)

        # Define the main widget for every visible element
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedHeight(300)
        self.setFixedWidth(500)

    # Swap screens to specified index
    def change_screen(self, index):
        self.textField.setText("")
        self.stackLayout.setCurrentIndex(index)


    # Create a button with an icon, width, height and connect it to a different screen
    def define_button(self, icon, w, h, screen, index):
        button = QPushButton()
        button.setIcon(QtGui.QIcon(icon))
        button.setIconSize(QtCore.QSize(w,h))
        button.setFixedSize(QtCore.QSize(w,h))
        button.clicked.connect(lambda: screen(index))
        return button
    
    # Search for a command based on text input. 
    def commandSearch(self):
        command = self.textField.text()
        command = command.lower()

        # Each command has an index number for the stack layout. If a command exists, swap to the screen that matches said index.
        commands = {"back":0, "radio": 1, "maps":2, "trip computer":3, "phone":4, "messages":5, 
                    "bluetooth":6, "seat":7, "settings":8}
        for entry in commands: 
            if (command == entry):
                index = commands.get(command)
                self.change_screen(index)
        
app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()


