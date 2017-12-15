# congress-candidates-2018

## Setup

```mkirtualenv congress-candidates-2018
pip install -r requirements.txt
```

If running <campfin/get_candidates.py> with the <--totals> flag I recommend getting 4 API keys from https://api.open.fec.gov/developers/ to avoid throttling. 
After retrieving them, in <~/.bashrc>:

```
export FEC_KEY_0=<key>
export FEC_KEY_1=<key>
export FEC_KEY_2=<key>
export FEC_KEY_3=<key>
```

Syntax and num keys matters. See <update_key()> function in <campfin/get_candidates.py>

##Fetch data from FEC api
```
python campfin/get_candidates.py --year 2018 //Get csv of candidates who filed for 2018
python campfin/get_candidates.py --year 2018 --totals //Get csv of candidates with fund totals for 2018
python campfin/get_candidates.py --year 2018 --districts //Get csv of districts with FEC ids and candidate count for 2018
```

##Get Rutgers data
```
python campfin/rutgers.py //Gets Rutgers candidates into a csv. 
                             //Should look over to look at unicode errors or if name/party are conjoined from typos.
```
                             
##Compare FEC data with Rutgers data (list of females registered to run for 2018)
1. <python campfin/get_candidates.py --year 2018 --totals>
2. <python campfin/rutgers.py>
3. <python compare/compare_rutgers.py --rutgers data/2018_rutgers.csv --fec 2018_totals.csv>
This adds a <rutgers_sex> label to FEC totals in <fec_gender.csv> and
a <candidate_id> label to Rutgers candidates in <data/rutgers_fec_ids.csv>.
