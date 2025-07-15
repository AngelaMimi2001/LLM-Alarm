import openai
import requests
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import os
import tkinter as tk  # GUI library
from datetime import datetime, timedelta
from tkinter import messagebox  # Tkinter module for dialog boxes
import sounddevice as sd
from scipy.io.wavfile import write
import requests
import re
import time
import serial
import atexit

# Configure your OpenAI and Spotify API credentials
openai.api_key = # "Replace with your OpenAI API key"
spotify_client_id = # "Replace with your Spotify client ID"
spotify_client_secret = # "Replace with your Spotify client secret"
spotify_redirect_uri = "http://localhost:8888/callback"

# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
                                               client_secret=spotify_client_secret,
                                               redirect_uri=spotify_redirect_uri,
                                               scope="user-read-playback-state,user-modify-playback-state"))

# Initialize serial communication with Arduino
arduino = serial.Serial('COM3', 9600)  # Replace 'COM3' with the correct port for your Arduino

# Convert words like "two" to numbers
def word_to_num(text):
    word_to_digit = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19, "twenty": 20
    }
    for word, digit in word_to_digit.items():
        text = re.sub(rf"\b{word}\b", str(digit), text, flags=re.IGNORECASE)
    return text


# Global variable to store the extracted activity
extracted_activity = None

# Function to convert speech to text and extract main activity
def audio_to_text():
    global extracted_activity
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for activity...")
        audio = recognizer.listen(source)
        try:
            # Convert audio to text
            text = recognizer.recognize_google(audio)
            print(f"Recognized Text: {text}")
            
            # Use OpenAI Chat API to extract main activity
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts the main activity from a sentence and converts it to '-ing' form with the first letter capitalized."},
                    {"role": "user", "content": f"Extract the main activity in this sentence and convert it to '-ing' form with the first letter capitalized. For example, 'I will do yoga at 6pm' becomes 'Doing yoga'. Sentence: {text}"}
                ]
            )
            
            # Store the extracted activity in the global variable
            extracted_activity = response['choices'][0]['message']['content'].strip()
            print(f"Extracted Activity (Stored): {extracted_activity}")
            
            # Return the text only
            return text
        
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError:
            print("API unavailable.")
            return None


