# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 08:00:44 2021

@author: jurem

# Re-assign anticholinergic value to individual substances that were before in combination with other drugs.

"""

import re
import pandas as pd





## Read in the files, and properly format.

meds = pd.read_csv('4_aa_scales_dosage_v2.csv', header=0, sep="|", dtype = str, encoding = 'cp1252')
# change all prescriptions to strings
meds['prescription'] = meds.prescription.astype(str)
# convert to lowercase
meds.loc[:,'prescription'] = meds['prescription'].str.lower()
#remove potential white-space from the front of prescription names
meds['prescription'] = meds.loc[:,'prescription'].apply(str.strip)
# change type to float
meds['aa_count'] = meds['aa_count'].astype(float)

# read in aa-scales
scales = pd.read_csv('aas_combined.csv')
# remove duplicates
scales.drug.value_counts()
scales = scales[~scales.duplicated(['drug'])]

# separate into individual scales
ancelin = scales[['drug','aa_ancelin']]; ancelin = ancelin.loc[ancelin['aa_ancelin']!=0]
boustani = scales[['drug','aa_boustani']]; boustani = boustani.loc[boustani['aa_boustani']!=0]
carnahan = scales[['drug','aa_carnahan']]; carnahan = carnahan.loc[carnahan['aa_carnahan']!=0]
cancelli = scales[['drug','aa_cancelli']]; cancelli = cancelli.loc[cancelli['aa_cancelli']!=0]
chew = scales[['drug','aa_chew']]; chew = chew.loc[chew['aa_chew']!=0]
han = scales[['drug','aa_han']]; han = han.loc[han['aa_han']!=0]
rudolph = scales[['drug','aa_rudolph']]; rudolph = rudolph.loc[rudolph['aa_rudolph']!=0]
ehrt = scales[['drug','aa_ehrt']]; ehrt = ehrt.loc[ehrt['aa_ehrt']!=0]
sittironnarit = scales[['drug','aa_sittironnarit']]; sittironnarit = sittironnarit.loc[sittironnarit['aa_sittironnarit']!=0]
kiesel = scales[['drug','aa_kiesel']]; kiesel = kiesel.loc[kiesel['aa_kiesel']!=0]
duran = scales[['drug','aa_duran']]; duran = duran.loc[duran['aa_duran']!=0]
briet = scales[['drug','aa_briet']]; briet = briet.loc[briet['aa_briet']!=0]
bishara = scales[['drug','aa_bishara']]; bishara = bishara.loc[bishara['aa_bishara']!=0]




## Supplement the prescriptions with anticholinergic scores

# create dictionaries with drugs as keys and anticholinergic activity as values
ancelin_dict = dict(zip(ancelin['drug'], ancelin['aa_ancelin']))
boustani_dict = dict(zip(boustani['drug'], boustani['aa_boustani']))
carnahan_dict = dict(zip(carnahan['drug'], carnahan['aa_carnahan']))
cancelli_dict = dict(zip(cancelli['drug'], cancelli['aa_cancelli']))
chew_dict = dict(zip(chew['drug'], chew['aa_chew']))
han_dict = dict(zip(han['drug'], han['aa_han']))
rudolph_dict = dict(zip(rudolph['drug'], rudolph['aa_rudolph']))
ehrt_dict = dict(zip(ehrt['drug'], ehrt['aa_ehrt']))
sittironnarit_dict = dict(zip(sittironnarit['drug'], sittironnarit['aa_sittironnarit']))
kiesel_dict = dict(zip(kiesel['drug'], kiesel['aa_kiesel']))
duran_dict = dict(zip(duran['drug'], duran['aa_duran']))
briet_dict = dict(zip(briet['drug'], briet['aa_briet']))
bishara_dict = dict(zip(bishara['drug'], bishara['aa_bishara']))

# helper code for finding the exact drug name among the prescriptions
    # Regex for pattern: a character except one of those in the bracket or start of string; drug name; a character except one of those in the bracket or end of string
def findDrug(prescription):
    pattern = re.search(r'([^a-zA-Z]+|^)({0})([^a-zA-Z]+|$)'.format(drug), prescription)
    if pattern:
        return 1
    else: return 0

# separate ino data frame with those drugs that were previously combination drugs and those that weren't
combos = meds.loc[meds['aa_count'] > 1].copy()
non_combos = meds.loc[meds['aa_count'] == 1].copy()
other = meds.loc[meds['aa_count'].isnull()].copy()

# for drugs that were previously part of combination prescriptions, repeat the assignment of aa-value
combos['aa_ancelin'] = 0
combos['aa_boustani'] = 0
combos['aa_carnahan'] = 0
combos['aa_cancelli'] = 0
combos['aa_chew'] = 0
combos['aa_han'] = 0
combos['aa_rudolph'] = 0
combos['aa_ehrt'] = 0
combos['aa_sittironnarit'] = 0
combos['aa_briet'] = 0
combos['aa_bishara'] = 0
combos['aa_kiesel'] = 0
combos['aa_duran'] = 0
drug_count = len(scales) # the count tracks the loop below
for drug in scales['drug']:
    print('Drugs left: ' + str(drug_count) + '\n' + 'Searching for ' + drug + '...')
    drug_finds = (combos.loc[:, 'aa_name'] == drug) # find rows with drug
    drug_indices = (drug_finds[drug_finds==1]).index
    # look up the anticholinergic score in the dictionary
    if len(drug_indices)>0:
        if drug in ancelin_dict:
            combos.loc[drug_indices,'aa_ancelin'] += ancelin_dict[drug]
        if drug in boustani_dict:
            combos.loc[drug_indices,'aa_boustani'] += boustani_dict[drug]
        if drug in carnahan_dict:
            combos.loc[drug_indices,'aa_carnahan'] += carnahan_dict[drug]
        if drug in cancelli_dict:
            combos.loc[drug_indices,'aa_cancelli'] += cancelli_dict[drug]
        if drug in chew_dict:
            combos.loc[drug_indices,'aa_chew'] += chew_dict[drug]
        if drug in han_dict:
            combos.loc[drug_indices,'aa_han'] += han_dict[drug]
        if drug in rudolph_dict:
            combos.loc[drug_indices,'aa_rudolph'] += rudolph_dict[drug]
        if drug in ehrt_dict:
            combos.loc[drug_indices,'aa_ehrt'] += ehrt_dict[drug]
        if drug in sittironnarit_dict:
            combos.loc[drug_indices,'aa_sittironnarit'] += sittironnarit_dict[drug]
        if drug in briet_dict:
            combos.loc[drug_indices,'aa_briet'] += briet_dict[drug]
        if drug in bishara_dict:
            combos.loc[drug_indices,'aa_bishara'] += bishara_dict[drug]
        if drug in kiesel_dict:
            combos.loc[drug_indices,'aa_kiesel'] += kiesel_dict[drug]
        if drug in duran_dict:
            combos.loc[drug_indices,'aa_duran'] += duran_dict[drug]
    drug_count -= 1 # update count


# export to .csv
for col in ['aa_ancelin', 'aa_boustani', 'aa_carnahan', 'aa_cancelli', 'aa_chew', 'aa_han',
            'aa_rudolph', 'aa_ehrt', 'aa_sittironnarit', 'aa_briet', 'aa_bishara', 'aa_kiesel',
            'aa_duran']:
    non_combos[col] = non_combos[col].astype(float)
    other[col] = other[col].astype(float)
meds = (pd.concat([combos, non_combos, other]))
prescriptions = meds.to_csv('5_aa_scales_dosage_v2.csv',index=False, header=True, sep='|')