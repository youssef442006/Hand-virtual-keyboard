# ⌨️ Virtual Hand Keyboard

this is an innovative Open-Source Virtual Keyboard that allows users to type in both **Arabic** and **English** simply by moving their hands in the air. Using Computer Vision, the project tracks finger movements to simulate a real typing experience without any physical hardware.



## 🌟 Features
* **Dual Language Support:** Full support for Arabic (with proper reshaping and BiDi) and English layouts.
* **Smart Suggestions:** Real-time word suggestions based on custom dictionaries.
* **Hand Gesture Control:** Typing via "Pinch" gesture or "Dwelling" (hovering).
* **High Performance:** Optimized rendering engine to ensure smooth FPS even during complex Arabic text processing.
* **Auto-Correction:** Intelligent matching for Arabic words with and without "AL" (ال) prefix.

## 🚀 Technologies Used
* **Python 3.x**
* **OpenCV:** For video capturing and image processing.
* **Mediapipe:** For high-fidelity hand tracking.
* **Pillow (PIL):** For advanced text rendering and Arabic font support.
* **Arabic Reshaper & Python-Bidi:** To handle the complexities of Arabic script.
* **Pynput:** To simulate actual keyboard strokes on the OS.

