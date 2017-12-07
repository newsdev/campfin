import json
import os

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
from utils import request_until_succeed, unicode_decode

base = "https://api.open.fec.gov/v1/"
house = "H"
api_key = os.environ.get('FEC_KEY', None)

"""Returns list of candidates in given year"""
def get_candidates(year):
    election_request = "election_year=" + year
    api_request = "api_key=" + api_key
    page = 1
    has_next_page = True
    payload = []
    print("Fetching House candidates in year %s" %str(year))
    while has_next_page:
        url = base + "/candidates/?page={}&per_page=100&office=H&sort=name&".format(str(page)) \
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

def sort_list(districts):
    district_list = []
    sorted_keys = sorted(districts, key=lambda k: len(districts[k]), reverse=True)

    for key in sorted_keys:
        district_list.append({"district":key, "candidates":districts[key]})
    return district_list

def write_district_dict(year, candidates):
    district_dict = count_districts(candidates)
    sorted_list = sort_list(district_dict)
    with open(year+"_districts.json", "w") as writefile:
        writefile.write(json.dumps(sorted_list, indent=4))

def request_candidate_totals(candidate_id):
    url = base + "candidate/" + candidate_id + "/totals/"
    url = url + "?per_page=20&sort=-cycle&page=1&designation=P&api_key=" + api_key
    data = json.loads(request_until_succeed(url))["results"]
    if data != []:
        return data[0]
    else:
        return None

def get_self_funds(candidates):
    self_fund_dict = {}
    for candidate in candidates:
        totals = request_candidate_totals(candidate["candidate_id"])
        if totals is not None:
            amount = totals["candidate_contribution"]
            self_fund_dict[candidate["candidate_id"]] = amount

    return self_fund_dict

if __name__ == '__main__':
    candidates = get_candidates("2018")
    write_district_dict("2018", candidates)
    self_funds = get_self_funds(candidates)
    with open(year+"_self_fund.json", "w") as writefile:
        writefile.write(json.dumps(self_funds, indent=4))

        

