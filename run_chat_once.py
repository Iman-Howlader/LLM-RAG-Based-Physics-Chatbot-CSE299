import requests
import uuid
from pathlib import Path

base_url = 'http://127.0.0.1:8001'
email = 'testuser_runonce@example.com'
password = 'runonce123'

# Register (ignore failure)
try:
    r = requests.post(f'{base_url}/register', data={'email': email, 'password': password}, timeout=30)
    print('/register', r.status_code, r.text)
except Exception as e:
    print('/register error', e)

# Login
r = requests.post(f'{base_url}/login', data={'email': email, 'password': password}, timeout=30)
print('/login', r.status_code, r.text)
r.raise_for_status()
token = r.json().get('token')
print('token', token)

# upload
unique_name = f'runonce_{uuid.uuid4().hex[:8]}.txt'
path = Path(unique_name)
path.write_text('This is a test document describing radar limitations and performance issues.')
with open(path, 'rb') as f:
    files = {'files': (unique_name, f, 'text/plain')}
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.post(f'{base_url}/upload', files=files, headers=headers, timeout=30)
    print('/upload', r.status_code, r.text)

# chat
payload = {
    'question': 'List two limitations mentioned.',
    'api_key': 'test_key',
    'model_name': 'llama-3.3-70b-versatile',
    'temperature': 0.1
}
headers = {'Authorization': f'Bearer {token}'}
r = requests.post(f'{base_url}/chat', json=payload, headers=headers, timeout=30)
print('/chat', r.status_code, r.text)
