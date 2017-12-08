import argparse
import csv
import simplejson as json
import os

def get_info(last):
    with open("reelection_inside.csv", 'r') as csvfile:
        congress = list(csv.DictReader(csvfile))
        for member in congress:
            if member["str_nyt_lastname"] == last:
                return member
        
def print_info(last):
    member = get_info(last)
    print("\n{}'s seat is up for re-election in 2018. \n \nVulnerability (according to www.inside_elections.com): {}."\
          .format(last, member["inside_elections_vulnerability"]))

def main():
    parser = argparse.ArgumentParser(
        description="2018 gives information about competitive seats for the 2018 midterm elections.")
    parser.add_argument('--last_name', '-last', dest='last', type=str, default=None, help="Last name of congressman.")

    args = parser.parse_args()

    if args.last:
        print_info(args.last) 

if __name__ == '__main__':
    main()
