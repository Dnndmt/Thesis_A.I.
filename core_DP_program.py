import ast
import itertools
import pandas as pd
import numpy as np
import re
from collections import Counter
import logging
import datetime

def day_filter1(df, trading_days, date, num_days=1):
    """ Function to select a specific number of days from a specified date
        It returns the filtered dataframe based on trading days
        Weekends are included"""
    i = list(trading_days).index(date)
    df.index = pd.to_datetime(df.index)
    end_day = trading_days[i + num_days - 1] + pd.Timedelta(hours=(24.0)-(1E-9))
    
    if trading_days[i].weekday() == 0: ## add the weekends here
        end_prev_day = trading_days[i-1] + pd.Timedelta(hours=(24.0)-(1E-9))
        df1 = df[((df.index > pd.to_datetime(end_prev_day)) & (df.index <= pd.to_datetime(end_day)))]
    else:
        df1 = df[((df.index > pd.to_datetime(trading_days[i])) & (df.index <= pd.to_datetime(end_day)))]

   
    return df1


def stock_counts(df, trading_days, tickers):
    """ Function that takes a df and trading days with tickers and
         returns the frequency and dates of the tickers on SA"""
 
    ticker_pattern="\'(.+?)\'"   
    dates = [] # This part should be done in a matrix
    freq = []
    prob = []
    df.index = pd.to_datetime(df.index)
    # Loop over the dates in the df
    for i, date in enumerate(trading_days):
        stop_day = df.index[-1]
        
        if date <= stop_day:
            window_date = trading_days[i]
            df1 = day_filter1(df, trading_days, date)
            
            lstr = "".join(list(df1.tickers))
            tickers = re.findall(ticker_pattern, lstr)
            tickerfd = Counter(tickers)
            #n = sum(tickerfd.values())

            tickerf = {tname: f
                       for tname, f in tickerfd.items()}

            freq.append(tickerf)
            dates.append(window_date)

    return freq, dates


# updated function to stop on last day of df
def stock_dist2(df, trading_days, tickers, wind_num=30):
    """ This function build the distribution for the mentions of a stock
        for a given period defined as the window 
        The days are based on trading days which have to be passed to the function"""
    
    ticker_pattern="\'(.+?)\'"
    df.index = pd.to_datetime(df.index)
    results = []
    dates = []
    freq1 = []
    prob1 = []
    for i, date in enumerate(trading_days):
        logger.info('Program is at date: {0} - Number: {1} - out of: {2}'.format(date, i, len(trading_days)))

        if len(trading_days) > len(df.index):
            stop_day = df.index[-wind_num] # set the last day to be on the df and not on tradin_days
        else:
            stop_day = trading_days[-wind_num]
        
        if date <= stop_day:
            window_date = trading_days[i + (wind_num - 1)]
            
            # Extract the fequency of mentions for each ticker on a 30 day period
            df_long = day_filter1(df, trading_days, date, wind_num)
            lstr_l = "".join(list(df_long.tickers))
            
            tickers_l = re.findall(ticker_pattern, lstr_l)
            tickerfm = Counter(tickers_l)
            tickerfm_d = {tname: f for tname, f in tickerfm.items()}
            
            # loop over all days in the 30 day window for frequency distribution
            freq = []
            prob = []
            timestamps = trading_days[i: i + wind_num ]  #list(df_long.index.normalize().unique())
            #print(len(timestamps))
            for timestamp in timestamps:
                
                df_short = day_filter1(df, trading_days, timestamp)
                lstr_s = "".join(list(df_short.tickers))
                tickers_s = re.findall(ticker_pattern, lstr_s)
                
                tickerfd = Counter(tickers_s)
            
                # get the daily frequency of each ticker in the 30 day period
                tickerf = {tname: (tickerfd[tname] + 1) for tname in tickers}
                #print(tickerf)
                tickerp = {tname: (tickerfd[tname] + 1) / 
                                  (tickerfm_d[tname] + len(timestamps))
                            if tname in tickerfm_d.keys()
                            else 1/30
                                  for tname in tickers}

                freq.append(tickerf)
                prob.append(tickerp)
                
                # this aggregates the probabilities into one dictionary
                dist_dict = {}
                freq_dict = {}

                for ticker in prob[0].keys(): # why prob[0] - to get the tickers
                    distribution = []
                    frequencies = []

                    [distribution.append(prob[x][ticker]) for x in range(len(prob))]
                    [frequencies.append(freq[z][ticker]) for z in range(len(freq))]

                    dist_dict[ticker] = distribution
                    freq_dict[ticker] = frequencies
                    
            freq1.append(freq_dict)
            #prob1.append(prob) # this is redundant as it is similar to results
            dates.append(window_date)
            results.append(dist_dict)
        else:
            break # break out of the loop if df has no more data 
    # really only need the results and dates since freq can not be used 
    return freq1, results, dates


