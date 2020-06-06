# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import csv
import pandas as pd
import re
import urllib.request

"""
Created on Fri Apr  3 20:51:17 2020

@author: Antti Luopajärvi

1) Web scraper for getting Robecosam's ESG scores and NASDAQ Nordic stock symbols.
   See https://yearbook.robecosam.com/ranking/
   and http://www.nasdaqomxnordic.com/shares/listed-companies/nordic-large-cap
2) Transforming ESG ranking data from three sources into csv-format.
"""

# 1)
# parsing the webpage with beautifulsoup
#url = "https://yearbook.robecosam.com/ranking/"
url = "https://www.spglobal.com/esg/csa/yearbook/ranking/"
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page,features='html.parser')

# for storing the values
companies_sam = []
scores_sam = []

# extracting company names and esg scores
for a in soup.findAll('div', attrs={'class':re.compile("mix item")}):
    companies_sam.append(a.find('div', attrs={'class':'company'}).text)
    scores_sam.append(a.find('div', attrs={'class':'percentile'}).text)
    
# parse nasdaq webpage
page = open('data/Nordic Large Cap - Listed Companies - Nasdaq.html', 'r', encoding='utf-8')
soup = BeautifulSoup(page,features='html.parser')

companies = []
symbols = []

# extracting company names and symbols
table = soup.find('table', attrs={'id':'listedCompanies'}).find('tbody')
for t in table:
    if (t != '\n'):
        rows = t.findAll('td')
        companies.append(rows[0].text) # first row, company name
        symbols.append(rows[1].text) # second row, symbol
        

# 2)
# storing the data in usable format
df = pd.DataFrame({'Company':companies_sam, 'ESG score':scores_sam})
df.to_csv(r'data\robecosam.csv',index=False,encoding='utf8')

# storing the data in usable format
df_nn = pd.DataFrame({'Name':companies, 'Symbol':symbols})
df_nn.to_csv(r'data\symbols_nasdaq_nordic.csv',index=False,encoding='utf8')

# convert excel files to csv
clean200 = pd.read_excel(r'data\clean200.xlsx')
clean200.to_csv(r'data\clean200.csv', index = None)
sbt = pd.read_excel(r'data\sciencebasedtargets.xlsx')
sbt.to_csv(r'data\sciencebasedtargets.csv', index = None)

# extract company names from sciencebasedtargets list 
# (only names, no scores or ratings included in rating)
companies_sbt = [] 
with open('data\sciencebasedtargets.csv', encoding='utf-8') as f:
    r = csv.reader(f)
    for row in r:
        companies_sbt.append(row[0])        