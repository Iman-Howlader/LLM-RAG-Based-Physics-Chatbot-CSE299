import time
import json
import uuid
from pathlib import Path
import requests

host = '127.0.0.1'
port = 8001
email = 'testuser1@example.com'
password = 'test1234'

base_url = f'http://{host}:{port}'
server_url = f'{base_url}/docs'

# Wait for server to be ready
for _ in range(10):
    try:
        resp = requests.get(server_url, timeout=2)
        if resp.status_code == 200:
            break
    except requests.RequestException:
        time.sleep(1)
else:
    raise RuntimeError('Server did not become ready in time')

# Register or ignore if already exists
for path in ['/register', '/login']:
    resp = requests.post(f'{base_url}{path}', data={'email': email, 'password': password})
    print(path, resp.status_code, resp.text)

login_resp = requests.post(f'{base_url}/login', data={'email': email, 'password': password})
login_resp.raise_for_status()
login_data = login_resp.json()
token = login_data.get('token')
print('login token', token)

# Prepare upload file with a unique name to avoid duplicate skipping
unique_name = f'chat_test_{uuid.uuid4().hex[:8]}.txt'
path_file = Path(unique_name)
path_file.write_text('This document describes radar system limitations and performance issues.', encoding='utf-8')

with open(path_file, 'rb') as f:
    files = {'files': (unique_name, f, 'text/plain')}
    headers = {'Authorization': f'Bearer {token}'}
    upload_resp = requests.post(f'{base_url}/upload', files=files, headers=headers)
    print('upload', upload_resp.status_code, upload_resp.text)
    if upload_resp.status_code != 200:
        raise RuntimeError('Upload failed')

chat_payload = {
    'question': 'What are two major limitations of this radar system mentioned in the report?',
    'api_key': 'test_key',
    'model_name': 'llama-3.3-70b-versatile',
    'temperature': 0.1,
}
chat_resp = requests.post(f'{base_url}/chat', json=chat_payload, headers=headers)
print('chat', chat_resp.status_code, chat_resp.text)
if chat_resp.status_code != 200:
    chat_resp.raise_for_status()
