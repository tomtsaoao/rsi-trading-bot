#!/usr/bin/python3
import config, talib, websocket, json
import numpy as np
from binance.client import Client
from binance.enums import *

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

TRADE_SYMBOL = "ETHUSDT"
TRADE_QUANTITY = 35
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

closes = []
in_position = False
client = Client(config.api_key, config.api_secret, tld='us')

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
	try:
		print("sending order")
		order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
		print(order)
	except Exception as e:
		print("an exception occureed - {}".format(e))
		return False

	return True

def on_open(ws):
	print('open connection')

def on_close(ws):
	print('close connection')

def on_message(ws, message):
	global closes, in_position
	json_message = json.loads(message)
	candle = json_message['k']
	is_candle_closed = candle['x']
	close = candle['c']
	print(close)

	if is_candle_closed:
		print("candle closed at {}".format(close))
		closes.append(float(close))
		print("closes")
		print(closes)

		if len(closes) > RSI_PERIOD:
			np_closes = np.array(closes)
			rsi = talib.RSI(np_closes, RSI_PERIOD)
			print("all rsis calculated so far")
			print(rsi)
			last_rsi = rsi[-1]
			print("the current rsi is {}".format(last_rsi))

			#Overbought state calculation
			if last_rsi > RSI_OVERBOUGHT:
				if in_position:
					print("Overbought! Sell!")
					order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
					if order_succeeded:
						in_position = False
				else:
					print("It is overbought, but you don't own any - nth to do")

			#Oversold state calculation
			if last_rsi < RSI_OVERSOLD:
				if in_position:
					print("It is oversold, but you already own it - nth to do")
				else:
					print("Oversold! Buy!")
					order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
					if order_succeeded:
						in_position = True

ws = websocket.WebSocketApp(SOCKET,on_open=on_open, on_close=on_close,  on_message=on_message)
ws.run_forever()
