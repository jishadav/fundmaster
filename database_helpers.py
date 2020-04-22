import sqlite3


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
        # try:
        print(fundamental_dict)
        self.cursor.execute("INSERT INTO fundamentals (symbol, date, sales, net_profit, eps, url) \
                            VALUES (:symbol, :date, :sales, :net_profit, :eps, :url)",
                            {"symbol": fundamental_dict['symbol'], "date": fundamental_dict['date'],
                                "sales": fundamental_dict['sales'],
                                "net_profit": fundamental_dict['net_profit'], "eps": fundamental_dict['eps'],
                                "url": fundamental_dict['url']})
        self.connection.commit()
        # except sqlite3.IntegrityError as e:
        #     pass
