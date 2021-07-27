# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 09:32:48 2019

@author: jurem

Add demographic data to the prescriptions.

"""


import pandas as pd
import numpy as np



meds = pd.read_csv('5_aa_scales_dosage_v2.csv', header=0, sep="|", dtype = str, encoding = 'cp1252')




## add age and sex

age_sex = pd.read_csv('age_sex.csv')
# transform id, birth year, and month to strings
age_sex['id'] = age_sex['id'].astype(str)
age_sex['birth_year'] = age_sex['birth_year'].astype(str)
age_sex['birth_month'] = age_sex['birth_month'].astype(str)
# add a column indicating the length of the month-string
age_sex['month_len'] = age_sex.loc[~age_sex['birth_month'].isna(), 'birth_month'].apply(len)
# add a '0' to the front of all 1-digit months so as to harmonize the formatting
age_sex.loc[age_sex['month_len']==1, 'birth_month'] = '0' + age_sex.loc[age_sex['month_len']==1, 'birth_month']
# create a new column with the properly formated month and year
age_sex['birth_date'] = "01" + '/' + age_sex['birth_month'] + '/' + age_sex['birth_year']
age_sex['birth_date'] = pd.to_datetime(age_sex['birth_date'], format = '%d/%m/%Y')
# merge the datasets
meds = pd.merge(meds, age_sex, on='id', how='left')
# add a column for age at prescription
meds['date'] = pd.to_datetime(meds.date)
meds['med_age'] = meds['date'] -  meds['birth_date']
meds['med_age'] = meds['med_age'].dt.total_seconds()/(24*3600)/365.242
meds.drop(['birth_year','birth_month'], axis=1, inplace=True)



## add date of assessment
test_dates = pd.read_csv('test_date.csv') # read in the date of the assessment
test_dates['id'] = test_dates['id'].astype(str)
test_dates.columns = ['id', 'date_1', 'date_2', 'date_3'] # rename the columns
# merge the datasets
meds = pd.merge(meds, test_dates, on='id', how='left')
# transorm to datetime format
meds['date_1'] = pd.to_datetime(meds['date_1'], format = '%Y-%m-%d')
meds['date_2'] = pd.to_datetime(meds['date_2'], format = '%Y-%m-%d')
meds['date_3'] = pd.to_datetime(meds['date_3'], format = '%Y-%m-%d')
del test_dates



## education
# read in education
education = pd.read_csv('education.csv', header=0, sep=",", dtype = str)
# choose only education code columns
education.drop(['age_completed_06-10', 'age_completed_12-13', 'age_completed_14-', 'year_ended'], axis=1, inplace=True)
# change all non-graduate-degree codings into 0
education[(education=='2') | (education=='3') | (education=='4') | (education=='5') | (education=='6') | (education=='-7')] = '0'
# change all non-answers to NaN's
education[(education=='-3')] = np.nan
# remove rows with only NaN's
education = education.dropna(subset=['first_1', 'first_2', 'first_3', 'first_4', 'first_5', 'second_1',
                         'second_2', 'second_3', 'second_4', 'second_5', 'second_6', 'second_7',
                         'third_0', 'third_1', 'third_2', 'third_3', 'third_4', 'third_5'], axis='rows', how='all')
# initialize columns
education['education_1'] = np.nan; education['education_2'] = np.nan; education['education_3'] = np.nan
# put college-degree codes found in either one of the columns into a single new column
education.loc[(education['first_1']=='0') | (education['first_2']=='0') | (education['first_3']=='0') | (education['first_4']=='0') | (education['first_5']=='0'), 'education_1'] = '0'
education.loc[(education['first_1']=='1') | (education['first_2']=='1') | (education['first_3']=='1') | (education['first_4']=='1') | (education['first_5']=='1'), 'education_1'] = '1'
education.loc[(education['second_1']=='0') | (education['second_2']=='0') | (education['second_3']=='0') | (education['second_4']=='0') | (education['second_5']=='0') | (education['second_6']=='0') | (education['second_7']=='0'), 'education_2'] = '0'
education.loc[(education['second_1']=='1') | (education['second_2']=='1') | (education['second_3']=='1') | (education['second_4']=='1') | (education['second_5']=='1') | (education['second_6']=='1') | (education['second_7']=='1'), 'education_2'] = '1'
education.loc[(education['third_0']=='0') | (education['third_1']=='0') | (education['third_2']=='0') | (education['third_3']=='0') | (education['third_4']=='0') | (education['third_5']=='0'), 'education_3'] = '0'
education.loc[(education['third_0']=='1') | (education['third_1']=='1') | (education['third_2']=='1') | (education['third_3']=='1') | (education['third_4']=='1') | (education['third_5']=='1'), 'education_3'] = '1'
# keep only the relevant columns
education = education[['id','education_1','education_2','education_3']]
# add education to main data frame
meds = pd.merge(meds, education, on='id', how='left')
# for each prescription, keep only the date of education before the prescription was issued
meds['education'] = meds['education_1'] # initiate new column
meds.loc[meds['date'] >= meds['date_2'], 'education'] = meds['education_2'] # for all the prescriptions issued after date_2, education will correspond to the education at the 2nd visit
meds.loc[meds['date'] >= meds['date_3'], 'education'] = meds['education_3'] # same as above, but for date_3 and 3rd visit
# drop unneccesary columns
meds.drop(['education_1','education_2','education_3'], axis=1, inplace=True)
del education



## deprivation
# read in the Townsend
deprivation = pd.read_csv('deprivation.csv', header=0, dtype = str)
# merge with main data frame
meds = pd.merge(meds, deprivation, on='id', how='left')
del deprivation



## smoking
smoking = pd.read_csv('tobacco.csv', header=0, dtype = str)
smoking['smoking_1'] = smoking.smoking_1.astype(str)
smoking.loc[(smoking['smoking_1'] == '-3') | (smoking['smoking_1'] == 'nan'), 'smoking_1'] = np.nan
# add to the main data frame
meds = pd.merge(meds, smoking, on='id', how='left')
# update using 2nd and 3rd visits
meds['smoking'] = meds['smoking_1'] # initiate new column
meds.loc[meds['date'] >= meds['date_2'], 'smoking'] = meds['smoking_2'] # for all the prescriptions issued after date_2, smoking will correspond to the smoking at the 2nd visit
meds.loc[meds['date'] >= meds['date_3'], 'smoking'] = meds['smoking_3'] # same as above, but for date_3 and 3rd visit
# remove columns
meds.drop(['smoking_1', 'smoking_2','smoking_3'], axis=1, inplace=True)
del smoking



## alcohol consumption
# read in the data frame
alcohol = pd.read_csv('alcohol.csv', header=0, dtype = str)
# add to the main data frame
meds = pd.merge(meds, alcohol, on='id', how='left')
# set first assessment visit as default
meds.rename({'alc_freq_1': 'alc_freq'}, axis=1, inplace=True)
# for each data point on alcohol consumption frequency, update by using the 2nd and 3rd visits
meds.loc[meds['date'] >= meds['date_2'], 'alc_freq'] = meds['alc_freq_2']
meds.loc[meds['date'] >= meds['date_3'], 'alc_freq'] = meds['alc_freq_3']
# set unknown data points to NaN
meds.loc[meds['alc_freq']=='-3', 'alc_freq'] = np.nan
# drop unneccesary columns
meds.drop(['alc_freq_2','alc_freq_3'], axis=1, inplace=True)
del alcohol



## physical activity
activity_type = pd.read_csv('activity_type.csv', header=0, dtype = str)
# change 'none' or 'prefer not to answer' to NaN
activity_type[(activity_type=='-7') | (activity_type=='-3')] = np.nan
# re-code
activity_type[(activity_type=='1') | (activity_type=='4')] = '1'
activity_type[(activity_type=='2') | (activity_type=='5')] = '2'
# initiate columns for all three visits
activity_type['activity_1'] = np.nan; activity_type['activity_2'] = np.nan; activity_type['activity_3'] = np.nan
# if the higher level of physical activity occurs as a response during the visit, override the lower activity levels
activity_type.loc[(activity_type['first_1']=='1') | (activity_type['first_2']=='1') | (activity_type['first_3']=='1') | (activity_type['first_4']=='1') | (activity_type['first_5']=='1'), 'activity_1'] = '1'
activity_type.loc[(activity_type['first_1']=='2') | (activity_type['first_2']=='2') | (activity_type['first_3']=='2') | (activity_type['first_4']=='2') | (activity_type['first_5']=='2'), 'activity_1'] = '2'
activity_type.loc[(activity_type['first_1']=='3') | (activity_type['first_2']=='3') | (activity_type['first_3']=='3') | (activity_type['first_4']=='3') | (activity_type['first_5']=='3'), 'activity_1'] = '3'

activity_type.loc[(activity_type['second_1']=='1') | (activity_type['second_2']=='1') | (activity_type['second_3']=='1') | (activity_type['second_4']=='1') | (activity_type['second_5']=='1'), 'activity_2'] = '1'
activity_type.loc[(activity_type['second_1']=='2') | (activity_type['second_2']=='2') | (activity_type['second_3']=='2') | (activity_type['second_4']=='2') | (activity_type['second_5']=='2'), 'activity_2'] = '2'
activity_type.loc[(activity_type['second_1']=='3') | (activity_type['second_2']=='3') | (activity_type['second_3']=='3') | (activity_type['second_4']=='3') | (activity_type['second_5']=='3'), 'activity_2'] = '3'

activity_type.loc[(activity_type['third_1']=='1') | (activity_type['third_2']=='1') | (activity_type['third_3']=='1') | (activity_type['third_4']=='1') | (activity_type['third_5']=='1'), 'activity_3'] = '1'
activity_type.loc[(activity_type['third_1']=='2') | (activity_type['third_2']=='2') | (activity_type['third_3']=='2') | (activity_type['third_4']=='2') | (activity_type['third_5']=='2'), 'activity_3'] = '2'
activity_type.loc[(activity_type['third_1']=='3') | (activity_type['third_2']=='3') | (activity_type['third_3']=='3') | (activity_type['third_4']=='3') | (activity_type['third_5']=='3'), 'activity_3'] = '3'
# remove unneccesary columns
activity_type = activity_type[['id', 'activity_1', 'activity_2', 'activity_3']]
# add to the main data frame
meds = pd.merge(meds, activity_type, on='id', how='left')
# set first assessment visit as default
meds.rename({'activity_1': 'activity'}, axis=1, inplace=True)
# for each data point on physical activity, update by using the 2nd and 3rd visits
meds.loc[meds['date'] >= meds['date_2'], 'activity'] = meds['activity_2']
meds.loc[meds['date'] >= meds['date_3'], 'activity'] = meds['activity_3']
# drop unneccesary columns
meds.drop(['activity_2','activity_3'], axis=1, inplace=True)
del activity_type



## BMI
# read in the data frame
bmi = pd.read_csv('bmi.csv', header=0, dtype = str)
# add to the main data frame
meds = pd.merge(meds, bmi, on='id', how='left')
# set first assessment visit as default
meds.rename({'bmi_1': 'bmi'}, axis=1, inplace=True)
# for each data point on BMI, update by using the 2nd and 3rd visits
meds.loc[meds['date'] >= meds['date_2'], 'bmi'] = meds['bmi_2']
meds.loc[meds['date'] >= meds['date_3'], 'bmi'] = meds['bmi_3']
# drop unneccesary columns
meds.drop(['bmi_2','bmi_3'], axis=1, inplace=True)
del bmi



### Identify prescriptions for dementia drugs and export (to help identify cases later on)
dementia = meds.loc[(meds['prescription'].str.contains('donepezil', na=False)) |
                    (meds['prescription'].str.contains('galantamine', na=False)) |
                    (meds['prescription'].str.contains('memantine', na=False)) |
                    (meds['prescription'].str.contains('rivastigmine', na=False))].copy()



#export .csv
prescriptions = meds.to_csv('6_demographics_v2.csv',index=False, header=True, sep='|')
age_sex.drop(['month_len'], axis=1, inplace=True)
prescriptions = age_sex.to_csv('age_sex_formatted.csv',index=False, header=True, sep='|')
prescriptions = dementia.to_csv('dementia_meds.csv',index=False, header=True, sep='|')

