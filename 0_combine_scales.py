# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:55:25 2020

@author: jurem

1. Homogenizes discordant drug names across the different anticholinergic scale and creates a single data frame containing all scales.
2. Creates a new scale that averages the scores from previously published scales (except meta-analysis-based scales).
3. Exports a table with drugs as rows and anticholinergic scales as columns; it includes only drugs that were scored with >0 by at least one scale.
"""

import os
import pandas as pd
import numpy as np
import re

# os.chdir('\\\\cmvm.datastore.ed.ac.uk/cmvm/sbms/users/s1876403/NOW')
os.chdir('D:\\PhD\\MAIN')

# read in aa-scales
kiesel = (pd.read_csv ('Kiesel.csv').sort_values(by=['aa'], ascending = False)) 
ancelin = (pd.read_csv ('Ancelin.csv').sort_values(by=['aa'], ascending = False))
boustani = (pd.read_csv ('Boustani.csv').sort_values(by=['aa'], ascending = False))
carnahan = (pd.read_csv ('Carnahan.csv').sort_values(by=['aa'], ascending = False))
cancelli = (pd.read_csv ('Cancelli.csv').sort_values(by=['aa'], ascending = False))
chew = (pd.read_csv ('Chew.csv').sort_values(by=['aa'], ascending = False))
rudolph = (pd.read_csv ('Rudolph_Sumukadas.csv').sort_values(by=['aa'], ascending = False))
ehrt = (pd.read_csv ('Ehrt.csv').sort_values(by=['aa'], ascending = False))
han = (pd.read_csv ('Han.csv').sort_values(by=['aa'], ascending = False))
sittironnarit = (pd.read_csv ('Sittironnarit.csv').sort_values(by=['aa'], ascending = False))
duran = (pd.read_csv ('Duran.csv').sort_values(by=['aa'], ascending = False))
briet = (pd.read_csv ('Briet.csv').sort_values(by=['aa'], ascending = False))
bishara = (pd.read_csv ('Bishara.csv').sort_values(by=['aa'], ascending = False))


# rename the columns
kiesel.columns = ['drug', 'aa_kiesel']
ancelin.columns = ['drug', 'aa_ancelin']
boustani.columns = ['drug', 'aa_boustani']
carnahan.columns = ['drug', 'aa_carnahan']
cancelli.columns = ['drug', 'aa_cancelli']
chew.columns = ['drug', 'aa_chew']
rudolph.columns = ['drug', 'aa_rudolph']
ehrt.columns = ['drug', 'aa_ehrt']
han.columns = ['drug', 'aa_han']
sittironnarit.columns = ['drug', 'aa_sittironnarit']
duran.columns = ['drug', 'aa_duran']
briet.columns = ['drug', 'aa_briet']
bishara.columns = ['drug', 'aa_bishara']

# create a list of scales 
scales = [kiesel, ancelin, boustani, carnahan, cancelli, chew, rudolph, ehrt, han, sittironnarit, duran, briet, bishara]
scales_names = ['Kiesel', 'Ancelin', 'Boustani', 'Carnahan', 'Cancelli', 'Chew', 'Rudolph', 'Ehrt', 'Han', 'Sittironnarit', 'Duran', 'Briet', 'Bishara']

# iterate through the list created above and for all scales:
    # convert to lowercase
for scale in scales:
    scale.loc[:,'drug'] = scale['drug'].str.lower() 
    # remove leading and trailing white spaces
for scale in scales:
    scale['drug'] = scale.loc[:,'drug'].apply(str.strip)

# read in the file with generic- and brand names for drugs and check for duplicates
drug_names = pd.read_csv('alternative drug names.csv', header=0, dtype = str, encoding = 'cp1252')
for col in drug_names:
    drug_names.loc[:, col] = drug_names[col].str.lower() # convert to lowercase
    drug_names.loc[~drug_names[col].isna(), col] = drug_names.loc[~drug_names[col].isna(), col].apply(str.strip) # remove left and right white spaces
l = [] # create list
for i in range(len(drug_names)): # iterate over entries in the file
    for j in range(len(drug_names.columns)):
      l.append(drug_names.iloc[i,j])  # append entries to the list
l = pd.DataFrame(l) # transform list to 1-column data frame
l.columns = ['drug_name'] # name columns
l = l[l['drug_name'].notna()] # remove NaN's
counts = l.drug_name.value_counts() # check numbers of counts for each entry




## Replace brand-/alternative names in the scales with generic names
# read in the file with alternative drug names that is formatted as a dictionary with alternative names as keys and proper generic names as values
drug_names = pd.read_csv('alternative drug names_reformatted.csv', header=0, dtype = str, encoding = 'cp1252').sort_values(by=['combination'], ascending = True)
for col in drug_names:
    drug_names.loc[:, col] = drug_names[col].str.lower() # convert to lowercase
    drug_names.loc[~drug_names[col].isna(), col] = drug_names.loc[~drug_names[col].isna(), col].apply(str.strip) # remove left and right white spaces
drug_names = drug_names.drop_duplicates() # drop duplicates
drug_names = (drug_names.loc[~drug_names['generic'].isnull()]).copy()

# create dictionary with alternative-/brand- and generic drug names
name_dict = dict(zip(drug_names['brand'], drug_names['generic']))

# code to find the exact drug name match
def findName(drug_name):
    # Regex: any character except the ones in the bracket at least once or start of string; drug name; any character except the ones in the bracket at least once or end of string
    pattern = re.search(r'([^a-zA-Z]+|^)({0})([^a-zA-Z]+|$)'.format(drug), drug_name) 
    if pattern:
        return 1
    else: return 0



# execute the replacing algorithm
drug_count = len(name_dict) # the count tracks the loop below
for drug in name_dict: 
    print('Substituting ' + drug + ' with ' + str(name_dict[drug]) + '...' + '\n' + 'Drugs left: ' + str(drug_count))
    for scale in scales:        
        name_rows = scale.loc[:, 'drug'].apply(lambda x: findName(x)) # find rows with drug (exact word match) VERY SLOW BECAUSE OF REGEX
        name_indices = list((name_rows[name_rows==1]).index) # mark the rows/indices of the data frame where the drug was found  
        scale.loc[name_indices, 'drug'] = scale.loc[name_indices, 'drug'].str.replace(drug, name_dict[drug], regex=False)
    drug_count -= 1 # track progress


## Remove potential duplicates from each scale
# identify scales with duplicate drug entries
count = 0
for scale in scales:
    if len(set(scale['drug']))!=len(scale):
        duplicates = 'Yes.'
    else: 
        duplicates = 'No.'
    print(scales_names[count] + ' duplicates? ' + duplicates)
    count += 1
# remove duplicates
kiesel = kiesel[~kiesel.duplicated(['drug'])]
ancelin = ancelin[~ancelin.duplicated(['drug'])]
boustani = boustani[~boustani.duplicated(['drug'])]
carnahan = carnahan[~carnahan.duplicated(['drug'])]
cancelli = cancelli[~cancelli.duplicated(['drug'])]
chew = chew[~chew.duplicated(['drug'])]
rudolph = rudolph[~rudolph.duplicated(['drug'])]
ehrt = ehrt[~ehrt.duplicated(['drug'])]
han = han[~han.duplicated(['drug'])]
sittironnarit = sittironnarit[~sittironnarit.duplicated(['drug'])]
duran = duran[~duran.duplicated(['drug'])]





## Prepare the new data frame.
# create a data frame that includes only those drugs from Kiesel's and Duran's lists that were not on any other list
kiesel_add_on = (kiesel.loc[(kiesel['drug']=='rotigotine') | (kiesel['drug']=='aclidinium bromide') | (kiesel['drug']=='dimetindene') | (kiesel['drug']=='etoricoxib')]).copy()
kiesel_add_on.columns = ['drug', 'aa_kiesel_add_on']
duran_add_on = (duran.loc[(duran['drug']=='ketotifen')]).copy()
duran_add_on.columns = ['drug', 'aa_duran_add_on']

# merge all scales into one data frame
scales = pd.merge(ancelin.copy(), chew.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), cancelli.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), han.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), rudolph.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), ehrt.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), sittironnarit.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), boustani.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), carnahan.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), briet.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), bishara.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), kiesel_add_on.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), duran_add_on.copy(), on='drug', how='outer')

# create columns indicating the number of times that a certain score appears
scales['aa_0'] = np.nan; scales['aa_05'] = np.nan; scales['aa_1'] = np.nan; scales['aa_2'] = np.nan; scales['aa_3'] = np.nan; scales['aa_4'] = np.nan

scales['aa_0'] = (scales['aa_ancelin'] == 0).astype(int) + (scales['aa_chew'] == 0).astype(int) + (scales['aa_cancelli'] == 0).astype(int) \
     + (scales['aa_han'] == 0).astype(int) + (scales['aa_rudolph'] == 0).astype(int) + (scales['aa_ehrt'] == 0).astype(int) + \
     (scales['aa_sittironnarit'] == 0).astype(int) + (scales['aa_boustani'] == 0).astype(int) + (scales['aa_carnahan'] == 0).astype(int) \
     + (scales['aa_kiesel_add_on'] == 0).astype(int) + (scales['aa_duran_add_on'] == 0).astype(int) + (scales['aa_briet'] == 0).astype(int) + (scales['aa_bishara'] == 0).astype(int)

scales['aa_05'] = (scales['aa_ancelin'] == 0.5).astype(int) + (scales['aa_chew'] == 0.5).astype(int) + (scales['aa_cancelli'] == 0.5).astype(int) \
     + (scales['aa_han'] == 0.5).astype(int) + (scales['aa_rudolph'] == 0.5).astype(int) + (scales['aa_ehrt'] == 0.5).astype(int) + \
     (scales['aa_sittironnarit'] == 0.5).astype(int) + (scales['aa_boustani'] == 0.5).astype(int) + (scales['aa_carnahan'] == 0.5).astype(int) \
     + (scales['aa_kiesel_add_on'] == 0.5).astype(int) + (scales['aa_duran_add_on'] == 0.5).astype(int) + (scales['aa_briet'] == 0.5).astype(int) + (scales['aa_bishara'] == 0.5).astype(int)
     
scales['aa_1'] = (scales['aa_ancelin'] == 1).astype(int) + (scales['aa_chew'] == 1).astype(int) + (scales['aa_cancelli'] == 1).astype(int) \
     + (scales['aa_han'] == 1).astype(int) + (scales['aa_rudolph'] == 1).astype(int) + (scales['aa_ehrt'] == 1).astype(int) + \
     (scales['aa_sittironnarit'] == 1).astype(int) + (scales['aa_boustani'] == 1).astype(int) + (scales['aa_carnahan'] == 1).astype(int) \
     + (scales['aa_kiesel_add_on'] == 1).astype(int) + (scales['aa_duran_add_on'] == 1).astype(int) + (scales['aa_briet'] == 1).astype(int) + (scales['aa_bishara'] == 1).astype(int)
     
scales['aa_2'] = (scales['aa_ancelin'] == 2).astype(int) + (scales['aa_chew'] == 2).astype(int) + (scales['aa_cancelli'] == 2).astype(int) \
     + (scales['aa_han'] == 2).astype(int) + (scales['aa_rudolph'] == 2).astype(int) + (scales['aa_ehrt'] == 2).astype(int) + \
     (scales['aa_sittironnarit'] == 2).astype(int) + (scales['aa_boustani'] == 2).astype(int) + (scales['aa_carnahan'] == 2).astype(int) \
     + (scales['aa_kiesel_add_on'] == 2).astype(int) + (scales['aa_duran_add_on'] == 2).astype(int) + (scales['aa_briet'] == 2).astype(int) + (scales['aa_bishara'] == 2).astype(int)
          
scales['aa_3'] = (scales['aa_ancelin'] == 3).astype(int) + (scales['aa_chew'] == 3).astype(int) + (scales['aa_cancelli'] == 3).astype(int) \
     + (scales['aa_han'] == 3).astype(int) + (scales['aa_rudolph'] == 3).astype(int) + (scales['aa_ehrt'] == 3).astype(int) + \
     (scales['aa_sittironnarit'] == 3).astype(int) + (scales['aa_boustani'] == 3).astype(int) + (scales['aa_carnahan'] == 3).astype(int) \
     + (scales['aa_kiesel_add_on'] == 3).astype(int) + (scales['aa_duran_add_on'] == 3).astype(int) + (scales['aa_briet'] == 3).astype(int) + (scales['aa_bishara'] == 3).astype(int)

scales['aa_4'] = (scales['aa_ancelin'] == 4).astype(int) + (scales['aa_chew'] == 4).astype(int) + (scales['aa_cancelli'] == 4).astype(int) \
     + (scales['aa_han'] == 4).astype(int) + (scales['aa_rudolph'] == 4).astype(int) + (scales['aa_ehrt'] == 4).astype(int) + \
     (scales['aa_sittironnarit'] == 4).astype(int) + (scales['aa_boustani'] == 4).astype(int) + (scales['aa_carnahan'] == 4).astype(int) \
     + (scales['aa_kiesel_add_on'] == 4).astype(int) + (scales['aa_duran_add_on'] == 4).astype(int) + (scales['aa_briet'] == 4).astype(int) + (scales['aa_bishara'] == 4).astype(int)
          
# add Duran's and Kiesel's scales to the end of the data frame
scales = pd.merge(scales.copy(), kiesel.copy(), on='drug', how='outer')
scales = pd.merge(scales.copy(), duran.copy(), on='drug', how='outer')

# remove drugs that were not scored higher than zero on any scale
scales = scales.fillna(0) # transform NaN to 0
scales = scales.loc[(scales['aa_05']!=0) | (scales['aa_1']!=0) | (scales['aa_2']!=0) | (scales['aa_3']!=0) | (scales['aa_4']!=0) \
                    | (scales['aa_kiesel']!=0) | (scales['aa_duran']!=0)]

# export
meds = scales.to_csv('UK Biobank/aas_combined.csv',index=False, header=True)