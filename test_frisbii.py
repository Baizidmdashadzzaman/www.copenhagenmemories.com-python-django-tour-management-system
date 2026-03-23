import requests
import json

api_key = 'priv_04c1346cd0a98436cf1c70a55ec4d55f'
url = 'https://checkout-api.frisbii.com/v1/session/charge'
data = {
    'order': {
        'handle': 'test-order-003',
        'amount': 1000,
        'currency': 'USD',
        'customer': {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'handle': 'cust-001'
        }
    },
    'accept_url': 'http://127.0.0.1:8000/accept/test-order-002',
    'cancel_url': 'http://127.0.0.1:8000/cancel/test-order-002'
}
response = requests.post(url, auth=(api_key, ''), json=data)
print(response.content)
with open('test_frisbii_out.txt', 'wb') as f:
    f.write(response.content)
