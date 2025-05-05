import websocket
import json
import csv
import os

file_path = "btc_trades.csv"

# Create CSV with header if it doesn't exist
if not os.path.exists(file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "price", "quantity", "side"])

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "stream" in data and "data" in data:
            if data["stream"] == "btcusdt@trade":
                trade = data["data"]
                timestamp = trade.get("T")
                price = trade.get("p")
                qty = trade.get("q")
                side = "buy" if trade.get("m") is False else "sell"

                print(f"{timestamp} | {side.upper()} | {price} x {qty}")

                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, price, qty, side])
    except Exception as e:
        print("Error parsing message:", e)

def on_error(ws, error):
    print("ERROR:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket opened")

socket_url = "wss://stream.binance.us:9443/stream?streams=btcusdt@trade/btcusdt@depth5"

ws = websocket.WebSocketApp(
    socket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

if __name__ == "__main__":
    ws.run_forever()
