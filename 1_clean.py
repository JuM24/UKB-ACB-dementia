# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 12:02:08 2019

@author: jurem

The code below:
    1. Supplements the rows that are missing drug codes with codes from the Read_v2-reader.
    2. For drugs that were classified as anticholinergic by at least one scale (and for some other drugs) substitutes the brand names by generic drug names.
    3. Removes from the sample (a) participants that have opted out of the study, (b) rows without prescriptions, (c) rows without dates.

The columns retained in the exported data frame are:
    - 'id': participant id
    - 'data_provider': 1 = England (Vision), 2 = Scotland, 3 = England (TPP), 4 = Wales
    - 'date': when the prescription was issued
    - 'prescription': full title of the prescription
    - 'quantity': quantity/dose of the prescribed drug, usually in mg

"""

import re
import pandas as pd
import numpy as np



## Read in the data and prepare it.
meds = pd.read_csv('gp_scripts_python.csv', header=0, sep=",", dtype = str, encoding = 'cp1252')
meds.drop(['Unnamed: 0'], axis=1, inplace=True) # drop unnecessary column
meds.columns = ['id', 'data_provider', 'date', 'read_code', 'bnf', 'dmd', 'prescription', 'quantity'] # re-name the columns
meds.loc[:,'prescription'] = meds.loc[:,'prescription'].str.lower() # convert prescription names to lowercase

codes = pd.read_csv('read-codes.csv', sep=",", dtype = str, encoding = "cp1252") # read in the codes
codes.columns = ['code', 'drug', 'status_flag'] # re-name the columns
codes['code'] = codes.code.astype(str) # change codes to strings
codes['code'] = codes.loc[:,'code'].apply(str.strip) # remove leading and trailing white spaces from read-codes in the read-code data frame
meds.loc[meds['read_code'].isna(), 'read_code'] = 'unknown' # change NA values in read_code column into 'unknown'
meds['read_code'] = meds.loc[:,'read_code'].apply(str.strip) # remove white spaces from read-codes in the prescriptions data frame
codes = codes.drop_duplicates(subset = 'code') # drop duplicate rows




## Some read-codes contain two 0s at the end; remove those.
# helper function to remove the additional 0's in some read-codes
def remove_00(code):
    if (code != 'unknown') & (len(code)==7) & (code[-2:len(code)]=='00'): # do not change the 'unknown'-strings, change only those with two 0s at the end
        new_code = code[0:-2] # retain everything but the last two characters of the string
        return new_code
    else:
        return code

meds['read_code'] = meds['read_code'].apply(remove_00) # run the helper function to remove the 00s




## Use the read-code list to supplement the data frame.
# create a dictionary with read-code/drug-name pairs
read_code_dict = (codes.groupby('code')['drug'].apply(lambda x: x.tolist())).to_dict()
# the prescriptions are individual lists; transform them to strings
for key in read_code_dict.keys():
    read_code_dict[key] = ''.join(read_code_dict[key])

# helper code to fill read-codes into the 'meds' dataset
def find_read_code(code):
    try:
        read_code = read_code_dict[code]
    except: # if the code doesn't exist, flag as "unknown"
        read_code = 'unknown'
    return read_code

# create a column for read-code-supplemented information
meds['prescription_read'] = np.nan
# plug each read-code in our sample into the dictionary as a key and create an additional column from the values
meds['prescription_read'] = meds.loc[:,'read_code'].apply(lambda x: find_read_code(x))
#convert to lowercase
meds.loc[:,'prescription_read'] = meds.loc[:,'prescription_read'].str.lower()
# put read-code-supplied drugs into the drug column
meds.loc[meds['prescription'].isna(), 'prescription'] = (meds.loc[meds['prescription'].isna(), 'prescription_read']).copy()
# change 'unknown' in prescription column back to NaN
meds.loc[meds['prescription']=='unknown', 'prescription'] = np.nan





## Standardize drug names for all anticholinergic drugs based on BNF

# read in the file with alternative drug names
drug_names = pd.read_csv('alternative drug names_reformatted.csv', header=0, dtype = str, encoding = 'cp1252')
for col in drug_names:
    drug_names.loc[:, col] = drug_names[col].str.lower() # convert to lowercase
    drug_names.loc[~drug_names[col].isna(), col] = drug_names.loc[~drug_names[col].isna(), col].apply(str.strip) # remove potential left and right white spaces
drug_names = drug_names.drop_duplicates() # drop duplicates
drug_names = (drug_names.loc[~drug_names['generic'].isnull()]).copy()

# create dictionary with alternative-/brand- and generic drug names
name_dict = dict(zip(drug_names['brand'], drug_names['generic']))

# function to find the drug name
def findName(drug_name):
    # Regex: one of the characters in the bracket or start of string or space; drug name; one of the characters in the bracket or space or end of string
    pattern = re.search(r'([^a-zA-Z]+|^)({0})([^a-zA-Z]+|$)'.format(drug), drug_name)
    if pattern:
        return 1
    else: return 0

# create a temporary data frame to speed up search
temp_frame = meds['prescription'].to_frame()
temp_frame['prescription_new'] = 'NULL'
drug_count = len(name_dict) # the count tracks the loop below
for drug in name_dict:
    print('Substituting ' + drug + ' with ' + str(name_dict[drug]) + '...' + '\n' + 'Drugs left: ' + str(drug_count))
    name_finds = (temp_frame.loc[temp_frame['prescription'].str.contains(drug, na=False), 'prescription'].apply(lambda x: findName(x))) # find rows with drug (exact word match)
    name_indices = name_finds[name_finds==1]
    drug_count -= 1
    if len(name_indices)>0:
        temp_frame.loc[name_indices.index, 'prescription_new'] = (temp_frame.loc[name_indices.index, 'prescription'].str.replace(drug, name_dict[drug], regex=False)).copy() # replace the drug
        temp_frame.loc[name_indices.index, 'prescription_new'] = (temp_frame.loc[name_indices.index, 'prescription_new'].str.replace('ee', 'e')).copy() # in some subsitutions, a drug name gets replaced by a drug name that ends with an e (dicycloverin --> dicycloverine); this leads to an additional 'e' after subsitution (dicycloverine --> dicycloverinee)


# attach temporary frame as new prescription column
meds['prescription_new'] = (temp_frame['prescription_new']).copy()

# rename columns
meds = meds.rename(columns = {'prescription':'prescription_old', 'prescription_new':'prescription'})

# for the prescriptions that weren't changed: set them to the same value as the old prescriptions
meds.loc[meds['prescription']=='NULL', 'prescription'] = (meds['prescription_old']).copy()

# based on skimming through the data frame, some entries have to be manually altered
meds.loc[meds['prescription'].str.contains('patch', na=False), 'prescription'] = (meds.loc[meds['prescription'].str.contains('patch', na=False), 'prescription'].str.replace('hyoscine', 'hyoscine hydrobromide')).copy()
meds.loc[meds['prescription'].str.contains('300', na=False), 'prescription'] = (meds.loc[meds['prescription'].str.contains('300', na=False), 'prescription'].str.replace('hyoscine', 'hyoscine hydrobromide')).copy()
meds.loc[meds['prescription'].str.contains('400', na=False), 'prescription'] = (meds.loc[meds['prescription'].str.contains('400', na=False), 'prescription'].str.replace('hyoscine', 'hyoscine hydrobromide')).copy()
meds.loc[meds['prescription'].str.contains('600', na=False), 'prescription'] = (meds.loc[meds['prescription'].str.contains('600', na=False), 'prescription'].str.replace('hyoscine', 'hyoscine hydrobromide')).copy()




## Misc. cleaning
# remove participants that have opted outs
opt_out = pd.read_csv('participant opt-out.csv')
opt_out.columns = ['id']
meds['id'] = meds['id'].astype(str)
opt_out['id'] = opt_out['id'].astype(str)
meds = meds.loc[~meds['id'].isin(opt_out.id)] 
meds = meds.reset_index(drop=True)
# remove rows with blank prescription column
meds = meds.loc[meds['prescription'].notnull()]
# remove rows with blank/invalid date
meds = meds.loc[~meds['date'].isna(), :] 
invalid_dates = ["01/01/1901", "02/02/1902", "03/03/1903", "07/07/2037"]
meds = meds.loc[~meds['date'].isin(invalid_dates), :]
#remove unnecessary columns
meds.drop(['read_code','bnf','dmd','prescription_read'], axis=1, inplace=True)
# change all prescriptions to strings
meds['prescription'] = meds.prescription.astype(str)
# convert to lowercase
meds.loc[:,'prescription'] = meds['prescription'].str.lower()
#remove potential white-space from the front of prescription names
meds['prescription'] = meds.loc[:,'prescription'].apply(str.strip)
#remove all '|' characters, as it will be used as a column separator
meds['prescription'] = meds['prescription'].str.replace('|', ' ')

#export to .csv
prescriptions = meds.to_csv('2_prescriptions_readv2_v2.csv', index=False, header=True, sep='|')
