library(tidyverse)
library(gridExtra)
library(survival)
library(survminer)
library(Hmisc)
library(gridExtra)
library(lubridate)
library(RNOmni)



# All diagnoses, which were made BEFORE the first date of prescription sampling have been removed; to access them, you need to separately import
# the file with all diagnoses and then incorporate what you need into the dataset.

# date_last refers to the last date of diagnoses sampling, so some years will have no information on prescriptions, as prescription sampling
# ended before diagnoses sampling did.


id_years <- read.csv('id_years_oral_v2.csv', sep = '|', row.names = 1)
save.image("id_years_v2.RData")

# for those id-year combinations that have an NA in dosage, set ddd_dose to NA
cols <- c("aa_ancelin_ddd_dose", "aa_boustani_ddd_dose", 
          "aa_carnahan_ddd_dose", "aa_cancelli_ddd_dose", "aa_chew_ddd_dose", "aa_rudolph_ddd_dose", "aa_ehrt_ddd_dose", "aa_han_ddd_dose", 
          "aa_sittironnarit_ddd_dose", "aa_briet_ddd_dose", "aa_bishara_ddd_dose", "aa_duran_ddd_dose", "aa_kiesel_ddd_dose")
for (col in cols){
  id_years[[col]][id_years$ddd_dose_NA>0] <- NA
}


## Set year 0 and identify participants that have died

# file with dates of death and dates of registration in the prescriptions dataset
dates <- read.csv('id_present.csv')
dates$date_first <- as.Date(dates$date_first,"%Y-%m-%d")
dates$date_death <- as.Date(dates$date_death,"%Y-%m-%d")

# remove the first year in the dataset for each participant, since it is unlikely to be complete (i.e. from Jan-Dec)
id_years$year <- as.integer(id_years$year); id_years$first_year <- as.integer(id_years$first_year)
id_years <- filter(id_years, year != first_year) # removed ? rows (other occurrences were already removed in prior data cleaning)
# identify the remaining earliest year (year 0) for each participant
early_years <- id_years %>% group_by(id) %>% summarise(year_0=min(year))
id_years <- merge(id_years, early_years, by='id')
# for those, for whom the earliest year is prior to 2000, set 2000 as year 0
id_years$year_0[id_years$year_0 < 2000] <- 2000
# set date 0 to be the beginning of year 0
id_years$date_0 <- as.Date(parse_date_time(id_years$year_0, "Y"))
# create a variable indicating whether the participant has died
id_years <- merge(id_years, subset(dates, select=c(id, date_death)), by='id', all.x = TRUE)
id_years$dead <- 0
id_years$dead[!is.na(id_years$date_death)] <- 1
# keep only the remaining earliest year for each participant
id_years <- filter(id_years, year == year_0) %>% arrange(year)





## Create variables for multimorbidity and for diagnoses of disorders to be used as covariates

# import all diagnoses
morbidity <- readRDS(file = 'diagnoses_all_cleaned.rds')
# keep only the relevant columns
morbidity <- filter(subset(morbidity, select=c(id, diagnosis, date, depression, stroke_i, stroke_h, diabetes, hyperchol, hypertension, dem_any, dis_other)),
                    id %in% id_years$id)
# create 'year' variable
morbidity$date <- morbidity$date <- as.Date(morbidity$date, '%Y-%m-%d')
morbidity$year <- as.numeric(format(morbidity$date, "%Y"))
# keep only diagnoses before year 0
morbidity <- merge(morbidity, dates, by='id', all.x = TRUE)
morbidity$date_first <- as.Date(morbidity$date_first,"%Y-%m-%d")
morbidity$year_0 <- format(as.Date(morbidity$date_first), "%Y")
morbidity$year_0[morbidity$year_0 < 2000] <- 2000
# create sub-data_frames for individual diagnoses up to year 0
depression <- filter(morbidity, depression==1, year <= year_0) %>% group_by(id) %>% summarise(depression=sum(depression))
stroke_i <- filter(morbidity, stroke_i==1, year <= year_0) %>% group_by(id) %>% summarise(stroke_i=sum(stroke_i))
stroke_h <- filter(morbidity, stroke_h==1, year <= year_0) %>% group_by(id) %>% summarise(stroke_h=sum(stroke_h))
diabetes <- filter(morbidity, diabetes==1, year <= year_0) %>% arrange(date) %>% distinct(id, .keep_all = TRUE) %>%
  group_by(id) %>% summarise(diabetes=sum(diabetes))
