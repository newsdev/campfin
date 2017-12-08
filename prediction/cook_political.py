import csv
import requests
import os
import os.path
from bs4 import BeautifulSoup

HOUSE_URL = 'https://cookpolitical.com/ratings/house-race-ratings'
SENATE_URL = 'https://cookpolitical.com/ratings/senate-race-ratings'
HEADERS = ['state', 'district', 'party', 'incumbent'] 
HOUSE_RATINGS = ['Likely Democratic', 'Lean Democratic', 'Democratic toss up',
'Republican toss up', 'Lean Republican', 'Likely Republican']
SENATE_RATINGS = ['Solid D', 'Likely D', 'Lean D',
'Toss up', 'Lean R', 'Likely R', 'Solid R']
DATA = [] 

def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

def read_tables(side, rows, rate_index):
    for row in rows[1:]:
        cells = row.findAll('td')
        row_dict = {HEADERS[i]:cells[i].string for i in range(len(HEADERS))}
        if side == 'HOUSE':
            row_dict['inside_elections_vulnerability'] = HOUSE_RATINGS[rate_index]
        else:
            row_dict['inside_elections_vulnerability'] = SENATE_RATINGS[rate_index]
        DATA.append(row_dict)

def scrape_house():
    soup = get_html(HOUSE_URL) 
    for i in range(len(HOUSE_RATINGS)):
        rows = soup.select(TABLE_NAME.format(str(i)))
        read_tables('HOUSE', rows, i)

def parse_senate(table):
    cols = table.select("ul.ratings-detail-page-table-7-column-ul")
    for i in range((len(cols)):
        incumbs = cols[i].findAll("li")

def scrape_senate():
    soup = get_html(SENATE_URL)
    dem_rows = soup.select("div.ratings-detail-page-table-7-column-main")[0]
    parse_table(dem_rows)
    
    repub_rows = soup.select("div.ratings-detail-page-table-7-column-main")[1]
    parse_table(repub_rows)

def csv_to_dict():
    items=[] 
    with open('reelection.csv', 'r') as csvfile:
        items = list(csv.DictReader(csvfile))    
    return items

def write_to_csv(list):
    csv_data = csv_to_dict()
    for csv_incumbent in csv_data: 
        for inside_incumbent in list: 
            if csv_incumbent['str_nyt_lastname'] == inside_incumbent['incumbent']:
                csv_incumbent['inside_elections_vulnerability'] = \
                inside_incumbent['inside_elections_vulnerability']
            elif csv_incumbent['str_state'] == inside_incumbent['state'] and \
                csv_incumbent['str_district'] == inside_incumbent['district']:
                csv_incumbent['inside_elections_vulnerability'] = \
                inside_incumbent['inside_elections_vulnerability']

    with open('reelection_inside.csv', 'w') as csvfile:
        keys = csv_data[0].keys()
        writer = csv.DictWriter(csvfile, keys)
        writer.writeheader()
        writer.writerows(csv_data) 
        print("Success! Wrote vulnerability rates according to https://www.insideelections.com to reelection_inside.csv")

if __name__ == '__main__':
    #scrape_house()
    scrape_senate()
    #write_to_csv(sorted(DATA, key=lambda k: k['incumbent']))
