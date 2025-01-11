import requests
import tkinter as tk
from tkinter import ttk
import threading
import time


# Function to fetch the current price of a cryptocurrency
def fetch_price(ticker):
    url = (
        f"https://api.coingecko.com/api/v3/simple/price?ids={ticker}&vs_currencies=usd"
    )
    response = requests.get(url)
    price_data = response.json()
    if ticker in price_data:
        return price_data[ticker]["usd"]
    else:
        return None


# Function to fetch detailed information about a cryptocurrency
def fetch_crypto_info(ticker):
    url = f"https://api.coingecko.com/api/v3/coins/{ticker}"
    response = requests.get(url)
    return response.json()


# Function to fetch the top 10 cryptocurrencies
def fetch_top_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False,
    }
    response = requests.get(url, params=params)
    return response.json()


# Function to check the price and notify the user
def monitor_price(ticker, target_price):
    while True:
        current_price = fetch_price(ticker)
        if current_price is not None:
            if current_price <= target_price:
                print(f"Notification: {ticker} has fallen to ${current_price}!")
            elif current_price >= target_price:
                print(f"Notification: {ticker} has risen to ${current_price}!")
        else:
            print(f"Error: Could not fetch price for {ticker}.")
        time.sleep(15)  # Check every 15 seconds


# Function to start monitoring in a separate thread
def start_monitoring():
    ticker = entry_ticker.get().lower()
    try:
        target_price = float(entry_target_price.get())
        threading.Thread(
            target=monitor_price, args=(ticker, target_price), daemon=True
        ).start()
        status_label.config(
            text=f"Monitoring {ticker} for price: ${target_price}", fg="green"
        )
    except ValueError:
        status_label.config(text="Please enter a valid target price.", fg="red")


# Function to check the current price
def check_price():
    ticker = entry_ticker.get().lower()
    current_price = fetch_price(ticker)
    if current_price is not None:
        price_label.config(
            text=f"Current price of {ticker}: ${current_price}", fg="blue"
        )
    else:
        price_label.config(text=f"Error: Could not fetch price for {ticker}.", fg="red")


# Function to show cryptocurrency information
def show_crypto_info():
    ticker = entry_ticker.get().lower()
    info = fetch_crypto_info(ticker)
    if "error" not in info:
        try:
            info_text = (
                f"Name: {info['name']}\n"
                f"Current Price: ${info['market_data']['current_price']['usd']}\n"
                f"Market Cap: ${info['market_data']['market_cap']['usd']}\n"
                f"24h Change: {info['market_data']['price_change_percentage_24h']}%\n"
                f"Total Supply: {info['market_data']['total_supply']}\n"
                f"Circulating Supply: {info['market_data']['circulating_supply']}\n"
            )
            info_label.config(text=info_text, fg="black")
        except KeyError:
            info_label.config(
                text="Error: Some data is missing for this cryptocurrency.", fg="red"
            )
    else:
        info_label.config(
            text="Error: Could not fetch info for this cryptocurrency.", fg="red"
        )


# Function to show top 10 cryptocurrencies
def show_top_cryptos():
    top_cryptos = fetch_top_cryptos()
    top_cryptos_text = "Top 10 Cryptos:\n"
    for crypto in top_cryptos:
        top_cryptos_text += (
            f"{crypto['name']} - ${crypto['current_price']} - "
            f"Market Cap: ${crypto['market_cap']}\n"
        )
    top_cryptos_label.config(text=top_cryptos_text, fg="black")


# Function to search for cryptocurrencies
def search_crypto():
    query = search_entry.get().lower()
    url = f"https://api.coingecko.com/api/v3/search?query={query}"
    response = requests.get(url)
    data = response.json()

    # Clear previous results
    listbox.delete(0, tk.END)

    # Display search results
    for coin in data["coins"]:
        listbox.insert(tk.END, coin["id"])  # Use 'id' for selection


# Function to handle selection from the listbox
def select_crypto(event):
    selected_ticker = listbox.get(listbox.curselection())
    entry_ticker.delete(0, tk.END)  # Clear the entry field
    entry_ticker.insert(0, selected_ticker)  # Insert the selected ticker


# Setting up the GUI
root = tk.Tk()
root.title("Crypto Tracker")
root.geometry("600x700")

# Create a canvas and a scrollable frame
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Add widgets to the scrollable frame
title_label = tk.Label(
    scrollable_frame, text="Crypto Tracker", font=("Helvetica", 16, "bold")
)
title_label.pack(pady=10)

tk.Label(scrollable_frame, text="Search Cryptocurrency:").pack(pady=5)
search_entry = tk.Entry(scrollable_frame, font=("Helvetica", 12))
search_entry.pack(pady=5)

search_button = tk.Button(scrollable_frame, text="Search", command=search_crypto)
search_button.pack(pady=5)

listbox = tk.Listbox(scrollable_frame, font=("Helvetica", 12), width=50)
listbox.pack(pady=5)
listbox.bind("<<ListboxSelect>>", select_crypto)

tk.Label(scrollable_frame, text="Enter Cryptocurrency Ticker (e.g., bitcoin):").pack(
    pady=5
)
entry_ticker = tk.Entry(scrollable_frame, font=("Helvetica", 12))
entry_ticker.pack(pady=5)

check_button = tk.Button(
    scrollable_frame, text="Check Current Price", command=check_price
)
check_button.pack(pady=5)

price_label = tk.Label(scrollable_frame, text="", font=("Helvetica", 12))
price_label.pack(pady=5)

info_button = tk.Button(
    scrollable_frame, text="Show Crypto Info", command=show_crypto_info
)
info_button.pack(pady=5)

info_label = tk.Label(
    scrollable_frame, text="", font=("Helvetica", 12), wraplength=500, justify="left"
)
info_label.pack(pady=5)

tk.Label(scrollable_frame, text="Enter Target Price:").pack(pady=5)
entry_target_price = tk.Entry(scrollable_frame, font=("Helvetica", 12))
entry_target_price.pack(pady=5)

monitor_button = tk.Button(
    scrollable_frame, text="Start Monitoring", command=start_monitoring
)
monitor_button.pack(pady=5)

status_label = tk.Label(scrollable_frame, text="", font=("Helvetica", 12))
status_label.pack(pady=5)

top_10_button = tk.Button(
    scrollable_frame, text="Show Top 10 Cryptos", command=show_top_cryptos
)
top_10_button.pack(pady=5)

top_cryptos_label = tk.Label(
    scrollable_frame, text="", font=("Helvetica", 12), justify="left", wraplength=500
)
top_cryptos_label.pack(pady=5)

footer_label = tk.Label(
    scrollable_frame,
    text="THY SHALL KNOWTH THE GLORY OF MANAS",
    font=("Helvetica", 10, "italic"),
    fg="gray",
)
footer_label.pack(side="bottom", anchor="se", pady=10)

# Start the GUI event loop
root.mainloop()