hyperchol <- filter(morbidity, hyperchol==1, year <= year_0) %>% arrange(date) %>% distinct(id, .keep_all = TRUE) %>%
  group_by(id) %>% summarise(hyperchol=sum(hyperchol))
hypertension <- filter(morbidity, hypertension==1, year <= year_0) %>% arrange(date) %>% distinct(id, .keep_all = TRUE) %>%
  group_by(id) %>% summarise(hypertension=sum(hypertension))
# create sub-data_frame for diagnoses of PD, HD, CJD, or MS at any point
dis_other <- filter(morbidity, dis_other==1) %>% group_by(id) %>% summarise(dis_other=sum(dis_other))
# for morbidities' counts, keep only those years before year 0
morbidity <- filter(morbidity, diagnosis != '') # remove blank diagnoses
comorbidity <- filter(morbidity, year < year_0)
comorbidity <- comorbidity %>% group_by(id) %>% summarise(comorbidity=length(id))




## Find diagnoses of dementia after year 0

# subset diagnoses to variables relevant to dementia
morbidity <- subset(morbidity, select=c(id, date, year, year_0, diagnosis, dem_any))
morbidity <- arrange(morbidity, date)
# in case of several diagnoses for same disorder, keep only the earliest for each participant
morbidity <- distinct(morbidity, id, diagnosis, .keep_all = TRUE)
# create data frames with dementia diagnoses based on medication
dem_meds <- read.csv('dementia_meds.csv', sep='|') # import data on dementia medication (donepezil, galantamine, memantine, rivastigmine) to make sure to exclude all with dementia diagnosis
dem_meds$date <- as.Date(dem_meds$date, '%Y-%m-%d')
dem_meds <- dem_meds %>% arrange(date) %>% distinct(id, .keep_all=TRUE) # identify earliest date of dementia medication
dem_meds <- subset(dem_meds, select=c(id, date)); colnames(dem_meds) <- c('id', 'date_dementia_meds')
dem_meds$year_dem_meds <- as.numeric(format(dem_meds$date_dementia_meds, "%Y"))
# create data frames with dementia diagnoses based on GP/hospital records
dementia <- filter(morbidity, dem_any == 1); dementia <- distinct(dementia, id, dem_any, .keep_all = TRUE)
dementia <- subset(dementia, select=c(id, date)); colnames(dementia) <- c('id', 'date_dementia')
dementia$year_dem <- as.numeric(format(dementia$date_dementia, "%Y"))




