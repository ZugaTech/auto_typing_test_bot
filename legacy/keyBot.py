from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pynput.keyboard import Key, Listener
import time
import random


class SmartTypingBot:
    def __init__(self, target_wpm=48):
        self.target_wpm = target_wpm
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)

    def debug_page_structure(self):
        """Debug: Print all possible text containers"""
        print("\n🔍 DEBUGGING PAGE STRUCTURE...")
        print("="*60)

        # Get all visible text elements
        script = """
        var elements = document.querySelectorAll('*');
        var results = [];
        
        elements.forEach(function(el) {
            var text = el.innerText || el.textContent;
            if (text && text.trim().length > 20 && text.split(' ').length > 5) {
                results.push({
                    tag: el.tagName,
                    id: el.id || 'none',
                    class: el.className || 'none',
                    text: text.substring(0, 100)
                });
            }
        });
        
        return results.slice(0, 10);
        """

        elements = self.driver.execute_script(script)

        print("📋 Found these text containers:")
        for i, el in enumerate(elements):
            print(f"\n  [{i+1}] Tag: {el['tag']}")
            print(f"      ID: {el['id']}")
            print(f"      Class: {el['class']}")
            print(f"      Text: {el['text'][:60]}...")

        print("\n" + "="*60)
        return elements

    def get_words_advanced(self):
        """Advanced word detection with JavaScript"""
        print("📖 Attempting advanced text detection...")

        # Wait for page to load
        time.sleep(2)

        # Strategy 1: Find by common IDs/Classes
        selectors = [
            "#row1", "#words", "#word", ".words", ".word",
            "#quote", ".quote", "#text", ".text",
            "[class*='word']", "[id*='word']",
            "[class*='quote']", "[class*='text']"
        ]

        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and len(text.split()) > 3:
                    print(f"✅ Found text using selector: {selector}")
                    return text.split()
            except:
                pass

        # Strategy 2: JavaScript - find largest text block
        print("🔍 Using JavaScript to find text...")
        script = """
        var all = document.querySelectorAll('*');
        var candidates = [];
        
        all.forEach(function(el) {
            var text = el.innerText || el.textContent;
            if (text) {
                text = text.trim();
                var words = text.split(/\\s+/);
                if (words.length >= 5 && words.length <= 200) {
                    candidates.push({
                        element: el,
                        text: text,
                        wordCount: words.length
                    });
                }
            }
        });
        
        candidates.sort((a, b) => {
            // Prefer elements with 20-100 words
            var scoreA = Math.abs(a.wordCount - 50);
            var scoreB = Math.abs(b.wordCount - 50);
            return scoreA - scoreB;
        });
        
        return candidates.length > 0 ? candidates[0].text : null;
        """

        text = self.driver.execute_script(script)
        if text:
            print(
                f"✅ Found text using JavaScript (length: {len(text.split())} words)")
            return text.split()

        # Strategy 3: Debug and manual selection
        print("\n❌ Auto-detection failed. Showing page structure...")
        elements = self.debug_page_structure()

        if elements:
            print("\n❓ Which element contains the typing text?")
            choice = input("Enter number (1-10) or 0 to cancel: ")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(elements):
                    # Try to find and get text
                    return elements[idx]['text'].split()
            except:
                pass

        return None

    def find_input_advanced(self):
        """Advanced input detection"""
        print("🔍 Detecting input field...")

        # Wait a bit
        time.sleep(1)

        # Strategy 1: Common selectors
        selectors = [
            (By.ID, "inputfield"),
            (By.ID, "input"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input.input"),
            (By.CSS_SELECTOR, "textarea"),
            (By.CSS_SELECTOR, "[contenteditable='true']"),
            (By.TAG_NAME, "input"),
        ]

        for by, selector in selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for element in elements:
                    if element.is_displayed():
                        print(f"✅ Found input: {by} = {selector}")
                        return element
            except:
                pass

        # Strategy 2: JavaScript
        script = """
        var inputs = document.querySelectorAll('input, textarea, [contenteditable="true"]');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                return inputs[i];
            }
        }
        return null;
        """

        element = self.driver.execute_script(script)
        if element:
            print("✅ Found input using JavaScript")
            return element

        print("❌ Could not find input field!")
        return None

    def type_fast(self, words, input_box):
        """Fast typing method"""
        base_delay = 60 / (self.target_wpm * 6)

        print(f"⚡ Typing at {self.target_wpm} WPM (delay: {base_delay:.4f}s)")

        for word in words:
            input_box.send_keys(word + ' ')
            time.sleep(base_delay * len(word) * random.uniform(0.9, 1.1))

    def start(self):
        try:
            print("\n" + "="*60)
            print(f"🎯 TARGET: {self.target_wpm} WPM")
            print("="*60)

            # Get words
            words = self.get_words_advanced()

            if not words:
                print("\n❌ FAILED to detect text!")
                print("\n💡 TIP: Try the OCR version (Solution 2) instead!")
                return

            print(f"✅ Found {len(words)} words")
            print(f"📝 First 10 words: {' '.join(words[:10])}")

            # Find input
            input_box = self.find_input_advanced()

            if not input_box:
                print("❌ Could not find input field!")
                return

            # Click and focus
            try:
                input_box.click()
            except:
                self.driver.execute_script("arguments[0].focus();", input_box)

            time.sleep(0.5)

            # Type
            start_time = time.time()
            self.type_fast(words, input_box)
            elapsed = time.time() - start_time

            actual_wpm = (len(words) / elapsed) * 60

            print("\n" + "="*60)
            print(f"✅ COMPLETED in {elapsed:.2f}s")
            print(f"🚀 Actual WPM: {actual_wpm:.1f}")
            print("="*60 + "\n")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


bot = None


def on_release(key):
    global bot
    if key == Key.f2:
        print("\n🔥 F2 PRESSED - STARTING...")
        if bot:
            bot.start()
    elif key == Key.esc:
        print("\n👋 EXITING...")
        if bot:
            bot.driver.quit()
        return False


def main():
    global bot

    print("\n🔥 SMART TYPING BOT - DEBUG VERSION")

    target = int(input("🎯 Target WPM (default 48): ") or "48")
    url = input("🌐 URL: ").strip()

    bot = SmartTypingBot(target_wpm=target)
    bot.driver.get(url)
    bot.driver.maximize_window()

    print("\n✅ Ready! Press F2 to start, ESC to exit")

    with Listener(on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
