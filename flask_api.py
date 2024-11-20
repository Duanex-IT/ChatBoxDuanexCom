import os
import re
import csv
import logging

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)
CORS(app)

# Caching
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
cache = Cache(app)

# Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"]
)
client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

with open("duanex.txt", "r") as file:
    my_data = file.read()

# Logging
logging.basicConfig(
        filename="bot_communication.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
)


def save_user_info(phone, email):
    file_exists = os.path.isfile("user_info.csv")
    with open("user_info.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Phone", "Email"])
        writer.writerow([phone, email])


def extract_phone_email(text):
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

    phone = re.search(phone_pattern, text)
    email = re.search(email_pattern, text)

    return phone.group(0) if phone else None, email.group(0) if email else None


first_interaction = True


@cache.cached(key_prefix=lambda: request.json.get("question"))
@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    global first_interaction
    data = request.get_json()
    question = data.get("question")
    user_ip = request.remote_addr

    phone, email = extract_phone_email(question)
    if phone or email:
        save_user_info(phone, email)

    answer = ask_bot(question)

    if first_interaction:
        answer += "\n\nYou can leave your phone number and email here if you'd like to stay in touch."
        first_interaction = False

    logging.info(f"Interaction from {user_ip}: Question: '{question}' | Answer: '{answer}'")

    return jsonify({"answer": answer})


def ask_bot(question, phone=None, email=None):
    completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. Here is information about our company: {my_data}"},
                {"role": "user", "content": question},
            ]
        )
    answer = completion.choices[0].message.content.strip()
    return answer


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
