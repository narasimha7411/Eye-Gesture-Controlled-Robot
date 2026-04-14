## 👁️ Eye Gesture and Offline Voice Controlled Rover Using ESP8266
📌 Project Overview

This project presents a real-time Eye Gesture and Offline Voice Controlled Rover designed to enable intuitive and hands-free human–robot interaction using computer vision, offline speech recognition, and wireless communication.

The system allows a user to control a rover using eye gestures (blink patterns and gaze direction) and offline voice commands, making it highly suitable for assistive robotics, hands-free navigation, and human–robot interaction research.
The complete system operates in real time with low latency and does not require any wearable sensors or internet connectivity.

🎯 Aim of the Project

To design and implement a real-time, hands-free rover navigation system using vision-based eye gestures and offline voice commands, ensuring low latency, high reliability, and improved accessibility.

🧠 Problem Statement

Conventional robotic control methods such as joysticks, keyboards, and mobile applications are unsuitable for:

Individuals with motor impairments

Hands-free or sterile environments

Situations requiring fast and intuitive interaction

This project addresses these limitations by using natural human eye movements and speech as control inputs, eliminating the need for physical controllers.

## ⚙️ System Architecture

The system is divided into four logical modules, following a  
Perception → Decision → Communication → Actuation pipeline.

🔹 Vision Module

Captures facial video using a webcam

Extracts facial landmarks using MediaPipe Face Mesh

Detects blink patterns and gaze direction

🔹 Voice Module

Performs fully offline speech recognition using Vosk

Converts spoken commands into rover actions

Works without internet connectivity

🔹 Communication Module

Sends control commands via HTTP over Wi-Fi

Uses lightweight GET requests for low latency

Asynchronous transmission prevents processing delays

🔹 Rover Module

ESP8266 runs an embedded HTTP server

Receives commands and controls motors

Executes movement using a differential drive mechanism

## 🖥️ Software Stack

Python 3.10+

OpenCV 4.x

MediaPipe Face Mesh

NumPy

Vosk (Offline Speech Recognition)

Requests (HTTP Communication)

Arduino IDE (ESP8266 Core)

## 🔩 Hardware Components

ESP8266 NodeMCU

L298N Dual H-Bridge Motor Driver

2 × DC Motors (Differential Drive)

Rover Chassis

Laptop / USB Webcam

Single 12V Battery Supply

Motors powered via L298N

ESP8266 powered from L298N 5V output

Common Ground Connection

## 👁️ Eye Gesture Control Logic
Blink Detection

Blink ratio computed using eyelid landmarks

Differentiates natural blinks from intentional gestures

Gesture Mapping

Gesture	Action  
Double Blink-> Move Forward  
Blink + Look Left->	Turn Left  
Blink + Look Right-> Turn Right  
Long Blink-> Stop  

Calibration

One-time center gaze calibration

Improves accuracy across different users

Advantages

Reduced false triggers

Works under moderate head movement

No wearable or infrared hardware required

## 🎙️ Voice Control Logic

Fully offline voice recognition using Vosk

No cloud services or internet required

Recognized commands:

forward

left

right

stop

blink

Command debounce logic prevents repeated triggers

## 🌐 Communication Method

HTTP GET requests sent from Python to ESP8266

Lightweight and easy to debug

Asynchronous requests ensure:

Vision processing remains smooth

No lag during command execution

Example Command
http://ESP_IP/FORWARD

## 🚗 Rover Control Logic

ESP8266 hosts a Wi-Fi web server

Receives commands and drives motors via L298N

Differential drive enables:

Forward motion

Left turn

Right turn

Stop

Non-blocking motor control ensures:

Continuous Wi-Fi responsiveness

Accurate 90° pivot turns

## 📁 Project Structure

```text
Eye-gesture-voice-controlled-rover/
├── Vision/
│   └── blink_and_gaze_detection.py
│
├── Voice/
│   └── voice_offline.py
│
├── Launcher/
│   └── control_launcher.pyw
│
├── Rover/
│   └── rover_code.ino
│
└── README.md
```

✅ Key Features

Hands-free robot navigation

Real-time eye gesture detection

Fully offline voice control

Low-latency HTTP communication

Modular and extensible architecture

Suitable for assistive technology

## 📊 Results

Accurate blink and gaze detection under normal lighting

Stable Wi-Fi communication with ESP8266

Average command execution latency below 300 ms

Reliable rover movement with reduced false positives

🚀 Applications

Assistive robotics for motor-impaired users

Smart wheelchairs and mobility aids

Defense and surveillance robots

Hands-free robotic control environments

Human–robot interaction research

🔮 Future Scope

Head-pose compensation for improved gaze accuracy

Obstacle detection using ultrasonic or LiDAR sensors

Smartphone-based vision processing

Multimodal interaction (eye + voice + facial expressions)

User studies for accessibility evaluation

## 👨‍💻 Author

Narasimha S 
Engineering Major Project  
Eye Gesture and Voice Controlled Rover

📜 License

This project is released for academic and educational use only.
Commercial use is not permitted without prior permission.
