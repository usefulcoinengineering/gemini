#!/usr/bin/env python3


import json
import base64
import hmac
import hashlib
import time

import libraries.credentials as credentials

def authenticate(payload):
    encodedpayload = json.dumps(payload).encode()
    b64 = base64.b64encode(encodedpayload)
    signature = hmac.new(credentials.secret.encode(), b64, hashlib.sha384).hexdigest()
    apihead = { 'Content-Type': "text/plain",
                'Content-Length': "0",
                'X-GEMINI-APIKEY': credentials.key,
                'X-GEMINI-PAYLOAD': b64,
                'X-GEMINI-SIGNATURE': signature,
                'Cache-Control': "no-cache" }
    wsshead = { 'X-GEMINI-PAYLOAD': b64.decode(),
                'X-GEMINI-APIKEY': credentials.key,
                'X-GEMINI-SIGNATURE': signature }

    return { 'sockheader': wsshead, 'restheader': apihead }
