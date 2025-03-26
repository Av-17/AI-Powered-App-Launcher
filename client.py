import requests

url = "http://127.0.0.1:8000/execute"
value = input("Enter someting to open : ")
headers = {"Content-Type": "application/json"}
data = {"prompt": value}

response = requests.post(url, json=data, headers=headers)
print(response.json())