# Step 3: Extract Alarm Time using LLM via HTTP Request
def analyze_text_for_time(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": # "Replace with your OpenAI API key"
    }
    text = word_to_num(text)  # Convert number words to digits in the input text
    prompt = (
        f"Extract only the time from this text: '{text}'. "
        f"Respond only with the time in 'HH:MM AM/PM' format, without any additional text."
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    response = requests.post(
        url,
        headers=headers,
        json={
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 20,  # Allows space for the exact time response
            "temperature": 0
        }
    )
    if response.status_code == 200:
        alarm_time = response.json()["choices"][0]["message"]["content"].strip()
        print("Detected Alarm Time:", alarm_time)
        
        # Post-process the response to clean up the time format
        cleaned_alarm_time = preprocess_alarm_time(alarm_time)
        return cleaned_alarm_time
    else:
        print("Error in text analysis:", response.status_code, response.text)
        return None

# New: Preprocessing function to clean the detected alarm time
def preprocess_alarm_time(alarm_time):
    # Standardize AM/PM formatting and clean up errors like "9.a.m"
    alarm_time = re.sub(r"\b(\d+)\.(am|pm)\b", r"\1 AM", alarm_time, flags=re.IGNORECASE)
    alarm_time = alarm_time.replace("am", "AM").replace("pm", "PM").replace(".", "").strip()

    # Check if we now have a proper "HH:MM AM/PM" format
    time_match = re.search(r"\b\d{1,2}:\d{2}\s*(AM|PM)\b", alarm_time, re.IGNORECASE)
    if time_match:
        return time_match.group(0)

    # Check for "HH AM/PM" format without minutes
    hour_only_match = re.search(r"\b\d{1,2}\s*(AM|PM)\b", alarm_time, re.IGNORECASE)
    if hour_only_match:
        return hour_only_match.group(0) + ":00"  # Add minutes to standardize

    # Check for duration in hours if no specific time is detected
    hours_match = re.search(r"\b\d+\b", alarm_time)
    if hours_match:
        return hours_match.group(0)

    return None


global_alarm_time = None  # Declare a global variable to store the alarm time

def set_alarm(alarm_time=None):
    global global_alarm_time
    if not alarm_time:
        alarm_time = hours_entry.get().strip()

    try:
        if ":" in alarm_time:  # Specific time format
            wake_up_time = datetime.strptime(alarm_time, "%I:%M %p")
            now = datetime.now()
            wake_up_time = wake_up_time.replace(year=now.year, month=now.month, day=now.day)
            if wake_up_time < now:
                wake_up_time += timedelta(days=1)
            wake_up_label.config(text=f"{extracted_activity}: " + wake_up_time.strftime("%I:%M %p"))
        else:  # Assume it's a duration in hours
            hours_to_add = int(alarm_time)
            wake_up_time = datetime.now() + timedelta(hours=hours_to_add)
            wake_up_label.config(text=f"{extracted_activity}: " + wake_up_time.strftime("%I:%M %p"))

        global_alarm_time = wake_up_time.strftime("%H:%M")
        check_alarm(global_alarm_time)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid time (e.g., '3' or '6:00 AM').")


def determine_urgency(text):
    """
    Use OpenAI's LLM to determine if a task described in the text is urgent.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": (
                    "You are a smart assistant that classifies whether a user's activity is urgent or not. "
                    "Urgent means time-sensitive or important to perform immediately (e.g. meetings, work deadlines, transportation, appointments). "
                    "Non-urgent means flexible or leisure activities (e.g. yoga, reading, shopping, playing games). "
                    "Only respond with 'Urgent' or 'Not Urgent'."
                )},
                {"role": "user", "content": f"Is this urgent? '{text}'"}
            ],
            max_tokens=5,
            temperature=0
        )

        classification = response['choices'][0]['message']['content'].strip().lower()
        if "urgent" in classification:
            print(f"Text: '{text}' - Urgency: Urgent")
            return True
        else:
            print(f"Text: '{text}' - Urgency: Not Urgent")
            return False

    except Exception as e:
        print(f"Error determining urgency via OpenAI: {e}")
        # Default to not urgent in case of error
        return False


# Function to gradually adjust the volume
def adjust_volume(device_id, start_volume, end_volume, step, delay):
    """
    Gradually adjust the volume from start_volume to end_volume.
    :param device_id: Spotify device ID
    :param start_volume: Initial volume level (0-100)
    :param end_volume: Final volume level (0-100)
    :param step: Step size for volume changes
    :param delay: Time (in seconds) between each step
    """
    if start_volume < end_volume:
        volume_range = range(start_volume, end_volume + 1, step)
    else:
        volume_range = range(start_volume, end_volume - 1, -step)

    for volume in volume_range:
        sp.volume(volume, device_id=device_id)
        time.sleep(delay)


def play_music_on_spotify(is_urgent):
    # Choose music track based on urgency
    if is_urgent:
        query = "energetic upbeat song"  # Search for an energetic song
    else:
        query = "relaxing easy comfortable tunes"  # Search for a relaxing song

    # Search for multiple tracks (e.g., limit=10) and randomly select one
    results = sp.search(q=query, type="track", limit=10)  # Get 10 tracks
    if not results['tracks']['items']:
        print("No track found for the query.")
        return

    # Randomly select a track from the results
    track = random.choice(results['tracks']['items'])
    track_uri = track['uri']

    # Get the active device ID
    devices = sp.devices()
    device_id = None
    for device in devices['devices']:
        if device['is_active']:
            device_id = device['id']
            break

    if device_id:
        # Start playback on the active device
        sp.start_playback(device_id=device_id, uris=[track_uri])
        if is_urgent:
            print(f"Playing urgent music: {track['name']} by {track['artists'][0]['name']}")
            adjust_volume(device_id, start_volume=0, end_volume=85, step=5, delay=0.09)
        else:
            print(f"Playing non-urgent music: {track['name']} by {track['artists'][0]['name']}")
            adjust_volume(device_id, start_volume=0, end_volume=100, step=10, delay=0.05)
    else:
        print("No active Spotify device found. Please open Spotify on your device.")


def stop_music_and_clear():
    global extracted_activity, is_urgent, global_alarm_time
    try:
        # Stop Spotify playback after gradually lowering volume
        devices = sp.devices()
        device_id = None
        for device in devices['devices']:
            if device['is_active']:
                device_id = device['id']
                break

        if device_id:
            # Gradually lower the volume based on urgency before stopping playback
            if is_urgent:
                adjust_volume(device_id, start_volume=85, end_volume=0, step=5, delay=0.09)
            else:
                adjust_volume(device_id, start_volume=100, end_volume=0, step=5, delay=0.09)

            sp.pause_playback(device_id=device_id)
            print("Music stops.")
        else:
            print("No active Spotify device found to stop playback.")
    except Exception as e:
        print(f"Error stopping music: {e}")

    #Send LED off command to Arduino
    arduino.write(b"LED:OFF\n") # Turn off LEDs

    # Clear the current activity, alarm time, and GUI display
    extracted_activity = None
    global_alarm_time = None
    is_urgent = None

    # Clear activity and alarm from the GUI
    wake_up_label.config(text="")  # Clear everything from the alarm display


# 更换成缓存文件的路径
cache_path = "C:/Users/DELL/Desktop/Physical Interaction/Project 2/音乐代码/.cache"


# 检查并删除已有的缓存文件
if os.path.exists(cache_path):
    os.remove(cache_path)
    print("缓存文件已删除，准备重新认证。")
else:
    print("未找到缓存文件，将进行首次认证。")


is_urgent = None  # Define the variable globally


def check_alarm(alarm_time):
    now = datetime.now().strftime("%H:%M")
    if now == alarm_time:
        play_music_on_spotify(is_urgent)
        arduino.write(b"LED:ON\n")
    else:
        root.after(1000, lambda: check_alarm(alarm_time))


def update_clock():
    global current_time
    current_time = datetime.now().strftime("%H:%M")  # Use 24-hour format
    clock_label.config(text=current_time)

    # Calculate the delay until the next minute
    now = datetime.now()
    next_minute = (60 - now.second) * 1000  # Time remaining in milliseconds
    root.after(next_minute, update_clock)  # Schedule the next update


def set_alarm_from_audio():
    global global_alarm_time, is_urgent
    text = audio_to_text()
    if text:
        time_text = word_to_num(text)
        alarm_time = analyze_text_for_time(time_text)
        if alarm_time:
            set_alarm(alarm_time)

    if text:
        is_urgent = determine_urgency(text)


# Initialize GUI window
root = tk.Tk()
root.title("Personalized Alarm Clock")
root.geometry("300x250")

# Display current time
clock_label = tk.Label(root, font=("Helvetica", 18))
clock_label.pack(pady=20)
update_clock()

# Set alarm buttons
#set_alarm_button = tk.Button(root, text="Set Alarm", command=lambda: set_alarm())
#set_alarm_button.pack(pady=10)

# Set alarm from audio
set_alarm_from_audio_button = tk.Button(root, text="Set Alarm", command=set_alarm_from_audio)
set_alarm_from_audio_button.pack(pady=10)


# Add a button to stop music and clear
stop_music_button = tk.Button(root, text="Stop Music", command=stop_music_and_clear)
stop_music_button.pack(pady=10)


# Function to simulate button clicks on key press
def on_key_press(event):
    if event.char == 'a':  # If 'a' is pressed
        set_alarm_from_audio_button.invoke()
    elif event.char == 's':  # If 's' is pressed
        stop_music_button.invoke()

# Bind keyboard events to the root window
root.bind('<Key>', on_key_press)


# Display appointing time
wake_up_label = tk.Label(root, font=("Helvetica", 14))
wake_up_label.pack(pady=10)

# Register serial cleanup to ensure the Arduino connection closes on script exit

def close_serial():
    if arduino:  # Check if Arduino connection exists
        arduino.close()
        print("Arduino connection closed.")

atexit.register(close_serial)  # Automatically call close_serial() when the script exits

# Run the application
root.mainloop()
