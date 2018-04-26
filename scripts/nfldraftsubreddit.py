# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 13:13:31 2018

@author: steph
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup as bs
import datetime as dt
import pandas as pd
import sched
import sqlite3 as db
from threading import Timer
import numpy as np
import logging
import seaborn as sns
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import re
from gsheets import Sheets
from gspread_pandas import Spread, Client
import random
import csv
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gdrive
import os

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
print(file_list)

baseurl = 'https://www.reddit.com'
subreddit = 'https://www.reddit.com/r/NFL_Draft/search?q=docs.google&restrict_sr=on&t=month'
#posts = requests.get(subreddit)
#posts.text
driver = webdriver.Chrome()
driver.get(subreddit)
soup = bs(driver.page_source, 'html.parser')


##########
soup = bs(driver.page_source, 'html.parser')
for link in soup.findAll(class_ = 'search-result-header'):
    for l in link:
        print(l['href'])

##########

driver.get(subreddit)
n = 0
linklist = []
while n < 30:
    soup = bs(driver.page_source, 'html.parser')
    for link in soup.findAll('a', href = True):
        try:
            if l['href'] not in linklist and 'r/NFL_Draft/' in link['href']:
                linklist.append(l['href'])
        except:
            continue
        
    if n == 0:
        driver.get(soup.find(class_ = 'nextprev').a.get('href'))
    else:
        for links in soup.findAll(class_ = 'nextprev'):
            try:
                driver.get(str(links.findAll('a', href = True)[1]).split('"')[1])
            except:
                continue
    n += 1
    
soup = bs(driver.page_source, 'html.parser')
for link in soup.findAll('a', href = True):
    try:
        if link['href'] not in linklist and 'https://www.reddit.com/r/NFL_Draft/' in link['href']:
            linklist.append(link['href'])
    except:
        continue
linklist    
        
csvfile = 'links.csv'
with open(csvfile, 'w') as output:
    writer = csv.writer(output, lineterminator = '\n')
    for val in linklist:
        writer.writerow([val])

    
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
drafts = []
for draft in listofdrafts:
    drafts.append(draft['href'])       
    
sheets = Sheets.from_files('c:/users/steph/Documents/client_secret.json')
sheets['1DpAfzbXpBuuhEB1cGDBTb4_3K91Y9NiiAujkOeRrJSc']

with open(csvfile) as output:
    reader = csv.reader(output)
    listoflinks = list(reader)
    for link in listoflinks:
        linklist.append(link[0])
        
completed = [listofdrafts[22]]
for i in range(0, len(listofdrafts)):
    completed.append(i)
completed

listofdrafts.index(driver.current_url)



#############
n = 4


if listofdrafts[n] not in completed:
    driver.get(listofdrafts[n])
    completed.append(listofdrafts[n])
    n += 1
    print(n, '\n', '\n', listofdrafts[n].split('/d/')[1])
else: 
    n += 1
    print(n, '\n'*2, "already counted")


def getnextdraft(ind):
    if listofdrafts[ind] not in completed:
        driver.get(listofdrafts[ind])
        completed.append(listofdrafts[ind])
        n += 1
        print(n, '\n', '\n', listofdrafts[ind].split('/d/')[1])
    else: 
        n += 1
        print(n, '\n'*2, "already counted")
        

###############
import requests

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if __name__ == "__main__":
    file_id = 'TAKE ID FROM SHAREABLE LINK'
    destination = 'DESTINATION FILE ON YOUR DISK'
    download_file_from_google_drive(file_id, destination)
    

download_file_from_google_drive('1DpAfzbXpBuuhEB1cGDBTb4_3K91Y9NiiAujkOeRrJSc', 
                                'c:\users\steph\documents')
#################
filetoget = random.choice(listofdrafts).split('/d/')[1].split('/')[0]
print(filetoget)
gdd.download_file_from_google_drive(file_id=filetoget,
                                    dest_path='./data/draft.zip',
                                    unzip=True)
###############


'''VIZ'''
import numpy as np
import pandas as pd
from scipy import stats, integrate
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes = True)

mocks = pd.read_csv('NFLMockDrafts2018.csv', engine = 'python')

def make_and_save_dist(player):
    plotdat = mocks.loc[mocks.Player == player]
    
    plotdat = plotdat.loc[np.abs(plotdat.Pick - 
                               plotdat.Pick.mean()) 
    <= (3 * plotdat.Pick.std())]
    if len(plotdat) > 2:
        plt.figure()
        g = sns.distplot(plotdat.Pick)
        g.set_title(player + 'Mock Draft Pick Distribution')
        if plotdat.Pick.mean() < 10:
            plt.xlim(0,32)
        elif plotdat.Pick.mean() < 40:
            plt.xlim(0, 64)
        elif plotdat.Pick.mean() < 100:
            plt.xlim(0, 128)
        else:
            plt.xlim(0,256)
        g.figure.savefig(player + '.png')
        plt.close()
  

for player in mocks.Player.unique():
    try:
        make_and_save_dist(player)
    except:
        continue

bigboard = mocks.groupby(['Player'], as_index = False)['Pick'].mean().sort_values(by = 'Pick')
bigboard

