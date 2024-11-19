import requests

url = "http://127.0.0.1:5000/chat"
headers = {"Content-Type": "application/json"}
data = {"question": "Test question"}

for i in range(6, 13):
    response = requests.post(url, json=data, headers=headers)
    print(f"Request {i+1}: Status Code {response.status_code}, Response: {response.json() if response.status_code == 200 else response.text}")
