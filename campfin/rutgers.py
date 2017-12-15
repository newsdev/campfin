import csv
import requests
from bs4 import BeautifulSoup

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
from utils import request_until_succeed, unicode_decode

state_style = "background-color: rgb(221, 221, 221);"
url = "http://cawp.rutgers.edu/buzz-2018-potential-women-candidates-us-congress-and-statewide-elected-executive#list"

def get_table(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    rows = soup.select("table.election-watch-table tbody tr")
    return rows

def get_name(strs):
    last = strs[-2]
    rest = " ".join(strs[:-2])
    return last + ", " + rest

def get_party(strs):
    return(strs[-1].strip("()"))

def check_office(str):
    if "U.S. Rep" in str:
        return "House"
    elif "U.S. Sen" in str:
        return "Senate"
    else:
        return None

def read_rows(table):
    candidates = []
    curr_state = ""
    for row in table[1:]:
        cells = row.findAll("td")
        if len(cells) == 0:
            continue

        state = cells[0].text.strip()
        name_party = cells[3].text.strip()
        office = check_office(cells[1].text.strip())

        """Update state if needed""" 
        if state != "":
            curr_state = state
            continue
        elif office is not None:

            """Split candidate name/party column into separate strings"""
            name_party_split = name_party.split(" ")
            name = get_name(name_party_split)
            party = get_party(name_party_split)

            """Fill dictiononary for candidate and append to data list"""
            row_dict = {} 
            row_dict["state"] = curr_state
            row_dict["office"] = office
            row_dict["district"] = cells[2].text.strip()
            row_dict["name"] = name
            row_dict["party"] = party
            row_dict["general_seat"] = cells[4].text.strip()
            row_dict["filing_date"] = cells[5].text.strip()
            row_dict["primary_date"] = cells[6].text.strip()
            row_dict["election_date"] = cells[7].text.strip()
            candidates.append(row_dict)
    return candidates
    
if __name__ == '__main__':
    print("Fetching html data from cawp.rutgers.edu")
    rows = get_table(url)

    print("Converting html table to list of dictionaries")
    candidates = read_rows(rows)

    print("Writing candidates to data/2018_rutgers.csv")
    keys = candidates[0].keys()
    with open("data/2018_rutgers.csv", "w") as csvfile:
        dict_writer = csv.DictWriter(csvfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(candidates)
