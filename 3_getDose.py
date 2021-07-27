# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 11:02:14 2020

@author: jurem
"""

### Prepare environment and load the data.

import pandas as pd
import re
import numpy as np


# data frame prescriptions
meds = pd.read_csv('3_aa_scales_v2.csv', header=0, dtype = str, encoding = 'cp1252', sep='|')

# change data types
for col in ['aa_ancelin', 'aa_boustani', 'aa_carnahan', 'aa_cancelli', 'aa_chew', 'aa_han',
            'aa_rudolph', 'aa_ehrt', 'aa_sittironnarit', 'aa_briet', 'aa_bishara', 'aa_kiesel',
            'aa_duran']:
    meds[col] = meds[col].astype(float)


# divide into anticholinergic drugs and non-anticholinergics
meds_non_aa = meds.loc[meds['scale_name'] == 'unknown']
meds = meds.loc[meds['scale_name'] != 'unknown']

# select only valid administration routes
meds_non_oral = (meds.loc[meds['admin_oral'] == '0']).copy() 
meds = (meds.loc[meds['admin_oral'] == '1']).copy()

# data frame listing anticholinergic drugs that were found in the sample
drug_list = pd.read_csv('drug_list.csv', header=0, dtype = str, encoding = 'cp1252')









### A. drug concentration 



## A1. find the numbers associated with concentrations (mg, milligram, microgram, ug, mg/ml, etc.)

# create a data frame that for each dosage found in the "prescription" column, adds a new column (dose_a1, etc.)
# regex: digit or dot (1 or more times); whitespace (0 or more times); one of the words in the brackets)
temp_1 = (meds['prescription'].str.extractall(r'([\d\.]+\s*(milligram|mg|gram[^a-zA-Z]*$|g[^a-zA-Z]*$|microgram|mcg))')).unstack() # "extractall" returns a new row for every find, even if there are several finds in one prescription; hence unstack()
temp_1.columns = ['dose_a1','dose_a2','dose_a3','dose_a4','blank_1','blank_2','blank_3','blank_4'] # blanks are due to two capture groups in the regex above
meds = meds.join(temp_1) # merge with the main data frame
meds = meds.drop(['blank_1','blank_2','blank_3','blank_4'], axis=1) # drop the additional columns

# some prescriptions have dosage data in the "quantity" column, so for those rows that have not yet been assigned a dose, search for it in "quantity"
temp_2 = (meds.loc[meds['dose_a1'].isnull(), 'quantity'].str.extractall(r'([\d\.]+\s*(milligram|mg|gram[^a-zA-Z]*$|g[^a-zA-Z]*$|microgram|mcg))')).unstack()
temp_2.columns = ['dose_b1','dose_b2','dose_b3','blank_1','blank_2','blank_3']
temp_2['from_quantity'] = 1 # additional column that indicates whether the dose was extracted from the 'quantity' column (it will help with data cleaning later)
meds = meds.join(temp_2)
meds.loc[meds['from_quantity'].isnull(), 'from_quantity'] = 0 # label those rows that did not get the dose extracted from the 'quantity' column with 0
meds = meds.drop(['blank_1','blank_2','blank_3'], axis=1)
# for those that have no dosage info in "prescription", add from "quantity"
meds.loc[meds['dose_a1'].isnull(), 'dose_a1'] = (meds.loc[meds['dose_a1'].isnull(), 'dose_b1']).copy()
meds.loc[meds['dose_a2'].isnull(), 'dose_a2'] = (meds.loc[meds['dose_a2'].isnull(), 'dose_b2']).copy()
meds.loc[meds['dose_a3'].isnull(), 'dose_a3'] = (meds.loc[meds['dose_a3'].isnull(), 'dose_b3']).copy()
meds.drop(['dose_b1','dose_b2','dose_b3'], axis=1, inplace=True)
# delete unnecessary variables
del temp_1
del temp_2


## A2. convert all concentrations to mg

# for each medicine in a prescription, create a new column with the number in mg
# subset only those rows that contain the word you're looking for (e.g. 'milligram'), then extract only the number associated with it (regex: digit or dot (1 or more times))

# originally in mg
meds.loc[((meds['dose_a1'].str.contains('milligram', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1_number'] = \
    ((meds.loc[((meds['dose_a1'].str.contains('milligram', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()
meds.loc[((meds['dose_a2'].str.contains('milligram', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2_number'] = \
    ((meds.loc[((meds['dose_a2'].str.contains('milligram', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()
meds.loc[((meds['dose_a3'].str.contains('milligram', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3_number'] = \
    ((meds.loc[((meds['dose_a3'].str.contains('milligram', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()
meds.loc[((meds['dose_a4'].str.contains('milligram', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4_number'] = \
    ((meds.loc[((meds['dose_a4'].str.contains('milligram', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()

meds.loc[((meds['dose_a1'].str.contains('mg', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1_number'] = \
    ((meds.loc[((meds['dose_a1'].str.contains('mg', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()
meds.loc[((meds['dose_a2'].str.contains('mg', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2_number'] = \
    ((meds.loc[((meds['dose_a2'].str.contains('mg', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()
meds.loc[((meds['dose_a3'].str.contains('mg', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3_number'] = \
    ((meds.loc[((meds['dose_a3'].str.contains('mg', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()
meds.loc[((meds['dose_a4'].str.contains('mg', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4_number'] = \
    ((meds.loc[((meds['dose_a4'].str.contains('mg', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy()

# originally in μg 
meds.loc[((meds['dose_a1'].str.contains('microgram', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1_number'] = \
    ((meds.loc[((meds['dose_a1'].str.contains('microgram', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
meds.loc[((meds['dose_a2'].str.contains('microgram', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2_number'] = \
    ((meds.loc[((meds['dose_a2'].str.contains('microgram', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
meds.loc[((meds['dose_a3'].str.contains('microgram', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3_number'] = \
    ((meds.loc[((meds['dose_a3'].str.contains('microgram', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
meds.loc[((meds['dose_a4'].str.contains('microgram', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4_number'] = \
    ((meds.loc[((meds['dose_a4'].str.contains('microgram', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001

meds.loc[((meds['dose_a1'].str.contains('mcg', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1_number'] = \
    ((meds.loc[((meds['dose_a1'].str.contains('mcg', regex=False)) & (~meds['dose_a1'].isnull())), 'dose_a1'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
meds.loc[((meds['dose_a2'].str.contains('mcg', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2_number'] = \
    ((meds.loc[((meds['dose_a2'].str.contains('mcg', regex=False)) & (~meds['dose_a2'].isnull())), 'dose_a2'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
meds.loc[((meds['dose_a3'].str.contains('mcg', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3_number'] = \
    ((meds.loc[((meds['dose_a3'].str.contains('mcg', regex=False)) & (~meds['dose_a3'].isnull())), 'dose_a3'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
meds.loc[((meds['dose_a4'].str.contains('mcg', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4_number'] = \
    ((meds.loc[((meds['dose_a4'].str.contains('mcg', regex=False)) & (~meds['dose_a4'].isnull())), 'dose_a4'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 0.001
    
# originally in g (because 'gram' and 'g' are sub-string within other doses - e.g., microgram - we have to use regex)
meds.loc[((meds['dose_a1'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a1'].isnull())), 'dose_a1_number'] = \
    ((meds.loc[((meds['dose_a1'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a1'].isnull())), 'dose_a1'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000
meds.loc[((meds['dose_a2'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a2'].isnull())), 'dose_a2_number'] = \
    ((meds.loc[((meds['dose_a2'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a2'].isnull())), 'dose_a2'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000
meds.loc[((meds['dose_a3'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a3'].isnull())), 'dose_a3_number'] = \
    ((meds.loc[((meds['dose_a3'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a3'].isnull())), 'dose_a3'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000
meds.loc[((meds['dose_a4'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a4'].isnull())), 'dose_a4_number'] = \
    ((meds.loc[((meds['dose_a4'].str.contains(r'[\d\.]+\s*gram', regex=True)) & (~meds['dose_a4'].isnull())), 'dose_a4'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000

# non-word and end of string after 'g'
meds.loc[((meds['dose_a1'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a1'].isnull())), 'dose_a1_number'] = \
    ((meds.loc[((meds['dose_a1'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a1'].isnull())), 'dose_a1'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000
meds.loc[((meds['dose_a2'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a2'].isnull())), 'dose_a2_number'] = \
    ((meds.loc[((meds['dose_a2'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a2'].isnull())), 'dose_a2'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000
meds.loc[((meds['dose_a3'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a3'].isnull())), 'dose_a3_number'] = \
    ((meds.loc[((meds['dose_a3'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a3'].isnull())), 'dose_a3'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000
meds.loc[((meds['dose_a4'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a4'].isnull())), 'dose_a4_number'] = \
    ((meds.loc[((meds['dose_a4'].str.contains(r'[\d\.]+\s*g\W*$', regex=True)) & (~meds['dose_a4'].isnull())), 'dose_a4'].str.extract(r'([\d\.]+)')).iloc[:,0].astype(float)).copy() * 1000



#####    OPTIONAL    #####

## Identification of null-value rows

# This part checks null values for dosage for each drug to manually supplement later.
# For each drug, it indicates whether there are any rows without assigned dosage.
# If that is the case for a given drug, (manually) add it to the 'NA_n' column of the drug_list; it will be checked and corrected later (as part of the 'meds_lost' data frame)

#drugs_left = len(drug_list.drug.tolist()) # list of all drugs
#drug_dict = {} # drugs as keys, number of null values in dosage column as values
#for drug in drug_list.drug.tolist():
    # look up the rows with the drug in the data frame
    #temp = meds.loc[meds['prescription'].str.contains(r'([^a-zA-Z]+|^)' + drug, regex=True)]
    # check the number of null values and add to the dictionary
    #drug_dict[drug] = len(temp.loc[temp['dose_a1_number'].isnull()])
    #drugs_left -= 1 # counter to soothe my inpatience
    #print('Drugs left: ' + str(drugs_left))
    #drug_list.loc[drug_list['drug'] == drug, 'NA_n'] = drug_dict[drug]

# record the number of NA's in the data frame with drugs
#for drug in drug_list.drug.tolist():
    #drug_list.loc[drug_list['drug'] == drug, 'NA_n'] = drug_dict[drug]


## Identification of non-straightforward doses

# This part is done manually, below is the example of the procedure for alimemazine.
# For every anticholinergic, subset a data frame with only that drug; then check (1) whether the dose assigned to the drugs makes sense and
# conforms to the BNF and (2) why some rows didn't get assigned any dose.
# Note the observations and use them to manually correct the problems after running the below algorithm.

#example = meds.loc[meds['prescription'].str.contains(r'([^a-zA-Z]+|^)(sertindole)', regex=True)]
#nulls = (example.loc[example['dose_a1_number'].isnull(), 'prescription']).value_counts()
#example.dose_a1_number.value_counts()


## A3. Automatically assign the dose.

# subset the data frame to include only rows for which dosage was found (also manually add it as 'dose_1st' row to the drug_list file)
meds_found = (meds.loc[~meds['dose_a1'].isnull()]).copy()
meds_found.loc[:, 'aa_name'] = np.nan # column with the name of the drug
meds_found.loc[:, 'dose'] = np.nan # column with dose
meds_found.loc[:, 'dose_units'] = 'mg' # column with dose units (mg, mg/ml, mg/5ml, etc.)
meds_found.loc[:, 'aa_count'] = 0 # column for the number of anticholinergics in the prescription (if more than 1, we will need to separate them later)
# subset the data frame to include only rows for which dosage was NOT found (the code below deals separately with (1. meds_found) incorrectly assigned dose and (2. meds_lost) missing dose, and then merges the data frames)
meds_lost = (meds.loc[meds['dose_a1'].isnull()]).copy() 
meds_lost.loc[:, 'aa_name'] = np.nan
meds_lost.loc[:, 'dose'] = np.nan # column with dose
meds_lost.loc[:, 'dose_units'] = 'mg' # the default unit is mg
meds_lost.loc[:, 'aa_count'] = 0
# for drugs that have the correct milligram dosage in the first dose column (based on manual checking; see 'dose_1st' column of 'drug_list.csv'), just use that column as dose
drugs = (pd.read_csv('aas_combined.csv', header=0, dtype = str, encoding = 'cp1252')).drug.tolist() # list of all anticholinergic drugs
drugs_left = len(drugs) # for counter
drug_combos = [] # list with drugs that appear in combination with other drugs on the list and need to be manually checked later (because they might complicate the DDD calculation)
for drug in drugs:
    print('Drugs left: ' + str(drugs_left) + '. Working on ' + drug + '.')
    # to rows that contain the drug and have been already named, increase the aa_count
    change = sum(meds_found['aa_count']) + sum(meds_lost['aa_count']) # to check whether it is a combo drug (see below)
    meds_found.loc[(meds_found['prescription'].str.contains(r'([^a-zA-Z]+|^)' + drug, regex=True)) & (~meds_found['aa_name'].isnull()), 'aa_count'] += 1            
    meds_lost.loc[(meds_lost['prescription'].str.contains(r'([^a-zA-Z]+|^)' + drug, regex=True)) & (~meds_lost['aa_name'].isnull()), 'aa_count'] += 1            
    if (sum(meds_found['aa_count']) + sum(meds_lost['aa_count'])) != change: # this checks if the two lines of code above changed anything (if yes, the drug was already named on some rows and thus occurrs in combination with another anticholinergic)
        drug_combos.append(drug)
    # to rows that contain the drug and that have not been named yet, give the name (for the ones where dose was found, assign the latter)
    meds_found.loc[(meds_found['prescription'].str.contains(r'([^a-zA-Z]+|^)' + drug, regex=True)) & (meds_found['aa_name'].isnull()), 'aa_name'] = drug            
    meds_lost.loc[(meds_lost['prescription'].str.contains(r'([^a-zA-Z]+|^)' + drug, regex=True)) & (meds_lost['aa_name'].isnull()), 'aa_name'] = drug            
    meds_found.loc[meds_found['aa_name'] == drug, 'dose'] = (meds_found.loc[meds_found['aa_name'] == drug, 'dose_a1_number']).copy()     
    meds_found.loc[meds_found['aa_name'] == drug, 'aa_count'] = 1 # set the aa_count to 1 (the default for all rows with only one anticholinergic)  
    meds_lost.loc[meds_lost['aa_name'] == drug, 'aa_count'] = 1    
    # update counter
    drugs_left -= 1




## A4. Manually correct the dose/units that do not fit to the straigthorward pattern above (i.e., where the dose for some reason does not correspond to 'dose_a1_number').

# set as floats
meds_found.loc[:, ['dose_a1_number', 'dose_a2_number', 'dose_a3_number', 'dose_a4_number']] = meds_found.loc[:, ['dose_a1_number', 'dose_a2_number', 'dose_a3_number', 'dose_a4_number']].astype(float)
meds_lost.loc[:, ['dose_a1_number', 'dose_a2_number', 'dose_a3_number', 'dose_a4_number']] = meds_lost.loc[:, ['dose_a1_number', 'dose_a2_number', 'dose_a3_number', 'dose_a4_number']].astype(float)

# aminophylline; NA: 225
drug = 'aminophylline'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('225')), 'dose'] = 225

# azathioprine; NA: 50 is mg
drug = 'azathioprine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# bromocriptine; NA: 1,2.5
drug = 'bromocriptine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5

# carbamazepine; NA: 100,200,400
drug = 'carbamazepine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')) & (meds_lost['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('400')), 'dose'] = 400

# chlordiazepoxide; NA: 10,25
drug = 'chlordiazepoxide'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 125

# colchicine; NA:500 is 0.5
drug = 'colchicine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 0.5

# famotidine; NA:40mg
drug = 'famotidine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('40')), 'dose'] = 40

# fexofenadine; NA:120,180
drug = 'fexofenadine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('120')), 'dose'] = 120
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('180')), 'dose'] = 180

# flavoxate; NA:200,100
drug = 'flavoxate'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# flunitrazepame; NA:1
drug = 'flunitrazepame'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1

# fluvoxamine; NA:50,100
drug = 'fluvoxamine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# isosorbide; NA:60,25,40,50,10
drug = 'isosorbide'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('60')), 'dose'] = 60
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('40')), 'dose'] = 40
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10

# methocarbamol; NA:0.75
drug = 'methocarbamol'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('0.75')), 'dose'] = 0.75

# naratriptan; NA:all 2.5
drug = 'naratriptan'
meds_lost.loc[(meds_lost['aa_name'] == drug), 'dose'] = 2.5

# nefazodone; NA:200,100
drug = 'nefazodone'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# nizatidine; NA:150,300
drug = 'nizatidine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('150')), 'dose'] = 150
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 300

# oxazepam; NA:10,15,30
drug = 'oxazepam'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('15')), 'dose'] = 15
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('30')), 'dose'] = 30

# tiotropium; NA:0.018
drug = 'tiotropium'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('0.018')), 'dose'] = 0.018

# trimipramine; NA:10,25,50
drug = 'trimipramine'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# alimemazine (30 and 7.5 are mg/5ml; 10 is mg)
drug = 'alimemazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 7.5), 'dose_units'] = 'mg/5ml'
    
# alverine (remove >120mg); NA: 60,120
drug = 'alverine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 120), 'dose_units'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 120), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('120')), 'dose'] = 120
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('60')), 'dose'] = 60
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('120')), 'dose'] = 120
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('120')), 'dose_units'] = 'mg'

# amantadine (100 is mg, 50 is mg/5ml); NA: 100
drug = 'amantadine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# amitriptyline 10,25,50 are mg or mg/5ml; when 1st is 2, use 2nd column
drug = 'amitriptyline'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_a2_number']).copy()

# amoxicillin 250 is mg or mg/5ml; NA: 250/number or 125/250 is 250, 500 is mg 
drug = 'amoxicillin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 250) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'

# ampicillin (125 is only mg/5ml, 250 is both mg and mg/5ml); NA: 100,250,500
drug = 'ampicillin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 125), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 250) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')), 'dose'] = 250
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 500

# aripiprazole (1mg/ml only, others are mg)
drug = 'aripiprazole'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_units'] = 'mg/1ml'

# atenolol (25 is both mg and mg/5ml; sometimes 1st, sometimes 2nd column); 12.5,50,100 are ok; 20 (is nifedipine) is 50; 2nd column when 2nd column is 12.5
drug = 'atenolol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['dose_a2_number'] == 20), 'dose'] = 50
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 12.5), 'dose'] = 12.5

# azatadine (0.5 is per 5ml, 1 is ok)
drug = 'azatadine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5), 'dose_units'] = 'mg/1ml'

# baclofen (remove 60); 5 may be mg/5ml
drug = 'baclofen'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 60), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'

# benztropine also has 5% and 2.5% eye drops
drug = 'benztropine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('%')), 'dose'] = np.nan

# betaxolol 0.25% and 0.5% eye drops
drug = 'betaxolol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('%')), 'dose'] = np.nan

# bisacodyl 2.74mg/ml rectal solution; NA: 5,10
drug = 'bisacodyl'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.74), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10

# brompheniramine 30 is 4/5mg/ml, 2 is mg/5ml; NA:2mg/5ml,12mg
drug = 'brompheniramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30), 'dose'] = 4
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_units'] = 'mg/5ml'

# buclizine keep only 3rd column; NA: pink=6.25 
drug = 'buclizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a3_number'].isnull()), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a3_number'].isnull()), 'dose_a3_number']).copy()

# cefalexin 125/5 is mg/ml, 250, 500 are mg; NA: 250,500
drug = 'cefalexin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 125), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')), 'dose'] = 250
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 500

# cetirizine 1 is mg/1ml, 5 is mg/5ml, 42000 and 84000 are creams; NA: 10
drug = 'cetirizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 40000), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 40000), 'dose_units'] = np.nan
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10

# chloroquine if 250 in second column, use second column; NA: 250,200,300
drug = 'chloroquine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 250), 'dose'] = 250
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')), 'dose'] = 250
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 300

# chlorpromazine when 20mg and ml in title, it refers to 5/1, 100 is mg or mg/5ml, to 20/1; NA: 100,10,50
drug = 'chlorpromazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/4ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# ciclosporin 14000,7000,3500,1000 are eye ointments; 100 is mg or mg/ml; NA:100
drug = 'ciclosporin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] >= 1000), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] >= 1000), 'dose_units'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 100

# cimetidine 250mg is 100/5 mg/ml suspension; 200 can be mg or mg/5ml; NA:200,400,800
drug = 'cimetidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 250), 'dose'] = 100
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 250), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('400')), 'dose'] = 400
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('800')), 'dose'] = 800

# citalopram those that contain ml are 40mg/ml or mg; NA: 10,20
drug = 'citalopram'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 40) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('20')), 'dose'] = 20

# clemastine 0.5 is mg/5ml; NA:1
drug = 'clemastine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1

# clindamycin 10 is mg/ml, 75 is mg or mg/5ml, 150 is mg or mg/ml, 300 is mg, 1000 is 2% cream, 25000 is 1% gel, 30000 is 1%, 40000 is 2% cream, 50000 is 1% gel, 60000 is 1% gel, 80000 is 2% cream, 9000 is 1% gel, 10000 is 1% gel, 150000 is 1% gel, then several others have blank 1st column but are % gels/solutions/creams; NA:150 
drug = 'clindamycin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 75) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 150) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 1000), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 1000), 'dose_units'] = np.nan
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('150')), 'dose'] = 150

# clonazepam 0.5 is mg, 0.25 is mg/5ml, 1 is mg/ml, 2 is mg; NA:500 is 0.5
drug = 'clonazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 0.5

# desloratadine 0.5 and 2.5 are 0.5/1, 5 is mg; NA:10
drug = 'desloratadine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10

# dexamethasone 3.3.,3.8,4,5 mg/ml, 6.6,8 mg/2ml, 20mg/5ml; 0.5 and 2 are mg or mg/5ml
drug = 'dexamethasone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 3.3), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 3.8), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 4.5), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 6.6), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 6.8), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 4) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'

# dextromethorphan 7.33 is mg, 7.5, 10 are mg/5ml, 15 is mg/ml; when there is a 2nd column, use that one
drug = 'dextromethorphan'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 7.5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose_a2_number']).copy()

# diazepam 1 is mg/5ml, 2.5 is mg/5ml or mg, 2 is mg or mg/5ml, 5 is mg or 5mg/2.5ml, 10 is mg or 10mg/2.5ml; NA:2,5mg
drug = 'diazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2.5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5

# dicycloverine 10 is mg or 10/5 mg/ml; NA:10,20mg
drug = 'dicycloverine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('20')), 'dose'] = 20

# digoxin 0.05 is mg/ml, all else is mg; NA: 125 is 0.125, 250 is 0.250
drug = 'digoxin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.05), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('125')), 'dose'] = 0.125
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')), 'dose'] = 0.25

# diltiazem 60 is mg or mg/5ml; NA:200,300,90,120,180,60 
drug = 'diltiazem'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 60) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 300
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('90')), 'dose'] = 90
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('120')), 'dose'] = 120
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('180')), 'dose'] = 180
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('60')), 'dose'] = 60

# dimenhydrinate is always 40; NA:40
drug = 'dimenhydrinate'
meds_found.loc[(meds_found['aa_name'] == drug), 'dose'] = 40
meds_lost.loc[(meds_lost['aa_name'] == drug), 'dose'] = 40

# dipyridamole 50 is mg/5ml, others are mg; NA:100mg
drug = 'dipyridamole'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# domperidone 1 and 5 is 1mg/ml and 5mg/5ml, else is mg; 500 is 10; NA: 10mg, 30,1,5
drug = 'domperidone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose_units'] = 'mg'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('30')), 'dose'] = 30
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose_units'] = 'mg/5ml'

# dosulepin delete greater than 80; NA:25,75
drug = 'dosulepin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 80), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 80), 'dose_units'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_lost['prescription'].str.contains('75')) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'

meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('75')), 'dose'] = 75

# doxepine >75 is 5% cream, all else is mg
drug = 'doxepine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 75), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 75), 'dose_units'] = np.nan

# escitalopram 20 may be mg or mg/ml
drug = 'escitalopram'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'

# fluoxetine 20 may be mg or mg/5ml; NA:20
drug = 'fluoxetine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('20')), 'dose'] = 20

# gentamicin is only mg/ml (20/2ml, 40/1ml, 80/2ml) or cream/ointment; remove values >80
drug = 'gentamicin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 40), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 80), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 80), 'dose_units'] = np.nan

# glycopyrronium only mg/ml: (0.2/1, 0.6/3, 0.5/5, 1/5, 2/5); when 0.085 choose second column; over 2 is bogus
drug = 'glycopyrronium'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.6), 'dose_units'] = 'mg/3ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.085), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.085), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 2), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 2), 'dose_units'] = np.nan

# guaifenesin only  mg/ml: (7.5/5, 50/5, 66.67/5, 100/5)
drug = 'guaifenesin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 7.5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 66.67), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/5ml'

# haloperidol: 0.5mg, 1mg/ml, 1.5mg, 2mg/ml, 5mg or 5mg/ml, 10mg, 20mg, 50mg/ml, 100mg/ml; NA:500 is 0.5,5,20
drug = 'haloperidol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 0.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('20')), 'dose'] = 20

# hydrocortisone 10mg or 10mg/5ml, 5mg, 2.5mg, 20mg, 25mg/1ml, 100mg/1ml, all else are creams and ointments
drug = 'hydrocortisone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/1ml'

# hydroxyzine 10 can be mg or mg/5ml; NA:10,25
drug = 'hydroxyzine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25

# hyoscine butylbromide 10mg or 10mg/5ml, 20mg/1ml; NA:10
drug = 'hyoscine butylbromide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10

# hyoscine hydrobromide 1 and 1.5 is cream, 0.3mg, 0.4mg/ml, 0.15mg, 0.6mg/ml; NA:300 is 0.3
drug = 'hyoscine hydrobromide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.4) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.6) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 0.3

# imipramine 25 can be mg or 25mg/5ml, 10 is mg; remove >25; NA:25
drug = 'imipramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 25), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 25), 'dose_units'] = np.nan
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25

# ipratropium when with salbutamol, always choose smaller column; 0.25mg/ml, 0.5/2ml or 0.5/1ml; 2.5 to 0.5mg/2ml; NA:boehringer is 0.2mg/1ml; if with salbutamol then 0.2mg/1ml
drug = 'ipratropium'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('salbutamol')), 'dose'] = 0.2
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('salbutamol')), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.25), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5) & (meds_found['prescription'].str.contains('2ml')), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5) & (meds_found['prescription'].str.contains('1ml')), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose'] = 0.5
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose_units'] = 'mg/2ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('salbutamol')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('salbutamol')), 'dose_units'] = 'mg/1ml'

# ketamine 50mg/5ml, 100mg/5ml, 200mg/20ml, 500mg/10ml, 1000mg/10ml; NA:1 is 1/10ml
drug = 'ketamine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200), 'dose_units'] = 'mg/20ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500), 'dose_units'] = 'mg/10ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1000), 'dose_units'] = 'mg/10ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose_units'] = 'mg/10ml'

# ketorolac 10 is mg or mg/ml, 30 is mg/ml
drug = 'ketorolac'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30), 'dose_units'] = 'mg/1ml'

# ketotifen 0.25mg/ml, 1 mg
drug = 'ketotifen'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'

# levofloxacin 5 is 5mg/ml, 500mg/100ml or 500mg
drug = 'levofloxacin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/100ml'

# levomepromazine 25mg/ml or mg; 2.5 is 25mg/ml; NA:25mg
drug = 'levomepromazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose'] = 25
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25

# lithium 520 is invalid; NA:400,250,200
drug = 'lithium'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 520), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 520), 'dose_units'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('ml', na=False)), 'dose'] = 520
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('ml', na=False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('400')), 'dose'] = 400
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')), 'dose'] = 250
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200

# lofepramine is 70mg or mg/5ml; NA:70
drug = 'lofepramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 70) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('70')), 'dose'] = 70

# loperamide 125 is 2; 0.2 is mg/ml, 1 is mg/5ml; NA:2mg when with simeticone, 2(mg)
drug = 'loperamide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 125), 'dose'] = 2
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.2), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2')), 'dose'] = 2
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('simeticone')), 'dose'] = 2

# loratadine 5 is 5mg/5ml
drug = 'loratadine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/5ml'

# lorazepam 4mg/1ml, 0.5/5ml, 1mg/5ml or mg; NA:1,2.5
drug = 'lorazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 4) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5

# metformin mg/ml: 500/5, 100/1; for 1,2,2.5,4,5,12.5,15,50 use 2nd column; NA:500,850; 850 when with pioglitazone
drug = 'metformin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 4), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 4), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('rosiglitazone')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('vildagliptin')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('linagliptin')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('alogliptin')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('dapagliflozin')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('canagliflozin')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('empagliflozin')), 'dose'] = 1000
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('saxagliptin')), 'dose'] = 1000
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 500
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('850')), 'dose'] = 850
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('pioglitazone')), 'dose'] = 850

# methylprednisolone 80/2; 40/1; 120/3; 10 is 40/1; delete over 120; NA:if with lidocaine, it's 40/1
drug = 'methylprednisolone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 80), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 40), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 120), 'dose_units'] = 'mg/3ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose'] = 40
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 120), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 120), 'dose_units'] = np.nan
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('lidocaine')), 'dose'] = 40
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('lidocaine')), 'dose_units'] = 'mg/1ml'

# metoprolol 5 is mg/5ml; 12.5 is 100; NA:50
drug = 'metoprolol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# midazolam 10/2, 2/2, 5/5, 7.5/1.5, 50/10, 2.5/0.5
drug = 'midazolam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 7.5), 'dose_units'] = 'mg/1.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/10ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose_units'] = 'mg/0.5ml'

# mirtazapine 15/1 or mg; else is mg; NA:30
drug = 'mirtazapine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('30')), 'dose'] = 30

# nefopam delete 20; NA:30 all
drug = 'nefopam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose'] = 30
meds_lost.loc[(meds_lost['aa_name'] == drug), 'dose'] = 30

# nitrazepam 2.5 is mg/ml; NA:5
drug = 'nitrazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5

# olanzapine 2.5 is mg/ml or mg, remove 210
drug = 'olanzapine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 210), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 210), 'dose_units'] = np.nan

# orphenadrine 25 is mg/5ml
drug = 'orphenadrine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose_units'] = 'mg/5ml'

# oxybutynin 2.5 is mg/5 and mg, 5 is mg/5 and mg; 3.9 (transdermal patch); NA:2.5,3,5
drug = 'oxybutynin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('3')), 'dose'] = 3
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5

# oxycodone 5 mg/5ml or mg, 10mg/ml or mg, 50mg/ml or mg, 20mg/2ml or mg
drug = 'oxycodone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2ml'

# paliperidone 75mg/0.75ml, 100mg/ml, 150mg/1.5ml
drug = 'paliperidone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 75) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/0.75ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 150) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1.5ml'

# paroxetine 10 is mg/5ml or mg, 20 is mg/10ml or mg; NA:20,30
drug = 'paroxetine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/10ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('20')), 'dose'] = 20
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('30')), 'dose'] = 30

# phenobarbital 15 is mg/5ml or mg, 200 is 200/1ml or mg; NA:30,60
drug = 'phenobarbital'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('30')), 'dose'] = 30
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('60')), 'dose'] = 60

# phenytoin 30 is mg/5ml, 90 is mg/5ml; NA:100,300
drug = 'phenytoin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 90), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 100

# pramipexole use 2nd column if it contains anything
drug = 'pramipexole'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose_a2_number']).copy() 

# prednisolone 5 is mg/5ml or mg, 20 is mg/100ml or mg, 25 is mg/ml or mg; >=30000, 1.9 are ointments; 1 when with cinchocaine; NA:1 when with cinchocaine, tab 5, tab 1, tab 2.5
drug = 'prednisolone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/100ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1.9), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1.9), 'dose_units'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] >= 30000), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] >= 30000), 'dose_units'] = np.nan
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('cinchocaine')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('tab')) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('tab')) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('tab')) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5

# prochlorperazine 5 is mg/5ml and mg, 12.5 is mg/ml and mg, 25 is mg/2ml and mg; NA:3,5,12.5mg/ml,25mg/2ml
drug = 'prochlorperazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('3')), 'dose'] = 3
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('12.5')), 'dose'] = 12.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('12.5')), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose_units'] = 'mg/2ml'

# procyclidine 5 is mg/5ml, 2 is 2.5/5ml; NA:2.5,5
drug = 'procyclidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose'] = 2.5
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5

# promazine 25 is mg/5ml, 50 is mg/5ml; NA:25,50
drug = 'promazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# promethazine 5 is mg/5ml; NA:25
drug = 'promethazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25

# propantheline 15 is mg/5ml or mg; NA:15
drug = 'propantheline'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15) & (meds_found['prescription'].str.contains('ml')), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('15')), 'dose'] = 15

# pyrilamine all are cream
drug = 'pyrilamine'
meds_found.loc[(meds_found['aa_name'] == drug), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug), 'dose_units'] = np.nan

# quetiapine 25 is mg or mg/5ml; remove the ones with several columns
drug = 'quetiapine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose_units'] = np.nan

# ranitidine 75 is mg or mg/5ml, 150 is mg or mg/10ml; NA:150,300,75
drug = 'ranitidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 75) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 150) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/10ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('150')), 'dose'] = 150
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 300
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('75')), 'dose'] = 75

# sertraline 100 is mg or mg/5ml, 50 is mg or mg/5ml; NA:50,100
drug = 'sertraline'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# sumatriptan 6 is mg/0.5ml; 10 is either nasal or mg; 12 is mg/ml; 20 is nasal; NA:12mg/ml, 50,100
drug = 'sumatriptan'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 6) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/0.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('12.5')), 'dose'] = 12.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('12.5')), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# temazepam 10 is mg or mg/5ml; NA:10mg,20mg
drug = 'temazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('20')), 'dose'] = 20

# theophylline 60 is mg/5ml or mg; NA:400,300,200,250
drug = 'theophylline'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 60) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('400')), 'dose'] = 400
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 300
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')), 'dose'] = 250

# thioridazine 25 is mg/5ml or mg; NA:10,25,50
drug = 'thioridazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# tizanidine 2 is mg or mg/5ml
drug = 'tizanidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'

# tobramycin 80 is 80/2ml, 300 is mg/2ml
drug = 'tobramycin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 80), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 300), 'dose_units'] = 'mg/2ml'

# tolterodine 2 is mg or mg/5ml; NA:1mg,2mg
drug = 'tolterodine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2')), 'dose'] = 2

# tramadol 100 is mg or mg/2ml; 325 is 37.5; NA:50,150,100 all mg
drug = 'tramadol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 325), 'dose'] = 37.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('150')), 'dose'] = 150
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# trandolapril 180 is 2; NA:0.5,1,2
drug = 'trandolapril'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 180), 'dose'] = 2
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('0.5')), 'dose'] = 0.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2')), 'dose'] = 2

# trazodone 50 is mg or mg/5ml; NA:50,100,150
drug = 'trazodone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('150')), 'dose'] = 150

# triamcinolone 5, 10, 20, 40 are mg/ml, 50 is mg/5ml, 80 is mg/2ml; 5000 or more is dermal paste
drug = 'triamcinolone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 40), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 80), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] >= 5000), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] >= 5000), 'dose_units'] = np.nan

# trifluoperazine 1, 5 are mg or mg/5ml; NA:1,5,10
drug = 'trifluoperazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10

# trihexyphenidyl 5, 2 are mg/5ml or mg
drug = 'trihexyphenidyl'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('5', na = False)), 'dose'] = 5

# triprolidine 10 is OK, for the rest take 2nd column
drug = 'triprolidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] != 10), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] != 10), 'dose_a2_number']).copy() 

# valproate 200 is mg or mg/5ml; NA:100,200,300,500 all mg
drug = 'valproate'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('300')), 'dose'] = 300
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 500

# venlafaxine 37.5 and 75 is mg or mg/5ml; NA:37.5,75 all mg
drug = 'venlafaxine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 37.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 75) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('37.5')), 'dose'] = 37.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('75')), 'dose'] = 75

# warfarin 1 is mg or mg/ml, 3 is mg or mg/5ml, 5 is mg or mg/5ml; NA:1,3,5
drug = 'warfarin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 3) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('1')), 'dose'] = 1
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('3')), 'dose'] = 3
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5

# zolmitriptan 5 is mg or mg/0.1ml; NA:2.5
drug = 'zolmitriptan'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/0.1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 1

# zuclopenthixol 200, 500, 50 are mg/ml; 
drug = 'zuclopenthixol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/1ml'

# clomipramine 25 is mg or mg/5ml; NA's: 25, 50 both mg
drug = 'clomipramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# metoclopramide 5 is mg or mg/5ml, 10 is mg or mg/2ml, 100 is mg/20ml, 500 and 900 2nd column; 5 with paracetamol, 10 when with aspirin; NA's: when with paracetamol 5; when with aspirin 10; tab AND 10 is 10; tab AND 5 is 5; inj AND 10 is 10/2
drug = 'metoclopramide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/20ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 900) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 900) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_a2_number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('paracetamol')), 'dose'] = 5
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('aspirin')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('paracetamol')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('aspirin')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('tab')) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('tab')) & (meds_lost['prescription'].str.contains('5')), 'dose'] = 5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('inj')) & (meds_lost['prescription'].str.contains('10')), 'dose'] = 10
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('inj')) & (meds_lost['prescription'].str.contains('10')), 'dose_units'] = 'mg/2ml'

# captopril; NA: 12.5,25,50
drug = 'captopril'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('12.5')), 'dose'] = 12.5
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('25')), 'dose'] = 25
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50

# cyclizine 10 is actually 30, 15 is mg/ml, 50 is either mg or 50/1
drug = 'cyclizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('1ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('5ml', na = False)), 'dose_units'] = 'mg/5ml'

# fluticasone/salmeterol always in combo 0.05/0.025, 0.125/0.025, 0.25/0.025, 0.1/0.05, 0.25/0.05, 0.5/0.05; NA's: 1st number always refers to fluticasone
drug = 'fluticasone/salmeterol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.125), 'dose'] = 0.15
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 0.125), 'dose'] = 0.15
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.1), 'dose'] = 0.15
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 0.1), 'dose'] = 0.15
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.5), 'dose'] = 0.55
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 0.5), 'dose'] = 0.55
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 0.05) & (meds_found['dose_a1_number'] == 0.025), 'dose'] = 0.075
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 0.25) & (meds_found['dose_a1_number'] == 0.025), 'dose'] = 0.275
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 0.25) & (meds_found['dose_a2_number'] == 0.05), 'dose'] = 0.3
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 0.25) & (meds_found['dose_a1_number'] == 0.05), 'dose'] = 0.3
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('50')) & (meds_found['prescription'].str.contains('evo')), 'dose'] = 0.075
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('250')) & (meds_found['prescription'].str.contains('evo')), 'dose'] = 0.275
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('125')) & (meds_found['prescription'].str.contains('evo')), 'dose'] = 0.150
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('100')) & (meds_found['prescription'].str.contains('accu')), 'dose'] = 0.150
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('250')) & (meds_found['prescription'].str.contains('accu')), 'dose'] = 0.275
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('500')) & (meds_found['prescription'].str.contains('accu')), 'dose'] = 0.550
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 0.075
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('125')), 'dose'] = 0.15
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 0.15
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('500')), 'dose'] = 0.55
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')) & (meds_lost['prescription'].str.contains('evo')), 'dose'] = 0.275
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('250')) & (meds_lost['prescription'].str.contains('accu')), 'dose'] = 0.3

# methadone 60mg/60ml, 50mg/5ml, 20mg/2ml, 10mg/ml, 1mg/ml; 5 is mg
drug = 'methadone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1), 'dose_units'] = 'mg/1ml'

# methotrexate 2.5 is mg and mg/1ml, 10 is mg and mg/0.2ml, mg/0.4; 25/0.5, 25/1; 25/1.25; 15/0.3l; 20/0.4; 50/2; 7.5/.75; 12.5/0.25; 12.5/0.5; 17.5/0.35; 5/2; 22.5/0.45; 30/0.6; 50/2; 100/1; 1000/40; when 2nd is 10, it is 10/1; NA:2.5
drug = 'methotrexate'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)) & (meds_found['prescription'].str.contains('0.2')), 'dose_units'] = 'mg/0.2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)) & (meds_found['prescription'].str.contains('0.4')), 'dose_units'] = 'mg/0.4ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('0.5')), 'dose_units'] = 'mg/0.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25) & (meds_found['prescription'].str.contains('1.25')), 'dose_units'] = 'mg/1.25ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15), 'dose_units'] = 'mg/0.3ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20), 'dose_units'] = 'mg/0.4ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 7.5), 'dose_units'] = 'mg/0.75ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5) & (meds_found['prescription'].str.contains('0.25')), 'dose_units'] = 'mg/0.25ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5) & (meds_found['prescription'].str.contains('0.5')), 'dose_units'] = 'mg/0.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 17.5), 'dose_units'] = 'mg/0.35ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 22.5), 'dose_units'] = 'mg/0.45ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30), 'dose_units'] = 'mg/0.6ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1000), 'dose_units'] = 'mg/40ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 10), 'dose'] = 10
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a2_number'] == 10), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('2.5')), 'dose'] = 2.5

# codeine 15 is mg or mg/ml, 25 is mg/5ml, 32.5 is 16mg/5ml, 3 is mg/5ml, 6.75 is mg/5ml; when with ibuprofen, paracetamol, or aspirin, take column that is smaller
drug = 'codeine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 32.5), 'dose'] = 16
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 32.5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 3), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 6.75), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('ibuprofen')) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('ibuprofen')) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose'] = \
    ((meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('ibuprofen')) & (meds_found['prescription'].str.contains('ml', na = False))])[['dose_a1_number', 'dose_a2_number']].min(axis=1)).copy()

# pethidine 10 is mg/ml, 50 is mg/ml or mg, 100 is mg/2ml, or 100/10ml; NA:50,100
drug = 'pethidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('2ml')), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100) & (meds_found['prescription'].str.contains('10ml')), 'dose_units'] = 'mg/10ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('50')), 'dose'] = 50
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('100')), 'dose'] = 100

# rotigotine several columns are multiple different doses, take average (2+4+6+8)/4 = 5
drug = 'rotigotine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['dose_a2_number'].isnull()), 'dose'] = 5

# risperidone 1 is mg or mg/ml; >6 is powder for injection; NA:3,6
drug = 'risperidone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('3')), 'dose'] = 3
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('6')), 'dose'] = 6

# levodopa it occurs with benserazide as levo/bense 50/12.5, 100/25; NA:see combo (x/x) occurrences with benserazide
drug = 'levodopa'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose'] = 50
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5), 'dose'] = 50
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose'] = 100
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose'] = 100
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 62.5), 'dose'] = 50
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 125), 'dose'] = 100

# diphenoxylate always always 2.5
drug = 'diphenoxylate'
meds_found.loc[(meds_found['aa_name'] == drug), 'dose'] = 2.5

# diphenhydramine 7, 10, 12.5 are mg/5ml; 25 and 50 are ok, 2nd row and >50 are bogus
drug = 'diphenhydramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 7), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 50), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] > 50), 'dose_units'] = np.nan

# ephedrine <7 is bogus, most are nasal drops
drug = 'ephedrine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] < 7), 'dose'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] < 7), 'dose_units'] = np.nan

# pseudoephedrine 300 is 45; 200 is 30; 30 is 30/5ml or 30 mg; 100 is 30/5mg/ml; 200 is 30; 500 is 30
drug = 'pseudoephedrine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 300), 'dose'] = 45
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 200), 'dose'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose'] == 100), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose'] == 100), 'dose'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose'] == 200), 'dose'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose'] == 500), 'dose'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose'] == 30) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'

# mequitazine
drug = 'mequitazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 300), 'dose'] = 45

# morphine 1/1, 1/5, 8.4/1, 10/1 or mg, 15/1 or mg, 20/1 or mg, 30/1 or mg, 60/2 or mg
drug = 'morphine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 1) & (meds_found['prescription'].str.contains('ml', na = False)) & (meds_found['prescription'].str.contains('5')), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 8.4) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 15) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 60) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2ml'

# lansoprazole 500 is 30; 5 is 5mg/ml; 30 is mg or 30mg/5ml
drug = 'lansoprazole'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 500), 'dose'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 30) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'

# nifedipine 20 is mg or mg/ml, 50 is 20
drug = 'nifedipine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose'] = 20

# fluphenazine 12.5/0.5, 25/1, 50/0.5, 100/1, 1 is mg; 10 is 0.5
drug = 'fluphenazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 12.5), 'dose_units'] = 'mg/0.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/0.5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose'] = 0.5

# perphenazine 10 and 25 are actually 2mg
drug = 'perphenazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose'] = 2
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 25), 'dose_units'] = 2

# furosemide mg/ml can be 20mg/2ml, 40mg/5ml, 50mg/5ml, 80mg/8ml; 2.5 is 20, 5 is 40, 10 is 80, 50 is 2nd
drug = 'furosemide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 20) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/2ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 40) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 80) & (meds_found['prescription'].str.contains('ml', na = False)), 'dose_units'] = 'mg/8ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2.5), 'dose'] = 20
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 5), 'dose'] = 40
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose'] = 80
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_a2_number']).copy()

# chlorphenamine 2/5, 10/1 are mg/ml
drug = 'chlorphenamine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 2), 'dose_units'] = 'mg/5ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 10), 'dose_units'] = 'mg/1ml'

# pipotiazine: 50 is mg/1ml, 100 is mg/2ml
drug = 'pipotiazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 50), 'dose_units'] = 'mg/1ml'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['dose_a1_number'] == 100), 'dose_units'] = 'mg/2ml'

# amiodarone: NA: contains 200, 200
drug = 'amiodarone'
meds_lost.loc[(meds_lost['aa_name'] == drug) & (meds_lost['prescription'].str.contains('200')), 'dose'] = 200

# join the two data frames
meds = pd.concat([meds_found, meds_lost])
meds.index = (list(range(len(meds))))
del meds_found
del meds_lost
print('Dosage done.')









### B. drug numbers/volumes 



## B1. numbers associated with  use the quantity column to derive the number/volume (regex: digit from 1-9, digit or dot (0 or more times); whitespace (0 or more times)
temp_number = (meds['quantity'].str.extractall(r'([1-9][\d\.]*\s*)')).unstack()
temp_number.columns = ['number_a1','number_a2','number_a3','number_a4','number_a5','number_a6','number_a7','number_a8','number_a9']
meds = meds.join(temp_number) # merge with the main data frame
del temp_number

# change the type of the number/volume to float
meds.loc[:, 'number_a1'] = meds.loc[:, 'number_a1'].str.replace('...','', regex=False)
meds.loc[:, 'number_a1'] = meds.loc[:, 'number_a1'].astype(float)
meds.loc[:, 'number_a2'] = meds.loc[:, 'number_a2'].astype(float)
meds.loc[:, 'number_a3'] = meds.loc[:, 'number_a3'].astype(float)
meds.loc[:, 'number_a4'] = meds.loc[:, 'number_a4'].astype(float)
meds.loc[:, 'number_a5'] = meds.loc[:, 'number_a5'].astype(float)
meds.loc[:, 'number_a6'] = meds.loc[:, 'number_a6'].astype(float)
meds.loc[:, 'number_a7'] = meds.loc[:, 'number_a7'].astype(float)
meds.loc[:, 'number_a8'] = meds.loc[:, 'number_a8'].astype(float)
meds.loc[:, 'number_a9'] = meds.loc[:, 'number_a9'].astype(float)

## set number/volume for those rows for which it is clear (others will be manually checked below)
meds.loc[:, 'from_quantity'] = (meds.loc[:, 'from_quantity']).astype(float) # convert to float so the calculation below works
# to those that just have one number in the quantity column, assign that as the number (only if the dose was NOT derived from the quantity column)
meds.loc[(meds['number_a2'].isnull()) & (~meds['number_a1'].isnull()) & (meds['from_quantity'] == 0) & (~meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number'] =  \
    (meds.loc[(meds['number_a2'].isnull()) & (~meds['number_a1'].isnull()) & (meds['from_quantity'] == 0) & (~meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number_a1']).copy()
# to those that have 2 numbers in the quantity column, assign the product of the two as the number (one probably refers to number of pills, the other to the number of packets)
meds.loc[(meds['number_a3'].isnull()) & (~meds['number_a2'].isnull()) & (meds['from_quantity'] == 0) & (~meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number'] = \
    (meds.loc[(meds['number_a3'].isnull()) & (~meds['number_a2'].isnull()) & (meds['from_quantity'] == 0) & (~meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number_a1']).copy() * \
        (meds.loc[(meds['number_a3'].isnull()) & (~meds['number_a2'].isnull()) & (meds['from_quantity'] == 0) & (~meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number_a2']).copy()
# if one of the two numbers has a dose unit associated with it, take the first column
meds.loc[(meds['number_a3'].isnull()) & (~meds['number_a2'].isnull()) & (meds['from_quantity'] == 0) & (meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number'] = \
    (meds.loc[(meds['number_a3'].isnull()) & (~meds['number_a2'].isnull()) & (meds['from_quantity'] == 0) & (meds['quantity'].str.contains(r'(milligram|mg|gram|microgram|mcg|ml)', na=False)), 'number_a1']).copy()

# subset data frames into found and not found quantity
meds_found = (meds.loc[~meds['number'].isnull()]).copy()
meds_lost = (meds.loc[meds['number'].isnull()]).copy() 
# additionally subset the meds without quantities into those that are truly missing quantities and those for which the
# algorithm above failed to assign quantities
# those that are truly missing are either NA's, 0's, have no numbers in the quantity column, or have numbers that refer to the dose
meds_lost_missing = (meds_lost.loc[(meds_lost['quantity'].isnull()) | (meds_lost['quantity'] == '0') | \
                                  (~meds_lost['quantity'].str.contains(r'([1-9{+}])', na=False)) | (meds_lost['number_a1'] == meds_lost['dose'])]).copy()
meds_lost_unfound = (meds_lost.loc[(~meds_lost['quantity'].isnull()) & (meds_lost['quantity'] != '0') & \
                                  (meds_lost['quantity'].str.contains(r'([1-9{+}])', na=False)) & (meds_lost['number_a1'] != meds_lost['dose'])]).copy()

####### OPTIONAL #######

# checking for errors of the automated algorithm for each drug
#example = meds_lost.loc[meds_lost['prescription'].str.contains(r'([^a-zA-Z]+|^)(cimetidine)', regex=True)]
#test = example.loc[~example['number'].isnull()]  
#print(test.number.value_counts())
#test.number.hist()
#test2 = example.loc[~example['number_a3'].isnull()]
#test3 = (example.loc[(example['number'].isnull())])[['prescription', 'quantity', 'number_a1', 'number_a2', 'number_a3', 'number_a4', 'number', 'dose']]
#test3 = test3.loc[(~test3['quantity'].isnull()) & (test3['quantity'] != '0') & (test3['quantity'].str.contains(r'([1-9{+}])')) & \
#                 (test3['number_a1'] != test3['dose'])]
#zzz = test3.quantity.value_counts()
#if (~test2['number_a4'].isnull().values.all()):
#    print ('\n' + 'CHECK OTHER COLUMNS')

# Identification of null-value rows

# This part checks null values for quantity for each drug to manually supplement later.
# For each drug, it indicates whether there are any rows without assigned quantity.
# If that is the case for a given drug, (manually) add it to the 'NA_n_dosage' column of the drug_list; it will be checked and corrected later (as part of the 'meds_lost' data frame)

#drugs_left = len(drug_list.drug.tolist()) # list of all drugs
#drug_dict = {} # drugs as keys, number of null values in quantity column as values
#for drug in drug_list.drug.tolist():
    # look up the rows with the drug in the data frame
    #temp = meds_lost.loc[meds_lost['prescription'].str.contains(r'([^a-zA-Z]+|^)' + drug, regex=True)]
    # check the number of null values (that have text in quantity column) and add to the dictionary
    #temp = temp.loc[(~temp['quantity'].isnull()) & (temp['quantity'] != '0') & (temp['quantity'].str.contains(r'([1-9{+}])')) & \
    #              (temp['number_a1'] != temp['dose'])]
    #drug_dict[drug] = len(temp)
    #drugs_left -= 1 # counter to soothe my inpatience
    #print('Drugs left: ' + str(drugs_left))
    #drug_list.loc[drug_list['drug'] == drug, 'NA_n_quantity'] = drug_dict[drug]

# record the number of NA's in the data frame with drugs
#for drug in drug_list.drug.tolist():
    #drug_list.loc[drug_list['drug'] == drug, 'NA_n'] = drug_dict[drug]
    

## B2. manual correction

# for the missing values, there is some overlap between them, so these can be partially automated
# others will be supplemented manually below, along with the manual changes for non-missing rows

# a) choose the first number
drugs_1 = ['ampicillin','atropine','bisacodyl','brompheniramine','cefalexin','clemastine','clindamycin','dexamethasone', \
           'dextromethorphan','dimenhydrinate','diphenoxylate','entacapone','ephedrine','glycopyrronium','guaifenesin','ketamine' \
               'ketotifen','methadone','methylprednisolone','midazolam','morphine','perphenazine','thioridazine','triamcinolone', \
                   'triprolidine']
for drug in drugs_1:
    meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()

# b) multiply first number and second number
drugs_1_2_a = ['aminophylline','azathioprine','celecoxib','chlortalidone','donepezil','doxepine','duloxetine','escitalopram', \
               'etoricoxib','famotidine','fentanyl','fesoterodine','fexofenadine','fluvoxamine','furosemide','hydralazine', \
                   'levocetirizine','metoprolol','naratriptan','nefopam','nizatidine','oxazepam','oxcarbazepine','pethidine', \
                       'propantheline','propiverine','reboxetine','rotigotine','selegiline','solifenacin','topiramate', \
                           'trandolapril','tranylcypromine','trospium','zolmitriptan']
for drug in drugs_1_2_a:
    meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()

# c) multiply first and second numbers only if '*' present in quantity; otherwise choose first number
drugs_1_2_b = ['amitriptyline','atenolol','baclofen','carbamazepine','carbidopa','chlorphenamine','chlorpromazine','ciclosporin','clomipramine', \
               'codeine','darifenacin','desloratadine','diazepam','dicycloverine','diltiazem','diphenhydramine','dipyridamole', \
                   'domperidone','gentamicin','hyoscine butylbromide','imipramine','isosorbide','levodopa','lithium','loperamide', \
                       'loratadine','lorazepam','metformin','methocarbamol','methotrexate','metoclopramide','mirtazapine', \
                           'nifedipine','nitrazepam','nortriptyline','orphenadrine','phenobarbital','phenytoin','pramipexole', \
                               'procyclidine','promazine','promethazine','ranitidine','risperidone','temazepam','tiotropium', \
                                   'tramadol','trazodone','triamterene','trifluoperazine','trihexyphenidyl','valproate','venlafaxine',
                                   'fluticasone/salmeterol']
for drug in drugs_1_2_b:
    meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
    meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number_a2']).copy()
    






# amiodarone: when 3rd, 56; NA: number_a1 (unless 2*28, then 56); NA: if 2nd==200, then 28; otherwise 1st*2nd
drug = 'amiodarone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('2*28', na=False)), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a2'] == 200), 'number'] = 28

# aclidinium bromide
# ampicillin # 25 and 500 are 28
drug = 'ampicillin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 25), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 500), 'number'] = 28

# atenolol 565 is 56, 784 is 28; when 3 exists, 1st*2nd
drug = 'atenolol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 565), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 784), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# alprazolam 
# aminophylline when 3, 1*2
drug = 'aminophylline'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# amoxapine
# asenapine
# azathioprine when 3, 1*2
drug = 'azathioprine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# bromocriptine
# bupropion >400 is 60
drug = 'bupropion'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] > 400), 'number'] = 60

# carbamazepine if >=4000, then 1st; if 3136, then 112; 2403 remove; 750 is 250; when 4th exists, it's 100
drug = 'carbamazepine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number'] > 4000), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number'] > 4000), 'number']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 3136), 'number'] = 112
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 2403), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 750), 'number'] = 250
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number'] = 100
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number'] > 4000), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number'] > 4000), 'number']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number'] > 4000), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number'] > 4000), 'number']).copy()

# carisoprodol
# celecoxib 7200 is 120; when 3, 1*2
drug = 'celecoxib'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 7200), 'number'] = 120
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# chlordiazepoxide
# clorazepate
# clozapine
# colchicine when 3, is 60; NA: 60
drug = 'colchicine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = 60
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 60

# cortisone
# cycloserine
# cyproheptadine
# darifenacin when 3, 1*2
drug = 'darifenacin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# desipramine
# digitoxin
# disopyramide 1 is bogus
drug = 'disopyramide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = np.nan

# donepezil when 3, 1*2
drug = 'donepezil'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# duloxetine when 3, 1*2
drug = 'duloxetine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# ergotamine 10000 is 100; NA: if 'X', then 100; otherwise 30
drug = 'ergotamine'
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 10000), 'number'] = 100
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number'] = 100

# etoricoxib when3, 1*2
drug = 'etoricoxib'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# famotidine when 3, 1*2
drug = 'famotidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# fentanyl when 3, 1*2
drug = 'fentanyl'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# fesoterodine when 3, 1*2
drug = 'fesoterodine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# fexofenadine if contains month, multiply number by 30; if >=900, divide by 30
drug = 'fexofenadine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('month')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('month')), 'number_a1']).copy() * 30
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 900), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 900), 'number_a1']).copy() / 30

# flavoxate when 3, 1*2; flavoxate: NA: 180
drug = 'flavoxate'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 180

# flunitrazepame
# flurazepam

# fluvoxamine when '/' in quantity, use a1
drug = 'fluvoxamine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('/', regex=False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('/', regex=False)), 'number_a1']).copy()

# hydralazine when 3, 1*2
drug = 'hydralazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# isosorbide 3136 is 56; when 3, 1*2
drug = 'isosorbide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 3136), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# levocetirizine >=900 divide by 30
drug = 'levocetirizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 900), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 900), 'number_a1']).copy() / 30

# loxapine
# lumiracoxib
# maprotiline
# meclizine
# methocarbamol 2016 is bogus, 14400 is 120
drug = 'methocarbamol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 2016), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 14400), 'number'] = 120

# naratriptan 1 is 6 when 3, 1*2
drug = 'naratriptan'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = 6
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# nefazodone 1 is 7; when 3, is 56; NA: 56
drug = 'nefazodone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = 7
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 56

# nizatidine when 3, 1*2
drug = 'nizatidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# nortriptyline
# oxazepam when 3, 1*2
drug = 'oxazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# oxcarbazepine 3, 1*2
drug = 'oxcarbazepine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# oxitropium if >=100, divide by 100; NA: if '200', 200
drug = 'oxitropium'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 100), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 100), 'number_a1']) / 7
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'] == 200), 'number'] = 200

# pericyazine
# phenelzine
# phenindamine
# pheniramine
# pimozide
# prednisone
# propiverine if 3, 1*2
drug = 'propiverine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# protriptyline
# quinidine
# reboxetine if 3, 1*2
drug = 'reboxetine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# selegiline if 3, 1*2
drug = 'selegiline'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# solifenacin if 3, 1*2
drug = 'solifenacin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# tiagabine
# tiotropium >=900, divide by 30; 3: if quantity has '*', then 1*2 (otherwise 1st column)
drug = 'tiotropium'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 900), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] >= 900), 'number_a1']).copy() / 30
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# topiramate if 3, 1*2
drug = 'topiramate'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# tranylcypromine if 3, 1*2
drug = 'tranylcypromine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# triamterene 3: if quantity has '*', then 1*2 (otherwise 1st column)
drug = 'triamterene'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# triazolam
# trimipramine; NA: if '*', 1st*2nd; otherwise 28
drug = 'trimipramine'
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 28
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# trospium if 3, 1*2
drug = 'trospium'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# vancomycin
# alimemazine if 3, 1*2; NA: if 'ml', then 3rd; otherwise 1st*2nd
drug = 'alimemazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a3']).copy()

# alverine if 3, 1*2; NA: if '*', then 1st*2nd; if 4th, 100
drug = 'alverine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (~meds_lost_unfound['number_a4'].isnull()), 'number'] = 100

# amantadine; NA: if 'ml', 3rd, otherwise 1st*2nd
drug = 'amantadine'
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a3']).copy()

# amitriptyline if 3 and contains '*', 1*2 (otherwise, 1st)
drug = 'amitriptyline'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# amoxicillin  >3000 is bogus; if 'day pack', 1st*28; if '1/52', 52; if 'ml', 1st; if '14+14', 28; if 1st==15, 15; if '*', 1*2; if 'Pack of', 60; if '500mg x 1', 21; NA: if '7', 28; if 'ml', 1st; if '*', 1st*2nd
drug = 'amoxicillin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] > 3000), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('day pack')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('day pack')), 'number_a1']).copy() * 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('1/52')), 'number'] = 52
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('14+14')), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 15), 'number'] = 15
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('Pack of')), 'number'] = 60
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('500mg x 1')), 'number'] = 21
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('7', na=False)), 'number'] = 28
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('30 -', na=False)), 'number'] = 30

# ampicillin  if 3, take 2
drug = 'ampicillin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy() 

# aripiprazole if 3, 1*2; NA: if 'ml', 1st; if '*', 1st*2nd
drug = 'aripiprazole'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# atenolol 10000 is 100; 3: if 'ml' or 'capsule', 1st; if '*', 1*2; if '28x3', 84; if 4, 1*2; 
drug = 'atenolol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 10000), 'number'] = 100 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('capsule')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('capsule')), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('28x3')), 'number'] = 84 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number_a2']).copy()

# azatadine
# baclofen 3: if 'ml', 1st; if '*', 1*2
drug = 'baclofen'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a2']).copy()

# benztropine
# betaxolol
# bisacodyl
# brompheniramine if 3, use 1
drug = 'brompheniramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 

# buclizine >1000 is 48; if 3, take a2; NA: 2nd
drug = 'buclizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] > 1000), 'number'] = 48 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy() 
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()

# captopril if 3, 1*2; NA: 56
drug = 'captopril'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 56

# cefalexin
# cetirizine if 3rd: 1*2 (unless has 'ml', then 1st); 1st has '84', 84; NA: if '3 X 10', 30; if '4 Pack', 120; if *', 1st*2nd, otherwise 1st
drug = 'cetirizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('84')), 'number'] = 84
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('3 X 10', na=False)), 'number'] = 30
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('4 Pack', na=False)), 'number'] = 120

# chloroquine 10976 is 112; if 3==14, 14; if 3==98, 14; if 2==250 AND 3==(100 OR 155), 1st; if 4, 1*2; NA: if 'tablet' or 'tabs', 1st
drug = 'chloroquine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 10976), 'number'] = 112
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 14), 'number'] = 14
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 98), 'number'] = 14
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 250) & (meds_found['number_a3'] == 100), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 250) & (meds_found['number_a3'] == 100), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 250) & (meds_found['number_a3'] == 155), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 250) & (meds_found['number_a3'] == 155), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 4), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 4), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 4), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('tablet', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('tablet', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('tabs', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('tabs', na=False)), 'number_a1']).copy()

# chlorpromazine if '1 month', 90
drug = 'chlorpromazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('1 month')), 'number'] = 90

# ciclosporin if 3, 1*2 (only if contains '*'; otherwise 1st)
drug = 'ciclosporin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# cimetidine when 3: if 2nd has '60', 60 (otherwise 1st); NA: if 'X', 60; if '*', 1st*2nd, otherwise 1st
drug = 'cimetidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 60), 'number'] = 60
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number'] = 60

# citalopram if 3 , 1*2 (unless 3rd is 3 OR 2, then take 2nd*3rd); NA: if '*', 1st* 2nd
drug = 'citalopram'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 2), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 2), 'number_a2']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 2), 'number_a3']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 3), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 3), 'number_a2']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a3'] == 3), 'number_a3']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# clemastine if 3, take 1
drug = 'clemastine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 

# clindamycin 
# clonazepam; NA: if 'ml', 1st
drug = 'clonazepam'
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# cyclizine when 'prescription' contains 'injection' AND not 'ergotamine' AND 1st==1, 5; when 3, 1; NA: if 'X', 100; otherwise 1st
drug = 'cyclizine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('injection')) & (~meds_found['prescription'].str.contains('ergotamine')) & (meds_found['number_a1'] == 1), 'number'] = 5
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number'] = 100

# desloratadine when 3, 1*2
drug = 'desloratadine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# dexamethasone 3: when 1st==1, 10; when 1st==10 OR 20, 10, 20; when 1st==2, 20; when 1st==3, 30; otherwise 1st
drug = 'dexamethasone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 1), 'number'] = 10
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 2), 'number'] = 20
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 3), 'number'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 10), 'number'] = 10
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 20), 'number'] = 20

# dextromethorphan
# diazepam 2028 is 560; 24336 is 8736; if 3: if '*', 1*2; if 'rectal', 1st*5; otherwise 1st
drug = 'diazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 2028), 'number'] = 560
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 24336), 'number'] = 8736
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('rectal')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('rectal')), 'number_a1']).copy() * 5
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', na=False, regex=False)), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# dicycloverine when 3: '*' 1*2; when 1st==1, 100; otherwise 1st
drug = 'dicycloverine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull() & (meds_found['quantity'].str.contains('*', regex = False))), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull() & (meds_found['quantity'].str.contains('*', regex = False))), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 1), 'number'] = 100

# digoxin when 3, 1*2; NA: if 'ml', 1st; if '*', 1st*2nd
drug = 'digoxin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# diltiazem when 3: if '*', 1*2; otherwise 112
drug = 'diltiazem'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = 112
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# dimenhydrinate when 3, 1st
drug = 'dimenhydrinate'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# dipyridamole 3: when 1st==120 OR 56 OR 60, 1st; when '*', 1*2; 
drug = 'dipyridamole'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 120), 'number'] = 120
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 56), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 60), 'number'] = 60
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# domperidone
# dosulepin if 3, 1*2; NA: if 'X' or '*', 1st*2nd; otherwise 1st
drug = 'dosulepin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number_a2']).copy()

# doxepine
# escitalopram 3: 1*2
drug = 'escitalopram'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# fluoxetine 3: if 'ml' or 'milli', 1st; otherwise 1*2; NA: if 'X', 30; if *', 1st*2nd, otherwise 1st
drug = 'fluoxetine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('milli')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('milli')), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number'] = 30
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# gentamicin 3:1*2
drug = 'gentamicin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# glycopyrronium
# guaifenesin
# haloperidol; NA: if '1 pack', 5; if '2 packs', 10; if '*', 1st*2nd; otherwise 1st
drug = 'haloperidol'
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('1 pack', na=False, regex = False)), 'number'] = 5
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('2 packs', na=False, regex = False)), 'number'] = 10

# hydrocortisone 560 is 56; 3: if '*', 1*2 (otherwise, 1st); NA: if 'supposit' or 'ampoule', 1st; if '*', 1st*2nd; if 'ml', 1st
drug = 'hydrocortisone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 560), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('supposit', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('supposit', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ampoule', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ampoule', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False,)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# hydroxyzine 3: if 'ml', 1st; otherwise 1*2; NA: if '2 X 14', 28; if '*', 1st*2nd; otherwise 1st
drug = 'hydroxyzine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('2 X 14', na=False)), 'number'] = 28

# hyoscine butylbromide 3: 1*2 (unless 'ml', then 1st)
drug = 'hyoscine butylbromide'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# hyoscine hydrobromide 3: if 1st==1 OR '*', 1*2; otherwise 1st; NA: if '10 X 1', 10; if '*', 1st*2nd; otherwise 1st
drug = 'hyoscine hydrobromide'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 1), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 1), 'number_a1']).copy() * meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a1'] == 1), 'number_a2'].copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1'].copy() * meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('10 X 1', na=False)), 'number'] = 10

# imipramine 3: if '*', 1*2; otherwise 1st
drug = 'imipramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# ketamine
# ketorolac when 3, 1*2; NA: 10
drug = 'ketorolac'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 10

# ketotifen when 3, 1
drug = 'ketotifen'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# levofloxacin
# levomepromazine 3: when 2nd==10, 1st*2nd; otherwise 1st; NA: if 1st==1, 10; otherwise 1st
drug = 'levomepromazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() 
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 10), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 10), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a2'] == 10), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 1), 'number'] = 10

# lithium 1 or 2 is 100 or 200; when 3: if '*', 1*2 (otherwise 1st)
drug = 'lithium'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = 100 
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 2), 'number'] = 200 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# lofepramine if contains 'month', 1st*56; 3: 1*2 (unless 'ml', then 1st); NA: if 1st==1 or 1st==2, 1st*56; if '*', 1st*2nd; otherwise 1st
drug = 'lofepramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('month')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('month')), 'number_a1']).copy() * 56 
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (~meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (~meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (~meds_found['quantity'].str.contains('ml', na = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 1), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 1), 'number_a1']).copy() * 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 2), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 2), 'number_a1']).copy() * 56

# loperamide 3: 1*2 (unless 'ml', then 1st)
drug = 'loperamide'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (~meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (~meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (~meds_found['quantity'].str.contains('ml', na = False)), 'number_a2']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', regex=False, na=False)), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', regex=False, na=False)), 'number_a1']).copy() * (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', regex=False, na=False)), 'number_a2']).copy()

# loratadine
# lorazepam if 3, 1*2
drug = 'lorazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()


# metformin if '8 weeks', 8*28; if '500 MG', 112; 11256 is 6272; 4:1*2;  3:'8*28'=224; 2nd==1, 1st; 2nd==2 OR 3 OR 4, 1st; (2nd==2 OR 3 OR 4) AND '*', 1st*2nd; 2nd==8, 224; 2nd== 12, 1*2; 2nd==15, 1st; 2nd==(28 OR 56 OR 84 OR 112 OR 120 OR 150 OR 168 OR 500), 1*2; 2nd==500 AND (3rd==5 OR 50), 1st
drug = 'metformin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('8 weeks')), 'number'] = 224
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('500 MG')), 'number'] = 112
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 11256), 'number'] = 6272
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 1), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 1), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 2), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 2), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 3), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 3), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 4), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 4), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 2) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 2) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 2) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 3) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 3) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 3) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 4) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 4) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 4) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 8), 'number'] = 224
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 12), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 12), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 12), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 15), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 15), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 28), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 28), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 28), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 56), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 56), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 56), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 84), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 84), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 84), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 112), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 112), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 112), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 120), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 120), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 120), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 150), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 150), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 150), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 168), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 168), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 168), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500) & (meds_found['number_a3'] == 5), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500) & (meds_found['number_a3'] == 5), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500) & (meds_found['number_a3'] == 50), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['number_a2'] == 500) & (meds_found['number_a3'] == 50), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('8*28')), 'number'] = 224
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a4'].isnull()), 'number_a2']).copy()

# methylprednisolone 63 is bogus; 3: 1st
drug = 'methylprednisolone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 63), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# metoprolol 3: 1*2
drug = 'metoprolol'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# midazolam if 3: 1st
drug = 'midazolam'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# mirtazapine if 3:1*2
drug = 'mirtazapine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# nefopam if 3, 1*2
drug = 'nefopam'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# nitrazepam 3:1*2 (unless 'ml', then 1st)
drug = 'nitrazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# olanzapine 3: 1*2 (unless 'TEMW'); NA: if '*', 1st*2nd; if 'ml', 1st
drug = 'olanzapine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('TEMW')), 'number'] = np.nan
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# orphenadrine 3: 1*2
drug = 'orphenadrine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# oxybutynin 3: if '*', 1*2; if '1 2*56', 112; if '1 pack of 56', 56; otherwise 1st; NA: if '*', 1st*2nd; if 'ml', 1st; if 'pack', 2nd
drug = 'oxybutynin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('1 2*56')), 'number'] = 112
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('1 pack of 56')), 'number'] = 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('pack', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('pack', na=False)), 'number_a2']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', regex=False, na=False)), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', regex=False, na=False)), 'number_a1']).copy() * (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', regex=False, na=False)), 'number_a2']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('patch', na=False)), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('patch', na=False)), 'number_a1']).copy()

# oxycodone 3: if '*', 1*2; 'TTO.' is nan; otherwise 1st; NA: if '*', 1st*2nd; if 'ml', 1st
drug = 'oxycodone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('TTO.')), 'number'] = np.nan
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (~meds_lost_missing['quantity'].str.contains('14/7', na=False)), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (~meds_lost_missing['quantity'].str.contains('14/7', na=False)), 'number_a1']).copy()

# paliperidone
# paroxetine 1 is 30; 3: 1*2 (unless 'ml', then 1st); NA: if 'ml', 1st; otherwise, 1st*2nd
drug = 'paroxetine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = 30
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# phenobarbital 1 is 28, 2 is 56; 3:1*2
drug = 'phenobarbital'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 2), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# phenytoin 3: 1*2
drug = 'phenytoin'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# pramipexole 3: if '*', 1*2 (otherwise 1st)
drug = 'pramipexole'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# prednisolone 3: when 'Pack of 56', 56; when '*', 1*2; otherwise 1st; NA: if 'ml', 1st; otherwise 1st*2nd
drug = 'prednisolone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('Pack of 56')), 'number'] = 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# prochlorperazine 42000 and 30000 are bogus; 3: when 'Pack of 56', 56; when '*', 1*2; otherwise 1st; NA: if 'ml' or 'ampoul', 1st; otherwise 1st*2nd
drug = 'prochlorperazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 42000), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 30000), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('Pack of 56')), 'number'] = 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ampoul', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ampoul', na=False)), 'number_a1']).copy()

# procyclidine 3: 1*2 (unless 'ml', then 1st)
drug = 'procyclidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# promazine 3: if '*' 1*2 (otherwise 1st)
drug = 'promazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# promethazine 3136 is 56, 2500 is 50; 3: 1*2 (unless 'ml', then 1st)
drug = 'promethazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 3136), 'number'] = 36
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 2500), 'number'] = 25
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# propantheline 3: 1*2
drug = 'propantheline'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# pyrilamine 
# quetiapine 3:if '*', 1*2; NA: if '*', 1st*2nd
drug = 'quetiapine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# ranitidine 3: 1*2 (unless 'ml', then 1st)
drug = 'ranitidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# sertraline if '2*28', 56; otherwise 1*2; NA: if'*', 1st*2nd; if 'ml', 1st; if 'Pack of 28', 28
drug = 'sertraline'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('2*28')), 'number'] = 56
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('Pack of 28', na=False)), 'number'] = 28

# sumatriptan 3: 1st (unless if '*', then 1*2); NA: if '*' or 'x', 1st*2nd; otherwise 1st
drug = 'sumatriptan'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('x', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('x', na=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('x', na=False)), 'number_a2']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('6', na=False)), 'number'] = 6

# temazepam 3: 1*2 (unless 'ml', then 1st)
drug = 'temazepam'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# theophylline 3: when '*', 1*2; otherwise 56; NA: if '*', 1st*2nd; if 'ml', 1st; if 'days', 56
drug = 'theophylline'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('days', na=False)), 'number'] = 56

# thioridazine
# tizanidine; NA: if 'ml', 1st
drug = 'tizanidine'
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# tobramycin
# tolterodine if 'mnth' OR 'MONTHS', 1st*28; 3:1*2
drug = 'tolterodine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('mnth')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('mnth')), 'number_a1']).copy() * 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTHS')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTHS')), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', regex=False, na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', regex=False, na=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', regex=False, na=False)), 'number_a2']).copy()

# tramadol 'mnth' is 1st*60; 3: if '*', 1*2; otherwise 1
drug = 'tramadol'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('mnth')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('mnth')), 'number_a1']).copy() * 60
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# trandolapril 1 is 28; 3: if '*', 1*2; otherwise 1
drug = 'trandolapril'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', na=False, regex=False)), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# trazodone 'month' or 'pack' is 28; 3: if '*', 1*2; otherwise 1
drug = 'trazodone'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('month')), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('pack')), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# triamcinolone 3: 1st
drug = 'triamcinolone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# trifluoperazine 3: 1st (unless if '*', then 1*2)
drug = 'trifluoperazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] < 10) & (~meds_found['number_a2'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] < 10) & (~meds_found['number_a2'].isnull()), 'number_a1']) * ((meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] < 10) & (~meds_found['number_a2'].isnull()), 'number_a2'])).copy()

# trihexyphenidyl 3: 1*2
drug = 'trihexyphenidyl'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# triprolidine
# valproate '2 MONTHS' is 56; 3: 1*2 (unless 'ml', then 1st)
drug = 'valproate'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('2 MONTHS')), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('ml', na = False)), 'number_a1']).copy()

# venlafaxine 3: 1*2
drug = 'venlafaxine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# warfarin '2 MONTHS' is 56; 3:1*2; NA: if 'ml', 1st; otherwise 1st*2nd
drug = 'warfarin'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('2 MONTHS')), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['number_a2'] == 28), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['number_a2'] == 28), 'number_a1']).copy() * (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['number_a2'] == 28), 'number_a2']).copy()
meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['number_a2'] == 42), 'number'] = (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['number_a2'] == 42), 'number_a1']).copy() * (meds_lost_missing.loc[(meds_lost_missing['aa_name'] == drug) & (meds_lost_missing['number_a2'] == 42), 'number_a2']).copy()

# zolmitriptan 3: 1*2
drug = 'zolmitriptan'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# zuclopenthixol 3: if 'x', 1*2; otherwise 1; NA: if '10', 10; otherwise 1
drug = 'zuclopenthixol'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 1
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('10', na=False)), 'number'] = 10

# clomipramine 'MONTH' is 28; 3136 is 56; 3: 1st (unless if '*', then 1*2)
drug = 'clomipramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTH')), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 3136), 'number'] = 56
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# metoclopramide if 'months' or 'box', 28*1st; 1764 is 40; 3600 is 60; 3: 'Pack of 42' is 42; '*', 1*2; otherwise 1st; if with paracetamol, 5mg
drug = 'metoclopramide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('months')), 'number'] = 28 * (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('months')), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 1764), 'number'] = 40
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 3600), 'number'] = 60
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('Pack of 42')), 'number'] = 42
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# chlorphenamine 3600 is 60; 3: '1 pack of 5' is 1*2; '*' is 1*2; otherwise 1st
drug = 'chlorphenamine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['number_a1'] == 3600), 'number'] = 60
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('1 pack of 5')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('1 pack of 5')), 'number_a1']) * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('1 pack of 5')), 'number_a2']).copy()

# carbidopa/levodopa 3: 1st (unless if '*', then 1*2)
drug = 'carbidopa/levodopa'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# carbidopa/levodopa 3: 1st (unless if '*', then 1*2)
drug = 'carbidopa'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# chlortalidone 3: 1*2
drug = 'chlortalidone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# codeine 3: 'x' or '*' is 1*2; otherwise 1st
drug = 'codeine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number_a2']).copy()

# diphenhydramine 3: 1*2
drug = 'diphenhydramine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# diphenoxylate 'pack' is 20
drug = 'diphenoxylate'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('pack')), 'number'] = 20

# atropine 'pack' is 20
drug = 'atropine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('pack')), 'number'] = 20

# entacapone 3: 1st
drug = 'entacapone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# fluphenazine 3: 'x' is 1*2; otherwise 1st; NA: if 'X', 1st*2nd; otherwise 1st
drug = 'fluphenazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('x')), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number_a2']).copy()

# furosemide 'MONTHS' is 1st*28; 3: *' is 1*2; otherwise 1st
drug = 'furosemide'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTHS')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTHS')), 'number_a1']).copy() * 28
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# lansoprazole 3: '*' is 1*2; otherwise 2nd; NA: if '*', 1st*2nd; otherwise 28
drug = 'lansoprazole'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = 28
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex = False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()

# levodopa 3: '*' is 1*2; otherwise 1st
drug = 'levodopa'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# morphine 'pack of 20' is 1st*20; if '*', 1*2; otherwise 1st
drug = 'morphine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('pack of 20')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('pack of 20')), 'number_a1']).copy() * 20
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# nifedipine 3: if '*', 1*2, otherwise 1st
drug = 'nifedipine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# perphenazine 3: 1st
drug = 'perphenazine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# pseudoephedrine 3: 1st; NA: if 'ml', 1st
drug = 'pseudoephedrine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('ml', na=False)), 'number_a1']).copy()

# methadone
# methotrexate 'MONTHS' is 1st*24; 3: if '*', 1*2, otherwise 1st
drug = 'methotrexate'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTHS')), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTHS')), 'number_a1']).copy() * 24
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()) & (meds_found['quantity'].str.contains('*', regex = False)), 'number_a2']).copy()

# paracetamol/codeine 'pack' or 'MONTH' is nan
drug = 'paracetamol/codeine'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('MONTH')), 'number'] = np.nan
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['quantity'].str.contains('pack')), 'number'] = np.nan

# risperidone 3: 1*2
drug = 'risperidone'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy() * (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a2']).copy()

# rotigotine 3: 1st
drug = 'rotigotine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# pethidine 3: 1st
drug = 'pethidine'
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['number_a3'].isnull()), 'number_a1']).copy()

# ipratropium
    # when with salbutamol, take 1st if not greater than 5
    # if quantity=NA and 'inhaler' in prescription, 200
    # ipratropium, ~nebuliser:
    # when (1 or 100 or 200), 200; when (2 or 400), 400; (600 or 3), 600; , (800 or 4), 800; 120 is 120
    # ipratropium, nebuliser:
    # when contains (28 or 40 or 60 or 80 or 120 or 100 or 112), is the number
    # when contains "3 packs of 60", 180
    # NA: if '120', 120; if '200', 200; if '100', 100;
        # 1st: if 1st==1, 200; if 1st==2, 400  
drug = 'ipratropium'
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('inhaler')) & (meds_found['quantity'].isnull()), 'number'] = 200
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 1), 'number'] = 200
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 100), 'number'] = 200
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 200), 'number'] = 200
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 2), 'number'] = 400
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 400), 'number'] = 400
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 3), 'number'] = 600
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 600), 'number'] = 600
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 4), 'number'] = 800
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 800), 'number'] = 800
meds_found.loc[(meds_found['aa_name'] == drug) & (~meds_found['prescription'].str.contains('nebuliser')) & (meds_found['number_a1'] == 120), 'number'] = 120
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('28')), 'number'] = 28
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('40')), 'number'] = 40
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('60')), 'number'] = 60
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('80')), 'number'] = 80
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('100')), 'number'] = 100
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('112')), 'number'] = 112
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('nebuliser')) & (meds_found['quantity'].str.contains('120')), 'number'] = 120
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('salbutamol', na=False)) & (meds_found['number_a1'] <= 5), 'number'] = (meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('salbutamol', na=False)) & (meds_found['number_a1'] <= 5), 'number_a1']).copy() * 60
meds_found.loc[(meds_found['aa_name'] == drug) & (meds_found['prescription'].str.contains('salbutamol', na=False)) & (meds_found['number_a1'] > 5), 'number'] = np.nan
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug), 'number_a1']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('x', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('x', na=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('x', na=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('X', na=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a1']).copy() * (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('*', na=False, regex=False)), 'number_a2']).copy()
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('120', na=False)), 'number'] = 120
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('200', na=False)), 'number'] = 200
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['quantity'].str.contains('100', na=False)), 'number'] = 100
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 1), 'number'] = 200
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['number_a1'] == 2), 'number'] = 400
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['prescription'].str.contains('salbutamol', na=False)) & (meds_lost_unfound['number_a1'] <= 5), 'number'] = (meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['prescription'].str.contains('salbutamol', na=False)) & (meds_lost_unfound['number_a1'] <= 5), 'number_a1']).copy() * 60
meds_lost_unfound.loc[(meds_lost_unfound['aa_name'] == drug) & (meds_lost_unfound['prescription'].str.contains('salbutamol', na=False)) & (meds_lost_unfound['number_a1'] > 5), 'number'] = np.nan

# join the three data frames
meds_found['date'] = pd.to_datetime(meds_found['date'], format = '%d/%m/%Y')
meds_lost_missing['date'] = pd.to_datetime(meds_lost_missing['date'], format = '%d/%m/%Y')
meds_lost_unfound['date'] = pd.to_datetime(meds_lost_unfound['date'], format = '%d/%m/%Y')
meds = (pd.concat([meds_found, meds_lost_missing, meds_lost_unfound])).sort_values(by='date')
meds.index = (list(range(len(meds))))
del meds_found
del meds_lost
del meds_lost_missing
del meds_lost_unfound
print('Quantities done.')









### C. Drug combinations


# In some cases, a prescription contains several anticholinergic drugs. To simplify analyses, the code below will separate each such prescription
# into individual compounds of a combination medicine, so that each compound occupies a separate row.


# subset the rows where an anticholinergic occur in combination with another one
meds.loc[:, 'aa_count'] = (meds.loc[:, 'aa_count']).copy().astype(float)
combo_frame = (meds.loc[meds['aa_count'] > 1]).copy()

# create new columns that will be used for the individual compounds of prescriptions
combo_frame['combo_drug_1'] = np.nan
combo_frame['combo_drug_2'] = np.nan
combo_frame['combo_drug_3'] = np.nan
combo_frame['combo_dose_1'] = np.nan
combo_frame['combo_dose_2'] = np.nan
combo_frame['combo_dose_3'] = np.nan
combo_frame['combo_dose_units_1'] = 'mg'
combo_frame['combo_dose_units_2'] = 'mg'
combo_frame['combo_dose_units_3'] = 'mg'


## create new columns for each drug in the prescription and create separate number and concentration columns


# code for checking the number of combinations
#example = combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(guaifenesin)', regex=True)]
#test = example.loc[example['combo_dose_1'].isnull()]
#example.dose_a1_number.value_counts()
#example.dose_a2_number.value_counts()

#test = example.loc[(example['prescription'].str.contains(r'([^a-zA-Z]+|^)(guaifenesin)', regex=True)) & \
#                             (~example['prescription'].str.contains(r'([^a-zA-Z]+|^)(buclizine)', regex=True)) & \
#                                 (example['prescription'].str.contains(r'([^a-zA-Z]+|^)(d)', regex=True))]
#test.dose_a1_number.value_counts()
#test.dose_a2_number.value_counts()


# carbidopa/levodopa; carbidopa/levodopa/entacapone
# carbi/levo always in combos: 12.5/50, 18.75/75, 25/100, 31.25/125, 37.5/150, 43.75/175, 50/200, 62.5/250 entacapone is always 200; NA: 62.5, 25/100, 12.5/50, 10/100
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(carbidopa)', regex=True), 'combo_drug_1'] = 'carbidopa'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(levodopa)', regex=True)), 'combo_drug_2'] = 'levodopa'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(entacapone)', regex=True)), 'combo_drug_3'] = 'entacapone'
combo_frame.loc[combo_frame['combo_drug_3'] == 'entacapone', 'combo_dose_3'] = 200
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 10) | (combo_frame['dose_a2_number'] == 10)), 'combo_dose_1'] = 10
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 10) | (combo_frame['dose_a2_number'] == 10)), 'combo_dose_2'] = 100
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 12.5) | (combo_frame['dose_a2_number'] == 12.5)), 'combo_dose_1'] = 12.5
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 12.5) | (combo_frame['dose_a2_number'] == 12.5)), 'combo_dose_2'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 18.75) | (combo_frame['dose_a2_number'] == 18.75)), 'combo_dose_1'] = 18.75
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 18.75) | (combo_frame['dose_a2_number'] == 18.75)), 'combo_dose_2'] = 75
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 25) | (combo_frame['dose_a2_number'] == 25)), 'combo_dose_1'] = 25
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 25) | (combo_frame['dose_a2_number'] == 25)), 'combo_dose_2'] = 100
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 31.25) | (combo_frame['dose_a2_number'] == 31.25)), 'combo_dose_1'] = 31.25
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 31.25) | (combo_frame['dose_a2_number'] == 31.25)), 'combo_dose_2'] = 125
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 37.5) | (combo_frame['dose_a2_number'] == 37.5)), 'combo_dose_1'] = 37.5
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 37.5) | (combo_frame['dose_a2_number'] == 37.5)), 'combo_dose_2'] = 150
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 43.75) | (combo_frame['dose_a2_number'] == 43.75)), 'combo_dose_1'] = 43.75
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 43.75) | (combo_frame['dose_a2_number'] == 43.75)), 'combo_dose_2'] = 175
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 50) | (combo_frame['dose_a2_number'] == 50)), 'combo_dose_1'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 50) | (combo_frame['dose_a2_number'] == 50)), 'combo_dose_2'] = 200
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 62.5) | (combo_frame['dose_a2_number'] == 62.5)), 'combo_dose_1'] = 62.5
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & ((combo_frame['dose_a1_number'] == 62.5) | (combo_frame['dose_a2_number'] == 62.5)), 'combo_dose_2'] = 250
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('10')), 'combo_dose_1'] = 10
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('10')), 'combo_dose_2'] = 100
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('62.5')), 'combo_dose_1'] = 62.5
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('62.5')), 'combo_dose_2'] = 250
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('25')), 'combo_dose_1'] = 25
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('25')), 'combo_dose_2'] = 100
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('12.5')), 'combo_dose_1'] = 12.5
combo_frame.loc[(combo_frame['combo_drug_1'] == 'carbidopa') & (combo_frame['dose_a1_number'].isnull()) & (combo_frame['prescription'].str.contains('12.5')), 'combo_dose_2'] = 50

# atropine/diphenoxylate: first row 0.025mg and a 2nd column for diphenoxylate 2.5mg; 0.6 first row is ok; others are 1% eye drops); NA: 0.025 is mg;
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(atropine)', regex=True), 'combo_drug_1'] = 'atropine'
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(atropine)', regex=True), 'combo_drug_2'] = 'diphenoxylate'
combo_frame.loc[combo_frame['combo_drug_1'] == 'atropine', 'combo_dose_1'] = 0.025
combo_frame.loc[combo_frame['combo_drug_1'] == 'atropine', 'combo_dose_2'] = 2.5

# atenolol/chlortalidone (100/25, 50/12.5); atenolol/nifedipine (50/20)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(atenolol)', regex=True), 'combo_drug_1'] = 'atenolol'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(atenolol)', regex=True)) & combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(chlortalidone)', regex=True), 'combo_drug_2'] = 'chlortalidone'
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(nifedipine)', regex=True), 'combo_drug_2'] = 'nifedipine'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'atenolol') & (combo_frame['combo_drug_2'] == 'chlortalidone') & ((combo_frame['dose_a1_number'] == 25) | (combo_frame['dose_a2_number'] == 25)), 'combo_dose_1'] = 100
combo_frame.loc[(combo_frame['combo_drug_1'] == 'atenolol') & (combo_frame['combo_drug_2'] == 'chlortalidone') & ((combo_frame['dose_a1_number'] == 25) | (combo_frame['dose_a2_number'] == 25)), 'combo_dose_2'] = 25
combo_frame.loc[(combo_frame['combo_drug_1'] == 'atenolol') & (combo_frame['combo_drug_2'] == 'chlortalidone') & ((combo_frame['dose_a1_number'] == 12.5) | (combo_frame['dose_a2_number'] == 12.5)), 'combo_dose_1'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'atenolol') & (combo_frame['combo_drug_2'] == 'chlortalidone') & ((combo_frame['dose_a1_number'] == 12.5) | (combo_frame['dose_a2_number'] == 12.5)), 'combo_dose_2'] = 12.5
combo_frame.loc[(combo_frame['combo_drug_1'] == 'atenolol') & (combo_frame['combo_drug_2'] == 'nifedipine') & ((combo_frame['dose_a1_number'] == 50) | (combo_frame['dose_a2_number'] == 50)), 'combo_dose_1'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'atenolol') & (combo_frame['combo_drug_2'] == 'nifedipine') & ((combo_frame['dose_a1_number'] == 20) | (combo_frame['dose_a2_number'] == 20)), 'combo_dose_2'] = 20

# codeine/paracetamol/buclizine (8/500/6.25)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(codeine)', regex=True), 'combo_drug_1'] = 'codeine'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(codeine)', regex=True)) & (combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(buclizine)', regex=True)), 'combo_drug_2'] = 'buclizine'
combo_frame.loc[combo_frame['combo_drug_1'] == 'codeine', 'combo_dose_1'] = 8
combo_frame.loc[combo_frame['combo_drug_1'] == 'codeine', 'combo_dose_2'] = 6.25

# diphenhydramine/dextromethorphan are invalid
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(diphenhydramine)', regex=True), 'dose'] = np.nan
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(diphenhydramine)', regex=True), 'dose_units'] = np.nan

# ephedrine/chlorphenamine; pseudoephedrine/chlorphenamine
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(chlorphenamine)', regex=True), 'combo_drug_1'] = 'chlorphenamine'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(chlorphenamine)', regex=True)) & combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(ephedrine)', regex=True), 'combo_drug_2'] = 'ephedrine'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(chlorphenamine)', regex=True)) & combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(pseudoephedrine)', regex=True), 'combo_drug_2'] = 'pseudoephedrine'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'chlorphenamine') & (combo_frame['combo_drug_2'] == 'ephedrine'), 'combo_dose_1'] = 10
combo_frame.loc[(combo_frame['combo_drug_1'] == 'chlorphenamine') & (combo_frame['combo_drug_2'] == 'ephedrine'), 'combo_dose_2'] = 15
combo_frame.loc[(combo_frame['combo_drug_1'] == 'chlorphenamine') & (combo_frame['combo_drug_2'] == 'pseudoephedrine'), 'combo_dose_1'] = 2
combo_frame.loc[(combo_frame['combo_drug_1'] == 'chlorphenamine') & (combo_frame['combo_drug_2'] == 'pseudoephedrine'), 'combo_dose_2'] = 30
combo_frame.loc[(combo_frame['combo_drug_1'] == 'chlorphenamine') & (combo_frame['combo_drug_2'] == 'pseudoephedrine'), 'combo_dose_units_1'] = 'mg/5ml'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'chlorphenamine') & (combo_frame['combo_drug_2'] == 'pseudoephedrine'), 'combo_dose_units_2'] = 'mg/5ml'

# ergotamine/cyclizine (2/100); cyclizine/morphine
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(cyclizine)', regex=True), 'combo_drug_1'] = 'cyclizine'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(cyclizine)', regex=True)) & (combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(ergotamine)', regex=True)), 'combo_drug_2'] = 'ergotamine'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(cyclizine)', regex=True)) & (combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(morphine)', regex=True)), 'combo_drug_2'] = 'morphine'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'ergotamine'), 'combo_dose_1'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'ergotamine'), 'combo_dose_2'] = 2
combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'morphine'), 'combo_dose_1'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'morphine'), 'combo_dose_2'] = (combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'morphine'), 'dose_a1_number']).copy()
combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'morphine'), 'dose_units'] = 'mg/1ml'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'cyclizine') & (combo_frame['combo_drug_2'] == 'morphine'), 'dose_units'] = 'mg/1ml'

# guaifenesin/pseudoephedrine (100/30/5 mg/mg/5ml)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(guaifenesin)', regex=True), 'combo_drug_1'] = 'guaifenesin'
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(guaifenesin)', regex=True), 'combo_drug_2'] = 'pseudoephedrine'
combo_frame.loc[combo_frame['combo_drug_1'] == 'guaifenesin', 'combo_dose_1'] = 100
combo_frame.loc[combo_frame['combo_drug_1'] == 'guaifenesin', 'combo_dose_2'] = 30
combo_frame.loc[combo_frame['combo_drug_1'] == 'guaifenesin', 'combo_dose_units_1'] = 'mg/5ml'
combo_frame.loc[combo_frame['combo_drug_1'] == 'guaifenesin', 'combo_dose_units_2'] = 'mg/5ml'

# hydrocortisone/gentamicin is cream
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(hydrocortisone)', regex=True), 'dose'] = np.nan
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(hydrocortisone)', regex=True), 'dose_units'] = np.nan

# lansoprazole/amoxicillin
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(lansoprazole)', regex=True), 'combo_drug_1'] = 'lansoprazole'
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(lansoprazole)', regex=True), 'combo_drug_2'] = 'amoxicillin'
combo_frame.loc[combo_frame['combo_drug_1'] == 'lansoprazole', 'combo_dose_1'] = 30
combo_frame.loc[combo_frame['combo_drug_1'] == 'lansoprazole', 'combo_dose_2'] = 500

# nortriptyline/fluphenazine (10/0.5)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(nortriptyline)', regex=True), 'combo_drug_1'] = 'nortriptyline'
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(nortriptyline)', regex=True), 'combo_drug_2'] = 'fluphenazine'
combo_frame.loc[combo_frame['combo_drug_1'] == 'nortriptyline', 'combo_dose_1'] = 10
combo_frame.loc[combo_frame['combo_drug_1'] == 'nortriptyline', 'combo_dose_2'] = 0.5

# amitriptyline/perphenazine (10/2, 25/2)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(amitriptyline)', regex=True), 'combo_drug_1'] = 'amitriptyline'
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(amitriptyline)', regex=True), 'combo_drug_2'] = 'perphenazine'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'amitriptyline') & ((combo_frame['dose_a1_number'] == 10) | (combo_frame['dose_a2_number'] == 10)), 'combo_dose_1'] = 10
combo_frame.loc[(combo_frame['combo_drug_1'] == 'amitriptyline') & ((combo_frame['dose_a1_number'] == 10) | (combo_frame['dose_a2_number'] == 10)), 'combo_dose_2'] = 2
combo_frame.loc[(combo_frame['combo_drug_1'] == 'amitriptyline') & ((combo_frame['dose_a1_number'] == 25) | (combo_frame['dose_a2_number'] == 25)), 'combo_dose_1'] = 25
combo_frame.loc[(combo_frame['combo_drug_1'] == 'amitriptyline') & ((combo_frame['dose_a1_number'] == 25) | (combo_frame['dose_a2_number'] == 25)), 'combo_dose_2'] = 2

# phenytoin is invalid
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(phenytoin)', regex=True), 'dose'] = np.nan
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(phenytoin)', regex=True), 'dose_units'] = np.nan

# prednisolone is invalid
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(prednisolone)', regex=True), 'dose'] = np.nan
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(prednisolone)', regex=True), 'dose_units'] = np.nan

# triamcinolone is invalid
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triamcinolone)', regex=True), 'dose'] = np.nan
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triamcinolone)', regex=True), 'dose_units'] = np.nan

# triamterene/furosemide (50/40); triamterene/chlortalidone (50/50)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triamterene)', regex=True), 'combo_drug_1'] = 'triamterene'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triamterene)', regex=True)) & combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(furosemide)', regex=True), 'combo_drug_2'] = 'furosemide'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triamterene)', regex=True)) & combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(chlortalidone)', regex=True), 'combo_drug_2'] = 'chlortalidone'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'triamterene'), 'combo_dose_1'] = 50
combo_frame.loc[(combo_frame['combo_drug_1'] == 'triamterene') & (combo_frame['combo_drug_2'] == 'furosemide'), 'combo_dose_2'] = 40
combo_frame.loc[(combo_frame['combo_drug_1'] == 'triamterene') & (combo_frame['combo_drug_2'] == 'chlortalidone'), 'combo_dose_2'] = 50

# triprolidine/pseudoephedrine (2nd/1st)
combo_frame.loc[combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triprolidine)', regex=True), 'combo_drug_1'] = 'triprolidine'
combo_frame.loc[(combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(triprolidine)', regex=True)) & (combo_frame['prescription'].str.contains(r'([^a-zA-Z]+|^)(pseudoephedrine)', regex=True)), 'combo_drug_2'] = 'pseudoephedrine'
combo_frame.loc[(combo_frame['combo_drug_1'] == 'triprolidine'), 'combo_dose_1'] = (combo_frame.loc[(combo_frame['combo_drug_1'] == 'triprolidine'), 'dose_a2_number']).copy()
combo_frame.loc[(combo_frame['combo_drug_1'] == 'triprolidine'), 'combo_dose_2'] = (combo_frame.loc[(combo_frame['combo_drug_1'] == 'triprolidine'), 'dose_a1_number']).copy()

# convert to long format (only the rows with several drugs) so that each drug within a prescription is in its own row
# first drug of the combination
combo_frame_1 = (combo_frame.loc[~combo_frame['combo_drug_1'].isnull()]).copy()
combo_frame_1.loc[:, 'aa_name'] = (combo_frame_1.loc[:, 'combo_drug_1']).copy()
combo_frame_1.loc[:, 'dose'] = (combo_frame_1.loc[:, 'combo_dose_1']).copy()
combo_frame_1.loc[:, 'dose_units'] = (combo_frame_1.loc[:, 'combo_dose_units_1']).copy()
combo_frame_1.drop(['combo_drug_1','combo_drug_2','combo_drug_3','combo_dose_1','combo_dose_2','combo_dose_3','combo_dose_units_1','combo_dose_units_2','combo_dose_units_3'], axis=1, inplace=True)
# second drug of the combination
combo_frame_2 = (combo_frame.loc[~combo_frame['combo_drug_2'].isnull()]).copy()
combo_frame_2.loc[:, 'aa_name'] = (combo_frame_2.loc[:, 'combo_drug_2']).copy()
combo_frame_2.loc[:, 'dose'] = (combo_frame_2.loc[:, 'combo_dose_2']).copy()
combo_frame_2.loc[:, 'dose_units'] = (combo_frame_2.loc[:, 'combo_dose_units_2']).copy()
combo_frame_2.drop(['combo_drug_1','combo_drug_2','combo_drug_3','combo_dose_1','combo_dose_2','combo_dose_3','combo_dose_units_1','combo_dose_units_2','combo_dose_units_3'], axis=1, inplace=True)
# third drug of the combination
combo_frame_3 = (combo_frame.loc[~combo_frame['combo_drug_3'].isnull()]).copy()
combo_frame_3.loc[:, 'aa_name'] = (combo_frame_3.loc[:, 'combo_drug_3']).copy()
combo_frame_3.loc[:, 'dose'] = (combo_frame_3.loc[:, 'combo_dose_3']).copy()
combo_frame_3.loc[:, 'dose_units'] = (combo_frame_3.loc[:, 'combo_dose_units_3']).copy()
combo_frame_3.drop(['combo_drug_1','combo_drug_2','combo_drug_3','combo_dose_1','combo_dose_2','combo_dose_3','combo_dose_units_1','combo_dose_units_2','combo_dose_units_3'], axis=1, inplace=True)
# combine the different compounds into a single data frame ('combo_frame_long' will now contain drug combinations as separate rows as opposed to one row)
combo_frame_long = pd.concat([combo_frame_1, combo_frame_2, combo_frame_3])
combo_frame_long['combo_drug'] = 1 # new column so that I will later know that these prescriptions were parts of combinations
# combine the new data frame with the main data frame
meds = (meds.loc[meds['aa_count'] <= 1]).copy()
meds = pd.concat([meds, combo_frame_long])
meds.loc[meds['combo_drug'].isnull(), 'combo_drug'] = 0
del combo_frame

# for the drugs that also appear as combos, supplement the missing doses by manual checking just like for other drugs in section A4
drug = 'atenolol' # NA: 50,100,25 are mg
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('25')), 'dose'] = 25
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('50')), 'dose'] = 50
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('100')), 'dose'] = 100
drug = 'nifedipine' # NA:20mg, 10mg, 40mg, 60mg
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('10')), 'dose'] = 10
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('20')), 'dose'] = 20
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('40')), 'dose'] = 40
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('60')), 'dose'] = 60
drug = 'codeine' # NA's: 30(mg), 8(mg), 12.8(mg), 15(mg), 60(mg), yellow=8mg, pink=8mg
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('30')), 'dose'] = 30
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('8')), 'dose'] = 8
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('12.8')), 'dose'] = 12.8
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('15')), 'dose'] = 15
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('60')), 'dose'] = 60
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('yellow')), 'dose'] = 8
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('pink')), 'dose'] = 8
drug = 'buclizine'
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('pink')), 'dose'] = 6.25
drug = 'ergotamine' # NA:2mg
meds.loc[(meds['aa_name'] == drug), 'dose'] = 2 
drug = 'morphine' # NA:91.6 when with kaolin
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('kaolin')), 'dose'] = 91.6 
drug = 'lansoprazole' # NA:15,30
meds.loc[(meds['aa_name'] == drug) & (meds['dose_a1_number'] == 15), 'dose'] = 15
meds.loc[(meds['aa_name'] == drug) & (meds['dose_a1_number'] == 30), 'dose'] = 30
drug = 'nortriptyline' # NA:10
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('10')), 'dose'] = 10
drug = 'triamterene' # NA:all 50
meds.loc[(meds['aa_name'] == drug), 'dose'] = 50
drug = 'furosemide' # NA:40,20,80
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('20')), 'dose'] = 20
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('40')), 'dose'] = 40
meds.loc[(meds['aa_name'] == drug) & (meds['prescription'].str.contains('80')), 'dose'] = 80
print ("Combinations done.")









### D. DDD

## Automatically assign DDD's to each drug.

ddd = (drug_list[['drug','ddd']]).copy() # oral tablet is the default dose (some will be manually altered below)
ddd.columns = ['aa_name','ddd']
ddd = ddd.loc[(ddd['ddd'].notnull()) & (ddd['aa_name'] != 'carbidopa/levodopa')] # because carbidopa/levodopa doesn't exist anymore
meds = pd.merge(meds, ddd, on='aa_name', how='outer')

## For those that have the DDD different for various administration routes, manually correct below.

# bromocriptine if dose==(5 OR 10), 40
meds.loc[(meds['aa_name'] == 'bromocriptine') & (meds['dose'] == 5), 'ddd'] = 40
meds.loc[(meds['aa_name'] == 'bromocriptine') & (meds['dose'] == 10), 'ddd'] = 40
# clindamycin if contains 'injection', 1800
meds.loc[(meds['aa_name'] == 'clindamycin') & (meds['prescription'].str.contains('injection', na=False)), 'ddd'] = 1800
# fentanyl if contains 'transdermal', 1.2
meds.loc[(meds['aa_name'] == 'fentanyl') & (meds['prescription'].str.contains('transdermal', na=False)), 'ddd'] = 1.2
# fluphenazine if contains 'ml', 1.00
meds.loc[(meds['aa_name'] == 'fluphenazine') & (meds['prescription'].str.contains('ml', na=False)), 'ddd'] = 1
# glycopyrronium if contains 'inj', 0.3
meds.loc[(meds['aa_name'] == 'glycopyrronium') & (meds['prescription'].str.contains('inj', na=False)), 'ddd'] = 0.3
# haloperidol if contains 'ml', 3.3
meds.loc[(meds['aa_name'] == 'haloperidol') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 3.3
# ipratropium if contains 'ml', 0.3
meds.loc[(meds['aa_name'] == 'ipratropium') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 0.3
# isosorbide if prescription_old contains either of these: mono,ismo,isotard,eumon,modisal,zemon,carmil,chemydur,isib,monomax,monomil,monosorb,relosorb,tardisc,
    #trangina,xismox,elantan,isodur,nyzamac, 40
    # if the above is not true: if contains lingual, 20; otherwise 60
meds.loc[(meds['aa_name'] == 'isosorbide') & (meds['prescription_old'].str.contains(r'(mono|ismo|isotard|eumon|modisal|zemon|carmil|chemydur|isib|monomax|monomil|monosorb|relosorb|tardisc|trangina|xismox|elantan|isodur|nyzamac)', na=False)), 'ddd'] = 40
meds.loc[(meds['aa_name'] == 'isosorbide') & (~meds['prescription_old'].str.contains(r'(mono|ismo|isotard|eumon|modisal|zemon|carmil|chemydur|isib|monomax|monomil|monosorb|relosorb|tardisc|trangina|xismox|elantan|isodur|nyzamac)', na=False)), 'ddd'] = 60
meds.loc[(meds['aa_name'] == 'isosorbide') & (~meds['prescription_old'].str.contains(r'(mono|ismo|isotard|eumon|modisal|zemon|carmil|chemydur|isib|monomax|monomil|monosorb|relosorb|tardisc|trangina|xismox|elantan|isodur|nyzamac)', na=False)) & (meds['prescription'].str.contains('lingual', na=False)), 'ddd'] = 20
# levomepromazine if contains 'ml', 100
meds.loc[(meds['aa_name'] == 'levomepromazine') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 100
# levofloxacin if contains 'infusion', 500
meds.loc[(meds['aa_name'] == 'levofloxacin') & (meds['prescription'].str.contains('infusion', na=False)), 'ddd'] = 500
# methylprednisolone if contains 'ml', 20
meds.loc[(meds['aa_name'] == 'methylprednisolone') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 20
# morphine if contains 'inj', 30
meds.loc[(meds['aa_name'] == 'morphine') & (meds['prescription'].str.contains('inj', na=False)), 'ddd'] = 30
# oxybutynin if contains 'transdermal', 3.9
meds.loc[(meds['aa_name'] == 'oxybutynin') & (meds['prescription'].str.contains('transdermal', na=False)), 'ddd'] = 3.9
# oxycodone if contains 'inj', 30
meds.loc[(meds['aa_name'] == 'oxycodone') & (meds['prescription'].str.contains('inj', na=False)), 'ddd'] = 30
# paliperidone if contains 'ml', 2.5
meds.loc[(meds['aa_name'] == 'paliperidone') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 2.5
# pipotiazine all injections
meds.loc[(meds['aa_name'] == 'pipotiazine'), 'ddd'] = 5
# prochlorperazine if contains 'inj', 50
meds.loc[(meds['aa_name'] == 'prochlorperazine') & (meds['prescription'].str.contains('inj', na=False)), 'ddd'] = 50
# sumatriptan if contains 'ml', 6
meds.loc[(meds['aa_name'] == 'sumatriptan') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 6
# tiotropium if dose==0.0025, 0.005
meds.loc[(meds['aa_name'] == 'tiotropium') & (meds['dose'] == 0.0025), 'ddd'] = 0.005
# tobramycin if contains 'nebuliser', 300; if contains 'inj', 240
meds.loc[(meds['aa_name'] == 'tobramycin') & (meds['prescription'].str.contains('nebuliser', na=False)), 'ddd'] = 300
meds.loc[(meds['aa_name'] == 'tobramycin') & (meds['prescription'].str.contains('nebuliser', na=False)), 'ddd'] = 240
# zuclopenthixol if contains 'ml', 15
meds.loc[(meds['aa_name'] == 'zuclopenthixol') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 15
# lithium can be carbonate or citrate
meds.loc[(meds['aa_name'] == 'lithium') & (~meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 1773.36
meds.loc[(meds['aa_name'] == 'lithium') & (meds['prescription'].str.contains('ml', na = False)), 'ddd'] = 5038.152



## In the manual corrections, some drugs were incorrectly assigned the dose or dose units; correct those.
# some have 'mg/xml' dose, but the dose was assigned as 'mg'
meds.loc[(meds['prescription'].str.contains('ml', na=False)) & (meds['dose_units']=='mg'), 'dose_units'] = 'mg/5ml'
# some have 'mg' dose, but the dose was assigned as 'mg/xml'
meds.loc[(~meds['prescription'].str.contains('ml', na=False)) & (meds['dose_units']!='mg') & (~meds['prescription'].str.contains('inj', na=False)) & \
         (~meds['prescription'].str.contains('crm', na=False)), 'dose_units'] = 'mg'
# some have digit in quantity column, but no assigned number; manually correct
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('patch', na = False)), 'number'] = (meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('patch', na = False)), 'number_a1']).copy()
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('x60', na = False)), 'number'] = (meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('x60', na = False)), 'number_a2']).copy()
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('56 tablet', na = False)), 'number'] = 56
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('2*56', na = False)), 'number'] = 108
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('100 ml', na = False)), 'number'] = 100
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('150 ml', na = False)), 'number'] = 150
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('630 ml', na = False)), 'number'] = 630
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('600 ml', na = False)), 'number'] = 600
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('28 tablet', na = False)), 'number'] = 28
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('4*28', na = False)), 'number'] = 4*28
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('10 ampoule', na = False)), 'number'] = 10
meds.loc[(~meds['number_a1'].isnull()) & (meds['number'].isnull()) & (meds['prescription'].str.contains('30 - Pack', na = False)), 'number'] = 30
# if "pack of" or "packs of", 1st*2nd
meds.loc[meds['quantity'].str.contains('pack of', na = False), 'number'] = (meds.loc[meds['quantity'].str.contains('pack of', na = False), 'number_a1']).copy() * (meds.loc[meds['quantity'].str.contains('pack of', na = False), 'number_a2']).copy()
meds.loc[meds['quantity'].str.contains('packs of', na = False), 'number'] = (meds.loc[meds['quantity'].str.contains('packs of', na = False), 'number_a1']).copy() * (meds.loc[meds['quantity'].str.contains('packs of', na = False), 'number_a2']).copy()








## Normalize dosage units to mg or ml/mg
conversion_number = 1/((meds['dose_units'].str.extract(r'([\d\.]+)')).astype(float)) # extract number from dose_units column (e.g. mg/5ml --> 1/5)
conversion_number.columns = ['conversion_number'] # change column name
meds = meds.reset_index(drop=True)
conversion_number = conversion_number.reset_index(drop=True)
meds = pd.concat([meds, conversion_number], axis=1)
meds.loc[meds['conversion_number'].isnull(), 'conversion_number'] = 1.0 # NaN's are those that are in mg; set their conversion number to 1
meds.loc[:, 'dose'] = (meds.loc[:, 'dose']).astype(float)
meds.loc[:, 'conversion_number'] = (meds.loc[:, 'conversion_number']).astype(float)
meds.loc[:, 'dose_standardised'] = (meds.loc[:, 'dose']).copy() * (meds.loc[:, 'conversion_number']).copy() # standardise the dose (e.g., mg/5ml --> mg/ml)
meds.loc[:, 'number'] = (meds.loc[:, 'number']).astype(float)
meds.loc[:, 'dose_total'] = (meds.loc[:, 'number']).copy() * (meds.loc[:, 'dose_standardised']).copy() # calculate the total dose in mg (by taking dose and quantity (number of volume) into account)
meds.loc[:, 'ddd'] = (meds.loc[:, 'ddd']).astype(float)
meds.loc[:, 'ddd_total'] = (meds.loc[:, 'dose_total']).copy() / (meds.loc[:, 'ddd']).copy() # calculate the ddd per prescription
print ('DDD done.')







### Final cleaning


# for drugs without an 'aa_name' (usually because of lack of ATC code), assign old 'scale_name' as 'aa_name'
meds.loc[(~meds['scale_name'].isnull()) & (meds['aa_name'].isnull()), 'aa_name'] = (meds.loc[(~meds['scale_name'].isnull()) & (meds['aa_name'].isnull()), 'scale_name']).copy()

# identify additional rows with invalid administration routes
meds.loc[(meds['prescription'].str.contains('crm', na = False)) | (meds['prescription'].str.contains(' cre', na = False)) \
         | (meds['prescription'].str.contains('%', na = False)), 'admin_oral'] = 0
meds.loc[meds['prescription'].str.contains('inhaler', na = False), 'admin_oral'] = 0 # inhalers
meds.loc[meds['prescription'].str.contains('fluticasone', na = False), 'admin_oral'] = 0
meds.loc[meds['prescription'].str.contains('salmeterol', na = False), 'admin_oral'] = 0
meds.loc[meds['prescription'].str.contains('tiotropium', na = False), 'admin_oral'] = 0
meds.loc[meds['prescription'].str.contains('ipratropium', na = False), 'admin_oral'] = 0

# set ddd, dose, and number for transdermal patches to NaN, as it is difficult to know how long the patient wears them
meds.loc[meds['prescription'].str.contains('transdermal', na = False), ['dose_standardised', 'number', 'dose_total', 'ddd_total']] = np.nan # transdermal patches (problematic to figure out dosage)
meds.loc[meds['prescription'].str.contains('patch', na = False), ['dose_standardised', 'number', 'dose_total', 'ddd_total']] = np.nan

# delete unnecessary columns
meds.drop(['scale_name','dose_a1','dose_a2','dose_a3','dose_a4','from_quantity','dose_a1_number',
       'dose_a2_number','dose_a3_number','dose_a4_number','number_a1','number_a2','number_a3','number_a4',
       'number_a5','number_a6','number_a7','number_a8','number_a9','conversion_number'], axis=1, inplace=True)

# concatenate all data frames
meds_all = pd.concat([meds, meds_non_oral, meds_non_aa])

# remove additionally created empty rows
meds_all = meds_all.loc[meds_all['id'].notnull()]

# export
prescriptions = meds_all.to_csv('4_aa_scales_dosage_v2.csv',index=False, header=True, sep='|')