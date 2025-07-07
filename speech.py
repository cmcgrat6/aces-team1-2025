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

# Wake control
awake = False

def listen():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return recognizer.recognize_google(audio).lower()

# Main loop
print("Say 'Hi Jaguar' to activate.")

while True:
    try:
        print("Listening...")
        text = listen()
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
            start = listen()
            speak("Destination?")
            end = listen()
            url = f"https://www.google.com/maps/dir/{start}/{end}"
            webbrowser.open(url)
            speak("Opened Google Maps.")
            awake = False
            continue

        # Telegram messaging
        if "send message" in text or "telegram" in text:
            speak("What should I send?")
            message = listen()
            print(f"[Mock] Would send this message via Telegram: {message}")
            speak("Message saved for Telegram demo.")
            with open("demo_mock_messages.txt", "a") as f:
                f.write(f"{message}\n")
            awake = False
            continue

        # Unknown
        speak("Command not recognized.")
        awake = False

    except sr.UnknownValueError:
        print("Could not understand.")
    except Exception as e:
        print("Error:", e)
