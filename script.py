from flask import Flask, jsonify
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from threading import Thread

app = Flask(__name__)

def get_ai_news(api_key):
    try:
        url = f"https://newsapi.org/v2/everything?q=artificial+intelligence&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def format_articles(articles):
    formatted_articles = ""
    for article in articles:
        formatted_articles += f"Title: {article['title']}\n"
        formatted_articles += f"Description: {article['description']}\n"
        formatted_articles += f"URL: {article['url']}\n\n"
    return formatted_articles

def send_email(subject, body, to_email, from_email, password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

def job():
    api_key = os.getenv('NEWS_API_KEY')
    to_email = os.getenv('TO_EMAIL')
    from_email = os.getenv('FROM_EMAIL')
    password = os.getenv('EMAIL_PASSWORD')

    articles = get_ai_news(api_key)
    formatted_articles = format_articles(articles)
    send_email("Weekly AI News", formatted_articles, to_email, from_email, password)

@app.route('/')
def index():
    return jsonify({"status": "Application is running!"})

def run_scheduler():
    # Exécuter la tâche immédiatement pour tester
    job()

    # Planification pour une fois par semaine
    schedule.every().sunday.at("10:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Lancer le planificateur dans un thread séparé
    Thread(target=run_scheduler).start()
    # Démarrer le serveur Flask
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
