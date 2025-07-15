# Echotune – Smart LLM-based Alarm

Echotune is an AI-powered reminder alarm clock that uses **large language models (LLMs)** and **Natural Language Processing (NLP)** to understand spoken schedules and assess task urgency. By integrating **OpenAI (ChatGPT) and Spotify APIs**, the system generates personalized alarms—with matching music, lighting, and on-screen displays—tailored to each activity. It is designed as a **hardware + software** system and requires the accompanying Arduino-based device to run properly.

---

## Features

- **Voice Recognition** – Set reminders hands-free using natural speech  
- **Natural Language Parsing (NLP/LLM)** – Extracts activity and time automatically  
- **Urgency Classification (LLM)** – Classifies events as **Urgent** or **Not Urgent** for personalized responses  
- **Music Playback** – Plays energetic or soothing music via Spotify based on urgency  
- **Light Emitting** – Controls LED lighting patterns via Arduino for visual cues  
- **Screen Display** – Displays current time and scheduled events on an OLED screen  
- **Real-Time Scheduling** – Checks and triggers alarms at precise times  
- **Stop & Reset** – One-button stop and system reset for quick interaction

---

## Technology Stack

- **Voice Recognition**: `speech_recognition` + Google Speech API  
- **Natural Language Understanding & Urgency Detection**: **OpenAI GPT-4 / GPT-3.5**  
- **Music Control**: `spotipy` + **Spotify Web API**  
- **Scheduling & GUI**: `datetime`, `tkinter`  
- **Hardware Communication**: `pyserial`, **Arduino** (LED + OLED)  
- **Hardware Logic**: `Light.ino` (LED PWM control), `Screen.ino` (OLED time & event display)

---

## Important Notes

1. **Hardware Dependency**  
   - This project requires the **Arduino-based hardware** I built specifically for this system.  
   - The Python code alone will not produce the full experience without connecting to this hardware.
   - **You also need to modify the actual hardware port name** in `main.py` according to your setup, for example:  
      ```python
      arduino_port = "COM3"  # Change to the correct port, e.g., "COM5"

2. **API Keys**  
   - Replace the placeholders in `main.py` with **your own API credentials**:  
     - **OpenAI API key**  
     - **Spotify client ID and secret**  

3. **File Storage Path Configuration**  
   - The default cache or temporary file paths in `Echotune.py` may need to be modified based on your system.  
   - For example, replace any hardcoded paths like:

      ```python
      cache_path = "C:/Users/YourName/Desktop/main/.cache"
      
---

## How to Run

### 1. Clone the Repository

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Upload Arduino Sketches
Open Light.ino and Screen.ino in Arduino IDE
Select the correct board & COM port
Upload the code to the Arduino

### 4. Run main.py

### 5. Interact with the System
Press the white button and set a reminder by voice: say something like “I want to do yoga at 9 AM.” or "I have an interview at 10AM."
The system will:
 - Extract activity & time
 - Determine urgency (Urgent / Not Urgent)
 - Schedule the alarm
 - Display info on both GUI and OLED screen
 - Trigger personalized music & light at the scheduled time
 - Stop the alarm by pressing the gray button connected to the Arduino
