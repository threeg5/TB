import websocket
import json
import csv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
print("🚀 Script started on Render...")
print("Starting script...")
print("🔐 Checking GOOGLE_CREDS...")


# Google Sheets auth
GOOGLE_CREDENTIALS_FILE = "crypto-coins-297801-f5a4c1fb679c.json"  # <-- replace with your real filename
GOOGLE_SHEET_NAME = "btc_trades.csv"                        # <-- match exactly what your sheet is called


# === GOOGLE SHEETS SETUP ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    print("🔐 Loading credentials from GOOGLE_CREDS...")
    creds_json = os.getenv("GOOGLE_CREDS")  # Must exist on Render

    if creds_json is None:
        raise ValueError("GOOGLE_CREDS environment variable is missing!")
    print("📦 GOOGLE_CREDS loaded. Parsing JSON...")
    creds_dict = json.loads(creds_json)

    print("🔐 Authorizing with Google...")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("btc_trades.csv").sheet1
    print("✅ Connected to Google Sheets.")
except Exception as e:
    print("❌ Google Sheets connection failed:", e)
    sheet = None

# === CSV SETUP ===
file_path = "btc_trades.csv"
if not os.path.exists(file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "price", "quantity", "side"])

# === Send Trade to Google Sheets ===
def upload_trade_to_google(timestamp, price, qty, side):
    try:
        if sheet:
            print(f"📝 Attempting to insert row: {[timestamp, price, qty, side]}")
            sheet.append_row([timestamp, price, qty, side])
            print("✅ Successfully appended to Google Sheet.")
    except Exception as e:
        print("❌ Failed to upload to Google Sheets:", e)


# === WebSocket Message Handler ===
def on_message(ws, message):
    try:
        data = json.loads(message)

        # Only process trade messages from the btcusdt stream
        if data.get("stream") == "btcusdt@trade" and "data" in data:
            trade = data["data"]

            ts = trade.get("T")
            timestamp = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
            price = trade.get("p")
            qty = trade.get("q")
            side = "buy" if not trade.get("m") else "sell"

            print(f"{timestamp} | {side.upper()} | {price} x {qty}")

            # Write to CSV
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, price, qty, side])

            # Write to Google Sheets
            upload_trade_to_google(timestamp, price, qty, side)

    except Exception as e:
        print("Error processing trade:", e)



def on_error(ws, error):
    print("ERROR:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket opened")

# === WebSocket Setup ===
socket_url = "wss://stream.binance.us:9443/stream?streams=btcusdt@trade"
ws = websocket.WebSocketApp(
    socket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

# === Start Everything ===
if __name__ == "__main__":
    print("Starting WebSocket...")
    ws.run_forever()
