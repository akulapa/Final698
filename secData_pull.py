# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 11:18:59 2018

@author: akulap
- https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
- http://www.openbookproject.net/books/bpp4awd/ch04.html
"""
import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
import os
import sqlite3

#Create SQLite connection
con = sqlite3.connect('D:/CUNY/698/edgar_Form8K.db')
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS Form8K')
cur.execute('CREATE TABLE Form8K (cik TEXT, company TEXT, type TEXT, date TEXT, path TEXT)')

#Set quarters, SEC stores data in quarters
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']

#Loop for years
for iYear in range(2017,2019,1):
    #Loop of quarters
    for quarter in quarters:
        #Quarter url
        secUrl = "https://www.sec.gov/Archives/edgar/daily-index/" + str(iYear) + "/"+ quarter + '/'
        
        #Get page and extract tables
        pageData = requests.get(secUrl)
        html_content = soup(pageData.content, 'html.parser')
        tables = html_content.findAll("table")
        
        #Loop through tables and get idx files
        for table in tables:
             if table.findParent("table") is None:
                 df = pd.read_html(str(table))[0]

        #Loop through each idx file and save it to local drive
        #Read only master files, it pipe(|) seperated and easy to read
        for index, row in df.iterrows():
            if row[0].startswith( 'master' ):
                idxUrl = "https://www.sec.gov/Archives/edgar/daily-index/" + str(iYear) + "/" + quarter + '/' + row[0]
                readIdx = requests.get(idxUrl)
                directory = 'D:/CUNY/698/edgarForm8K/' + str(iYear) + "/" + quarter + '/'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open('D:/CUNY/698/edgarForm8K/' + str(iYear) + "/" + quarter + '/' + row[0], 'wb') as f:
                    f.write(readIdx.content)
                    f.close()

#Set interested companies
companies = ['Ford Motor', 
           'Fiat', 'Chrysler', 
           'General Motors', 
           'Mercedes',
           'BMW',
           'Volkswagen',
           'Audi', 'Bentley', 'Bugatti', 'Lamborghini', 'Porsche',
           'Toyota',
           'Nissan Motor',
           'Honda Motor',
           'Subaru',
           'Mitsubishi', 'Renault',
           'Mazda',
           'Hyundai',
           'Tata',
           'Zhejiang', 'Geely', 'Polestar', 'Volvo'
        ]

#Read each file and check for companies
for iYear in range(2017,2019,1):
    for quarter in quarters:
        directory = 'D:/CUNY/698/edgarForm8K/' + str(iYear) + "/" + quarter + '/'
        for file in os.listdir(directory):
            if file.startswith( 'master' ):
                idfFile = os.path.join(directory, file)
                file_content = open(idfFile, "r")
                
                #Get matching recored, that is 8-K filing and belongs to interested companies
                records = [tuple(line.rstrip().split('|')) for line in file_content if ((line.find("|edgar/data") > 0) and (line.find("|8-K") > 0)) for company in companies if (line.find(company) > 0)]
                file_content.close()
                
                #Write to SQLite database
                cur.executemany('INSERT INTO Form8K VALUES (?, ?, ?, ?, ?)', records)
                con.commit()

#Close the connection
con.close()


import requests
from bs4 import BeautifulSoup

url = "https://www.sec.gov/Archives/edgar/data/1000275/0001140361-17-000073.txt"
html = requests.get(url)
soup = BeautifulSoup(html.content, 'html.parser')

# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out

# get text
text = soup.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text)