## Import APOE data
apoe <- readRDS('APOE_SNPs_20112020.rds') # file APOE genotype
apoe$row_name_len <- sapply(rownames(apoe), nchar) # column with number of characters in row name
apoe <- filter(apoe, row_name_len == 15) # remove rows with invalid names
apoe$id <- substring(rownames(apoe), 1,7) # create proper id variable
# code APOE genotypes
apoe$apoe <- NA
apoe$apoe[apoe$rs429358_C == 2 & apoe$rs7412_T == 2] <- 'e1/e1'
apoe$apoe[apoe$rs429358_C == 1 & apoe$rs7412_T == 2] <- 'e1/e2'
apoe$apoe[apoe$rs429358_C == 1 & apoe$rs7412_T == 1] <- 'e1/e3 / e2/e4'
apoe$apoe[apoe$rs429358_C == 2 & apoe$rs7412_T == 1] <- 'e1/e4'
apoe$apoe[apoe$rs429358_C == 0 & apoe$rs7412_T == 2] <- 'e2/e2'
apoe$apoe[apoe$rs429358_C == 0 & apoe$rs7412_T == 1] <- 'e2/e3'
apoe$apoe[apoe$rs429358_C == 0 & apoe$rs7412_T == 0] <- 'e3/e3'
apoe$apoe[apoe$rs429358_C == 1 & apoe$rs7412_T == 0] <- 'e3/e4'
apoe$apoe[apoe$rs429358_C == 2 & apoe$rs7412_T == 0] <- 'e4/e4'
apoe <- subset(apoe, select=c(id, apoe))
# simplified genotypes
apoe$apoe_carrier <- NA
apoe$apoe_carrier[apoe$apoe=="e2/e2" | apoe$apoe=="e2/e3" | apoe$apoe=="e1/e2"] <- "e2"
apoe$apoe_carrier[apoe$apoe=="e3/e3" | apoe$apoe=='e1/e3 / e2/e4'] <- "e3"
apoe$apoe_carrier[apoe$apoe=="e3/e4" | apoe$apoe=="e4/e4" | apoe$apoe=="e1/e4"] <- "e4"




# Merge into one data frame
id_years <- merge(id_years, comorbidity, by='id', all.x = TRUE)
id_years <- merge(id_years, dementia, by='id', all.x = TRUE)
id_years$dementia <- 0
id_years$dementia[!is.na(id_years$date_dementia)] <- 1 # identify those diagnoses with dementia
id_years <- merge(id_years, dem_meds, by='id', all.x = TRUE)
id_years$dementia_meds <- 0
id_years <- transform(id_years, date_dementia_meds = pmin(date_dementia, date_dementia_meds, na.rm = TRUE)) # for those with dementia information from both sources, choose the earliest date
id_years$dementia_meds[!is.na(id_years$date_dementia_meds)] <- 1 # identify those with dementia with extended criteria that includes medication
id_years <- merge(id_years, dis_other, by='id', all.x = TRUE)
id_years <- merge(id_years, depression, by='id', all.x = TRUE)
id_years <- merge(id_years, stroke_i, by='id', all.x = TRUE)
id_years <- merge(id_years, stroke_h, by='id', all.x = TRUE)
id_years <- merge(id_years, diabetes, by='id', all.x = TRUE)
id_years <- merge(id_years, hyperchol, by='id', all.x = TRUE)
id_years <- merge(id_years, hypertension, by='id', all.x = TRUE)
id_years <- merge(id_years, apoe, by='id', all.x = TRUE)




## Calculate person-time

# set date of status (right-censoring, death, or dementia)
id_years$date_status <- id_years$date_dementia
id_years$date_status[id_years$dead==1 & is.na(id_years$date_dementia)] <- id_years$date_death[id_years$dead==1 & is.na(id_years$date_dementia)] # right-censoring at date of death
id_years$date_status[is.na(id_years$date_status)] <- format(as.Date('2020-06-30'), '%Y-%m-%d') # right censoring at the end of sampling
id_years$year_status <- as.numeric(format(id_years$date_status, "%Y"))
id_years$person_time <- id_years$year_status - as.numeric(id_years$year_0)
# identify those with diagnosis of (or prescriptions for) dementia before time point 0 (and within a year of year 0)
id_years$date_status_meds <- id_years$date_dementia_meds
id_years$date_status_meds[id_years$dead==1 & is.na(id_years$date_dementia_meds)] <- id_years$date_death[id_years$dead==1 & is.na(id_years$date_dementia_meds)] # right-censoring at date of death
id_years$date_status_meds[is.na(id_years$date_status_meds)] <- format(as.Date('2020-06-30'), '%Y-%m-%d') # right censoring at the end of sampling
id_years$year_status_meds <- as.numeric(format(id_years$date_status_meds, "%Y"))
id_years$person_time_with_meds <- id_years$year_status_meds - as.numeric(id_years$year_0)
id_years <- filter(id_years, person_time_with_meds > 1)
# remove participants with diagnosis of HD, PD, CJD, or MS
id_years <- filter(id_years, is.na(dis_other))



