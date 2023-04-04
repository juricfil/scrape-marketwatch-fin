import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#example aapl Apple, nvda NVIDIA
ticker = input('Enter ticker symbol ')
ticker = ticker.lower()

def income_scrape(ticker_input):
    '''
    Scraping marketwatch's financial statements based on the ticker symbol
    '''
    url_income = f"https://www.marketwatch.com/investing/stock/{ticker_input}/financials?mod=mw_quote_tab"
    page = requests.get(url_income, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table',attrs={'aria-label':'Financials - data table'})
    dates_list = soup.find('thead', class_='table__header').get_text().split()[2:7]
    rows = table.find('tbody').find_all('tr')

    income_dict_func = {
        #'EPS (Basic)' : eps_list,
        #'Sales Growth' : sales_growth_list,
        #'Sales/Revenue' : sales_list
    }

    for row in rows:
        if 'EPS (Basic)' in row.get_text() and 'Growth' not in row.get_text():
            income_dict_func['EPS (Basic)'] = row.get_text().split()[4:]
        elif 'Sales Growth' in row.get_text():
            income_dict_func['Sales Growth'] = row.get_text().split()[4:]
        elif 'Sales/Revenue' in row.get_text():
            income_dict_func['Sales/Revenue'] = row.get_text().split()[2:]
        elif 'Diluted Shares Outstanding' in row.get_text():
            income_dict_func['Diluted Shares Outstanding'] = row.get_text().split()[6:]
        elif 'Net Income' in row.get_text() and 'Consolidate' not in row.get_text() and 'Growth' not in row.get_text() and 'Extra' not in row.get_text() and 'Common' not in row.get_text():
            income_dict_func['Net Income'] = row.get_text().split()[4:]
    return income_dict_func, dates_list

def cash_scrape(ticker_input):
    '''
    Scraping marketwatch's cash flow based on the ticker symbol
    '''
    url_cash = f'https://www.marketwatch.com/investing/stock/{ticker_input}/financials/cash-flow'
    page = requests.get(url_cash, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table',attrs={'aria-label':'Financials - Financing Activities data table'})
    #dates = table.find('thead', class_='table__header').get_text().split()[2:7]
    rows = table.find('tbody').find_all('tr')

    cash_dict_func = {
        #'Free Cash Flow' : free_cash_list,
        #'Free Cash Flow Growth' : cash_growth_list
        #'Free Cash Flow Yield' : cash_yield_list
    }

    for row in rows:
        if 'Free Cash Flow Growth' in row.get_text():
            cash_dict_func['Free Cash Flow Growth'] = row.get_text().split()[8:]
        elif 'Free Cash Flow Yield' in row.get_text():
            cash_dict_func['Free Cash FLow Yield'] = row.get_text().split()[8:]
        elif 'Free Cash Flow' in row.get_text():
            cash_dict_func['Free Cash Flow'] = row.get_text().split()[6:]
        elif 'Cash Dividends Paid - Total' in row.get_text():
            cash_dict_func['Cash Dividends Paid - Total'] = row.get_text().split()[10:]
    return cash_dict_func

def balance_scrape(ticker_input):
    '''
    Scraping marketwatch's balance sheet based on the ticker symbol
    '''
    url_balance= f'https://www.marketwatch.com/investing/stock/{ticker_input}/financials/balance-sheet'
    page = requests.get(url_balance, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')

    intraday_price_scraped = soup.find('div',class_='intraday__data').get_text().split()[1]

    table = soup.find('table',attrs=
                      {'aria-label':"Financials - Liabilities & Shareholders' Equity data table"})
    #dates = table.find('thead', class_='table__header').get_text().split()[2:7]
    rows = table.find('tbody').find_all('tr')

    debt_dict_func = {
        #'Long-term Debt': longterm_debt_list
        }

    for row in rows:
        if 'Long-Term Debt' in row.get_text() and 'Capitalized' not in row.get_text():
            debt_dict_func['Long-Term Debt'] = row.get_text().split()[4:]
        elif 'Total Equity' in row.get_text():
            debt_dict_func['Total Equity'] = row.get_text().split()[4:]
    return debt_dict_func, intraday_price_scraped

def equity_value_growth_calc(shares_outstanding,intraday_price):
    '''
    Calculates equity value growth from number of outstanding shares and current stock price
    '''
    shares_outstanding = shares_outstanding[-1]
    equity_value_growth_func = (float(shares_outstanding[0:-1])*intraday_price)
    equity_value_growth_func = str(round(equity_value_growth_func)) + 'B'
    return equity_value_growth_func

def ROIC_calc(net_income, dividends_payed, total_debt, total_equity):
    ROIC = []
    for (net_income_single, dividends_payed_single, total_debt_single, total_equity_single) in zip(net_income,dividends_payed,total_debt,total_equity):
        net_income_single = float(net_income_single[0:-1])
        dividends_payed_single = float(dividends_payed_single[1:-2])
        total_debt_single = float(total_debt_single[0:-1])
        total_equity_single = float(total_equity_single[0:-1])
        ROIC.append((net_income_single - dividends_payed_single)/(total_debt_single + total_equity_single))
    return ROIC

def export_to_pdf(merged_dict_financials_func):
    '''
    Create data frame from merged Dictionaries and export to PDF
    '''
    complete_table = pd.DataFrame.from_dict(merged_dict_financials_func, columns = dates, orient='index')

    fig, ax =plt.subplots(figsize=(10,4))
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=complete_table.values, rowLabels=complete_table.index.values, colLabels=complete_table.columns, loc='center')

    pdf_file = PdfPages(f"Scraped-data-{ticker.upper()}.pdf")
    pdf_file.savefig(fig, bbox_inches='tight')
    pdf_file.close()


income_dict, dates = income_scrape(ticker)
cash_dict = cash_scrape(ticker)
debt_dict, intraday_price_currently = balance_scrape(ticker)
eqity_value_growth = equity_value_growth_calc(income_dict['Diluted Shares Outstanding'], float(intraday_price_currently) )
ROIC_stock = ROIC_calc(income_dict['Net Income'],cash_dict['Cash Dividends Paid - Total'],debt_dict['Long-Term Debt'],debt_dict['Total Equity'])

merged_dict_financials = {**income_dict, **cash_dict, **debt_dict}
export_to_pdf(merged_dict_financials)
