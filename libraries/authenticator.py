#!/usr/bin/env python3


import json
import base64
import hmac
import hashlib
import time

import libraries.credentials as credentials

def authenticate(payload):
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(credentials.secret.encode(), b64, hashlib.sha384).hexdigest()

if __name__ == "__main__":
    import ssl
    import websocket

    import resourcelocator
    from authenticator import authenticate

    # Define functions
    def on_close(ws): logger.info(f'{ws} connection closed.')
    def on_open(ws): logger.info(f'{ws} connection opened.')
    def on_error(ws, error): print(error)
    def on_message(ws, message): print(message)

    # Define pair.
    pair = 'BTCUSD'

    # Define filter.
    filtering = ''
    usefilter = True
    if usefilter: filtering = 'trades=true'

    # Construct payload.
    request = resourcelocator.sockgenuine + 'v1/marketdata/' + pair + '?' + filtering
    nonce = int(time.time()*1000)
    payload = {'request': request,'nonce': nonce}
    auth = authenticate(payload)

    # Establish websocket connection.
    ws = websocket.WebSocketApp(request, on_message=on_message)
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
