# -*- coding: utf-8 -*-

import csv
import collections
import numpy as np
import pandas as pd

"""
Created on Wed Apr  8 12:54:18 2020

@author: Antti Luopajärvi

Organizing data from multiple sources. Going through different ranking datatables and combining 
them into one.
"""

def check_match(word1, word2, common_words):
    """
    Function to test if two company names with minor spelling differences match.

    Parameters
    ----------
    word1 : list
        words in company 1 name..
    word2 : list
        words in company 2 name.
    common_words: list
        common words in company names.

    Returns
    -------
    True is matches, otherwise False.

    """
    
    # setting the information about longer word, default is word1
    words = [word1, word2]
    i = 0
    if len(word2) > len(word1): i = 1
    
    # how many similar words
    matches = set(word1) & set(word2)
    amount = len(matches)
    
    # if list of common words is empty, use a default one
    common_w = common_words
    if len(common_w) < 1:
        common_w = ['ltd','inc','co','plc','as',\
                    'ab','spa','nv','corp','se',\
                    'property','group', 'inc.',\
                    'corp.','corporation','incorporated'\
                    'limited', 'etf','fund','bond',\
                    'treasury','sa','global',\
                    'markets','ag', 'international',\
                    'holding', 'holdings', 'a/s',\
                    'bank', 'consumer', 'products',\
                    'tbk', 'pt', 'asa', 'realty', \
                    'trust', 'estate', 'investment',\
                    'banco', 'de', 'del', 'pharmaceutical',\
                    'ndustries', 'energy', 'grupo', 'sab',\
                    'oyj', 'oy']
    for c in common_w:
        if c in matches: amount-=1
        
    # relation between same words and length of the word    
    result = amount/len(words[i]) # divided with length of longer word
    
    # using threshold value, return whether companies are same or not
    if result < 0.5: return False
    else: return True


def check_symbols(df_companies, df_symbols, stock_market):
    """
    Function to go through dataframe of company names and search their stock
    symbol from file containing them.

    Parameters
    ----------
    df_companies : dataframe
        company names.
    df_symbols : dataframe
        dataframe containing company names and corresponding stock symbols.
    stock_market : string
        which stock market's symbols are examined.
    Returns
    -------
    company_symbols_list : list

    """
    
    # for storing informationg about symbols, 
    symbols = []
    for i in range(len(df_companies)):
        symbols.append('na')
    
    # going through the company names from the symbols-dataframe
    # common_words = find_common_words(df_companies, stock_market)
    for i in range(len(df_companies)):
        r = df_companies['Company'][i].strip().lower().split()
        for j in range(len(df_symbols)):
            s = df_symbols['Name'][j].strip().lower().split()
            if check_match(r,s,[]): symbols[i] = df_symbols['Symbol'][j]
    
    return symbols
    

def check_occurances(df_base, df_c200, df_s):
    """
    Function to check whether the name of a company in Robecosam's ESG rating list is included or not in
    1) Clean200's list
    2) Sciencebasedtargets's list.

    Parameters
    ----------
    df_base : dataframe
        "Base" dataframe, Robecosam's list of companies.
    df_c200 : dataframe
        Clean200's list.
    df_s : dataframe
        Sciencebasedtargets' list.

    Returns
    -------
    clean_bools : list
        Binary info of whether company is included(1) in clean200 list or not(0).
    sbt_bools : list
        Binary info of whether company is included(1) in sciencebasedtargets list or not(0).
    countries : list
        Country where the company originates from, if info is available.

    """
    
    # for storing binary data about occurance of company names on clean200 and sciencebasedtarget's rankings
    clean_bools = np.zeros(len(df_robeco))
    sbt_bools = np.zeros(len(df_robeco))
    
    # for storing informationg about companies origin countries, 
    # initializing array of strings full of "na's"
    countries = []
    for i in range(len(df_robeco)):
        countries.append("na")
           
    # going through all the companies in robecosam's ranking. 
    # storing the information about whether the company name is found in clean200 
    # or sciencebasedtarget's rankings.
    for i in range(len(df_robeco)):
        for j in range (len(df_clean)):
            if df_robeco['Company'][i].strip().lower() == \
                df_clean['Short Name'][j].strip().lower():
                    clean_bools[i] = 1
                    break
        
        # sciencebasedtargets- list
        r = df_robeco['Company'][i].strip().lower().split()
        for k in range (len(df_sbt)):
            s = df_sbt['Company Name'][k].strip().lower().split()
            if check_match(r,s, []): 
                sbt_bools[i] = 1
                countries[i] = df_sbt['Country'][k]
                break
            
    return clean_bools, sbt_bools, countries


def find_common_words(df, stock_market):
    """
    A function to find commonly occuring words in company names that have been assigned a
    stock symbol.
    These will be taken in consideration when comparing company names with different spelling. 

    Parameters
    ----------
    df : dataframe
        dataframe of companies which have been allocated with common stock symbol.
    stock_market: string
        represents the column name of which stock market's symbols are examined.

    Returns
    -------
    list of common words in company names.

    """
    
    # taking 20 most common stock symbols in list
    common_symbols = df[stock_market].value_counts()[:20].index.tolist()
    
    # extract "na" from list, not interested in those 
    try:
        common_symbols.remove('na')
    except:
        print("no na's!")
        return []
    
    # get names of the companies which are allocated with some of these common stock symbols
    companies = df.loc[df[stock_market].isin(common_symbols)]['Company'].tolist()

    # store the words in these names
    words = []     
    for c in companies:
        words_c = c.split()
        for w in words_c:
            words.append(w)
    
    # get most common words
    common_words = []
    common_words_counts = collections.Counter(words).most_common(round(0.7*len(words)))
    for w in common_words_counts:
        common_words.append(w[0])
    
    return common_words
              
# ====================================================================================   

# importing data
df_clean = pd.read_csv('../data/clean200.csv')
df_robeco = pd.read_csv('../data/robecosam.csv')
df_sbt = pd.read_csv('../data/sciencebasedtargets.csv')
df_symbols_nq = pd.read_csv('../data/symbols_nasdaq.csv')
df_symbols_nyse = pd.read_csv('../data/symbols_nyse.csv')
df_symbols_nordic = pd.read_csv('../data/symbols_nasdaq_nordic.csv')

# checking the occurances of companies between three rating lists
clean_bools, sbt_bools, countries = check_occurances(df_robeco, df_clean, df_sbt)

# finding the stock symbols for companies from stock symbol lists 
symbols_nq = check_symbols(df_robeco,df_symbols_nq, 'Symbol NQ')
symbols_nyse = check_symbols(df_robeco,df_symbols_nyse, 'Symbol NYSE')
symbols_nordic = check_symbols(df_robeco,df_symbols_nordic, 'Symbol NQ North')
       
# adding colums to dataframe, containing information about company's 
# occurance in clean200's and sciencebasedtargets' lists, plus the origin
# country of the company and stock symbol
df_robeco['Clean200'] = clean_bools
df_robeco['ScienceBasedTargets'] = sbt_bools
df_robeco['Country'] = countries
df_robeco['Symbol NQ'] = symbols_nq
df_robeco['Symbol NYSE'] = symbols_nyse
df_robeco['Symbol NQ_North'] = symbols_nordic

# drop rows for which stock symbol was not found
df_final = df_robeco.loc[(df_robeco['Symbol NQ'] != 'na') \
                        |(df_robeco['Symbol NYSE'] != 'na') \
                        |(df_robeco['Symbol NQ_North'] != 'na')]

df_final.to_csv('../data/combined_data.csv')