import requests

response = requests.post("http://127.0.0.1:5000/ad/",
                         json={'title': 'new_title', "description": "1234567890", "owner_id": 1},
                         )
print(response.json())
response = requests.get("http://127.0.0.1:5000/ad/2/")

print(response.json())
response = requests.patch("http://127.0.0.1:5000/ad/2/",
                          json={"title": "vvery_old_title","owner_id": "2"})

print(response.json())
response = requests.delete("http://127.0.0.1:5000/ad/3/")

print(response.json())
