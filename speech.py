# imports
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot
import threading
import speech_recognition as sr
import pyttsx3 # text to speech
import re # regular expressions (regex)
import screen_brightness_control as sbc #system brightness
from ctypes import cast, POINTER # cast COM for pycaw  && access COM object members
from comtypes import CLSCTX_ALL # access everything in COM object
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # system volume
from urllib.parse import quote # quotation mark for url-safe string
import requests # for Google Maps API

# Google API key (currently using personal gmail)
GOOGLE_MAPS_API_KEY = "AIzaSyDM4IvsH8I3YMgcQE_xyus6XxGZ3ZjTp9Y"

# read out travel distance && time required
def get_travel_info(destination):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": "Jaguar Land Rover Shannon",  # fixed start location for demo
        "destination": destination,
        "key": GOOGLE_MAPS_API_KEY
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        leg = data["routes"][0]["legs"][0]
        distance = leg["distance"]["text"]
        duration = leg["duration"]["text"]
        return distance, duration
    elif data["status"] == "OVER_QUERY_LIMIT":
        print("API quota exceeded.")
        return "quota_exceeded", "quota_exceeded"
    else:
        print("Error getting travel info:", data["status"])
        return None, None


# signals to avoid thread warnings
class SpeechSignals(QObject):
    change_screen = pyqtSignal(int)
    change_station = pyqtSignal(str)
    load_map = pyqtSignal(str)
    scroll = pyqtSignal(int)
    open_chat = pyqtSignal(str)
    toggle_radio = pyqtSignal(bool)    
    toggle_bluetooth = pyqtSignal(bool)

