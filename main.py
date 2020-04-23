from data_collection.data_scraper import Scraper
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from feature_extraction import FeatureExtractor

# scraper = Scraper()
# scraper.update_company_db()
# scraper.download_bse_500_index_list()

# bse_500_df = pd.read_csv('MarketWatch.csv')
# scraper.extract__complete_fundamental_data(bse_500_df)

# end_date = datetime.datetime.now().date()
# start_date = (end_date - relativedelta(years=6))
# scraper.update_daily_stock_prices(start_date, end_date)



# scraper.close()


feature_extractor = FeatureExtractor()
feature_extractor.prepare_input_data_set()