## Clean up variables

# set missing values to 0
id_years$depression[is.na(id_years$depression)] <- 0
id_years$stroke_i[is.na(id_years$stroke_i)] <- 0
id_years$stroke_h[is.na(id_years$stroke_h)] <- 0
id_years$diabetes[is.na(id_years$diabetes)] <- 0
id_years$hyperchol[is.na(id_years$hyperchol)] <- 0
id_years$hypertension[is.na(id_years$hypertension)] <- 0
id_years$comorbidity[is.na(id_years$comorbidity)] <- 0
id_years[id_years==''] <- NA
# we're just interested whether they were ever diagnosed; not how many times
id_years$depression[id_years$depression>0] <- 1 
id_years$stroke_h[id_years$stroke_h>0] <- 1 
id_years$stroke_i[id_years$stroke_i>0] <- 1 
id_years$stroke <- 0 # one variable for both stroke types
id_years$stroke[id_years$stroke_i==1 | id_years$stroke_h==1] <- 1
id_years$hyperchol[id_years$hyperchol>0] <- 1 
id_years$hypertension[id_years$hypertension>0] <- 1 
id_years$diabetes[id_years$diabetes>0] <- 1 
# change variable classes
id_years$sex <- as.factor(id_years$sex)
id_years$dementia <- as.factor(id_years$dementia)
id_years$dead <- as.factor(id_years$dead)
id_years$meds_count <- as.numeric(id_years$meds_count)
id_years$med_age <- as.numeric(id_years$med_age)
id_years$data_provider <- as.factor(id_years$data_provider)
id_years$education <- as.factor(id_years$education)
id_years$deprivation <- as.numeric(id_years$deprivation)
id_years$bmi <- as.numeric(id_years$bmi)
id_years$smoking[id_years$smoking=='-3'] <- NA
id_years$smoking <- as.factor(id_years$smoking)
id_years$alc_freq <- as.factor(id_years$alc_freq)
id_years$activity <- as.factor(id_years$activity)
id_years$comorbidity <- as.numeric(id_years$comorbidity)
id_years$diabetes <- as.factor(id_years$diabetes)
id_years$hyperchol <- as.factor(id_years$hyperchol)
id_years$hypertension <- as.factor(id_years$hypertension)
id_years$depression <- as.numeric(id_years$depression)
id_years$stroke <- as.factor(id_years$stroke)
id_years$apoe_carrier <- as.factor(id_years$apoe_carrier)
id_years$dis_other <- NULL
# remove cases with events before age 60
id_years$birth_date <- as.Date(id_years$birth_date,"%Y-%m-%d")
id_years$age_diag <- NA
id_years$age_diag <- as.numeric(difftime(id_years$date_status, id_years$birth_date, units = 'days'))/365.25
id_years <- filter(id_years, age_diag >= 60)





rm(apoe, dis_other, comorbidity, dates, depression, diabetes, hyperchol, hypertension, morbidity, early_years, dementia, stroke_h, stroke_i, col, cols, dem_meds)
save.image("id_years_cleaned_v2.RData")




## Prepare for modelling

# prescription data are inaccurate after 2015, so remove those
id_years <- filter(id_years, year<=2015)

# re-code dementia
id_years$dementia <- as.character(id_years$dementia)
id_years$dementia[id_years$dementia=='1'] <- '2'
id_years$dementia[id_years$dementia=='0'] <- '1'
id_years$dementia <- as.numeric(id_years$dementia)

