import requests

# Set the API endpoint URL
url = "http://192.168.1.44:5000/api/v1/upload_file"

# Read the file and convert it to a binary stream
# Set the JSON data to be sent in the request body
json_data = {
    "api-token": "34311fd2-e889-38b2-8604-d9c822242100",
    "file-name": "test.py",
    "file-path": "/home/mathieu/",
    "admin": 1
}

# Set the headers
headers = {
    "Content-Type": "application/json"
}

# Read the file to be uploaded
file = open("/home/mathieu/test.py", "rb")
file_data = file.read()

# Send the POST request with the file and JSON data
response = requests.post(url, json=json_data, headers=headers, files={"file": file})

# Print the response
print(response.text)
