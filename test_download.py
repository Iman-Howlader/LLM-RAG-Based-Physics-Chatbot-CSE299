import requests
from pathlib import Path

base = 'http://127.0.0.1:8001'
email='testuser_runonce@example.com'
password='runonce123'

# login
r = requests.post(f'{base}/login', data={'email':email,'password':password})
print('/login', r.status_code)
if r.status_code!=200:
    print(r.text)
    raise SystemExit(1)
token = r.json().get('token')
print('token', token)

# list documents
headers={'Authorization':f'Bearer {token}'}
r = requests.get(f'{base}/documents', headers=headers)
print('/documents', r.status_code, r.text)
js = r.json()
if not js.get('documents'):
    print('no documents to download')
    raise SystemExit(0)
first = js['documents'][0]['filename']
print('first file', first)

# download
r = requests.get(f'{base}/download/{first}', headers=headers, timeout=30)
print('/download', r.status_code, r.headers.get('Content-Disposition'))
if r.status_code==200:
    out = Path('downloaded_'+first)
    out.write_bytes(r.content)
    print('saved', out, out.stat().st_size)
