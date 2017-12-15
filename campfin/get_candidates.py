import argparse
import csv
import json
import os
import sys
import time

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
from utils import request_until_succeed, unicode_decode

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="The election year you'd like to retrieve data for")
parser.add_argument("--totals", help="Get totals for each candidate", action="store_true")
parser.add_argument("--districts", help="Get data on district races", action="store_true")

args = parser.parse_args()
year = args.year
totals = args.totals
districts = args.districts

base = "https://api.open.fec.gov/v1/"
house = "H"
api_key = os.environ.get('FEC_KEY_3', None)
set_fields = set()


"""Returns list of candidates in given year"""
def get_candidates(year):
    election_request = "election_year=" + year
    api_request = "api_key=" + api_key
    page = 1
    has_next_page = True
    payload = []
    print("Fetching House candidates in year %s" %str(year))
    while has_next_page:
        url = base + "/candidates/?page={}&per_page=100&sort=name&".format(str(page)) \
                + election_request + "&" + api_request
                
        results = json.loads(request_until_succeed(url))["results"]
        if results == []:
            has_next_page = False
            print("Iterated through {} pages of candidates.".format(str(page-1)))
            print("Total number of candidates in %s: %s" %(str(year), str(len(payload))))
            print("-------------------------------------------------------------")
            return payload
        else:
            payload.extend(results)
            page += 1

"""Returns dictionary of state_district:[candidates]"""
def count_districts(candidates):
    districts = {}
    for candidate in candidates:
        if candidate["state"] is not None and candidate["district"] is not None:
            key = candidate["state"] + candidate["district"]
            if key in districts:
                districts.get(key).append(candidate["candidate_id"])
            else:
                districts[key] = [candidate["candidate_id"]]

    return districts

"""Writes to csv districts, candidate_ids, count"""
def count_districts_csv(candidates):
    districts = []
    dictionary = count_districts(candidates)
    for d in dictionary:
        districts.append({"district":d, "candidates":dictionary.get(d), "count":len(dictionary.get(d))})
    return districts

"""Sorts a dictionary according to length of value"""
def sort_list(districts):
    district_list = []
    sorted_keys = sorted(districts, key=lambda k: len(districts[k]), reverse=True)

    for key in sorted_keys:
        district_list.append({"district":key, "candidates":districts[key]})
    return district_list

"""Writes the list of districts:candidate_ids to a json file"""
def write_district_dict(year, candidates):
    district_dict = count_districts(candidates)
    sorted_list = sort_list(district_dict)
    with open(year+"_districts.json", "w") as writefile:
        writefile.write(json.dumps(sorted_list, indent=4))

"""API request for the candidate/{candidate_id}/totals"""
def request_candidate_totals(candidate_id):
    global api_key
    url = base + "candidate/" + candidate_id + "/totals/"
    url = url + "?per_page=20&sort=-cycle&page=1&designation=P&api_key=" + api_key
    data = json.loads(request_until_succeed(url))["results"]
    if data != []:
        return data[0]
    else:
        print("no totals")
        return None

"""Updates the key between the 4 in the environment so that 
requests aren't throttled"""
def update_key(num):
    global api_key
    index = num % 4
    api_key = os.environ.get('FEC_KEY_%s' %str(index), None)

"""Gets the totals from the candidates"""
def get_self_funds(candidates):
    print("-------------------------------------------------------------")
    print("Retrieving self contributions from candidates.")
    self_funders = []
    total_candidates = len(candidates)
    curr = 1
    global set_fields
    for candidate in candidates:
        update_key(curr)
        set_fields |= set(candidate.keys())
        print("candidate {} out of {}".format(str(curr), str(total_candidates)))
        totals = request_candidate_totals(candidate["candidate_id"])
        """Get totals"""
        if totals is not None:
            amount = totals["candidate_contribution"]
            set_fields |= set(totals.keys())
            candidate.update(totals)
            print(amount)
        
        self_funders.append(candidate)
        curr += 1

    return self_funders

"""Dumps list of districts/candidates to json"""
def read_districts():
    districts = []
    with open("data/2018_districts.json", "r") as readfile:
        districts = json.dumps(readfile.read())
    return districts

"""Opens the csv of candidates and outputs list"""
def get_candidates_csv(path):
    candidates = []
    with open(path, "r") as csvfile:
        candidates = [{k: v for k, v in row.items()} \
                for row in csv.DictReader(csvfile, skipinitialspace=True)]
    return candidates

"""Writes dictionary to path"""
def write_candidates_csv(candidates, path):
    keys = candidates[0].keys() 
    with open(path, "w") as csvfile:
        dict_writer = csv.DictWriter(csvfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(candidates)
    print("Wrote to %s." %path)

"""Writes candidates w totals to csv"""
def write_totals_csv(candidates_totals, path):
    with open(path, "w") as csvfile:
        dict_writer = csv.DictWriter(csvfile, list(set_fields))
        dict_writer.writeheader()
        dict_writer.writerows(candidates_totals)
    print("Wrote to %s." %path)

"""Candidates --> csv"""
def get_cands_only(year):
    candidates = get_candidates(year)
    write_candidates_csv(candidates, "data/{}_candidates.csv".format(year))

"""Candidates w totals --> csv"""
def get_totals(year):
    candidates = get_candidates(year)
    #Get self funds of candidates
    candidates_funds = get_self_funds(candidates)
    write_totals_csv(candidates_funds, "data/%s_totals.csv" %year)

"""District count --> csv"""
def get_districts(year):
    candidates = get_candidates(year)
    districts = count_districts_csv(candidates)
    write_candidates_csv(districts, "data/%s_districts.csv" %year)

if __name__ == '__main__':
    if year is None:
        print("Must specify election year.")
        sys.exit()
    elif totals:
        get_totals(year)
    elif districts:
        get_districts(year)
    else:
        get_cands_only(year)
