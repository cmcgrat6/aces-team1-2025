# 
# run pip install SpeechRecognition pyttsx3 PyAudio pycaw screen-brightness-control (python-telegram-bot==13.15)
# have to say "hi jaguar" everytime before giving commands
# commands to test [go to sleep, increase/decrease/set volume/brightness to XX, send message (only a mock for now), open maps]
#

import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# from telegram import Bot
import re

# Telegram setup
# TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
# CHAT_ID = 'YOUR_CHAT_ID'
# bot = Bot(token=TELEGRAM_TOKEN)

# TTS setup
engine = pyttsx3.init()
def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Audio recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Volume setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

def set_volume(value):
    value = max(0, min(100, value))
    volume_interface.SetMasterVolumeLevelScalar(value / 100.0, None)


def listen():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return recognizer.recognize_google(audio).lower()

# Main loop
def main():
    # Wake control
    awake = False
    print("Say 'Hi Jaguar' to activate.")

    while True:
        try:
            print("Listening...")
            text = input() #listen()
            print("You said:", text)

            if not awake:
                if "hi jaguar" in text:
                    awake = True
                    speak("Yes?")
                continue

            # Sleep command
            if "go to sleep" in text:
                speak("Going to sleep.")
                awake = False
                continue

            # Volume commands
            if "volume" in text:
                if "increase" in text:
                    current = volume_interface.GetMasterVolumeLevelScalar() * 100
                    set_volume(int(current + 10))
                    speak("Volume increased.")
                elif "decrease" in text:
                    current = volume_interface.GetMasterVolumeLevelScalar() * 100
                    set_volume(int(current - 10))
                    speak("Volume decreased.")
                elif "set" in text:
                    match = re.search(r"(\d+)", text)
                    if match:
                        set_volume(int(match.group(1)))
                        speak("Volume set.")
                awake = False
                continue

            # Brightness commands
            if "brightness" in text:
                if "increase" in text:
                    sbc.set_brightness("+=10")
                    speak("Brightness increased.")
                elif "decrease" in text:
                    sbc.set_brightness("-=10")
                    speak("Brightness decreased.")
                elif "set" in text:
                    match = re.search(r"(\d+)", text)
                    if match:
                        sbc.set_brightness(int(match.group(1)))
                        speak("Brightness set.")
                awake = False
                continue

            # Maps
            if "open maps" in text or "navigate" in text:
                speak("Starting point?")
                start = input() #listen()
                speak("Destination?")
                end = input() #listen()
                url = f"https://www.google.com/maps/dir/{start}/{end}"
                webbrowser.open(url)
                speak("Opened Google Maps.")
                awake = False
                continue

            # Telegram messaging
            if "send message" in text or "telegram" in text:
                speak("What should I send?")
                message = input() #listen()
                print(f"[Mock] Would send this message via Telegram: {message}")
                speak("Message saved for Telegram demo.")
                with open("demo_mock_messages.txt", "a") as f:
                    f.write(f"{message}\n")
                awake = False
                continue

            # GUI Switches
            commands = {"back":0, "home":0, "return":0, "radio": 1, "map":2, "nav":2, "satnav":2, "trip":3, "computer":3, "phone":4, "vehicle":5, 
                    "info":5, "bluetooth":6, "seat":7, "settings":8}
            for entry in commands: 
                if (entry == text):
                    awake = False
                    return commands.get(entry)
                
            # Radio Stations
            stations = {"rte one": "RTE 1", "rte two": "RTE 2", "newstalk": "NEWSTALK", "spin": "SPIN SW"}
            for entry in stations:
                if (entry in text):
                    awake = False
                    return stations.get(entry)
            
            # Unknown
            speak("Command not recognized. Please try again.")

        except sr.UnknownValueError:
            print("Could not understand.")
        except Exception as e:
            print("Error:", e)

