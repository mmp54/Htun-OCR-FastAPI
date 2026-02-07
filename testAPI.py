import requests

url = "https://htun-ocr-fastapi-2.onrender.com/ocr"
files = {"file": open("test.jpg", "rb")}  # replace test.jpg with your image

r = requests.post(url, files=files)
print(r.json())
