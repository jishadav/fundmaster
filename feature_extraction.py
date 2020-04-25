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

    def extract_over_year_fundamental_features(self, symbol):
        dates = self.db.get_available_dates(symbol)
        fundamental_features_df = pd.DataFrame(
            columns=['symbol', 'date', 'Sales Change', 'Net Profit Margin Change', 'EPS Change'])
        i = 0
        for cur_date in dates:
            over_year_date = cur_date - relativedelta(years=1)
            res = self.db.get_over_the_period_fundamental_data(
                symbol, cur_date, over_year_date)
            if res:
                sales_change = change_between_numbers(res[0], res[1])
                net_profit_margin_change = change_between_numbers(
                    (res[2]/res[0]), (res[3]/res[1]))
                eps_change = change_between_numbers(res[4], res[5])
                fundamental_features_df.loc[i] = [
                    symbol, cur_date, sales_change, net_profit_margin_change, eps_change]
                i = i + 1
        return fundamental_features_df

    def extract_prev_qtr_fundamental_features(self, over_year_change_df):
        for row in range(len(over_year_change_df)):
            symbol = over_year_change_df.loc[row, 'symbol']
            cur_date = over_year_change_df.loc[row, 'date']
            prev_qtr_date = cur_date - \
                relativedelta(months=3) + relativedelta(day=31)
            res = self.db.get_over_the_period_fundamental_data(
                symbol, cur_date, prev_qtr_date)
            if res:
                sales_change = change_between_numbers(res[0], res[1])
                net_profit_margin_change = change_between_numbers(
                    (res[2]/res[0]), (res[3]/res[1]))
                eps_change = change_between_numbers(res[4], res[5])
                over_year_change_df.loc[row,
                                        'prev_qtr_sales_change'] = sales_change
                over_year_change_df.loc[row,
                                        'prev_qtr_npm_change'] = net_profit_margin_change
                over_year_change_df.loc[row,
                                        'prev_qtr_eps_change'] = eps_change

        over_year_change_df = over_year_change_df.dropna().reset_index(drop=True)
        return over_year_change_df

    def calculate_over_year_change_from_previous_quarter(self, over_year_change_df):
        for row in range(len(over_year_change_df)):
            if row > 0:
                over_year_change_df.loc[row, 'over_year_sales_quarter_change'] = change_between_numbers(float(
                    over_year_change_df.loc[row-1, "Sales Change"]), float(over_year_change_df.loc[row, "Sales Change"]))
                over_year_change_df.loc[row, 'over_year_npm_quarter_change'] = change_between_numbers(float(
                    over_year_change_df.loc[row-1, "Net Profit Margin Change"]), float(over_year_change_df.loc[row, "Net Profit Margin Change"]))
                over_year_change_df.loc[row, 'over_year_eps_quarter_change'] = change_between_numbers(float(
                    over_year_change_df.loc[row-1, "EPS Change"]), float(over_year_change_df.loc[row, "EPS Change"]))
        over_year_change_df = over_year_change_df.dropna().reset_index(drop=True)
        return over_year_change_df

    def calculate_target_variable(self, symbol, previous_quarter_end_date):
        first_month_start_date = previous_quarter_end_date + timedelta(days=1)
        first_month_first_half_end_date = first_month_start_date + \
            timedelta(days=14)
        first_month_first_half_stock_average_price = self.db.get_stock_price_for_period(
            symbol, first_month_start_date, first_month_first_half_end_date)

        third_month_end_date = previous_quarter_end_date + \
            relativedelta(months=3)
        third_month_second_half_start_date = third_month_end_date - \
            timedelta(days=14)
        third_month_second_half_stock_average_price = self.db.get_stock_price_for_period(
            symbol, third_month_second_half_start_date, third_month_end_date)

        # if first_month_first_half_stock_average_price and third_month_second_half_stock_average_price:
        #     quarter_price_difference = third_month_second_half_stock_average_price - \
        #         first_month_first_half_stock_average_price
        #     target_value = 1 if quarter_price_difference > 0 else 0
        #     return target_value

        if first_month_first_half_stock_average_price and third_month_second_half_stock_average_price:
            quarter_price_change = change_between_numbers(first_month_first_half_stock_average_price, third_month_second_half_stock_average_price)
            # third_month_second_half_stock_average_price - \
            #     first_month_first_half_stock_average_price
            # print(first_month_first_half_stock_average_price, third_month_second_half_stock_average_price, quarter_price_change)
            target_value = 1 if quarter_price_change > 0 else 0
            return quarter_price_change

        else:
            return False

    def prepare_input_data_set(self):
        companies_list = self.db.get_companies_with_fundamentals()
        input_data_set = pd.DataFrame(columns=['symbol', 'date', 'Sales Change', 'Net Profit Margin Change',
                                               'EPS Change', 'prev_qtr_sales_change', 'prev_qtr_npm_change',
                                               'prev_qtr_eps_change', 'Price Change'])  # ,   #Price change 1 means increase , and 0 means decrease
        i = 0
        for symbol in companies_list:
            over_year_fundamental_features_df = self.extract_over_year_fundamental_features(
                symbol)
            prev_qtr_fundamental_features = self.extract_prev_qtr_fundamental_features(
                over_year_fundamental_features_df)

            # over_year_change_df = self.calculate_over_year_change_from_previous_quarter(fundamental_features_df)

            for row in range(len(prev_qtr_fundamental_features)):
                target_value = self.calculate_target_variable(
                    symbol, prev_qtr_fundamental_features.loc[row, "date"])
                if target_value is not False:
                    input_data_set.loc[i] = prev_qtr_fundamental_features.loc[row]

                    input_data_set.loc[i, 'Price Change'] = target_value
                    i = i + 1
                    print(i)

            # break
        # print(input_data_set.columns)
        input_data_set.to_csv("input_data_set.csv")