# speechThread class
class speechThread(QRunnable):
    def __init__(self, gui=None):
        super().__init__()
        self.signals = SpeechSignals()
        self.awake = False
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self._running = True
        self.read_messages = []

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

        # keywords for changing screens
        self.screen_commands = {
            ("open radio", "go to radio"): (1, "Opening Radio Screen."),
            ("open maps", "go to maps"): (2, "Opening Navigation Screen."),
            ("open trip computer", "go to trip"): (3, "Opening Trip Computer Screen."),
            ("open phone", "go to phone"): (4, "Opening Phone Screen."),
            ("open vehicle", "go to vehicle", "vehicle info"): (5, "Opening Vehicle Info Screen."),
            ("open bluetooth", "go to bluetooth"): (6, "Opening Bluetooth Screen."),
            ("open messages", "go to messages"): (7, "Opening Messages Screen."),
            ("open settings", "go to settings"): (8, "Opening Settings Screen."),
            ("go back", "go home", "return to main"): (0, "Returning to main screen."),
        }

        # keywords for changing radio stations
        self.station_commands = {
            ("switch to rte 1",): ("RTE 1", "Now playing RTE 1."),
            ("switch to rte 2",): ("RTE 2", "Now playing RTE 2."),
            ("switch to news talk",): ("Newstalk", "Now playing News Talk."),
            ("switch to spin southwest", "switch to spin sw"): ("SPIN SW", "Now playing Spin Southwest."),
        }

    # stop running
    def stop(self):
        self._running = False

    # voice output
    speak_lock = threading.Lock()

    def speak(self, text):
        print("Assistant:", text)
        with self.speak_lock:
            self.engine.say(text)
            self.engine.runAndWait()

    # change volume value
    def set_volume(self, value):
        value = max(0, min(100, value))
        self.volume_interface.SetMasterVolumeLevelScalar(value / 100.0, None)

    # voice input
    def listen(self, timeout=None, phrase_time_limit=None):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                return self.recognizer.recognize_google(audio).lower()
            except sr.WaitTimeoutError: # no input after some time
                return None
            except sr.UnknownValueError: #not sure what is said
                return ""
            except Exception as e:
                print("Error:", e)
                return ""
           
    # cancel navigation
    def is_cancel_command(self, text):
        # cancel
        cancel_keywords = ["go back", "cancel", "stop navigation", "stop navigate", "never mind", "nevermind", "exit", "back"]
        return any(keyword in text.lower() for keyword in cancel_keywords)

    @pyqtSlot()
    def run(self):
        print("Say 'Hi Jaguar' to activate.") # wake word
        while self._running:
            try:
                if not self.awake:
                    # no wake word said
                    print("Listening (sleep mode)...")
                    text = self.listen(timeout=3, phrase_time_limit=5)
                    if text:
                        print("You said (sleep mode):", text)
                        if "hi jaguar" in text: # wake word said
                            self.awake = True
                            self.speak("Hello, how can I help you?")
                    continue

                print("Listening for command...") # waiting for command
                text = self.listen(timeout=5, phrase_time_limit=5)

                if text is None:
                    self.speak("No command received, going to sleep.") # return to sleep after some time without commands
                    self.awake = False
                    continue

                if text == "":
                    print("Could not understand command.") # something is said but not understood
                    continue

                print("You said:", text)

                # settle change screen commands first
                for keywords, (screen_num, response) in self.screen_commands.items():
                    if any(keyword in text for keyword in keywords):
                        self.signals.change_screen.emit(screen_num)
                        self.speak(response)
                        break
                else:
                    # change station commands
                    for keywords, (station_name, response) in self.station_commands.items():
                        if any(keyword in text for keyword in keywords):
                            self.signals.change_station.emit(station_name)
                            self.speak(response)
                            self.awake = False
                            continue

                    # return to sleep mode
                    if "go to sleep" in text:
                        self.speak("Going to sleep.")
                        self.awake = False
                        continue
                        
                    if "thank you" in text:
                        self.speak("You are welcome.")
                        self.awake = False
                        continue
                    
                    # toggling bluetooth
                    if "turn on bluetooth" in text:
                        self.signals.toggle_bluetooth.emit(True)
                        self.speak("Turning on Bluetooth.")
                        self.awake = False
                        continue
                    elif "turn off bluetooth" in text:
                        self.signals.toggle_bluetooth.emit(False)
                        self.speak("Turning off Bluetooth.")
                        self.awake = False
                        continue

                    # toggling radio
                    if "turn on radio" in text:
                        self.signals.toggle_radio.emit(True)
                        self.speak("Turning on radio.")
                        continue
                    elif "turn off radio" in text:
                        self.signals.toggle_radio.emit(False)
                        self.speak("Turning off radio.")
                        self.awake = False
                        continue

                    # set volume
                    if "volume" in text:
                        current = self.volume_interface.GetMasterVolumeLevelScalar() * 100
                        match = re.search(r"(\d+)", text)

                        if "set" in text and match:
                            self.set_volume(int(match.group(1)))
                            self.speak(f"Volume set to {match.group(1)}.")
                        elif "increase" in text:
                            if match:
                                self.set_volume(int(match.group(1)))
                                self.speak(f"Volume increased to {match.group(1)}.")
                            else:
                                self.set_volume(int(current + 10))
                                self.speak("Volume increased.")
                        elif "decrease" in text:
                            if match:
                                self.set_volume(int(match.group(1)))
                                self.speak(f"Volume decreased to {match.group(1)}.")
                            else:
                                self.set_volume(int(current - 10))
                                self.speak("Volume decreased.")
                        self.awake = False
                        continue

                    # set brightness
                    if "brightness" in text:
                        current = sbc.get_brightness()[0]
                        if "increase" in text:
                            sbc.set_brightness(int(current + 10))
                            self.speak("Brightness increased.")
                        elif "decrease" in text:
                            sbc.set_brightness(int(current - 10))
                            self.speak("Brightness decreased.")
                        elif "set" in text:
                            match = re.search(r"(\d+)", text)
                            if match:
                                sbc.set_brightness(int(match.group(1)))
                                self.speak("Brightness set.")
                        self.awake = False
                        continue

                    # navigation commands
                    if any(kw in text for kw in ["navigate", "open navigation", "bring me to"]):
                        self.signals.change_screen.emit(2)
                    
                        destination = None
                        if "bring me to" in text:
                            destination = text.split("bring me to", 1)[1].strip()
                        else:
                            for _ in range(3): # 3 times before auto cancel
                                self.speak("Where are you going?")
                                response = self.listen(timeout=5, phrase_time_limit=10)
                    
                                if response:
                                    print(f"You said: {response}")
                    
                                    if self.is_cancel_command(response):
                                        self.speak("Navigation cancelled.")
                                        destination = None
                                        break
                    
                                    destination = response
                                    break
                                else:
                                    self.speak("That doesn't sound like a valid destination. Let's try again.")
                            else:
                                self.speak("Failed to get a valid destination, cancelling.")
                                self.awake = False
                                continue
                    
                        # actual destination is given
                        if destination and not self.is_cancel_command(destination):
                            start = "Jaguar Land Rover Shannon"
                            dest_encoded = quote(destination)
                            map_url = f"https://www.google.com/maps/dir/{start}/{dest_encoded}"
                            self.signals.load_map.emit(map_url)
                    
                            distance, duration = get_travel_info(destination)
                            if distance == "quota_exceeded":
                                self.speak("Sorry, I've reached the daily limit. Try again later.")
                            elif distance and duration:
                                self.speak(f"The distance is {distance} and it will take approximately {duration}.")
                            else:
                                self.speak("I couldn't retrieve travel information.")
                        
                        continue 

                    # scrolling function
                    if "scroll down" in text:
                        self.signals.scroll.emit(100)
                        self.speak("Scrolled down.")
                        continue
                    elif "scroll up" in text:
                        self.signals.scroll.emit(-100)
                        self.speak("Scrolled up.")
                        continue
                        
                    # open specific chat screen
                    if "open chat with" in text:
                        match = re.search(r"open chat with (.+)", text)
                        if match:
                            name = match.group(1).strip().title()  # Capitalizes like 'John', 'Amy'
                            self.signals.open_chat.emit(name)
                            self.speak(f"Opening chat with {name}.")
                        else:
                            self.speak("I didn't catch the name. Please try again.")
                        continue

                    # read out messages sent and received
                    if "read messages from" in text:
                        match = re.search(r"read messages from (.+)", text)
                        if match:
                            name = match.group(1).strip().title()
                            self.signals.open_chat.emit(name)
                            try:
                                with open("messages.txt", "r") as f:
                                    lines = [line.strip() for line in f if line.startswith(name)]
                                if not lines:
                                    self.speak(f"No messages found for {name}.")
                                else:
                                    self.speak(f"Reading messages with {name}.")
                                    for line in lines:
                                        # Skip lines like 'Name To:'
                                        if "From:" in line:
                                            msg = line.split("From:")[1].strip()
                                            self.speak(f"{name} said: {msg}")
                                        elif "To:" in line:
                                            msg = line.split("To:")[1].strip()
                                            self.speak(f"You said: {msg}")
                            except Exception as e:
                                print("Error reading messages:", e)
                                self.speak("Failed to read messages.")
                        else:
                            self.speak("I didn't catch the name. Please say something like 'Read messages from Amy'.")
                        continue

                    self.speak("Command not recognized.")

            # error
            except Exception as e:
                print("Error:", e)
        
        # close thread when program is stopped
        print("Speech thread exiting cleanly.")
