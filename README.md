# auto_typing_test_bot

Automates typing on browser-based typing test sites (10FastFingers, MonkeyType, etc.) to hit a target WPM.

Built for personal benchmarking and to understand how browser automation interacts with real-time text input.

## Requirements

- Python 3.7+
- Google Chrome installed

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python typing_assistant.py
```

1. Set your target WPM when prompted
2. Choose fresh or profile browser session
3. Navigate to a typing test site
4. Press **F2** when the test text is loaded - typing starts automatically
5. Press **ESC** to quit

## How it works

Injects JavaScript to extract word elements from the page, then sends keystrokes with randomized delays to stay within the target WPM range. Falls back to a largest-text-block strategy if site-specific selectors don't match.

## Note

For personal use and learning only. Check the ToS of any site before using.