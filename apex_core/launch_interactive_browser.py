"""
launch_interactive_browser.py
Launches an interactive Chrome window that stays open continuously on Leo's screen.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def open_persistent_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)  # Keeps Chrome window open after script exits

    print("[Apex Browser Agent] Launching interactive Chrome window...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://accounts.google.com/signup")
    print("[Apex Browser Agent] Chrome window successfully opened on Leo's screen!")

if __name__ == "__main__":
    open_persistent_chrome()
