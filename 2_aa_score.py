# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 12:03:40 2019

@author: jurem

Flag each anticholinergic prescription as such and add a column with rating of anticholinergic activity.

The exported data frame RETAINS the following columns:
    - 'id': participant id
    - 'data_provider': 1 = England (Vision), 2 = Scotland, 3 = England (TPP), 4 = Wales
    - 'date': when the prescription was issued
    - 'prescription': full title of the prescription
    - 'quantity': quantity/strength of the prescribed drug, usually in mg
The following new columns are ADDED:
    - 'drug_present': was the drug present on the anticholinergic scale (1) or not (0)
    - 'aa': anticholinergic score of the drug based on the scale
    - 'drug_scale': the name of the drug as it appears in the scale
"""

import re
import pandas as pd





## Read in the files, and properly format.

meds = pd.read_csv('2_prescriptions_readv2_v2.csv', header=0, sep="|", dtype = str, encoding = 'cp1252')
# change all prescriptions to strings
meds['prescription'] = meds.prescription.astype(str)
# convert to lowercase
meds.loc[:,'prescription'] = meds['prescription'].str.lower()
#remove potential white-space from the front of prescription names
meds['prescription'] = meds.loc[:,'prescription'].apply(str.strip)

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

# create a column for the anticholinergic activity of the drug
meds['aa_ancelin'] = 0
meds['aa_boustani'] = 0
meds['aa_carnahan'] = 0
meds['aa_cancelli'] = 0
meds['aa_chew'] = 0
meds['aa_han'] = 0
meds['aa_rudolph'] = 0
meds['aa_ehrt'] = 0
meds['aa_sittironnarit'] = 0
meds['aa_briet'] = 0
meds['aa_bishara'] = 0
meds['aa_kiesel'] = 0
meds['aa_duran'] = 0
meds['scale_name'] = 'unknown' # drug name as listed on the anticholinergic scale (makes it easier later on, because it removes the dose, etc.)
drug_count = len(scales) # the count tracks the loop below
for drug in scales['drug']:
    print('Drugs left: ' + str(drug_count) + '\n' + 'Searching for ' + drug + '...')
    drug_finds = (meds.loc[meds['prescription'].str.contains(drug, na=False), 'prescription'].apply(lambda x: findDrug(x))) # find rows with drug
    drug_indices = (drug_finds[drug_finds==1]).index
    # look up the anticholinergic score in the dictionary
    if len(drug_indices)>0:
        if drug in ancelin_dict:
            meds.loc[drug_indices,'aa_ancelin'] += ancelin_dict[drug]
        if drug in boustani_dict:
            meds.loc[drug_indices,'aa_boustani'] += boustani_dict[drug]
        if drug in carnahan_dict:
            meds.loc[drug_indices,'aa_carnahan'] += carnahan_dict[drug]
        if drug in cancelli_dict:
            meds.loc[drug_indices,'aa_cancelli'] += cancelli_dict[drug]
        if drug in chew_dict:
            meds.loc[drug_indices,'aa_chew'] += chew_dict[drug]
        if drug in han_dict:
            meds.loc[drug_indices,'aa_han'] += han_dict[drug]
        if drug in rudolph_dict:
            meds.loc[drug_indices,'aa_rudolph'] += rudolph_dict[drug]
        if drug in ehrt_dict:
            meds.loc[drug_indices,'aa_ehrt'] += ehrt_dict[drug]
        if drug in sittironnarit_dict:
            meds.loc[drug_indices,'aa_sittironnarit'] += sittironnarit_dict[drug]
        if drug in briet_dict:
            meds.loc[drug_indices,'aa_briet'] += briet_dict[drug]
        if drug in bishara_dict:
            meds.loc[drug_indices,'aa_bishara'] += bishara_dict[drug]
        if drug in kiesel_dict:
            meds.loc[drug_indices,'aa_kiesel'] += kiesel_dict[drug]
        if drug in duran_dict:
            meds.loc[drug_indices,'aa_duran'] += duran_dict[drug]
        meds.loc[(meds.index.isin(drug_indices)) & (meds['scale_name']=='unknown'), 'scale_name'] = drug # add drug name as listed on the scale (do it only for prescriptions for which drug_scale=='unknown')
    drug_count -= 1 # update count




# for drug combinations that some scales assign aa-scores that are not just simple additions of the individual drugs
# (Han et al.: acetominophen/codeine, acetominophen/codeine/caffeine; Rudolph et al.: carbidopa/levodopa),
# assign prescriptions with those combinations, the score for the combination

# re-define the function without the '/' so that it identifies only combos of the two drugs in question and not additional ones
def findCombo(prescription):
    pattern = re.search(r'([^a-zA-Z]+|^)({0})([^a-zA-Z]+|$)'.format(drug), prescription)
    if pattern:
        return 1
    else: return 0

combos = ['paracetamol/codeine/caffeine', 'paracetamol/codeine', 'carbidopa/levodopa', 'diphenoxylate/atropine']
drug_count = len(combos) # the count tracks the loop below
for drug in combos:
    print('Drugs left: ' + str(drug_count) + '\n' + 'Searching for ' + drug + '...')
    drug_finds = (meds.loc[meds['prescription'].str.contains(drug, na=False), 'prescription'].apply(lambda x: findCombo(x))) # find rows with drug
    drug_indices = (drug_finds[drug_finds==1]).index
    # look up the anticholinergic score in the dictionary
    if len(drug_indices)>0:
        if drug in ancelin_dict:
            meds.loc[drug_indices,'aa_ancelin'] = ancelin_dict[drug]
        if drug in boustani_dict:
            meds.loc[drug_indices,'aa_boustani'] = boustani_dict[drug]
        if drug in carnahan_dict:
            meds.loc[drug_indices,'aa_carnahan'] = carnahan_dict[drug]
        if drug in cancelli_dict:
            meds.loc[drug_indices,'aa_cancelli'] = cancelli_dict[drug]
        if drug in chew_dict:
            meds.loc[drug_indices,'aa_chew'] = chew_dict[drug]
        if drug in han_dict:
            meds.loc[drug_indices,'aa_han'] = han_dict[drug]
        if drug in rudolph_dict:
            meds.loc[drug_indices,'aa_rudolph'] = rudolph_dict[drug]
        if drug in ehrt_dict:
            meds.loc[drug_indices,'aa_ehrt'] = ehrt_dict[drug]
        if drug in sittironnarit_dict:
            meds.loc[drug_indices,'aa_sittironnarit'] = sittironnarit_dict[drug]
        if drug in briet_dict:
            meds.loc[drug_indices,'aa_briet'] = briet_dict[drug]
        if drug in bishara_dict:
            meds.loc[drug_indices,'aa_bishara'] = bishara_dict[drug]        
        if drug in kiesel_dict:
            meds.loc[drug_indices,'aa_kiesel'] = kiesel_dict[drug]
        if drug in duran_dict:
            meds.loc[drug_indices,'aa_duran'] = duran_dict[drug]
        meds.loc[(meds.index.isin(drug_indices)) & (meds['scale_name']=='unknown'), 'scale_name'] = drug # add drug name as listed on the scale (do it only for prescriptions for which drug_scale=='unknown')
    drug_count -= 1 # update count




## Misc. cleaning

# flag the prescriptions with a potentially topical, ophthalmic, otic, or nasal administration route

# list with words that indicate "invalid" administration route
funky_administration = ['topical','ophthalmic','otic','nasal', 'nose drop', 'nose drops', 'cream', 'eye drp', 'eye susp', 'ear drop', \
                        'ear drops', 'oint', 'spray', 'gel', 'eye dro', ' dro ', 'paste', 'lotion', 'drops', 'neomycin', 'pyrilamine',
                        'ketorolac', 'betaxolol']
meds['admin_oral'] = '1'
for admin in funky_administration:
    print('Checking for "' + str(admin) + '"' + '...')
    meds.loc[meds['prescription'].str.contains(admin, regex=False, na=False), 'admin_oral'] = '0' # all non-orally and non-inhaled drugs

# export to .csv
prescriptions = meds.to_csv('3_aa_scales_v2.csv',index=False, header=True, sep='|')
