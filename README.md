# Typing Performance Assistant

An intelligent automation tool designed to help users optimize and test their typing speed (Words Per Minute) on various online platforms.

## Description

The **Typing Performance Assistant** is a Python-based utility that assists users in achieving consistent typing speeds. By automating the typing process, it allows for precise WPM calibration and testing across different typing environments. It is designed for educational purposes, helping users understand terminal typing speeds and browser interaction patterns.

*Note: This tool is intended for personal performance optimization and educational use.*

## Key Features

- **Dynamic WPM Targeting**: Set your desired Words Per Minute and the assistant will adjust its typing cadence accordingly.
- **Intelligent Word Extraction**: Uses multiple strategies to identify typing text blocks across various websites.
- **Robust Browser Integration**: Supports both fresh sessions and profile-persisted sessions using Selenium and Chrome.
- **Natural Typing Simulation**: Includes randomized delays between characters and words to simulate human-like typing patterns.

## Installation

1. Ensure you have **Python 3.7+** and **Google Chrome** installed.
2. Clone this repository or download the source code.
3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## How to Use

1. Run the main script:
   ```bash
   python typing_assistant.py
   ```
2. Follow the on-screen prompts to set your **Target WPM** and choose a browser launch method.
3. Navigate to your preferred typing test website (e.g., 10FastFingers, MonkeyType, etc.).
4. Once the test content is loaded, press **`F2`** to start the assistant.
5. To exit the application, press **`ESC`**.

## Repository Structure

- `typing_assistant.py`: The main application logic.
- `requirements.txt`: List of Python dependencies.
- `.gitignore`: Configured to keep the repository clean of temporary files and drivers.

## Disclaimer

This tool is for educational and optimization purposes only. Please respect the terms of service of any website you use this with.
