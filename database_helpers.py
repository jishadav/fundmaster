import sqlite3
import datetime

def string_to_date(date_string):
    """Convert the date string to datetime object"""
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()


class Db():
    '''
    Data base helper functions
    '''

    def __init__(self):
        self.database = "fundmaster_db.db"
        self.databse_connect()
        self.databse_init()

    def databse_connect(self):
        """Connect to the SQLite3 database."""
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def databse_init(self):
        """Initialise the SQLite3 database."""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS company (\
                            symbol TEXT UNIQUE NOT NULL, security_code TEXT, \
                                name TEXT, industry TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stock_prices (\
                            symbol TEXT NOT NULL references company(symbol) \
                            ON DELETE CASCADE, \
                            date TEXT, \
                            open REAL, high REAL, low REAL, \
                            close REAL, volume REAL, \
                            CONSTRAINT unq UNIQUE (symbol, date))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS fundamentals (\
                            symbol TEXT NOT NULL references company(symbol)  \
                            ON DELETE CASCADE, \
                            date TEXT NOT NULL, \
                            sales REAL, net_profit REAL, eps REAL, url TEXT, \
                            CONSTRAINT unq UNIQUE (symbol, date))")

    def close(self):
        self.connection.close()

    def insert_company_data(self, symbol, security_code, name, industry):
        """Insert the company data to db"""
        try:
            self.cursor.execute("INSERT INTO company (symbol, security_code, name, industry) \
                                VALUES (:symbol, :security_code, \
                                    :name, :industry)",
                                {"symbol": symbol, "security_code":
                                    security_code, "name": name,
                                    "industry": industry})
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            pass

    def get_company_details_from_sec_code(self, security_code):
        '''Return the Company details for the symbol'''
        self.cursor.execute(
            "SELECT security_code, symbol, name FROM company where security_code = :security_code",
            {"security_code": security_code})
        details = self.cursor.fetchone()
        if details:
            company = {
                'security_code': details[0], 'symbol': details[1], 'name': details[2]}
            return company
        else:
            return False

    def check_fundamental_url_already_inserted(self, url):
        '''Check whether the fundamental url is already scraped and updated the details into db'''
        self.cursor.execute(
            "SELECT * FROM fundamentals WHERE url = :url", {"url": url})
        res = self.cursor.fetchall()
        if len(res) == 0:
            return False
        else:
            return True

    def insert_fundamentals_data(self, fundamental_dict):
        """Insert the index data to db"""
        try:
            print(fundamental_dict)
            self.cursor.execute("INSERT INTO fundamentals (symbol, date, sales, net_profit, eps, url) \
                                VALUES (:symbol, :date, :sales, :net_profit, :eps, :url)",
                                {"symbol": fundamental_dict['symbol'], "date": fundamental_dict['date'],
                                    "sales": fundamental_dict['sales'],
                                    "net_profit": fundamental_dict['net_profit'], "eps": fundamental_dict['eps'],
                                    "url": fundamental_dict['url']})
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            pass

    def get_companies_with_fundamentals(self):
        self.cursor.execute(
            "SELECT DISTINCT symbol FROM fundamentals")
        res = self.cursor.fetchall()
        if len(res) == 0:
            return False
        else:
            return [r[0] for r in res]

    def check_bhav_copy_already_inserted(self, date):
        '''Check whether the fundamental url is already scraped and updated the details into db'''
        self.cursor.execute(
            "SELECT * FROM stock_prices WHERE date = :date", {"date": date})
        res = self.cursor.fetchall()
        if len(res) == 0:
            return False
        else:
            return True

    def insert_stock_price_data(self, symbol, date, open_, high, low, close, volume):
        """Insert the stock data to db"""
        try:
            self.cursor.execute("INSERT INTO stock_prices (symbol, date, open, high, low, close, volume) \
                                VALUES (:symbol, :date, :open, :high, :low, :close, :volume)",
                                {"symbol": symbol, "date": date, "open": open_, "high": high, "low": low, "close": close, "volume": volume})
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            pass

    def get_available_dates(self, symbol):
        """ Return the period end date of quarters from the fundamentals tabls for the symbol provided"""
        self.cursor.execute(
            "SELECT date FROM fundamentals WHERE symbol = :symbol ORDER BY date", {"symbol": symbol})
        res = self.cursor.fetchall()
        if len(res) == 0:
            return False
        dates = [string_to_date(date[0]) for date in res]
        return dates

    def get_over_the_period_fundamental_data(self, symbol, cur_date, over_period_date):
        """
        Return the fundamental data for the current date and an year before that for the symbol provided
        """
        self.cursor.execute("SELECT s.sales, l.sales, s.net_profit, l.net_profit, s.eps, l.eps \
                                FROM fundamentals s JOIN fundamentals l \
                                on s.symbol = l.symbol \
                                WHERE s.symbol = :symbol \
                                AND s.date = :over_period_date and l.date = :cur_date ",
                                {"symbol": symbol, "cur_date": cur_date,
                                 "over_period_date": over_period_date})
        result = self.cursor.fetchone()  # (cur_quarter_sales, over_the_year_quarter_sales, cur_quarter_net profie, over_the_year_net_profit, cur_quarter_eps, over_the_year_quarter_eps)
        return result
    
    def get_stock_price_for_period(self, symbol, start_date, end_date):
        self.cursor.execute(
            "SELECT avg(close) FROM stock_prices WHERE symbol = :symbol AND date >= :start_date AND date <= :end_date ORDER BY date", {"symbol": symbol, "start_date": start_date, "end_date": end_date})
        res = self.cursor.fetchone()
        return res[0]