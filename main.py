from data_collection.data_scraper import Scraper
import pandas as pd

scraper = Scraper()
# scraper.update_company_db()
# scraper.download_bse_500_index_list()

bse_500_df = pd.read_csv('MarketWatch.csv')
scraper.extract__complete_fundamental_data(bse_500_df)
scraper.close()