# categorise BMI
id_years$bmi_class[id_years$bmi >= 18.5 & id_years$bmi < 25] <- '18.5-25'
id_years$bmi_class[id_years$bmi < 18.5] <- '<18.5'
id_years$bmi_class[id_years$bmi >= 25 & id_years$bmi < 30] <- '25-30'
id_years$bmi_class[id_years$bmi >= 30 & id_years$bmi < 35] <- '30-35'
id_years$bmi_class[id_years$bmi >= 35 & id_years$bmi < 40] <- '35-40'
id_years$bmi_class[id_years$bmi >= 40] <- '>40'
id_years$bmi_class <- as.factor(id_years$bmi_class)

# remove outliers
cols <- c("meds_count", "aa_ancelin", "aa_boustani", "aa_carnahan", "aa_cancelli", "aa_chew", "aa_rudolph", "aa_ehrt",
          "aa_han", "aa_sittironnarit", "aa_briet", "aa_bishara", "aa_duran", "aa_kiesel", "aa_ancelin_n", "aa_boustani_n", 
          "aa_carnahan_n", "aa_cancelli_n", "aa_chew_n", "aa_rudolph_n", "aa_ehrt_n", "aa_han_n", "aa_sittironnarit_n", "aa_briet_n", 
          "aa_bishara_n", "aa_duran_n", "aa_kiesel_n",  "aa_ancelin_ddd_dose", "aa_boustani_ddd_dose", 
          "aa_carnahan_ddd_dose", "aa_cancelli_ddd_dose", "aa_chew_ddd_dose", "aa_rudolph_ddd_dose", "aa_ehrt_ddd_dose", "aa_han_ddd_dose", 
          "aa_sittironnarit_ddd_dose", "aa_briet_ddd_dose", "aa_bishara_ddd_dose", "aa_duran_ddd_dose", "aa_kiesel_ddd_dose", 
          "deprivation", "comorbidity")
for (col in cols){
  avg <- mean(id_years[[col]][id_years[[col]] != 0], na.rm = TRUE) # calculate mean of non-zero rows
  SD <- sd(id_years[[col]][id_years[[col]] != 0], na.rm = TRUE) # calculate sd of non-zero rows
  prev_na <- sum(is.na(id_years[[col]]))
  id_years[[col]][id_years[[col]] > (avg + 3*SD)] <- NA
  new_na <- sum(is.na(id_years[[col]])) - prev_na # calculate number of NA'd rows
  print(paste(col, new_na, 100*new_na/nrow(id_years)))
}

# create separate polypharmacy variables for each scale (=total medication count - anticholinergics according to scale)
id_years$aa_ancelin_poly <- id_years$meds_count - id_years$aa_ancelin_n 
id_years$aa_boustani_poly <- id_years$meds_count - id_years$aa_boustani_n 
id_years$aa_carnahan_poly <- id_years$meds_count - id_years$aa_carnahan_n 
id_years$aa_cancelli_poly <- id_years$meds_count - id_years$aa_cancelli_n 
id_years$aa_chew_poly <- id_years$meds_count - id_years$aa_chew_n 
id_years$aa_rudolph_poly <- id_years$meds_count - id_years$aa_rudolph_n 
id_years$aa_ehrt_poly <- id_years$meds_count - id_years$aa_ehrt_n 
id_years$aa_han_poly <- id_years$meds_count - id_years$aa_han_n 
id_years$aa_sittironnarit_poly <- id_years$meds_count - id_years$aa_sittironnarit_n 
id_years$aa_briet_poly <- id_years$meds_count - id_years$aa_briet_n 
id_years$aa_bishara_poly <- id_years$meds_count - id_years$aa_bishara_n 
id_years$aa_duran_poly <- id_years$meds_count - id_years$aa_duran_n 
id_years$aa_kiesel_poly <- id_years$meds_count - id_years$aa_kiesel_n 

