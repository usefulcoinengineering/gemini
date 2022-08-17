#!/usr/bin/env python3
#
# library name: pricemonitor.py
# library author: munair simpson
# library created: 20220817
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.
# library legacy: originally "dealseeker.py" because it waited on a fall from websocket session highs.

import ssl, json
import websocket

def on_message( ws, message ) : 
    jsonresponse = message.json()
    jsondatadump = json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') )
    print ( jsondatadump )

ws = websocket.WebSocketApp( "wss://api.gemini.com/v1/marketdata/btcusd?trades=true", on_message = on_message )
ws.run_forever( sslopt = { "cert_reqs" : ssl.CERT_NONE } )
