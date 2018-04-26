# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 21:45:40 2018

@author: steph
"""

import time
from bs4 import BeautifulSoup as bs
import datetime as dt
import pandas as pd
from selenium import webdriver
import matplotlib.pyplot as plt
import csv
from pathlib import Path
import numpy as np
import imgkit
from scipy import stats, integrate
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes = True)

'''
Use Reddit Search feature to find only those drafts with Google Docs
Extract the link for every post in the last month containing a Google Docs link (presumably to a mock draft)
'''

subreddit = 'https://www.reddit.com/r/NFL_Draft/search?q=docs.google&restrict_sr=on&t=month'
driver = webdriver.Chrome()
driver.get(subreddit)
soup = bs(driver.page_source, 'html.parser')

linklist = []
for link in soup.findAll('a', href = True):
    try:
        if link['href'] not in linklist and 'https://www.reddit.com/r/NFL_Draft/' in link['href']:
            linklist.append(link['href'])
    except:
        continue
    
    
'''
Extract the Google Docs url from each post
'''

listofdrafts = []
for link in linklist:
    try:
        driver.get(link)
    except:
        continue
    time.sleep(1)
    soup = bs(driver.page_source, 'html.parser')
    for link in soup.findAll('a', href = True):
        try:
            if 'docs.google.com' in link['href'] and link['href'] not in listofdrafts:
                listofdrafts.append(link['href'])
        except:
            continue
        
'''
Run through the list of Google Docs links and mark those which have been completed
Of Note: finding a programmatic way to handle this was too daunting in the timeframe leading up to the draft, so each
doc was handled manually (with some logic in Excel to automate the writing process)
Of Note II: many sheets had different formatting, and even different spelling for player names, so that also was handled with logic in Excel
Of Note III: several mock drafts were done in Word format, but that difficulty was overcome with a templated method in Excel
'''

completed = []
if listofdrafts[n] not in completed:
    driver.get(listofdrafts[n])
    completed.append(listofdrafts[n])
    n += 1
    print(n, '\n', '\n', listofdrafts[n].split('/d/')[1])
else: 
    n += 1
    print(n, '\n'*2, "already counted")
    
 
    
'''
Now that the data is there, assemble a data frame and do calculations on the pick distribution for each player
'''


data_folder = Path("c:/GitHub/NFLDraft2018/data")
plots_folder = Path("c:/GitHub/NFLDraft2018/plots")
pltfold = "c:/GitHub/NFLDraft2018/plots/"

mocks = pd.read_csv(data_folder / 'NFLMockDrafts2018.csv', engine = 'python')
pd.set_option('display.max_colwidth', -1)
pd.options.display.float_format = '{:,.1f}'.format

def make_and_save_dist(player):
    plotdat = mocks.loc[mocks.Player == player]
    
    plotdat = plotdat.loc[np.abs(plotdat.Pick - 
                               plotdat.Pick.mean()) 
    <= (3 * plotdat.Pick.std())]
    if len(plotdat) > 2:
        plt.figure()
        g = sns.distplot(plotdat.Pick)
        g.set_title(player + ' Mock Draft Pick Distribution')
        if plotdat.Pick.mean() < 10:
            plt.xlim(0,32)
        elif plotdat.Pick.mean() < 40:
            plt.xlim(0, 64)
        elif plotdat.Pick.mean() < 100:
            plt.xlim(0, 128)
        else:
            plt.xlim(0,256)
        imgpath = "{}{}{}".format(pltfold, player, '.png')
        g.figure.savefig(imgpath)
        plt.close()
        imgstr = '<img src="{}" /> '.format(imgpath)
        return(imgstr)

'''
Run via mapping as a column in the data frame:
for player in mocks.Player.unique():
    try:
        make_and_save_dist(player)
    except:
        continue
'''

# Get min, max, average draft slot
def lowerbound(x):
    return x.quantile(0.025)
def upperbound(x):
    return x.quantile(0.975)
aggfuns = {'Min' : 'min', 'Average': 'mean', 'Max' : 'max', 'StandardDev' : 'std', 
           'LowerBound' : lowerbound, 'UpperBound': upperbound}

bigboard = mocks.groupby(['Player',], as_index = False)['Pick'].agg(aggfuns).sort_values(by = 'Average')
bigboard['Pick'] = bigboard['Average'].rank(ascending = 1)
bigboard = bigboard[['Pick', 'Player', 'Average', 'LowerBound', 'UpperBound', 'Min', 'Max', 'StandardDev']]
bigboard['Distribution'] = bigboard['Player'].map(make_and_save_dist)
#bigboard = bigboard.dropna(subset = ['Distribution'])
bigboard[:255].to_html('2018draft.html', escape = False, index = False)

'''
Apply custom formatting so the table doesn't look like garbage
'''

css = """
<style type=\"text/css\">
table {
color: #333;
font-family: Helvetica, Arial, sans-serif;
width: 640px;
border-collapse:
collapse; 
border-spacing: 0;
}
td, th {
border: 1px solid transparent; /* No more visible border */
height: 30px;
}
th {
background: #DFDFDF; /* Darken header a bit */
font-size: x-large;
font-weight: bold ;
text-align: center;
}
td {
background: #FAFAFA;
text-align: center;
}
table tr:nth-child(odd) td{
background-color: white;
}
</style>
"""
'''
write the CSS to the html file
'''
text_file = open("2018draft.html", "a")
text_file.write(css)
text_file.close()