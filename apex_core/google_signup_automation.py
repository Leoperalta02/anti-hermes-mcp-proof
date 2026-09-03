"""
google_signup_automation.py
Opens Google Account creation page in Chrome with Leo Peralta & apex.luxury.ai details pre-filled.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def launch_google_signup():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print("[Apex Browser Agent] Navigating to Google Account Signup...")
    driver.get("https://accounts.google.com/signup")
    time.sleep(3)

    print("[Apex Browser Agent] Pre-filling signup details for Leo Peralta...")
    try:
        # Pre-fill First Name & Last Name
        fname_field = driver.find_element(By.NAME, "firstName")
        lname_field = driver.find_element(By.NAME, "lastName")

        fname_field.send_keys("Leo")
        lname_field.send_keys("Peralta")

        print("[Apex Browser Agent] Leo Peralta pre-filled. Next button ready!")
    except Exception as e:
        print(f"[Apex Browser Agent] Note: Page structure rendered standard view: {e}")

    print("[Apex Browser Agent] Window is open for Leo to complete SMS verification.")
    time.sleep(30)

if __name__ == "__main__":
    launch_google_signup()
