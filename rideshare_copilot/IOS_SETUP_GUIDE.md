# Rideshare Profit Copilot - iPhone 16 Pro Max Setup Guide

This guide enables **100% hands-free profit calculation** while driving for Uber, Lyft, and Walmart Spark on iOS.

---

## 1. How It Operates (Zero-Touch Driving Flow)

```
[Phone mounted on dashboard running Uber / Lyft / Spark]
                        │
       [Offer chime sounds on the phone]
                        │
          [You speak one word: "Check"]
                        │
[iOS Voice Control triggers the Copilot Shortcut]
                        │
[Takes screenshot ➔ Extracts Pay & Miles via on-device OCR]
                        │
[Car Bluetooth / Phone Speaker announces in 1 sec]:
   🟢 "Uber Green. 2 dollars and 40 cents a mile. 4 miles total."
   🔴 "Lyft Red. 75 cents a mile. Pass."
```

- **You never touch the phone.**
- **No apps need to be switched.**
- **Zero ban risk:** It only reads pixels on your own device—never interacts with driver app code or servers.

---

## 2. Setting Up Voice Control (Hands-Free Wake Word)

This makes your iPhone listen for your custom trigger word without needing "Hey Siri".

1. On your iPhone 16 Pro Max, open **Settings**.
2. Go to **Accessibility** ➔ **Voice Control**.
3. Toggle **Voice Control** to **ON** (a small blue microphone icon appears in the status bar/Dynamic Island).
4. Tap **Commands** ➔ **Custom** ➔ **Create New Command...**
5. Configure the command:
   - **Phrase:** Type `Check` (or `Scan`, `Radar`, `Evaluate`).
   - **Action:** Tap **Run Shortcut**.
   - Select your shortcut: **Rideshare Copilot**.
6. Tap **Save**.

Now, whenever you say **"Check"**, your iPhone instantly runs the analysis.

---

## 3. Creating the "Rideshare Copilot" Apple Shortcut

You can create this directly inside the native **Shortcuts** app on your iPhone:

### Step-by-Step Shortcut Recipe:
1. Open the **Shortcuts** app on your iPhone.
2. Tap the **+** (plus) in the top right to create a new shortcut. Name it **Rideshare Copilot**.
3. Add the following sequence of actions:

```
1. [Take Screenshot]
   - Action: "Take Interactive Screenshot" or "Take Screenshot"

2. [Extract Text from Image]
   - Action: "Extract Text from [Screenshot]" (Uses Apple's native Vision OCR on-device)

3. [Run JavaScript on Text / Match Regex]
   - Action: "Match Text"
   - Match Fare: `\$\s*(\d+(?:\.\d{2})?)`
   - Match Miles: `(\d+(?:\.\d+)?)\s*(?:mi|miles)`

4. [Calculate Rate]
   - Calculate: `Fare / Miles`

5. [Conditional / If Statement]:
   - If [Calculation Result] is greater than or equal to 1.75:
       - Set Verdict to "Green"
       - Text: "[App] Green. [Calculation Result] dollars a mile. Take it."
   - Otherwise:
       - Set Verdict to "Red"
       - Text: "[App] Red. [Calculation Result] a mile. Pass."

6. [Speak Text]
   - Action: "Speak [Text]"
   - Voice: Samantha or Siri (American)
   - Rate: Normal / Slightly fast (1.1x)
   - Audio Route: Default (Automatically plays over Car Bluetooth or Speakers)
```

---

## 4. Alternative Quick-Trigger: Action Button or Back-Tap

If you ever prefer a tactile click instead of speaking:

- **Action Button (iPhone 16 Pro Max):**
  - Settings ➔ **Action Button** ➔ Slide to **Shortcut** ➔ Choose **Rideshare Copilot**.
  - One long-press on the side button scans the screen and speaks the rate.

- **Back Tap (Dashboard or Hand):**
  - Settings ➔ **Accessibility** ➔ **Touch** ➔ **Back Tap** ➔ **Double Tap** ➔ Choose **Rideshare Copilot**.

---

## 5. Testing the Calibration Dashboard Locally

You can run the interactive simulator on your computer right now to test real offer scenarios and audio playback:

```powershell
# From the project directory:
python -m http.server 8080 --directory rideshare_copilot
```
Then open: `http://localhost:8080/dashboard.html` in your browser.
