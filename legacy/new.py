from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pynput.keyboard import Key, Listener as KeyListener
import time
import random
import subprocess
import os
import sys


class UltimateTypingBot:
    def __init__(self, target_wpm=48):
        self.target_wpm = target_wpm
        self.driver = None
        self.words = []
        self.chrome_process = None

    def kill_existing_chrome(self):
        """Kill all Chrome processes to start fresh"""
        print("\n🔄 Closing existing Chrome instances...")
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],
                               capture_output=True, timeout=5)
                time.sleep(2)
                print("✅ Chrome closed")
            return True
        except:
            print("⚠️  Could not close Chrome automatically")
            return False

    def launch_chrome_with_debugging(self):
        """Launch Chrome with remote debugging"""
        print("\n🚀 Opening Chrome with debugging enabled...")

        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if not chrome_path:
            print("❌ Chrome not found")
            return False

        try:
            # Launch with minimal flags for compatibility
            self.chrome_process = subprocess.Popen([
                chrome_path,
                "--remote-debugging-port=9222",
                "--user-data-dir=" +
                os.path.join(os.environ['TEMP'], 'chrome_bot_profile')
            ])

            print("✅ Chrome launched!")
            print("⏳ Waiting 5 seconds for Chrome to fully start...")
            time.sleep(5)
            return True

        except Exception as e:
            print(f"❌ Failed to launch Chrome: {e}")
            return False

    def connect_to_chrome(self):
        """Connect to Chrome with minimal options (FIX for excludeSwitches error)"""
        print("\n⚙️  Connecting to Chrome...")

        options = Options()

        # ONLY set debugger address - no other options that cause conflicts
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        # These are safe to add after connection
        options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            # Anti-detection script
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("✅ Connected successfully!")
            print(f"   Current URL: {self.driver.current_url}")
            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\n🔄 Trying fallback method (fresh Chrome)...")
            return self.fallback_fresh_chrome()

    def fallback_fresh_chrome(self):
        """Fallback: Start fresh Chrome if connection fails"""
        print("\n⚙️  Starting fresh Chrome (fallback)...")

        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("detach", True)

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("✅ Fresh Chrome started successfully!")
            return True

        except Exception as e:
            print(f"❌ Fallback also failed: {e}")
            return False

    def setup(self):
        """Complete setup with automatic fallback"""
        print("\n" + "="*60)
        print("🔧 AUTOMATIC SETUP")
        print("="*60)

        # Ask user preference
        print("\n📋 Chrome Launch Method:")
        print("   [1] Try to use your profiles (may need Chrome closed)")
        print("   [2] Fresh temporary profile (always works)")

        choice = input("\nChoice (1-2, default 2): ").strip() or "2"

        if choice == "1":
            # Method 1: Try debugging connection
            self.kill_existing_chrome()
            time.sleep(2)

            if self.launch_chrome_with_debugging():
                if self.connect_to_chrome():
                    print("\n💡 You can now switch to any Chrome profile!")
                    print("   Click the profile icon (top-right) and switch")
                    return True

            # If failed, will fall back automatically in connect_to_chrome()

        else:
            # Method 2: Fresh Chrome (guaranteed to work)
            return self.fallback_fresh_chrome()

        return False

    def navigate_to_site(self, url):
        """Navigate to URL"""
        if not url:
            return True

        print(f"\n🌐 Navigating to: {url}")

        try:
            self.driver.get(url)
            self.driver.maximize_window()
            time.sleep(3)
            print("✅ Page loaded!")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            print("💡 You can navigate manually in the browser")
            return False

    def extract_words(self):
        """Extract words from page"""
        print("\n🔍 Extracting words...")

        script = """
        var spans = document.querySelectorAll('span[data-current]');
        if (spans.length === 0) return null;
        
        var words = [];
        spans.forEach(function(span) {
            var text = span.innerText || span.textContent;
            if (text && text.trim()) {
                words.push(text.trim());
            }
        });
        return words.length > 0 ? words : null;
        """

        try:
            words = self.driver.execute_script(script)
            if words and len(words) > 10:
                print(f"   ✅ Found {len(words)} words!")
                return words
            else:
                print(f"   ⚠️  Only found {len(words) if words else 0} words")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        return None

    def find_textarea(self):
        """Find input field"""
        selectors = [
            'textarea[placeholder="Start typing..."]',
            'textarea.notranslate',
            'textarea',
        ]

        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                pass

        return None

    def type_words(self):
        """Type words with ACCURATE WPM timing"""
        if not self.words:
            print("❌ No words to type!")
            return

        textarea = self.find_textarea()
        if not textarea:
            print("❌ No input field found!")
            return

        textarea.click()
        time.sleep(0.5)

        # IMPROVED WPM CALCULATION
        # Average word length in English: 5 chars
        # For accurate WPM: words_per_minute = characters_per_minute / 5
        # characters_per_minute = target_wpm * 5
        # characters_per_second = (target_wpm * 5) / 60
        # delay_per_char = 1 / characters_per_second

        chars_per_second = (self.target_wpm * 5) / 60
        base_delay = 1 / chars_per_second

        # Reduce variance for more consistent speed
        char_variance = (0.92, 1.08)  # Tighter range = more accurate
        space_multiplier = 0.4  # Faster spaces

        print(f"\n⚡ TYPING {len(self.words)} WORDS")
        print(f"   Target WPM: {self.target_wpm}")
        print(f"   Optimized delay: {base_delay:.4f}s per char")
        print(f"   Expected time: {(len(self.words) * 6 * base_delay):.1f}s")
        print("\n   Starting in 3...")
        time.sleep(1)
        print("   2...")
        time.sleep(1)
        print("   1...")
        time.sleep(1)
        print("   🚀 GO!\n")

        start_time = time.time()
        typed_count = 0

        for i, word in enumerate(self.words):
            try:
                # Type each character
                for char in word:
                    textarea.send_keys(char)
                    time.sleep(base_delay * random.uniform(*char_variance))

                # Type space
                textarea.send_keys(' ')
                time.sleep(base_delay * space_multiplier)

                typed_count += 1

                # Progress every 10 words
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    current_wpm = (typed_count / elapsed) * 60
                    remaining = len(self.words) - typed_count
                    eta = (remaining * 6 * base_delay)
                    print(
                        f"   📊 {typed_count}/{len(self.words)} | {current_wpm:.1f} WPM | ETA: {eta:.0f}s")

            except Exception as e:
                print(f"   ⚠️  Error at word {i}: {e}")
                break

        # Final results
        elapsed = time.time() - start_time
        actual_wpm = (typed_count / elapsed) * 60
        accuracy_percent = (actual_wpm / self.target_wpm) * 100

        print(f"\n" + "="*60)
        print(f"✅ TYPING COMPLETE!")
        print(f"="*60)
        print(f"   Words typed:    {typed_count}/{len(self.words)}")
        print(f"   Time taken:     {elapsed:.2f}s")
        print(f"   Target WPM:     {self.target_wpm}")
        print(f"   Actual WPM:     {actual_wpm:.1f}")
        print(f"   Accuracy:       {accuracy_percent:.1f}% of target")
        print(f"   Difference:     {actual_wpm - self.target_wpm:+.1f} WPM")

        if 45 <= actual_wpm <= 55:
            print(f"   🎯 PERFECT! Within 45-55 WPM range!")
        elif actual_wpm >= 40:
            print(f"   ✅ GREAT! Above 40 WPM!")
        elif actual_wpm >= self.target_wpm * 0.9:
            print(f"   👍 GOOD! Within 10% of target!")

        print("="*60 + "\n")

    def run(self):
        """Main execution"""
        print("\n🎯 STARTING BOT")
        time.sleep(1)

        self.words = self.extract_words()

        if not self.words:
            print("\n❌ No words found!")
            print("💡 Make sure you're on the Practice Test page")
            print("   Navigate there in Chrome, then press F2 again")
            return

        print(f"\n✅ Ready to type {len(self.words)} words!")
        print(f"   Preview: {' '.join(self.words[:25])}")
        print(f"   Last 5: {' '.join(self.words[-5:])}")

        confirm = input("\n❓ Start typing now? (y/n): ")

        if confirm.lower() == 'y':
            self.type_words()
        else:
            print("❌ Cancelled. Press F2 to try again.")


