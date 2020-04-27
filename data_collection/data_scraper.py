import datetime
import os
import time
from datetime import timedelta
from decimal import Decimal
from re import sub
import pandas as pd
from database_helpers import Db
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


def currency_to_decimal(currency_string):
    return float(Decimal(sub(r'[^\d.-]', '', currency_string)))


def bse_date_string_to_date(date_string):
    return datetime.datetime.strptime(date_string, '%d-%b-%y').strftime('%Y-%m-%d')


class Scraper():
    """
    Scrape fundamental results data and historical
    stock prices from bse website

    The data is to be stored in a sqlite dattabse for the future use.
    """

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': os.getcwd()}
        chrome_options.add_experimental_option('prefs', prefs)
        # chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_window_position(0, 0)
        self.browser.set_window_size(700, 700)
        self.db = Db()

    def close(self):
        self.browser.close()
        self.browser.quit()
        self.db.close()

    def update_company_db(self):
        '''
        Download the company list from bse website and add
        those information to the database
        '''
        # Delete the existing company list csv file and download the latest one
        if os.path.exists("Equity.csv"):
            os.remove("Equity.csv")

        # Download the company list csv
        bse_url = "https://www.bseindia.com/corporates/List_Scrips.aspx"
        self.browser.get(bse_url)
        self.browser.find_element_by_xpath(
            """//*[@id="ContentPlaceHolder1_ddSegment"]""").send_keys("Equity")
        self.browser.find_element_by_xpath(
            """//*[@id="ContentPlaceHolder1_ddlStatus"]""").send_keys("Active")
        self.browser.find_element_by_xpath(
            """//*[@id="ContentPlaceHolder1_btnSubmit"]""").click()
        self.browser.find_element_by_xpath(
            """//*[@id="ContentPlaceHolder1_lnkDownload"]/i""").click()
        time.sleep(5)

        # insert bse companies into database
        df = pd.read_csv('Equity.csv')
        for i in range(len(df)):
            symbol = df.loc[i, "Security Id"]
            security_code = int(df.loc[i, "Security Code"])
            name = df.loc[i, "Security Name"]
            industry = df.loc[i, "Industry"]
            self.db.insert_company_data(symbol, security_code,
                                        name, industry)

    def download_bse_500_index_list(self):
        '''
        Download the list of companies indexed in S&P BSE 500
        '''
        index_url = "https://www.bseindia.com/markets/equity/EQReports/MarketWatch.html?index_code=17"
        self.browser.get(index_url)
        self.browser.find_element_by_xpath(
            """//*[@id="divmain"]/div[1]/div/div[1]/div[2]/a/i""").click()

    def extract_fundamental_data(self, sec_code):
        '''
        Scrape the fundamental data from bse website for the security code
        '''
        company_details = self.db.get_company_details_from_sec_code(sec_code)
        if company_details['security_code']:
            sec_code = company_details['security_code']
            name = company_details['name'].replace('&#39', '%27')
            current_date = datetime.datetime.now()
            previous_quarter = pd.PeriodIndex(
                [current_date - pd.DateOffset(months=3)], freq='Q-MAR').quarter[0]
            year = current_date.year if previous_quarter in [
                1, 2] else current_date.year - 1
            qtr_offset = (year - 1994) * 4 + previous_quarter
            qtr_range = range(qtr_offset, qtr_offset-24, -1)  # For 5 years
            for qtr in qtr_range:
                fundamentals_url = "https://www.bseindia.com/corporates/Results.aspx?Code=" + \
                    sec_code + "&Company=" + name \
                    + "&qtr=" + str(qtr) + "&RType="
                if self.db.check_fundamental_url_already_inserted(fundamentals_url):
                    continue
                self.browser.get(fundamentals_url)
                try:
                    table_parent = self.browser.find_element_by_xpath(
                        """//*[@id="ContentPlaceHolder1_tbl_typeID"]/tbody""")
                except NoSuchElementException as e:
                    try:
                        self.browser.find_element_by_xpath(
                            """//*[@id="ContentPlaceHolder1_lnkDetailed"]""").click()
                        table_parent = self.browser.find_element_by_xpath(
                            """//*[@id="ContentPlaceHolder1_tbl_typeID"]/tbody""")
                    except:
                        continue
                except:
                    continue
                rows = table_parent.find_elements_by_xpath(".//tr")
                million = 1000000
                row_data = {'symbol': None, 'date': None, 'sales': None, 'net_profit': None,
                            'eps': None, 'url': None, }
                row_data['symbol'] = company_details['symbol']
                row_data['url'] = fundamentals_url
                for row in rows:
                    try:
                        row_elts = row.find_elements_by_xpath(".//td")
                        if row_elts[0].text in ['Date End']:
                            row_data['date'] = bse_date_string_to_date(
                                row_elts[1].text)
                        elif row_elts[0].text in ['Net Sales/Revenue From Operations', 'Net Sales', 'Interest Earned/Net Income from sales/services']:
                            row_data['sales'] = currency_to_decimal(
                                row_elts[1].text) * million
                        elif row_elts[0].text in ['Net Profit']:
                            row_data['net_profit'] = currency_to_decimal(
                                row_elts[1].text) * million
                        elif row_elts[0].text in ['Basic for discontinued & continuing operation', 'Basic EPS after Extraordinary items',
                                                  'Basic & Diluted EPS after Extraordinary items', 'Basic & Diluted EPS before Extraordinary items',
                                                  'Basic earnings per share after extraordinary items',
                                                  'Basic EPS before Extraordinary items', 'Basic EPS for continuing operation']:
                            row_data['eps'] = currency_to_decimal(
                                row_elts[1].text)
                    except:
                        continue
                if all([row_data['date'], row_data['sales'], row_data['net_profit'], row_data['eps']]):
                    self.db.insert_fundamentals_data(row_data)
                else:
                    return

    def extract_complete_fundamental_data(self, company_df):
        '''
        Scrape the fundamental data of all the symbols in the dataframe provided
        '''
        i = 0
        for row in range(len(company_df)):
            i = i+1
            if i < 565:
                continue
            sec_code = str(company_df.loc[row, "Security Code"])
            self.extract_fundamental_data(sec_code)

    def update_daily_stock_prices(self, start_date, end_date):
        '''
        Download the daily bhavcopies and insert the stock prices into the database
        '''
        delta = timedelta(days=1)
        companies_with_fundamentals = self.db.get_companies_with_fundamentals()
        while start_date <= end_date:
            print(start_date)
            if (start_date.weekday() not in [5, 6]):
                dd = start_date.strftime("%d")
                mm_indigits = start_date.strftime("%m")
                yy2digits = start_date.strftime("%y")
                bse_bhavcopy_file = "EQ" + dd + mm_indigits + yy2digits + "_CSV.ZIP"
                bse_bhavcopy_url = "https://www.bseindia.com/download/BhavCopy/Equity/" + bse_bhavcopy_file
                if self.db.check_bhav_copy_already_inserted(start_date):
                    start_date += delta
                    continue
                try:
                    df = pd.read_csv(bse_bhavcopy_url, compression='zip')
                except:
                    start_date += delta
                    continue
                for i in range(len(df)):
                    sec_code = df.loc[i, "SC_CODE"]
                    company_details = self.db.get_company_details_from_sec_code(
                        str(sec_code))
                    if not company_details:
                        continue
                    if company_details['symbol'] not in companies_with_fundamentals:
                        continue
                    date = start_date
                    open_ = float(df.loc[i, "OPEN"])
                    high = float(df.loc[i, "HIGH"])
                    low = float(df.loc[i, "LOW"])
                    close = float(df.loc[i, "CLOSE"])
                    volume = float(df.loc[i, "NO_OF_SHRS"])
                    self.db.insert_stock_price_data(
                        company_details['symbol'], date, open_, high, low, close, volume)

            start_date += delta
