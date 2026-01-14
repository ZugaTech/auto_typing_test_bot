from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pynput.keyboard import Key, Listener as KeyListener
import time
import random
import re


class CompleteTypingBot:
    def __init__(self, target_wpm=48):
        self.target_wpm = target_wpm
        self.driver = None
        self.words = []
        self.wait = None

    def setup(self):
        """Initialize browser"""
        print("\n⚙️  Starting browser...")

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

        self.driver.get("https://somewheretypingtest.com/test")
        self.driver.maximize_window()

        print("✅ Browser loaded")
        time.sleep(3)

    def navigate_to_test(self):
        """Navigate through the wizard to reach the typing test"""
        print("\n🧭 Navigating through pages...")

        # Page 1: Test Info
        print("   📄 Page 1: Test Info")
        try:
            # Look for Next/Continue button
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                text = btn.text.lower()
                if any(word in text for word in ['next', 'continue', 'start', 'begin']):
                    print(f"   ✅ Clicking: {btn.text}")
                    btn.click()
                    time.sleep(2)
                    break
        except Exception as e:
            print(f"   ⚠️  Page 1 navigation: {e}")

        # Page 2: Personal Info (might need to fill or skip)
        print("   📄 Page 2: Personal Info")
        try:
            # Look for Skip or Next button
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                text = btn.text.lower()
                if any(word in text for word in ['skip', 'next', 'continue']):
                    print(f"   ✅ Clicking: {btn.text}")
                    btn.click()
                    time.sleep(2)
                    break
        except Exception as e:
            print(f"   ⚠️  Page 2 navigation: {e}")

        # Page 3: Practice (or go to Page 4: Typing Test)
        print("   📄 Page 3: Practice / Page 4: Typing Test")
        try:
            # Check if we're on Practice or Typing Test page
            page_text = self.driver.find_element(By.TAG_NAME, "body").text

            if "Practice" in page_text:
                print("   ✅ On Practice page")
                # Look for Skip Practice Test button
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if 'skip' in btn.text.lower() and 'practice' in btn.text.lower():
                        print(
                            f"   ⚠️  Found Skip Practice - staying on practice for testing")
                        # Don't skip - we want to test on practice
                        break

            time.sleep(2)

        except Exception as e:
            print(f"   ⚠️  Page 3/4 navigation: {e}")

        print("   ✅ Navigation complete!\n")

    def extract_test_text(self):
        """Extract the typing test text"""
        print("🔍 Extracting test text...")

        # Wait for content to load
        time.sleep(2)

        # Multiple extraction strategies
        strategies = [
            ("Specific selectors", """
                var selectors = [
                    '.practice-text', '#practice-text',
                    '.test-text', '#test-text',
                    '.typing-text', '#typing-text',
                    '[data-test-text]', '[data-practice-text]'
                ];
                
                for (var i = 0; i < selectors.length; i++) {
                    var el = document.querySelector(selectors[i]);
                    if (el) {
                        var text = el.innerText || el.textContent;
                        if (text && text.length > 50) {
                            return {
                                method: selectors[i],
                                text: text,
                                hasSpaces: text.includes(' ')
                            };
                        }
                    }
                }
                return null;
            """),

            ("Search for oak tree text", """
                var bodyText = document.body.innerText;
                var startIdx = bodyText.indexOf('old oak') !== -1 ? 
                              bodyText.indexOf('old oak') - 10 : 
                              bodyText.indexOf('Theold');
                
                if (startIdx >= 0) {
                    var endIdx = bodyText.indexOf('important one of all', startIdx) + 25;
                    var text = bodyText.substring(Math.max(0, startIdx), endIdx);
                    return {
                        method: 'Body text search',
                        text: text.trim(),
                        hasSpaces: text.includes(' ')
                    };
                }
                return null;
            """),

            ("Long text blocks", """
                var allElements = document.querySelectorAll('div, p, span, pre');
                var candidates = [];
                
                for (var i = 0; i < allElements.length; i++) {
                    var text = allElements[i].innerText;
                    if (text && text.length > 100 && text.length < 2000) {
                        // Skip if it's navigation/UI text
                        if (!text.includes('Test Info') && 
                            !text.includes('Personal Info') &&
                            !text.includes('Test Summary')) {
                            candidates.push({
                                text: text,
                                length: text.length,
                                hasSpaces: text.includes(' ')
                            });
                        }
                    }
                }
                
                if (candidates.length > 0) {
                    // Sort by length, prefer medium length
                    candidates.sort((a, b) => Math.abs(a.length - 500) - Math.abs(b.length - 500));
                    return {
                        method: 'Long text block',
                        text: candidates[0].text,
                        hasSpaces: candidates[0].hasSpaces
                    };
                }
                return null;
            """),

            ("All visible text analysis", """
                var fullText = document.body.innerText;
                var lines = fullText.split('\\n');
                
                // Find the longest line that looks like typing test content
                var bestLine = '';
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i].trim();
                    if (line.length > 200 && line.length < 2000) {
                        if (line.includes('tree') || line.includes('oak') || 
                            line.includes('meadow') || line.includes('Theold')) {
                            bestLine = line;
                            break;
                        }
                    }
                }
                
                if (bestLine) {
                    return {
                        method: 'Line analysis',
                        text: bestLine,
                        hasSpaces: bestLine.includes(' ')
                    };
                }
                return null;
            """)
        ]

        for name, script in strategies:
            try:
                print(f"   Trying: {name}...")
                result = self.driver.execute_script(script)

                if result and result.get('text'):
                    text = result['text'].strip()
                    has_spaces = result.get('hasSpaces', False)

                    print(f"   ✅ SUCCESS with {name}!")
                    print(f"   Method: {result.get('method', name)}")
                    print(f"   Length: {len(text)} chars")
                    print(f"   Has spaces: {has_spaces}")
                    print(f"   Preview: {text[:100]}...")

                    return text, has_spaces

            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:50]}")

        # Fallback: Save debug info
        print("\n   ⚠️  All methods failed. Saving debug info...")
        self.driver.save_screenshot("test_page.png")

        with open("test_page.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)

        with open("test_page_text.txt", "w", encoding="utf-8") as f:
            f.write(self.driver.find_element(By.TAG_NAME, "body").text)

        print("   💾 Saved: test_page.png, test_page.html, test_page_text.txt")

        return None, False

    def segment_text(self, text):
        """Segment text without spaces into words"""
        print("\n🔧 Segmenting concatenated text...")

        # Simple dictionary of common words
        common_words = set("""
        the be to of and a in that have it for not on with he as you do at
        this but his by from they we say her she or an will my one all would
        there their what so up out if about who get which go me when make can
        like time no just him know take people into year your good some could
        them see other than then now look only come its over think also back
        after use two how our work first well way even new want because any
        these give day most us old oak tree stood edge meadow longer anyone
        remember massive branches stretched skyward shelter birds squirrels
        gathering place those seeking shade generations carved initials bark
        love stories friendships etched weathered skin summer children built
        tire swings sturdy limbs laughter ringing warm air autumn golden leaves
        rained confetti blanketing ground crisp colorful carpet during quiet
        winter bare strong waiting patiently spring renewal young woman sat
        beneath rough book resting lap seen countless unfold hers another
        moment felt important
        """.split())

        text = text.replace(' ', '').lower()
        n = len(text)

        # Dynamic programming
        dp = [None] * (n + 1)
        dp[0] = (0, 0)

        for i in range(1, n + 1):
            best_cost = float('inf')
            best_split = 0

            for j in range(max(0, i - 15), i):
                if dp[j] is None:
                    continue

                word = text[j:i]

                if word in common_words:
                    cost = 0
                elif len(word) == 1 and word in 'ai':
                    cost = 0
                else:
                    cost = len(word) ** 2

                total_cost = dp[j][0] + cost

                if total_cost < best_cost:
                    best_cost = total_cost
                    best_split = j

            dp[i] = (best_cost, best_split)

        # Backtrack
        words = []
        i = n
        while i > 0:
            split_pos = dp[i][1]
            words.append(text[split_pos:i])
            i = split_pos

        words.reverse()

        print(f"   ✅ Segmented into {len(words)} words")
        print(f"   Preview: {' '.join(words[:20])}...")

        return words

    def find_input(self):
        """Find input field"""
        selectors = [
            "input[type='text']",
            "textarea",
            "[contenteditable='true']",
            "input.input",
            "#input"
        ]

        for sel in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    if el.is_displayed():
                        print(f"✅ Found input: {sel}")
                        return el
            except:
                pass

        return None

    def type_text(self):
        """Type the extracted text"""
        if not self.words:
            print("❌ No words to type!")
            return

        # Find input
        input_field = self.find_input()
        if not input_field:
            print("❌ Could not find input field!")
            return

        # Focus
        input_field.click()
        time.sleep(0.5)

        # Calculate timing
        base_delay = 60 / (self.target_wpm * 6)

        print(f"\n⚡ TYPING {len(self.words)} WORDS")
        print(f"   Target WPM: {self.target_wpm}")
        print(f"   Char delay: {base_delay:.4f}s")
        print("\n   Starting in 3...")
        time.sleep(1)
        print("   2...")
        time.sleep(1)
        print("   1...")
        time.sleep(1)
        print("   🚀 GO!\n")

        start_time = time.time()

        for i, word in enumerate(self.words):
            try:
                # Type word
                for char in word:
                    input_field.send_keys(char)
                    time.sleep(base_delay * random.uniform(0.9, 1.1))

                # Space
                input_field.send_keys(' ')
                time.sleep(base_delay * 0.7)

                # Progress
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    current_wpm = ((i + 1) / elapsed) * 60
                    print(
                        f"   📊 {i+1}/{len(self.words)} words | {current_wpm:.1f} WPM")

            except Exception as e:
                print(f"   ⚠️  Error at word {i}: {e}")
                break

        # Results
        elapsed = time.time() - start_time
        actual_wpm = (len(self.words) / elapsed) * 60

        print(f"\n" + "="*60)
        print(f"✅ COMPLETED!")
        print(f"="*60)
        print(f"   Time:       {elapsed:.2f}s")
        print(f"   Words:      {len(self.words)}")
        print(f"   Target WPM: {self.target_wpm}")
        print(f"   Actual WPM: {actual_wpm:.1f}")
        print(f"   Difference: {actual_wpm - self.target_wpm:+.1f} WPM")
        print("="*60 + "\n")

    def run(self):
        """Main execution"""
        # Navigate to test page
        self.navigate_to_test()

        # Extract text
        text, has_spaces = self.extract_test_text()

        if not text:
            print("\n❌ Could not extract text!")
            print("💡 Check debug files: test_page.png, test_page_text.txt")

            # Manual input
            manual = input("\n📝 Paste text manually? (y/n): ")
            if manual.lower() == 'y':
                text = input("Text: ").strip()
                has_spaces = ' ' in text

        if not text:
            print("❌ No text available!")
            return

        # Process text
        if has_spaces:
            print("\n✅ Text has spaces, using as-is")
            self.words = text.split()
        else:
            print("\n⚠️  Text has NO spaces, segmenting...")
            self.words = self.segment_text(text)

        if not self.words:
            print("❌ No words!")
            return

        print(f"\n✅ Ready to type {len(self.words)} words!")
        print(f"   First 15: {' '.join(self.words[:15])}")

        confirm = input("\nStart typing? (y/n): ")
        if confirm.lower() == 'y':
            self.type_text()


# Global instance
bot = None


def on_key(key):
    global bot

    if key == Key.f2:
        print("\n🚀 F2 - Starting bot...")
        if bot:
            try:
                bot.run()
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

    elif key == Key.esc:
        print("\n👋 Exiting...")
        if bot and bot.driver:
            bot.driver.quit()
        return False


def main():
    global bot

    print("\n" + "🔥"*30)
    print("  COMPLETE TYPING TEST BOT")
    print("  Navigates Multi-Page Wizard")
    print("🔥"*30)

    target = int(input("\n🎯 Target WPM (default 48): ") or "48")

    print("\n⚙️  Initializing...")
    bot = CompleteTypingBot(target_wpm=target)
    bot.setup()

    print("\n" + "="*60)
    print("⌨️  CONTROLS:")
    print("   F2  - Navigate and start typing")
    print("   ESC - Exit")
    print("="*60)
    print("\n⏳ Press F2 when ready...\n")

    with KeyListener(on_press=on_key) as listener:
        listener.join()


if __name__ == "__main__":
    main()
