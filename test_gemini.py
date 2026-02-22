import os
from google.genai import Client

if __name__ == '__main__':
    client = Client(api_key=os.environ.get('GOOGLE_API_KEY'))
    resp = client.chat.create(model='gemini-1.0', messages=[{'role':'user','content':'Hello from test'}])
    print('type of response', type(resp))
    try:
        print('last:', resp.last)
    except Exception as e:
        print('no last attr', e)
    print('repr', resp)
    print('dir:', dir(resp))
