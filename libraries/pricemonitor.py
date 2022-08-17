#!/usr/bin/env python3
#
# library name: pricemonitor.py
# library author: munair simpson
# library created: 20220817
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.
# library legacy: originally "dealseeker.py" because it waited on a fall from websocket session highs.

import ssl
import websocket

def on_message(ws, message):
    print(message)

ws = websocket.WebSocketApp(
    "wss://api.gemini.com/v1/marketdata/ensusd?top_of_book=true&bids=false",
    on_message=on_message)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
