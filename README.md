# 🚗 **Robot Control System** 🤖

A Python-based system for controlling MiR robots through natural language commands using both text and voice interfaces. The system processes natural language inputs, converts them into API commands, and sends them to the robot for execution.

## 📝 **Project Overview**

This project enables intuitive control of MiR robots by:

- **Processing natural language commands** through text or voice input.
- **Converting speech to text** using the Whisper AI model.
- **Analyzing commands** using Natural Language Processing (NLP).
- **Sending REST API requests** to the robot for execution.

---

## 🛠️ **System Architecture**

The system consists of four main components:

### 1️⃣ **REST API Client (`rest.py`)**
The foundation of the system that handles all communication with the MiR robot's REST API. It includes:

- Robot type configuration (MIR200/MIR250)
- Position and mission management
- Command execution functionality
- Error handling and request management

### 2️⃣ **Natural Language Processing (`transcript_post_processing.py`)**
Processes text commands using **spaCy** for NLP operations. Its features include:

- **Extracting key instructions, positions, and mission names** from natural language input.
- **Matching commands to available robot actions** using similarity scoring.
- **Disambiguating commands** when multiple matches are found.
- Integrating with the REST API client to execute commands.

### 3️⃣ **Voice Recognition (`Whisper_Live.py`)**
Manages real-time voice input processing using the **Whisper AI** model:

- **Recording audio** through the system microphone.
- **Processing recordings** using the Faster Whisper model.
- **Converting speech to text** for further processing.
- Handling temporary file management for audio processing.

### 4️⃣ **Main Application (`main.py`)**
Coordinates all components and provides the user interface. Its responsibilities include:

- **Initializing system components**.
- Managing the **command input loop**.
- Routing commands through the **processing pipeline**.
- Handling **user interaction and feedback**.

---

## Setup and Installation

Follow these steps to set up and run the project locally:

### 1. Clone the Repository
To start, clone this repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/seergiromero/MiR-Voice-Controller.git
cd MiR-Voice-Controller/
```

### 2. Install Required Dependencies
Use pip to install all the necessary dependencies listed in the requirements.txt file:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

---

## 📂 **Project Structure**

```plaintext
MiR-Voice-Controller/
│
├── rest.py                   # Manages communication with the robot's API
├── transcript_post_processing.py # Processes text and NLP commands
├── Whisper_Live.py           # Manages real-time voice input
├── main.py                   # Coordinates components and UI
└── README.md                 # Project documentation
