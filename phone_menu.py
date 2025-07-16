from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea, QStackedLayout, QGridLayout)
from PyQt6.QtCore import Qt

def create_phone_menu(change_screen_callback, define_button):
    phoneMainContainer = QWidget()
    phoneMainLayout = QVBoxLayout(phoneMainContainer)

    # Top bar
    phoneTabs = QHBoxLayout()
    dialerTab = QPushButton("Dialer")
    contactsTab = QPushButton("Contacts")
    recentsTab = QPushButton("Recents")
    voicemailTab = QPushButton("Voicemail")
    for tab in [dialerTab, contactsTab, recentsTab, voicemailTab]:
        tab.setFixedHeight(40)
        phoneTabs.addWidget(tab)

    phoneMainLayout.addLayout(phoneTabs)

    # Stack for each phone sub-screen
    phoneStack = QStackedLayout()

    # Dialer
    dialerScreen = QWidget()
    dialerLayout = QVBoxLayout(dialerScreen)
    phoneInput = QLineEdit()
    phoneInput.setReadOnly(True)
    phoneInput.setAlignment(Qt.AlignmentFlag.AlignCenter)
    phoneInput.setFixedHeight(50)
    dialerLayout.addWidget(phoneInput)

    dialPad = QGridLayout()
    buttons = [("1", 0, 0), ("2", 0, 1), ("3", 0, 2), ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 3, 0), ("0", 3, 1), ("#", 3, 2), ]
    for text, row, col in buttons:
        btn = QPushButton(text)
        btn.setFixedSize(80, 60)
        btn.clicked.connect(lambda _, t=text: phoneInput.setText(phoneInput.text() + t))
        dialPad.addWidget(btn, row, col)

    dialerLayout.addLayout(dialPad)

    actionsLayout = QHBoxLayout()
    callBtn = QPushButton("Call")
    deleteBtn = QPushButton("Delete")
    callBtn.setFixedSize(100, 40)
    deleteBtn.setFixedSize(100, 40)
    deleteBtn.clicked.connect(lambda: phoneInput.setText(phoneInput.text()[:-1]))
    actionsLayout.addWidget(callBtn)
    actionsLayout.addWidget(deleteBtn)

    dialerLayout.addLayout(actionsLayout)
    dialerLayout.addWidget(define_button("Back", 160, 40, change_screen_callback, 0))

    # Contacts
    contactsScreen = QWidget()
    contactsLayout = QVBoxLayout(contactsScreen)
    contactsScroll = QScrollArea()
    contactsWidget = QWidget()
    contactsListLayout = QVBoxLayout(contactsWidget)
    names = ["Amy", "Carl", "Dave work", "Home", "John", "Landlord", "Monica", "Morgan", "Pizza", "Tyrell"]
    for name in names:
        contactsListLayout.addWidget(QLabel(name))
    contactsScroll.setWidget(contactsWidget)
    contactsScroll.setWidgetResizable(True)
    contactsScroll.setFixedHeight(200)
    contactsLayout.addWidget(contactsScroll)
    contactsLayout.addWidget(define_button("Back", 160, 40, change_screen_callback, 0))

    # Recents
    recentsScreen = QWidget()
    recentsLayout = QVBoxLayout(recentsScreen)
    recents = ["Pizza - Yesterday", "Amy - Today", "Home - Missed"]
    for call in recents:
        recentsLayout.addWidget(QLabel(call))
    recentsLayout.addWidget(define_button("Back", 160, 40, change_screen_callback, 0))

    # Voicemail
    voicemailScreen = QWidget()
    voicemailLayout = QVBoxLayout(voicemailScreen)
    voicemails = ["Voicemail 1 - 0:43", "Voicemail 2 - 2:17"]
    for msg in voicemails:
        voicemailLayout.addWidget(QLabel(msg))
    voicemailLayout.addWidget(define_button("Back", 160, 40, change_screen_callback, 0))

    # Add all to stack
    phoneStack.addWidget(dialerScreen) # [0]
    phoneStack.addWidget(contactsScreen) # [1]
    phoneStack.addWidget(recentsScreen) # [2]
    phoneStack.addWidget(voicemailScreen) # [3]

    # Tab switching
    dialerTab.clicked.connect(lambda: phoneStack.setCurrentIndex(0))
    contactsTab.clicked.connect(lambda: phoneStack.setCurrentIndex(1))
    recentsTab.clicked.connect(lambda: phoneStack.setCurrentIndex(2))
    voicemailTab.clicked.connect(lambda: phoneStack.setCurrentIndex(3))

    phoneMainLayout.addLayout(phoneStack)

    # Return the main container
    return phoneMainContainer
