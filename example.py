import requests

url = "http://127.0.0.1:5000/generate_questions"

# Open the PDF file in binary mode
pdf_path = "resume.pdf"
files = {'pdf_file': open(pdf_path, 'rb')}

# Additional prompt as form data
data = {'additional_prompt': 'Focus on machine learning'}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    print("Generated Questions:", response.json())
else:
    print("Error:", response.text)
