# -*- coding: utf-8 -*-

import csv
import numpy as np
import pandas as pd
import yfinance as yf

"""
Created on Mon Apr  6 13:29:30 2020

@author: Antti Luopajärvi

Calculating financial data.

Data sources:
    Yahoo Finance
    Trading economics https://tradingeconomics.com/bonds bond yields.

"""

def get_betas(s):
    """
    Using yfinance, getting stock betas from Yahoo finance database.

    Parameters
    ----------
    s : list
        stock symbols

    Returns
    -------
    list of betas.

    """
    
    # Use yahoo finance database to get betas
    betas = []
    for i in s:
        try:
            ticker = yf.Ticker(i)
            betas.append(ticker.info['beta'])
        except:
            print("Beta not found for " + i)
            betas.append(None)
    
    return betas
        

def get_average_dividend_yields(s):
    """
    Get 5 year average dividend yields using Yahoo Finance.

    Parameters
    ----------
    s : list
        stock symbols.

    Returns
    -------
    None.

    """
    
    # Use yahoo finance database to get yields
    yields = []
    for i in s:
        ticker = yf.Ticker(i)
        try:
            yields.append(ticker.info['fiveYearAvgDividendYield'])
        except:
            print("Yield not found for " + i)
            yields.append(None)
    
    return yields


def get_pe(s):
    """
    Get trailing price-to-earnings ratios for stocks.

    Parameters
    ----------
    s : list
        stock symbols.

    Returns
    -------
    pes : list
        p/e-ratios of stocks.

    """
    
    # Use yahoo finance database to get p/e's
    pe = []
    for i in s:
        ticker = yf.Ticker(i)
        try:
            pe.append(ticker.info['trailingPE'])
        except:
            print("P/E not found for " + i)
            pe.append(None)
    
    return pe
    

def market_returns(markets, names):
    """
    Calculating average market returns.

    Parameters
    ----------
    markets : Dataframe
        dataframes with market index information.
    names : list
        names of corresponding stock markets.

    Returns
    -------
    annual_returns : Dataframe
        annual average returns of each market in dataframe.

    """
    
    # calculate monthly changes
    for m in markets:
        m["Change"] = [(m_close-m_open)/m_open for m_open, m_close in zip (m['Open'],m['Adj Close'])]
    
    print("\nAverage change in monthly returns, number of examinations")
    i = 0
    for m in markets:
        print(names[i], np.mean(m['Change']), len(m['Change']))
        i+=1
    
    # calculating annual change of return
    annuals_markets = []
    annuals = []
    j = 0
    for m in markets:  
        i = 1
        while i < (len(m)-12): # iterate until end of file
            open_jan = m['Open'][i] # january 1st open value
            close_jan = m['Adj Close'].values[i+12] # next year's january 1st close value
            
             # annual change in value
            annuals.append((close_jan - open_jan)/open_jan)
            i += 12 # next year
        annuals_markets.append([names[j],np.mean(annuals)])
        j+=1
    
    print("\nAverage annual returns") 
    for a in annuals_markets:
        print(a)
    
    return pd.DataFrame(annuals_markets,columns=['Market','Average Return'])
    

def er(companies, rf, mrp):
    """
    Calculate expected returns.

    Parameters
    ----------
    companies : dataframe
        data on companies stocks
    rf : list
        risk-free rates for different markets.
    mr : list
        market risk premiums for different markets.

    Returns
    -------
    None.

    """
    
    ers = np.zeros([len(companies)])
    # indeces
    columns_indeces = [5,6,7]
    beta_index = 8
    
    # nasdaq and nyse
    for c in range(2):
        for i in range(len(companies)):
            if (companies.values[i][columns_indeces[c]] != 'na'):
                ers[i] = capm(companies.values[i][beta_index],rf[c],mrp[c])
    
    # for nasdaq north, company's origin country has to be determined since rf-rate and mr-premiums
    # are country specific for this market
    for i in range(len(companies)):
        # split to seperate country suffix
        splitted = str.split(companies.values[i][7],'.')
        market_index = 2 # default, CO
        if splitted[-1] == 'HE':
            market_index+=1
        elif splitted[-1] == 'ST':
            market_index+=2
        ers[i] = capm(companies.values[i][beta_index],rf[market_index],mrp[market_index])
    
    return ers
    
    
