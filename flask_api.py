import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

with open("duanex.txt", "r") as file:
    my_data = file.read()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")
    answer = ask_bot(question)
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
