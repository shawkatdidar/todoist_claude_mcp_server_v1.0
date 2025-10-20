import requests

url = "http://127.0.0.1:8000/mcp"

# Change this between "ping" and "list_tasks"
payload = {"method": "ping"}

resp = requests.post(url, json=payload)

print("Status:", resp.status_code)
print("Response:", resp.json())
