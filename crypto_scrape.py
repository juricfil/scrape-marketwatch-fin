import requests
from bs4 import BeautifulSoup

def scrape_crypto_data():
    url_income = "https://coinmarketcap.com/"
    page = requests.get(url_income, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table')
    rows = table.find('tbody').find_all('tr')

    # Define lists to use
    crypto_ticker_list = []
    prices_list = []
    daily_price_change_list = []
    weekly_price_change_list = []

    #Loop through rows
    for row in rows[0:5]:
        row_data = row.find_all('span')
        ticker = row.find('p',{'class':'sc-4984dd93-0 iqdbQL coin-item-symbol'}).get_text()
        crypto_ticker_list.append(ticker)
        prices_list.append(row_data[1].get_text())
        daily_price_change_list.append(row_data[4].get_text())
        weekly_price_change_list.append(row_data[6].get_text())

    return crypto_ticker_list, prices_list, daily_price_change_list, weekly_price_change_list

crypto_tickers, prices, daily_price_change, weekly_price_change = scrape_crypto_data()


# Import the required libraries
from tkinter import *
from tkinter import ttk

# Create an instance of tkinter frame
win = Tk()

# Set the size of the tkinter window and title
win.title('Crypto Market Scrape')
win.geometry("1000x600")

# Create an object of Style widget
style = ttk.Style()
style.theme_use('clam')

# Add a Treeview widget
tree = ttk.Treeview(win, column=("Ticker", "Price", "Daily Price Change","Weekly Price change"), show='headings', height=5)
tree.column("# 1", anchor=CENTER)
tree.heading("# 1", text="Ticker")
tree.column("# 2", anchor=CENTER)
tree.heading("# 2", text="Price")
tree.column("# 3", anchor=CENTER)
tree.heading("# 3", text="Daily Price Change")
tree.column("# 4", anchor=CENTER)
tree.heading("# 4", text="Weekly Price change")
# Insert the data in Treeview widget
for (i,j,k,l) in zip(crypto_tickers, prices, daily_price_change, weekly_price_change):
    tree.insert('', 'end', text="1", values=(i,j,k,l))

tree.pack()

win.mainloop()