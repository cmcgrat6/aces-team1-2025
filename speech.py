from PyQt6.QtCore import QRunnable, pyqtSlot
import speech_recognition as sr
import pyttsx3
import webbrowser
import re
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class speechThread(QRunnable):
    def __init__(self, gui):
        super().__init__()
        self.gui = gui
        self.awake = False
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self._running = True

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

        # Map voice commands to screen numbers and spoken feedback
        self.screen_commands = {
            ("open radio", "go to radio"): (1, "Opening Radio."),
            ("open maps", "go to maps", "navigate"): (2, "Opening Navigation."),
            ("open trip computer", "go to trip"): (3, "Opening Trip Computer."),
            ("open phone", "go to phone"): (4, "Opening Phone."),
            ("open vehicle", "go to vehicle", "vehicle info"): (5, "Opening Vehicle Info."),
            ("open bluetooth", "go to bluetooth"): (6, "Opening Bluetooth."),
            ("open messages", "go to messages"): (7, "Opening Messages."),
            ("open settings", "go to settings"): (8, "Opening Settings."),
            ("go back", "go home", "return to main"): (0, "Returning to main screen."),
        }

    def stop(self):
        self._running = False

    def speak(self, text):
        print("Assistant:", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def set_volume(self, value):
        value = max(0, min(100, value))
        self.volume_interface.SetMasterVolumeLevelScalar(value / 100.0, None)

    def listen(self, timeout=None, phrase_time_limit=None):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                return self.recognizer.recognize_google(audio).lower()
            except sr.WaitTimeoutError:
                # Timeout waiting for phrase to start
                return None
            except sr.UnknownValueError:
                # Speech unintelligible
                return ""
            except Exception as e:
                print("Error:", e)
                return ""

    @pyqtSlot()
    def run(self):
        print("Say 'Hi Jaguar' to activate.")

        while self._running:
            try:
                if not self.awake:
                    print("Listening (sleep mode)...")
                    text = self.listen(timeout=5, phrase_time_limit=5)
                    if text:
                        print("You said (sleep mode):", text)
                        if "hi jaguar" in text:
                            self.awake = True
                            self.speak("Hello, how can I help you?")
                    continue

                # Awake mode: wait for command with timeout
                print("Listening for command...")
                text = self.listen(timeout=5, phrase_time_limit=5)

                if text is None:  # Timeout no speech detected
                    self.speak("No command received, going to sleep.")
                    self.awake = False
                    continue

                if text == "":  # Unintelligible speech
                    print("Could not understand command.")
                    continue

                print("You said:", text)

                # Check screen switching commands first
                for keywords, (screen_num, response) in self.screen_commands.items():
                    if any(keyword in text for keyword in keywords):
                        self.gui.change_screen_voice(screen_num)
                        self.speak(response)
                        break
                else:
                    # Process other commands here

                    if "go to sleep" in text:
                        self.speak("Going to sleep.")
                        self.awake = False
                        continue

                    # Volume control
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
                        continue

                    # Brightness control
                    if "brightness" in text:
                        if "increase" in text:
                            sbc.set_brightness("+=10")
                            self.speak("Brightness increased.")
                        elif "decrease" in text:
                            sbc.set_brightness("-=10")
                            self.speak("Brightness decreased.")
                        elif "set" in text:
                            match = re.search(r"(\d+)", text)
                            if match:
                                sbc.set_brightness(int(match.group(1)))
                                self.speak("Brightness set.")
                        continue

                    # Google Maps navigation
                    if "open google map" in text:
                        self.speak("Starting point?")
                        start = self.listen(timeout=5, phrase_time_limit=10)
                        if not start:
                            self.speak("No starting point received, cancelling.")
                            self.awake = False
                            continue
                        self.speak("Destination?")
                        end = self.listen(timeout=5, phrase_time_limit=10)
                        if not end:
                            self.speak("No destination received, cancelling.")
                            self.awake = False
                            continue
                        url = f"https://www.google.com/maps/dir/{start}/{end}"
                        webbrowser.open(url)
                        self.speak("Opened Google Maps.")
                        continue

                    # Scroll demo
                    if "scroll down" in text:
                        self.gui.scrollContent(50)
                        self.speak("Scrolled down.")
                        continue
                    elif "scroll up" in text:
                        self.gui.scrollContent(-50)
                        self.speak("Scrolled up.")
                        continue

                    # Messaging mock
                    if "send message" in text or "telegram" in text:
                        self.speak("What should I send?")
                        message = self.listen(timeout=5, phrase_time_limit=10)
                        if message:
                            with open("demo_mock_messages.txt", "a") as f:
                                f.write(f"{message}\n")
                            self.speak("Message saved for demo.")
                        else:
                            self.speak("No message received.")
                        continue

                    # If no recognized commands
                    self.speak("Command not recognized.")

        print("Speech thread exiting cleanly.")
