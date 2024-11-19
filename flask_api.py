import os
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
# Cache responses for 300 sec
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


@cache.cached(key_prefix=lambda: request.json.get("question"))
@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    data = request.get_json()
    question = data.get("question")

    user_ip = request.remote_addr

    answer = ask_bot(question)

    logging.info(f"Interaction from {user_ip}: Question: '{question}' | Answer: '{answer}'")

    return jsonify({"answer": answer})


def ask_bot(question):
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