# variables for anticholinergic drug according to ANY scale
id_years$aa_any<-apply(X=subset(id_years, select = c(aa_ancelin_n,aa_boustani_n,aa_carnahan_n,aa_cancelli_n,aa_chew_n,aa_rudolph_n,aa_ehrt_n,aa_han_n,
                                                     aa_sittironnarit_n,aa_briet_n,aa_bishara_n,aa_duran_n,aa_kiesel_n)), 
                       MARGIN=1, FUN=max)
id_years$poly_cov <- id_years$meds_count-id_years$aa_any

# Hanlon's + polypharmacy + log(year)
m_ancelin <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_ancelin)+ sqrt(aa_ancelin_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_boustani <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_boustani)+ sqrt(aa_boustani_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_carnahan <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_carnahan)+ sqrt(aa_carnahan_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_cancelli <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_cancelli)+ sqrt(aa_cancelli_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_chew <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_chew)+ sqrt(aa_chew_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_rudolph <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_rudolph)+ sqrt(aa_rudolph_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_ehrt <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_ehrt)+ sqrt(aa_ehrt_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_han <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_han)+ sqrt(aa_han_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_sittironnarit <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_sittironnarit)+ sqrt(aa_sittironnarit_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_briet<- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_briet)+ sqrt(aa_briet_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_bishara <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_bishara)+ sqrt(aa_bishara_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_duran <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_duran)+ sqrt(aa_duran_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_kiesel <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_kiesel)+ sqrt(aa_kiesel_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_ancelin_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_ancelin_n)+ sqrt(aa_ancelin_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_boustani_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_boustani_n)+ sqrt(aa_boustani_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_carnahan_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_carnahan_n)+ sqrt(aa_carnahan_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_cancelli_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_cancelli_n)+ sqrt(aa_cancelli_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_chew_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_chew_n)+ sqrt(aa_chew_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_rudolph_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_rudolph_n)+ sqrt(aa_rudolph_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_ehrt_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_ehrt_n)+ sqrt(aa_ehrt_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_han_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_han_n)+ sqrt(aa_han_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_sittironnarit_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_sittironnarit_n)+ sqrt(aa_sittironnarit_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_briet_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_briet_n)+ sqrt(aa_briet_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_bishara_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_bishara_n)+ sqrt(aa_bishara_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_duran_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_duran_n)+ sqrt(aa_duran_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_kiesel_n <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_kiesel_n)+ sqrt(aa_kiesel_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_ancelin_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_ancelin_ddd_dose)+ sqrt(aa_ancelin_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_boustani_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_boustani_ddd_dose)+ sqrt(aa_boustani_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_carnahan_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_carnahan_ddd_dose)+ sqrt(aa_carnahan_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_cancelli_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_cancelli_ddd_dose)+ sqrt(aa_cancelli_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_chew_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_chew_ddd_dose)+ sqrt(aa_chew_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_rudolph_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_rudolph_ddd_dose)+ sqrt(aa_rudolph_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_ehrt_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_ehrt_ddd_dose)+ sqrt(aa_ehrt_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_han_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_han_ddd_dose)+ sqrt(aa_han_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_sittironnarit_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_sittironnarit_ddd_dose)+ sqrt(aa_sittironnarit_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_briet_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_briet_ddd_dose)+ sqrt(aa_briet_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_bishara_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_bishara_ddd_dose)+ sqrt(aa_bishara_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_duran_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_duran_ddd_dose)+ sqrt(aa_duran_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_kiesel_ddd_dose <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(aa_kiesel_ddd_dose)+ sqrt(aa_kiesel_poly) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_poly_simple <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(poly_cov) + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)
m_poly <- coxph(data=id_years, Surv(person_time, dementia) ~ scale(poly_cov) + aa_any + sex + data_provider + med_age + log(year) + education + deprivation + bmi_class +   smoking + alc_freq + activity + comorbidity + depression+stroke + diabetes+hyperchol+hypertension+apoe_carrier)