## Functions for entropy
def entropy2(lst_dict_prob):
    results = []
    for i in range(len(lst_dict_prob)):
        results.append({ticker: -np.dot(np.array(list(prob)), np.log2(np.array(list(prob))))  
         for ticker, prob in lst_dict_prob[i].items() })
    return results


def get_ts(results, df_tickers):
    """ Functions takes the results of the entropy2 function and this is then processed 
        and a dictionary is returned with all entropy values"""
    ts_dict = {}
    for ticker in list(tickers):
        ts = []
        [ts.append(results[i][ticker]) for i in range(len(results)) 
                        if ticker in results[i].keys()]
        ts_dict[ticker] = ts
    return ts_dict


def kl_div_max(lst_dict_prob):
    """ Calculate the KL Diviergence between two list of probability distributions
        Both lists have to be of the same lenght and now the prob max entropy is used
        This can be applied to any other probability distribution with relevant
        Comparable events"""
    max_entropy = [1/30]*30
    Q = np.array(max_entropy)
    results = []
    for i in range(len(lst_dict_prob)):    
        results.append({ticker: np.dot(np.array(list(prob)), np.log2(np.array(list(prob)) / Q))  
         for ticker, prob in lst_dict_prob[i].items()})
    return results

def kl_div_prev(lst_dict_prob):
    """ Calculate the KL Diviergence between two list of probability distributions
        Both lists have to be of the same lenght and now the prob max entropy is used
        This can be applied to any other probability distribution with relevant
        Comparable events"""
    
    results = []
    for i in range(len(lst_dict_prob)):
        if i > 0:
            Q = np.array(lst_dict_prob[i-1])
            results.append({ticker: np.dot(np.array(list(prob)), 
                                           np.log2(np.array(list(prob)) / np.array(list(prob2))))  
             for (ticker, prob), (ticker2, prob2) in zip(lst_dict_prob[i].items(), 
                                                         lst_dict_prob[i-1].items())})
    return results

def get_counts(freq, tickers):
    """ Function that receives the output of stock_counts and builds
        A timeseries list of it and returns a dictionary with tickers and counts"""
    freq_dict = {}
    for ticker in tickers:
        
        count = []
        for i in range(len(freq)):
            x = freq[i].get(ticker)
            if x == None:
                count.append(0)
            else:
                count.append(x)
        freq_dict[ticker] = count
    
    return freq_dict


### Logging Settings ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

now = datetime.datetime.now()
file_handler = logging.FileHandler('.//extract_dist_{}.log'.format(now.strftime("%Y-%m-%d %H-%M-%S")))
file_handler.setFormatter(formatter)

# create a streamhandler to also display output on screen
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


# Data
#df_SA = pd.read_csv('.//SA_master_final', index_col=['datetime'], encoding='utf-8')
#del df_SA['Unnamed: 0']

trading_days = np.load('.//Data_2//Trading_days.npy')

tickers = np.load('.//Data_2//Tickers.npy')
df_sample = pd.read_csv('.//df_sample', encoding='utf-8', index_col=0)

df_sample = df_sample.iloc[:500,:]

#### Run Program

# Calculate Probability distributions from adjusted frequencies
f, d, t = stock_dist2(df_sample, trading_days, tickers)

# Calculate Frequencies 
freq, dates = stock_counts(df_sample, trading_days, tickers)
# Dictionary of frequencies
lst_counts = get_counts(freq, tickers)


M = np.array([f, d, t])

N = np.array([freq, dates])
# Calculate Entropy

ent_results = entropy2(M[1,:])
ent_dict = get_ts(ent_results, tickers)

# KL Divergence from Max Entropy & Prev Day
kl_results = kl_div_max(M[1,:])
kl_max_dict = get_ts(kl_results, tickers)

prev_kl_results = kl_div_prev(M[1,:])
prev_kl_dict = get_ts(prev_kl_results, tickers)

## Save Data on seperate files for easy handling & plotting

np.save('.//Distributions.npy', M)
np.save('.//Frequen_dates', N)
np.save('.//Frequencies.npy', np.array(lst_counts))

M1 = np.array([ent_dict, kl_max_dict, prev_kl_dict])
np.save('.//Entropy_KL_Div.npy', M1)

print(M.shape, len(lst_counts), M1.shape)
