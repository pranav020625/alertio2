from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import json

app = Flask(__name__)
CORS(app)

def send_email_alert(email_receiver, subject, message):
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = email_receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, email_receiver, msg.as_string())
        print(f"Email Sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_price(url, selector):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        price_text = driver.find_element(By.CSS_SELECTOR, selector).text
        driver.quit()
        return float(price_text.replace("₹", "").replace(",", "").strip())
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def price_checker(data):
    amazon_url = data.get("amazon_url")
    flipkart_url = data.get("flipkart_url")
    email_receiver = data.get("email")
    target_price = float(data.get("target_price"))

    amazon_price = get_price(amazon_url, ".a-price-whole") if amazon_url else None
    flipkart_price = get_price(flipkart_url, "._30jeq3._16Jk6d") if flipkart_url else None

    if amazon_price and amazon_price <= target_price:
        send_email_alert(email_receiver, "🔥 Amazon Price Drop Alert!", f"Price: ₹{amazon_price}\n{amazon_url}")

    if flipkart_price and flipkart_price <= target_price:
        send_email_alert(email_receiver, "🔥 Flipkart Price Drop Alert!", f"Price: ₹{flipkart_price}\n{flipkart_url}")

@app.route("/start-tracking", methods=["POST"])
def start_tracking():
    data = request.json
    # Save data for Jenkins to read
    with open("tracking_data.json", "w") as f:
        json.dump(data, f)
    return jsonify({"status": "Tracking data saved"}), 200

@app.route("/")
def home():
    return jsonify({"status": "Price Alert Service is running!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
