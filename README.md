# Fundmaster

This is an experimental work to find out the effect of quarterly results on the price of stock in Indian market. 

## Problem Statement

To predict increase or decrease in the stock price after the announcement of quarterly financial results. Assumption is that the companies announce the results for a quarter at least before the third month of the next quarter. 

Assume a company announces their results for previous quarter during the quarter Q. I took the average price of the second half of the third month of Q. Subtracted this from the average price of the first half of the first month of Q. This difference specifies the increase or decrase on the stock price, which is my target variable. I addressed this as a classification problem. 

## Approach

My approach to this problem consists of following major steps

1. Data Collection
2. Pre processing
3. Feature engineering
4. Implementation of Machine Learning algorithm
5. Comparison and analysis of the results

### 1. Data Collection

Quarterly financial results and stock price data are extracted from the BSE website.



