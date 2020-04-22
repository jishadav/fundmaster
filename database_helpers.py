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

    def insert_company_data(self, symbol, security_code, name, industry):
        """Insert the company data to db"""
        # try:
        self.cursor.execute("INSERT INTO company (symbol, security_code, name, industry) \
                            VALUES (:symbol, :security_code, \
                                :name, :industry)",
                            {"symbol": symbol, "security_code":
                                security_code, "name": name,
                                "industry": industry})
        self.connection.commit()
        # except sqlite3.IntegrityError as e:
        #     pass
