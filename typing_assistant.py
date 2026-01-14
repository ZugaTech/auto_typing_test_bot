import os
import sys
import time
import random
import subprocess
from pynput.keyboard import Key, Listener
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class TypingAssistant:
    """
    A tool designed to help users optimize their typing performance by automating 
    the typing process on various typing test platforms. This assistant focuses 
    on achieving consistent Words Per Minute (WPM) targets.
    """
    
    def __init__(self, target_wpm=60):
        self.target_wpm = target_wpm
        self.driver = None
        self.words = []
        self.chrome_process = None

    def setup_browser(self, method="fresh"):
        """Initialize the browser connection."""
        print(f"\n[INFO] Setting up browser (Method: {method})...")
        
        options = Options()
        # Common anti-detection and stability flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if method == "profile":
            # Attempt to connect to an existing Chrome instance with debugging enabled
            port = 9222
            profile_path = os.path.join(os.environ.get('TEMP', '.'), 'typing_assistant_profile')
            
            # Simple check for chrome path on Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            chrome_path = next((p for p in chrome_paths if os.path.exists(p)), None)
            
            if chrome_path:
                print(f"[INFO] Launching Chrome with remote debugging on port {port}...")
                self.chrome_process = subprocess.Popen([
                    chrome_path,
                    f"--remote-debugging-port={port}",
                    f"--user-data-dir={profile_path}"
                ])
                time.sleep(3)
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            else:
                print("[WARN] Chrome installation not found. Falling back to fresh session.")
                method = "fresh"

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            # Hide automation flags
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("[SUCCESS] Browser connected.")
            return True
        except Exception as e:
            print(f"[ERROR] Browser setup failed: {e}")
            return False

    def extract_words(self):
        """Extract words using multiple strategy fallbacks."""
        print("\n[INFO] Extracting words from page...")
        
        strategies = [
            # Strategy 1: Common spans (10fastfingers style)
            """
            var spans = document.querySelectorAll('span[data-word-index], span[data-current]');
            if (spans.length > 0) {
                return Array.from(spans).map(s => s.innerText.trim()).filter(t => t.length > 0);
            }
            return null;
            """,
            # Strategy 2: Largest text block identification
            """
            var elements = document.querySelectorAll('div, p, section');
            var best = null;
            var maxWords = 0;
            elements.forEach(el => {
                var text = el.innerText || "";
                var words = text.split(/\s+/).filter(w => w.length > 1);
                if (words.length > 10 && words.length > maxWords) {
                    maxWords = words.length;
                    best = words;
                }
            });
            return best;
            """
        ]

        for i, script in enumerate(strategies):
            try:
                words = self.driver.execute_script(script)
                if words and len(words) > 5:
                    print(f"[SUCCESS] Strategy {i+1} found {len(words)} words.")
                    self.words = words
                    return True
            except:
                continue
        
        print("[ERROR] Could not extract words automatically.")
        return False

    def find_input_field(self):
        """Find the active typing input field."""
        selectors = [
            "inputfield", "input", "textarea", 
            "input[type='text']", "[contenteditable='true']"
        ]
        
        for sel in selectors:
            try:
                # Try as ID first, then as selector/tag
                elements = self.driver.find_elements(By.ID, sel) or \
                           self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    if el.is_displayed():
                        return el
            except:
                continue
        return None

    def perform_typing(self):
        """Execute typing with target WPM timing."""
        if not self.words:
            print("[ERROR] No words to type.")
            return

        input_field = self.find_input_field()
        if not input_field:
            print("[ERROR] Could not find typing input field.")
            return

        # Timing calculation: 5 characters per word is the standard WPM calculation
        # Target CPS = (WPM * 5) / 60
        # Delay per character = 1 / target_cps
        target_cps = (self.target_wpm * 5) / 60
        base_delay = 1 / target_cps
        
        print(f"\n[STARTING] Target: {self.target_wpm} WPM | Words: {len(self.words)}")
        print("Prepare the browser window... Starting in 3 seconds.")
        time.sleep(3)

        input_field.click()
        start_time = time.time()
        
        for i, word in enumerate(self.words):
            try:
                # Type characters
                for char in word:
                    input_field.send_keys(char)
                    # Add natural variance
                    time.sleep(base_delay * random.uniform(0.8, 1.2))
                
                # Type space (or enter if last word)
                input_field.send_keys(" ")
                time.sleep(base_delay * 0.5)
                
                if (i + 1) % 10 == 0:
                    print(f" Progress: {i+1}/{len(self.words)} words typed...")
            except Exception as e:
                print(f"[ERROR] During typing: {e}")
                break

        elapsed = time.time() - start_time
        actual_wpm = (len(self.words) / (elapsed / 60)) if elapsed > 0 else 0
        print(f"\n[FINISHED] Completed in {elapsed:.2f}s | Actual WPM: {actual_wpm:.1f}")

    def run_cli(self):
        """Main CLI interface."""
        print("="*40)
        print("      TYPING PERFORMANCE ASSISTANT")
        print("="*40)
        
        try:
            self.target_wpm = int(input("Enter Target WPM (default 60): ") or "60")
        except:
            self.target_wpm = 60
            
        print("\nLaunch Options:")
        print("1. Fresh Session (Recommended)")
        print("2. Profile Session (Reuse session data)")
        choice = input("Choice [1/2]: ")
        
        method = "profile" if choice == "2" else "fresh"
        if not self.setup_browser(method):
            return

        print("\nCommands:")
        print(" - Navigate to your typing test URL in the browser.")
        print(" - Press F2 to extract words and start typing.")
        print(" - Press ESC to exit.")
        
        def on_press(key):
            if key == Key.f2:
                if self.extract_words():
                    self.perform_typing()
            elif key == Key.esc:
                print("\n[EXIT] Closing Assistant...")
                if self.driver:
                    self.driver.quit()
                return False

        with Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    assistant = TypingAssistant()
    assistant.run_cli()