def capm(beta, rf, mrp):
    """
    Calculate expected return by Capital asset pricing model

    Parameters
    ----------
    beta : float
        stock beta.
    rf : float
        risk-free rate.
    mrp : float
        market risk premium.

    Returns
    -------
    er : float
        expected return.

    """
    
    return rf + beta*mrp
        
   
# read the data
df_nasdaq = pd.read_csv('../data/^IXIC.csv')
df_nyse = pd.read_csv('../data/^NYA.csv')
df_co = pd.read_csv('../data/^OMXC20.csv').dropna(axis=0,how='any') # drop rows with null-values
df_he = pd.read_csv('../data/^OMXH25.csv').dropna(axis=0,how='any')
df_st = pd.read_csv('../data/^OMX.csv').dropna(axis=0,how='any')
markets = [df_nasdaq,df_nyse,df_co,df_he,df_st]
names = ['Nasdaq','NYSE','CO','HE','ST']

# average returns
annual_returns = market_returns(markets,names)

# 10 y government bond yields used as risk free rates for each market
rf_rates = [0.006,0.006,-0.0019,-0.0004,-0.0007]
annual_returns['Risk free rate'] = rf_rates
# market premium = average market return - risk free rate
annual_returns['Market risk premium'] = annual_returns['Average Return']-annual_returns['Risk free rate']

annual_returns.to_csv('../data/market_data.csv')


# ==== 2. getting stock betas =====

#  get data
df_companies = pd.read_csv('../data/version_8.csv')

# for using yahoo finance database , nordic companies need a stock market suffix to the end
# of the stock symbols: e.g. "FORTUM.HE" = "Stock market of Helsinki"
df_symbols_nq_north = df_companies.loc[:,['Country','Symbol NQ North']]
countries = ['Finland','Sweden','Denmark']
suffixes = ['.HE','.ST','.CO']
for c in range(len(countries)):
   df_symbols_nq_north.loc[df_symbols_nq_north['Country'] == countries[c], 'Symbol NQ North'] +=suffixes[c] 

# in nordic markets, some stocks are "A, B or C"- types. 
# in these casesm the spelling in yahoo requires a dash instead of a space.
# E.g. "TEL2 B.ST" has to be TEL2-B.ST"
list_symbols = df_symbols_nq_north['Symbol NQ North'].values
letters = ['A','B','C']
for s in range(len(list_symbols)):
    try:
        splitted = str.replace(list_symbols[s],'.',' ').split()   
        if splitted[1] in letters:
            list_symbols[s] = str.replace(list_symbols[s], ' ', '-')
    except:
        pass

# replace with edited stock symbols
df_companies['Symbol NQ North'] = list_symbols
df_companies = df_companies.drop(axis=0,columns=['Unnamed: 0','Unnamed: 0.1','Unnamed: 0.1.1'])
print(df_companies.head())

# drop companies for which stock symbols aren't available
df_companies = df_companies.loc[(df_companies['Symbol NQ'] != 'na')\
                                | (df_companies['Symbol NYSE'] != 'na')\
                                | (df_companies['Symbol NQ North'] != 'na')]

# extract stock symbols and save into a list. 
# in the data, there is three columns for different markets, but only most companies
# are only listed on one market.
df_symbols = df_companies.loc[:,'Symbol NQ':'Symbol NQ North']

list_symbols = []
for i in range(len(df_symbols)):
    row = df_symbols.iloc[i,:].values
    for j in row: 
        if j != 'na': 
            list_symbols.append(j)
            break


# get ratios
betas = get_betas(list_symbols)
yields = get_average_dividend_yields(list_symbols)
pe = get_pe(list_symbols)
df_companies['Beta'] = betas
df_companies['Dividend yield'] = yields
df_companies['P/E'] = pe

# drop rows with missing data
df_companies = df_companies.dropna(axis=0,how='any',subset=['Beta','Dividend yield','P/E'])
df_companies.to_csv('../data/version_9.csv')

data = pd.read_csv('../data/version_12.csv')
md = pd.read_csv('../data/market_data.csv')
rf = md['Risk free rate']
mrp = md['Market risk premium']
ers = er(data, rf, mrp)
data['Expected return'] = ers
data.to_csv('../data/data_combined.csv')