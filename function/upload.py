import requests
# belum dibuat fungsinya
# URL of your FastAPI application
base_url = "http://127.0.0.1:8000"

# Endpoint for uploading files
upload_endpoint = f"{base_url}/upload/"

# Path to the file you want to upload
file_path = "doc/demo.docx"

# Prepare the file to upload
files = {"file": ("demo.docx", open(file_path, "rb"))}

# Make the request to upload the file
response = requests.post(upload_endpoint, files=files)

# Check if the request was successful
if response.status_code == 200:
    # Get the JSON response containing the file path and URL
    response_data = response.json()
    
    # Extract the file URL from the response
    file_url = response_data["file_url"]
    
    print("File uploaded successfully.")
    print("File URL:", file_url)
else:
    print("Error uploading file:", response.text)

class upload():
    def __init__(self, db_con, model, path):
        # Create a new Document
        self.db_con = db_con
        self.model = model
        self.path = path
    
    def request(self):
        return