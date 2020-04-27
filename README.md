# Fundmaster

This is an experimental work to find out the effect of quarterly results on the price of stock in Indian market. 

## Problem Statement

To predict increase or decrease in the stock price after the announcement of quarterly financial results. Assumption is that the companies announce the results for a quarter at least before the third month of the next quarter. 

Assume a company announces their results for previous quarter during the quarter Q. I took the average price of the second half of the third month of Q. Subtracted this from the average price of the first half of the first month of Q. This difference specifies the increase or decrease on the stock price, which is my target variable. I addressed this as a classification problem. 

## Approach

My approach to this problem consists of following major steps

1. Data Collection
2. Feature engineering
3. Implementation of Machine Learning algorithm
4. Comparison and analysis of the results

### 1. Data Collection

Quarterly financial results and stock price data are extracted from the BSE website.
Companies selected were from the S&P BSE 500 index. We fetched previous 6 years data.
Daily stock prices were collected from the *BSE bhav copies*.

After fetching the data we are storing it in an SQLite database. 
Database helper functions can be used as
```
from database_helpers import Db
db = Db()
security_code = 500010
db.get_company_details_from_sec_code(str(security_code))
```

To run the functions in the data scraper module, an example is as follows

```
from data_collection.data_scraper import Scraper
scraper = Scraper()
scraper.download_bse_500_index_list()
```
There are functions for 

+ Updating the latest company list into Database
+ Downloading the S&P BSE 500 index listed companies
+ Extracting the fundamental data 
+ Collecting the stock prices data 


### 2. Feature Extraction

For making this experiment simple, I have collected only sales, net profit and eps values from the financial results.
From these values I have calculated below features.
1. Percentage of sales change from the previous quarter
2. Percentage of net profit margin change from the previous quarter
3. Percentage of eps change from the previous quarter
4. Percentage of Year-Over-Year quarterly sales change
5. Percentage of Year-Over-Year quarterly net profit margin change
6. Percentage of Year-Over-Year quarterly eps change

#### Target variable

The target variable/output value denotes whether there is a change in stock price during the quarter of the results announcement. Please note that Quarterly Results of a quarter are announced in the next quarter.

The output calculation is as follows
Calculate the average stock price of the first half of the first month of the quarter (A)
Calculate the average stock price of the second half of the third month of the quarter (B)
Find the percentage change from A to B  (C)
If C is positive target value is set as 1 other wise it is 0

Features extraction functions can be run as
```
from feature_extraction import FeatureExtractor
feature_extractor = FeatureExtractor()
feature_extractor.prepare_input_data_set()
```

### 3. Implementation of machine learning algorithms

For training, basic algorithms like Decision tree, Random forest etc. are tried out. 
Input data set consisted of 10201 samples with 6 features. 
Implementation is done with the help of Scikit-learn libraries.
Experiments can be found in the ```Stock price prediction``` notebook

### 4. Results and future work

Initially I have used only the previous quarter changes as features. A decision tree classifier gave 55.48 % accuracy and  50.68 precision value. Precision is important here as in real market we are selecting the positive cases only and the number of true cases should be maximised.

Later I used year over year quarterly changes as my features. For the decision tree classifier produced 56.20 % accuracy and 50.11 precision

Then I combined these features and which gave 56.80 % accuracy and 51.25 % precision values

I know these values are not at all exciting, but getting a 50% accuracy itself is great in stock market and people make money even with that with proper risk money management and profit booking strategies.

I have selected very few features for this experiment. There are dozens of other features which can be extracted from the quarterly results. Future work can be to experiment with these features. Some of the potential features are given below

+ Price to earning ratio
+ Debt to equity ratio
+ Quick ratio
+ EV/EBITDA
+ PEG ratio
+ Return on equity
+ Current ratio
+ Dividend yield
+ Receivable turns
+ Inventory turnover ratio
+ Return on assets



