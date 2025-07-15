# Echotune – Smart Voice-Controlled Alarm

Echotune is a **smart, voice-controlled reminder system** that integrates **LLM-based natural language understanding**, **music playback**, and **ambient lighting** to deliver personalized alarms.  
It is designed as a **hardware + software** system and requires the accompanying Arduino-based device to run properly.

---

## ✨ Features

- **Voice Recognition** – Set reminders hands-free using natural speech  
- **Natural Language Parsing (LLM)** – Extracts activity and time automatically  
- **Urgency Classification (LLM)** – Classifies events as **Urgent** or **Not Urgent** for personalized responses  
- **Music Playback** – Plays energetic or soothing music via Spotify based on urgency  
- **Light Emitting** – Controls LED lighting patterns via Arduino for visual cues  
- **Screen Display** – Displays current time and scheduled events on an OLED screen  
- **Real-Time Scheduling** – Checks and triggers alarms at precise times  
- **Stop & Reset** – One-button stop and system reset for quick interaction

---

## 🛠️ Technology Stack

- **Voice Recognition**: `speech_recognition` + Google Speech API  
- **Natural Language Understanding & Urgency Detection**: **OpenAI GPT-4 / GPT-3.5**  
- **Music Control**: `spotipy` + **Spotify Web API**  
- **Scheduling & GUI**: `datetime`, `tkinter`  
- **Hardware Communication**: `pyserial`, **Arduino** (LED + OLED)  
- **Hardware Logic**: `Light.ino` (LED PWM control), `Screen.ino` (OLED time & event display)

---

## ⚠️ Important Notes

1. **Hardware Dependency**  
   - This project requires the **Arduino-based hardware** (with LED and OLED screen) I built specifically for this system.  
   - The Python code alone will not produce the full experience without connecting to this hardware.

2. **API Keys**  
   - Replace the placeholders in `Echotune.py` with **your own API credentials**:  
     - **OpenAI API key**  
     - **Spotify client ID and secret**  
   - ⚠️ **Never upload personal API keys to a public repository.**

3. **Environment**  
   - Tested on **Python 3.8+** and **Arduino Uno**  
   - Works on both Windows and macOS (adjust COM port as needed)

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/Echotune.git
cd Echotune