bot = None


def on_key(key):
    global bot

    if key == Key.f2:
        print("\n🚀 F2 PRESSED - Starting bot...")
        if bot:
            try:
                bot.run()
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

    elif key == Key.f3:
        print("\n🔄 F3 PRESSED - Re-extracting words...")
        if bot:
            bot.words = bot.extract_words()
            if bot.words:
                print(f"✅ Refreshed! {len(bot.words)} words ready")

    elif key == Key.esc:
        print("\n👋 ESC PRESSED - Exiting...")
        if bot and bot.chrome_process:
            try:
                bot.chrome_process.terminate()
            except:
                pass
        return False


def main():
    global bot

    print("\n" + "🔥"*30)
    print("  ULTIMATE TYPING BOT v10.0 FINAL")
    print("  • Auto Chrome Launch")
    print("  • Accurate WPM Timing")
    print("  • Bulletproof Connection")
    print("🔥"*30)

    # Get target WPM
    try:
        target = int(input("\n🎯 Target WPM (default 48): ") or "48")
    except:
        target = 48

    # Create bot instance
    bot = UltimateTypingBot(target_wpm=target)

    # Setup (handles everything automatically)
    if not bot.setup():
        print("\n❌ Setup failed completely.")
        print("💡 Try running as administrator or check Chrome installation")
        return

    # Get URL
    print("\n🌐 Navigation:")
    url = input("   Enter URL (or press Enter to navigate manually): ").strip()

    if url:
        bot.navigate_to_site(url)
    else:
        print("✅ Navigate manually in the Chrome window that opened")

    # Instructions
    print("\n" + "="*60)
    print("📋 READY TO TYPE!")
    print("="*60)
    print("   CONTROLS:")
    print("   • F2  = Extract words and start typing")
    print("   • F3  = Re-extract words (if page changed)")
    print("   • ESC = Exit bot")
    print()
    print("   INSTRUCTIONS:")
    print("   1. Go to the Practice Test page in Chrome")
    print("   2. Make sure typing test is visible")
    print("   3. Press F2 to start")
    print("="*60)
    print("\n⏳ Waiting for F2...\n")

    # Start keyboard listener
    with KeyListener(on_press=on_key) as listener:
        listener.join()

    print("\n👋 Bot terminated. Chrome may stay open (detached).")


if __name__ == "__main__":
    main()
