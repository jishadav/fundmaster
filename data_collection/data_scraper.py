import os
import time

from database_helpers import Db
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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

    def close(self):
        self.browser.close()
        self.browser.quit()

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
        db = Db()
        for i in range(len(df)):
            symbol = df.loc[i, "Security Id"]
            security_code = int(df.loc[i, "Security Code"])
            name = df.loc[i, "Security Name"]
            industry = df.loc[i, "Industry"]
            db.insert_company_data(symbol, security_code,
                                   name, industry)

    def download_bse_500_index_list(self):
        '''
        Download the list of ompanies indexed in S&P BSE 500
        '''
        index_url = "https://www.bseindia.com/markets/equity/EQReports/MarketWatch.html?index_code=17"
        self.browser.get(index_url)
        self.browser.find_element_by_xpath(
            """//*[@id="divmain"]/div[1]/div/div[1]/div[2]/a/i""").click()

    def extract_fundamental_data(self, symbol):
        pass
