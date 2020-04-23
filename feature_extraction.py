from datetime import timedelta

import pandas as pd
from database_helpers import Db
from dateutil.relativedelta import relativedelta


def change_between_numbers(first, second):
    '''
    Calculate percentage of change between two numbers
    Basic formula doe not work well with negative numbers, use this function to calculate the percentage of change
    '''
    if first == 0:
        first = first + 0.1
        second = second + 0.1
    change = ((second - first) / first) * 100
    if first < 0 and second < 0:
        change = change * -1
    elif first < 0:
        change = change * -1

    return change


class FeatureExtractor():
    """
    Extract the features from the fundamentals
    """

    def __init__(self):
        self.db = Db()

    def close(self):
        self.db.close()

    def extract_fundamental_features(self, symbol):
        dates = self.db.get_available_dates(symbol)
        fundamental_features_df = pd.DataFrame(columns=['date', 'Sales Change', 'Net Profit Margin Change', 'EPS Change'])
        i = 0
        for cur_date in dates:
            over_year_date = cur_date - relativedelta(years=1)
            res = self.db.get_over_the_year_fundamental_data(
                symbol, cur_date, over_year_date)
            if res:
                sales_change = change_between_numbers(res[0], res[1])
                net_profit_margin_change = change_between_numbers(
                    (res[2]/res[0]), (res[3]/res[1]))
                eps_change = change_between_numbers(res[4], res[5])
                fundamental_features_df.loc[i] = [cur_date, sales_change, net_profit_margin_change, eps_change]
                i = i + 1
        return fundamental_features_df
    
    def calculate_target_variable(self, symbol, previous_quarter_end_date):
        first_month_start_date = previous_quarter_end_date + timedelta(days=1)
        first_month_first_half_end_date = first_month_start_date + timedelta(days=14)
        first_month_first_half_stock_average_price = self.db.get_stock_price_for_period(symbol, first_month_start_date, first_month_first_half_end_date)
        
        third_month_end_date = previous_quarter_end_date + relativedelta(months=3)
        third_month_second_half_start_date = third_month_end_date - timedelta(days=14)
        third_month_second_half_stock_average_price = self.db.get_stock_price_for_period(symbol, third_month_second_half_start_date, third_month_end_date)
        
        if first_month_first_half_stock_average_price and  third_month_second_half_stock_average_price:
            quarter_price_difference = third_month_second_half_stock_average_price - first_month_first_half_stock_average_price
            target_value = 1 if quarter_price_difference > 0 else 0
            print(first_month_first_half_stock_average_price, third_month_second_half_stock_average_price)
            print(quarter_price_difference, target_value, "\n")
            return target_value
        else:
            print("first_month_start_date", first_month_start_date)
            return False
        # print(stock_prices)

    def prepare_input_data_set(self):
        companies_list = self.db.get_companies_with_fundamentals()
        input_data_set = pd.DataFrame(columns=['date', 'Sales Change', 'Net Profit Margin Change', 'EPS Change', 'Price Change']) #,   #Price change 1 means increase , and 0 means decrease
        i = 0
        for symbol in companies_list:
            fundamental_features_df = self.extract_fundamental_features(symbol)
            for row in range(len(fundamental_features_df)):
                target_value = self.calculate_target_variable(symbol, fundamental_features_df.loc[row, "date"])
                if target_value is not False:
                    input_data_set.loc[i] = fundamental_features_df.loc[row]
                    input_data_set.loc[i, 'Price Change'] = target_value
                    i = i + 1
        input_data_set.to_csv("input_data_set.csv")

