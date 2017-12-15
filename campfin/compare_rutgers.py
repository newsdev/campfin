import csv
import os

from get_candidates import get_candidates_csv

updated_female = []
updated_all = []

def compare(females, all):
    global updated_female
    global updated_all
    num_cands = len(all)
    num_female = len(females)

    females = sorted(females, key=lambda x:x['name'])
    all = sorted(all, key=lambda x:x['name'])
    count = 0 
    c_last = 0
    f_last = 0
    for c in range(c_last, num_cands):
        for f in range(f_last, num_female):
            if all[c]["name"].lower() == females[f]["name"].lower():
                count = count + 1
                c_last = c + 1
                f_last = f + 1
                all[c]["rutgers_sex"] = "F"
                females[f]["candidate_id"] = all[c]["candidate_id"]
                #females[f]["committee_id"] = all[c]["committee_id"]
                break
    updated_female = females
    updated_all = all
    print("Found %s candidates in common." %str(count))
                
def write_to_csv(list, headers, path):
    with open(path, "w") as csvfile:
        dict_writer = csv.DictWriter(csvfile, headers)
        dict_writer.writeheader()
        dict_writer.writerows(list)
    print("Wrote to %s ." %path)

if __name__ == '__main__':
    females = get_candidates_csv("data/2018_rutgers_12_13.csv")
    all = get_candidates_csv("data/2018_candidates_12_13_funds_all.csv")
    compare(females, all)

    all_headers = set(all[0].keys())
    all_headers.add("rutgers_sex")

    female_headers = set(females[0].keys())
    female_headers.add("candidate_id")
    #female_headers.add("committee_id")

    write_to_csv(updated_all, all_headers, "data/fec_gender_flag.csv")
    write_to_csv(updated_female, female_headers, "data/rutgers_fec_ids.csv")


