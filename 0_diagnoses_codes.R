###
#
#
# This code imports the diagnoses and the dates when those diagnoses were made, and creates a data frame with columns for each relevant diagnosis.
#
#
###


library(plyr)
library(tidyverse)



## Import the codes for each disorder

codes <- read.csv('codes_in_sample.csv', header=TRUE)
# remove potential white space and convert to lower case
codes <- data.frame(sapply(codes, trimws))
codes$disorder <- tolower(codes$disorder) 
codes$source <- tolower(codes$source)
codes$code <- as.character(codes$code)
codes$n <- as.numeric(codes$n)

# add "priority" column, which indicates that codes that refer to both general dementia as well as a specific dementia should preferentialy refer to the specific one
codes$priority <- 1; codes$priority[codes$disorder=='other dementia'] <- 2

# separate codes into inpatient and primary care
codes_gp <- filter(codes, source=='gp')
codes_inpatient <- filter(codes, source=='inpatient')

# arrange by priority and in case of duplicates, keep only the first ('high priority"; i.e., specific dementia) occurrence
codes_inpatient <- codes_inpatient %>% arrange(priority)
codes_gp <- codes_gp %>% arrange(priority)
codes_inpatient <- distinct(codes_inpatient, code, .keep_all = TRUE)
codes_gp <- distinct(codes_gp, code, .keep_all = TRUE)





### Get the inpatient diagnoses ###


## Prepare files

# import files
icd9 <- readRDS('icd9.rds') # data field 41271
icd9_dates <- readRDS('icd9_dates.rds') # data field 41281
icd10 <- readRDS('icd10.rds') # data field 41270
icd10_dates <- readRDS('icd10_dates.rds') # 41280

# transform blank cells to NA's
icd9[icd9==""]  <- NA 
icd9_dates[icd9_dates==""]  <- NA 
icd10[icd10==""]  <- NA 
icd10_dates[icd10_dates==""]  <- NA 

# rename columns
colnames(icd9) <- as.character(c('id', seq(1,ncol(icd9)-1))) 
colnames(icd9_dates) <- as.character(c('id', seq(1,ncol(icd9_dates)-1)))
colnames(icd10) <- as.character(c('id', seq(1,ncol(icd10)-1)))
colnames(icd10_dates) <- as.character(c('id', seq(1,ncol(icd10_dates)-1)))

# remove rows that contain only NA's
icd9 <- icd9[rowSums(is.na(icd9))!=ncol(icd9)-1,]
icd9_dates <- icd9_dates[rowSums(is.na(icd9_dates))!=ncol(icd9_dates)-1,]
icd10 <- icd10[rowSums(is.na(icd10))!=ncol(icd10)-1,]
icd10_dates <- icd10_dates[rowSums(is.na(icd10_dates))!=ncol(icd10_dates)-1,]

# change class of all columns to character
icd9 <- as.data.frame(sapply(icd9, as.character))
icd9_dates <- as.data.frame(sapply(icd9_dates, as.character))
icd10 <- as.data.frame(sapply(icd10, as.character))
icd10_dates <- as.data.frame(sapply(icd10_dates, as.character))

# change to long format
icd9 <- icd9 %>%  pivot_longer(-id, names_to = "diagnosis", values_drop_na=TRUE); colnames(icd9) <- c('id', 'column', 'diagnosis');
icd9_dates <- icd9_dates %>%  pivot_longer(-id, names_to = "diagnosis", values_drop_na=TRUE); colnames(icd9_dates) <- c('id', 'column', 'date');
icd10 <- icd10 %>%  pivot_longer(-id, names_to = "diagnosis", values_drop_na=TRUE); colnames(icd10) <- c('id', 'column', 'diagnosis');
icd10_dates <- icd10_dates %>%  pivot_longer(-id, names_to = "diagnosis", values_drop_na=TRUE); colnames(icd10_dates) <- c('id', 'column', 'date');

# merge diagnoses with dates
icd9 <- merge(icd9, icd9_dates, by=c('id', 'column'))
icd9$version <- '9'
icd9$date <- as.Date(icd9$date, '%Y-%m-%d')
icd10 <- merge(icd10, icd10_dates, by=c('id', 'column'))
icd10$version <- '10'
icd10$date <- as.Date(icd10$date, '%Y-%m-%d')


## Add the most recently published diagnoses.
# import and merge with dates
diagnoses_dates <- read.csv('hesin.txt', sep="\t") # 
diagnoses <- read.csv('hesin_diag.txt', sep="\t")
diagnoses_dates <- subset(diagnoses_dates, select=c(eid, ins_index, admidate))
diagnoses <- subset(diagnoses, select=c(eid, ins_index, diag_icd9, diag_icd10))
diagnoses <- merge(diagnoses, diagnoses_dates, by=c('eid', 'ins_index'), all.x = TRUE)
diagnoses$eid <- as.factor(diagnoses$eid)
diagnoses$admidate <- as.Date(diagnoses$admidate, '%d/%m/%Y')
# retain the relevant columns
icd9_new <- subset(filter(diagnoses, diag_icd9!=''), select=c(eid, diag_icd9, admidate))
colnames(icd9_new) <- c('id', 'diagnosis','date')
icd9_new$version <- '9'
icd9_new <- data.frame(sapply(icd9_new, trimws))
icd10_new <- subset(filter(diagnoses, diag_icd10!=''), select=c(eid, diag_icd10, admidate))
colnames(icd10_new) <- c('id', 'diagnosis', 'date')
icd10_new$version <- '10'
icd10_new <- data.frame(sapply(icd10_new, trimws))
# merge with the old diagnoses and delete duplicates
icd9$column <- NULL
icd9_update <- rbind(icd9, icd9_new)
icd9_update <- icd9_update %>% arrange(date)
icd9_update <- distinct(icd9_update, id, diagnosis, .keep_all = TRUE)
icd10$column <- NULL
icd10_update <- rbind(icd10, icd10_new)
icd10_update <- icd10_update %>% arrange(date)
icd10_update <- distinct(icd10_update, id, diagnosis, .keep_all = TRUE)


## Merge ICD-9 and ICD-10.
icd <- rbind(icd9_update, icd10_update)

# remove rows without date and with invalid dates
icd <- filter(icd, !is.na(icd$date)) # removed 4 rows and 0 participants
icd$date[icd$date=="1901-01-01" | icd$date=="1902-02-02" | icd$date=="1903-03-03" | icd$date=="2037-07-07"] <- NA
icd <- filter(icd, !is.na(id) & !is.na(date)) # removed 0 rows

# export for potential further processing
write.csv(icd, 'inpatient_clinical.csv', row.names = FALSE)





## Add a column for each relevant diagnosis

# dis_other
icd$dis_other <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='dis_other' & codes_inpatient$code_system=='ICD9']){
  icd$dis_other[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='dis_other' & codes_inpatient$code_system=='ICD10']){
  icd$dis_other[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_dis_other <- icd$date; icd$date_dis_other[icd$dis_other==0] <- NA

# depression
icd$depression <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='depression' & codes_inpatient$code_system=='ICD9']){
  icd$depression[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='depression' & codes_inpatient$code_system=='ICD10']){
  icd$depression[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_depression <- icd$date; icd$date_depression[icd$depression==0] <- NA

# falls
icd$fall <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='fall' & codes_inpatient$code_system=='ICD9']){
  icd$fall[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='fall' & codes_inpatient$code_system=='ICD10']){
  icd$fall[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_fall <- icd$date; icd$date_fall[icd$fall==0] <- NA

# femur fracture
icd$femur_fracture <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='femur fracture' & codes_inpatient$code_system=='ICD9']){
  icd$femur_fracture[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='femur fracture' & codes_inpatient$code_system=='ICD10']){
  icd$femur_fracture[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_femur_fracture <- icd$date; icd$date_femur_fracture[icd$femur_fracture==0] <- NA

# pelvic/lumbar fracture
icd$pelvic_fracture <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='pelvic/lumbar fracture' & codes_inpatient$code_system=='ICD9']){
  icd$pelvic_fracture[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='pelvic/lumbar fracture' & codes_inpatient$code_system=='ICD10']){
  icd$pelvic_fracture[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_pelvic_fracture <- icd$date; icd$date_pelvic_fracture[icd$pelvic_fracture==0] <- NA

# shoulder/upper arm fracture
icd$shoulder_fracture <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='shoulder/upper arm fracture' & codes_inpatient$code_system=='ICD9']){
  icd$shoulder_fracture[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='shoulder/upper arm fracture' & codes_inpatient$code_system=='ICD10']){
  icd$shoulder_fracture[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_shoulder_fracture <- icd$date; icd$date_shoulder_fracture[icd$shoulder_fracture==0] <- NA

# forearm fracture
icd$forearm_fracture <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='forearm fracture' & codes_inpatient$code_system=='ICD9']){
  icd$forearm_fracture[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='forearm fracture' & codes_inpatient$code_system=='ICD10']){
  icd$forearm_fracture[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_forearm_fracture <- icd$date; icd$date_forearm_fracture[icd$forearm_fracture==0] <- NA

# wrist fracture
icd$wrist_fracture <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='wrist fracture' & codes_inpatient$code_system=='ICD9']){
  icd$wrist_fracture[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='wrist fracture' & codes_inpatient$code_system=='ICD10']){
  icd$wrist_fracture[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_wrist_fracture <- icd$date; icd$date_wrist_fracture[icd$wrist_fracture==0] <- NA

# ischaemic stroke
icd$stroke_i <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='stroke_i' & codes_inpatient$code_system=='ICD9']){
  icd$stroke_i[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='stroke_i' & codes_inpatient$code_system=='ICD10']){
  icd$stroke_i[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_stroke_i <- icd$date; icd$date_stroke_i[icd$stroke_i==0] <- NA

# haemorrhagic stroke
icd$stroke_h <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='stroke_h' & codes_inpatient$code_system=='ICD9']){
  icd$stroke_h[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='stroke_h' & codes_inpatient$code_system=='ICD10']){
  icd$stroke_h[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_stroke_h <- icd$date; icd$date_stroke_h[icd$stroke_h==0] <- NA

# diabetes
icd$diabetes <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='diabetes' & codes_inpatient$code_system=='ICD9']){
  icd$diabetes[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='diabetes' & codes_inpatient$code_system=='ICD10']){
  icd$diabetes[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_diabetes <- icd$date; icd$date_diabetes[icd$diabetes==0] <- NA

# hypercholesterolemia
icd$hyperchol <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='hypercholesterolemia' & codes_inpatient$code_system=='ICD9']){
  icd$hyperchol[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='hypercholesterolemia' & codes_inpatient$code_system=='ICD10']){
  icd$hyperchol[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_hyperchol <- icd$date; icd$date_hyperchol[icd$hyperchol==0] <- NA

# hypertension
icd$hypertension <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='hypertension' & codes_inpatient$code_system=='ICD9']){
  icd$hypertension[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='hypertension' & codes_inpatient$code_system=='ICD10']){
  icd$hypertension[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_hypertension <- icd$date; icd$date_hypertension[icd$hypertension==0] <- NA

# AF
icd$AF <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='af' & codes_inpatient$code_system=='ICD9']){
  icd$AF[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='af' & codes_inpatient$code_system=='ICD10']){
  icd$AF[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_AF <- icd$date; icd$date_AF[icd$AF==0] <- NA

# AD
icd$AD <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='adem' & codes_inpatient$code_system=='ICD9']){
  icd$AD[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='adem' & codes_inpatient$code_system=='ICD10']){
  icd$AD[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_AD <- icd$date; icd$date_AD[icd$AD==0] <- NA

# VaD
icd$dem_vascular <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='vad' & codes_inpatient$code_system=='ICD9']){
  icd$dem_vascular[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='vad' & codes_inpatient$code_system=='ICD10']){
  icd$dem_vascular[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_dem_vascular <- icd$date; icd$date_dem_vascular[icd$dem_vascular==0] <- NA

# Other dementia
icd$dem_other <- 0
# icd9
for (c in codes_inpatient$code[codes_inpatient$disorder=='other dementia' & codes_inpatient$code_system=='ICD9']){
  icd$dem_other[icd$diagnosis==c & icd$version==9] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
# icd10
for (c in codes_inpatient$code[codes_inpatient$disorder=='other dementia' & codes_inpatient$code_system=='ICD10']){
  icd$dem_other[icd$diagnosis==c & icd$version==10] <- 1 # label diagnosis as present
  codes_inpatient$n[codes_inpatient$code==c] <- length(unique(icd$id[icd$diagnosis==c])) # count the number of occurrences
}
icd$date_dem_other <- icd$date; icd$date_dem_other[icd$dem_other==0] <- NA

# diagnosis of any dementia
icd$dem_any <- rowSums(subset(icd, select=c(AD, dem_vascular, dem_other)), na.rm = TRUE)


# export
write.csv(icd, 'diagnoses_inpatient.csv', row.names = FALSE)



## Final cleaning of inpatient diagnoses

# create a data frame with patients diagnosed with dis_other and arrange ascending by date of diagnosis 
dis_other <- filter(subset(icd, select=c(id, diagnosis, date, dis_other, date_dis_other)), dis_other==1) %>% arrange(date_dis_other)
dis_other <- distinct(dis_other, .keep_all = TRUE) # remove multiple occurrences on the same date
dis_other_count <- dis_other %>% group_by(id) %>% summarize(dis_other_count=sum(dis_other)) # count the occurrences for each participant
# create a data frame with patients diagnosed with depression and arrange ascending by date of diagnosis 
depression <- filter(subset(icd, select=c(id, diagnosis, date, depression, date_depression)), depression==1) %>% arrange(date_depression)
depression <- distinct(depression, .keep_all = TRUE) # remove multiple occurrences on the same date
depression_count <- depression %>% group_by(id) %>% summarize(depression_count=sum(depression)) # count the occurrences for each participant
# create a data frame with patients diagnosed with falls and arrange ascending by date of diagnosis 
fall <- filter(subset(icd, select=c(id, diagnosis, date, fall, date_fall)), fall==1) %>% arrange(date_fall)
fall <- distinct(fall, .keep_all = TRUE)
fall_count <- fall %>% group_by(id) %>% summarize(fall_count=sum(fall))
# create a data frame with patients diagnosed with femur fracture and arrange ascending by date of diagnosis 
femur_fracture <- filter(subset(icd, select=c(id, diagnosis, date, femur_fracture, date_femur_fracture)), femur_fracture==1) %>% arrange(date_femur_fracture)
femur_fracture <- distinct(femur_fracture, .keep_all = TRUE)
femur_fracture_count <- femur_fracture %>% group_by(id) %>% summarize(femur_fracture_count=sum(femur_fracture))
# create a data frame with patients diagnosed with pelvic/lumbar fracture and arrange ascending by date of diagnosis 
pelvic_fracture <- filter(subset(icd, select=c(id, diagnosis, date, pelvic_fracture, date_pelvic_fracture)), pelvic_fracture==1) %>% arrange(date_pelvic_fracture)
pelvic_fracture <- distinct(pelvic_fracture, .keep_all = TRUE)
pelvic_fracture_count <- pelvic_fracture %>% group_by(id) %>% summarize(pelvic_fracture_count=sum(pelvic_fracture))
# create a data frame with patients diagnosed with shoulder/upper arm fracture and arrange ascending by date of diagnosis 
shoulder_fracture <- filter(subset(icd, select=c(id, diagnosis, date, shoulder_fracture, date_shoulder_fracture)), shoulder_fracture==1) %>% arrange(date_shoulder_fracture)
shoulder_fracture <- distinct(shoulder_fracture, .keep_all = TRUE)
shoulder_fracture_count <- shoulder_fracture %>% group_by(id) %>% summarize(shoulder_fracture_count=sum(shoulder_fracture))
# create a data frame with patients diagnosed with forearm fracture and arrange ascending by date of diagnosis 
forearm_fracture <- filter(subset(icd, select=c(id, diagnosis, date, forearm_fracture, date_forearm_fracture)), forearm_fracture==1) %>% arrange(date_forearm_fracture)
forearm_fracture <- distinct(forearm_fracture, .keep_all = TRUE)
forearm_fracture_count <- forearm_fracture %>% group_by(id) %>% summarize(forearm_fracture_count=sum(forearm_fracture))
# create a data frame with patients diagnosed with wrist and arrange ascending by date of diagnosis 
wrist_fracture <- filter(subset(icd, select=c(id, diagnosis, date, wrist_fracture, date_wrist_fracture)), wrist_fracture==1) %>% arrange(date_wrist_fracture)
wrist_fracture <- distinct(wrist_fracture, .keep_all = TRUE)
wrist_fracture_count <- wrist_fracture %>% group_by(id) %>% summarize(wrist_fracture_count=sum(wrist_fracture))
# create a data frame with patients diagnosed with ischaemic stroke and arrange ascending by date of diagnosis 
stroke_i <- filter(subset(icd, select=c(id, diagnosis, date, stroke_i, date_stroke_i)), stroke_i==1) %>% arrange(date_stroke_i)
stroke_i <- distinct(stroke_i, .keep_all = TRUE)
stroke_i_count <- stroke_i %>% group_by(id) %>% summarize(stroke_i_count=sum(stroke_i))
# create a data frame with patients diagnosed with haemorrhagic stroke and arrange ascending by date of diagnosis 
stroke_h <- filter(subset(icd, select=c(id, diagnosis, date, stroke_h, date_stroke_h)), stroke_h==1) %>% arrange(date_stroke_h)
stroke_h <- distinct(stroke_h, .keep_all = TRUE)
stroke_h_count <- stroke_h %>% group_by(id) %>% summarize(stroke_h_count=sum(stroke_h))
# create a data frame with patients diagnosed with diabetes and arrange ascending by date of diagnosis 
diabetes <- filter(subset(icd, select=c(id, diagnosis, date, diabetes, date_diabetes)), diabetes==1) %>% arrange(date_diabetes)
# create a data frame with patients diagnosed with hypercholesterolaemia and arrange ascending by date of diagnosis 
hyperchol <- filter(subset(icd, select=c(id, diagnosis, date, hyperchol, date_hyperchol)), hyperchol==1) %>% arrange(date_hyperchol)
# create a data frame with patients diagnosed with hypertension and arrange ascending by date of diagnosis 
hypertension <- filter(subset(icd, select=c(id, diagnosis, date, hypertension, date_hypertension)), hypertension==1) %>% arrange(date_hypertension)
# create a data frame with patients diagnosed with AF and arrange ascending by date of diagnosis 
AF <- filter(subset(icd, select=c(id, diagnosis, date, AF, date_AF)), AF==1) %>% arrange(date_AF)
# create a data frame with patients diagnosed with AD and arrange ascending by date of diagnosis
AD <- filter(subset(icd, select=c(id, diagnosis, date, AD, date_AD)), AD==1) %>% arrange(date_AD)
# create a data frame with patients diagnosed with vascular dementia and arrange ascending by date of diagnosis
dem_vascular <- filter(subset(icd, select=c(id, diagnosis, date, dem_vascular, date_dem_vascular)), dem_vascular==1) %>% arrange(date_dem_vascular)
# same for other dementias
dem_other <- filter(subset(icd, select=c(id, diagnosis, date, dem_other, date_dem_other)), dem_other==1) %>% arrange(date_dem_other) 
# indicate any fracture
icd$fracture_any <- 0
icd$fracture_any[icd$femur_fracture==1 | icd$pelvic_fracture==1 | icd$shoulder_fracture==1 | icd$forearm_fracture==1 |
                   icd$wrist_fracture==1] <- 1
icd$date_fracture_any[icd$fracture_any==1] <- as.character(icd$date[icd$fracture_any==1])
fracture_any <- filter(subset(icd, select=c(id, diagnosis, date, fracture_any, date_fracture_any, femur_fracture, date_femur_fracture,
                                            pelvic_fracture, date_pelvic_fracture, shoulder_fracture, date_shoulder_fracture,
                                            forearm_fracture, date_forearm_fracture, wrist_fracture, date_wrist_fracture)), 
                       fracture_any==1) %>% arrange(date_fracture_any)
# treat multiple fractures in one individual on same day as duplicates (i.e., due to same incident) and remove
fracture_any <- distinct(fracture_any, id, fracture_any, date_fracture_any, .keep_all = TRUE)
fracture_any_count <- fracture_any %>% group_by(id) %>% summarize(fracture_any_count=sum(fracture_any))
# re-join the cleaned (of duplicates) diagnoses and export
icd <- filter(icd, depression!=1 & fall!=1 & femur_fracture!=1 & pelvic_fracture!=1 & shoulder_fracture!=1 & forearm_fracture!=1
              & wrist_fracture!=1 & stroke_i!=1 & stroke_h!=1 & dis_other!=1)
icd <- rbind.fill(icd, dis_other, depression, fall, stroke_i, stroke_h, fracture_any)


# final cleaning of duplicates (i.e. "true" duplicates: identical rows)
icd <- distinct(icd)
write.csv(icd, 'diagnoses_inpatient_cleaned.csv', row.names = FALSE)

# for all disorders, remove duplicates (retain the diagnosis on the earliest available date) and potentially add number of occurrences (for some)
dis_other$date <- NULL
dis_other$diagnosis <- NULL
dis_other <- dis_other[!duplicated(dis_other[,c('id')]),]
dis_other <- merge(dis_other, dis_other_count, by='id', all.x=TRUE)
depression$date <- NULL
depression$diagnosis <- NULL
depression <- depression[!duplicated(depression[,c('id')]),]
depression <- merge(depression, depression_count, by='id', all.x=TRUE)
fall$date <- NULL
fall$diagnosis <- NULL
fall <- fall[!duplicated(fall[,c('id')]),]
fall <- merge(fall, fall_count, by='id', all.x=TRUE)
femur_fracture$date <- NULL
femur_fracture$diagnosis <- NULL
femur_fracture <- femur_fracture[!duplicated(femur_fracture[,c('id')]),]
femur_fracture <- merge(femur_fracture, femur_fracture_count, by='id', all.x=TRUE)
pelvic_fracture$date <- NULL
pelvic_fracture$diagnosis <- NULL
pelvic_fracture <- pelvic_fracture[!duplicated(pelvic_fracture[,c('id')]),]
pelvic_fracture <- merge(pelvic_fracture, pelvic_fracture_count, by='id', all.x=TRUE)
shoulder_fracture$date <- NULL
shoulder_fracture$diagnosis <- NULL
shoulder_fracture <- shoulder_fracture[!duplicated(shoulder_fracture[,c('id')]),]
shoulder_fracture <- merge(shoulder_fracture, shoulder_fracture_count, by='id', all.x=TRUE)
forearm_fracture$date <- NULL
forearm_fracture$diagnosis <- NULL
forearm_fracture <- forearm_fracture[!duplicated(forearm_fracture[,c('id')]),]
forearm_fracture <- merge(forearm_fracture, forearm_fracture_count, by='id', all.x=TRUE)
wrist_fracture$date <- NULL
wrist_fracture$diagnosis <- NULL
wrist_fracture <- wrist_fracture[!duplicated(wrist_fracture[,c('id')]),]
wrist_fracture <- merge(wrist_fracture, wrist_fracture_count, by='id', all.x=TRUE)
stroke_i$date <- NULL
stroke_i$diagnosis <- NULL
stroke_i <- stroke_i[!duplicated(stroke_i[,c('id')]),]
stroke_i <- merge(stroke_i, stroke_i_count, by='id', all.x=TRUE)
stroke_h$date <- NULL
stroke_h$diagnosis <- NULL
stroke_h <- stroke_h[!duplicated(stroke_h[,c('id')]),]
stroke_h <- merge(stroke_h, stroke_h_count, by='id', all.x=TRUE)
diabetes$date <- NULL
diabetes$diagnosis <- NULL
diabetes <- diabetes[!duplicated(diabetes[,c('id')]),]
hyperchol <- hyperchol[!duplicated(hyperchol[,c('id')]),]
hyperchol$date <- NULL
hyperchol$diagnosis <- NULL
hypertension <- hypertension[!duplicated(hypertension[,c('id')]),]
hypertension$date <- NULL
hypertension$diagnosis <- NULL
AF <- AF[!duplicated(AF[,c('id')]),]
AF$date <- NULL
AF$diagnosis <- NULL
AD <- AD[!duplicated(AD[,c('id')]),]
AD$date <- NULL
AD$diagnosis <- NULL
dem_vascular <- dem_vascular[!duplicated(dem_vascular[,c('id')]),]
dem_vascular$date <- NULL
dem_vascular$diagnosis <- NULL
dem_other <- dem_other[!duplicated(dem_other[,c('id')]),]
dem_other$date <- NULL
dem_other$diagnosis <- NULL

# merge 
icd_diagnosed <- merge(dis_other, depression, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, femur_fracture, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, fall, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, pelvic_fracture, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, shoulder_fracture, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, forearm_fracture, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, wrist_fracture, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, stroke_i, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, stroke_h, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, diabetes, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, hyperchol, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, hypertension, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, AF, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, AD, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, dem_vascular, by='id', all=TRUE)
icd_diagnosed <- merge(icd_diagnosed, dem_other, by='id', all=TRUE)

# merge with original dataset that contains all participants (also those without the relevant diagnoses)
icd <- distinct(icd, id, .keep_all = TRUE) # keep only one entry for each participant
icd <- subset(icd, select=c(id)) # remove unnecessary columns
icd <- merge(icd, icd_diagnosed, all = TRUE)

# create column indicating presence of any dementia
icd$dem_any <- rowSums(subset(icd, select=c(AD, dem_vascular, dem_other)), na.rm = TRUE)
icd$dem_any[icd$dem_any > 0] <- 1

# create column indicating number of all fractures
# one incident could have caused several fractures; to avoid counting each of the latter as a separate fall,
# we bind the fractures into one data frame, remove duplicates based on date and id and then separate again
colnames(femur_fracture)[which(names(femur_fracture) == "date_femur_fracture")] <- "date_fracture" # change colname so that rbind doesn't complain
colnames(pelvic_fracture)[which(names(pelvic_fracture) == "date_pelvic_fracture")] <- "date_fracture"
colnames(shoulder_fracture)[which(names(shoulder_fracture) == "date_shoulder_fracture")] <- "date_fracture"
colnames(forearm_fracture)[which(names(forearm_fracture) == "date_forearm_fracture")] <- "date_fracture"
colnames(wrist_fracture)[which(names(wrist_fracture) == "date_wrist_fracture")] <- "date_fracture"
femur_fracture$femur_fracture_count <- NULL; femur_fracture$femur_fracture <- NULL # remove column with counts
pelvic_fracture$pelvic_fracture_count <- NULL; pelvic_fracture$pelvic_fracture <- NULL
shoulder_fracture$shoulder_fracture_count <- NULL; shoulder_fracture$shoulder_fracture <- NULL
forearm_fracture$forearm_fracture_count <- NULL; forearm_fracture$forearm_fracture <- NULL
wrist_fracture$wrist_fracture_count <- NULL; wrist_fracture$wrist_fracture <- NULL
fractures_all <- rbind(femur_fracture, pelvic_fracture, shoulder_fracture, forearm_fracture, wrist_fracture) # bind
fractures_all <- distinct(fractures_all, .keep_all = TRUE) # remove duplicates (i.e., multiple fractures due to same incident)
colnames(fractures_all)[which(names(fractures_all) == "date_fracture")] <- "date_fracture_any"
fractures_all$fracture_any_count <- 1
fractures_all_ids <- fractures_all %>% group_by(id) %>% summarize(fracture_any_count=sum(fracture_any_count)) # separate into an id-based data frame
fractures_all <- fractures_all[!duplicated(fractures_all[,c('id')]),] # remove all but the first date from the non-id-based data frame
fractures_all$fracture_any_count <- NULL
icd <- merge(icd, fractures_all, by='id', all = TRUE) # merge with main dataset
icd <- merge(icd, fractures_all_ids, by='id', all = TRUE) # merge with main dataset

# change NA's to 0's (indicating that the participant was not diagnosed with the relevant disorder)
icd$dis_other[is.na(icd$dis_other)] <- 0 
icd$dis_other_count[is.na(icd$dis_other_count)] <- 0 
icd$depression[is.na(icd$depression)] <- 0 
icd$depression_count[is.na(icd$depression_count)] <- 0 
icd$fall[is.na(icd$fall)] <- 0 
icd$fall_count[is.na(icd$fall_count)] <- 0 
icd$femur_fracture[is.na(icd$femur_fracture)] <- 0 
icd$femur_fracture_count[is.na(icd$femur_fracture_count)] <- 0 
icd$pelvic_fracture[is.na(icd$pelvic_fracture)] <- 0 
icd$pelvic_fracture_count[is.na(icd$pelvic_fracture_count)] <- 0 
icd$shoulder_fracture[is.na(icd$shoulder_fracture)] <- 0 
icd$shoulder_fracture_count[is.na(icd$shoulder_fracture_count)] <- 0 
icd$forearm_fracture[is.na(icd$forearm_fracture)] <- 0 
icd$forearm_fracture_count[is.na(icd$forearm_fracture_count)] <- 0 
icd$wrist_fracture[is.na(icd$wrist_fracture)] <- 0 
icd$wrist_fracture_count[is.na(icd$wrist_fracture_count)] <- 0 
icd$stroke_i[is.na(icd$stroke_i)] <- 0 
icd$stroke_i_count[is.na(icd$stroke_i_count)] <- 0 
icd$stroke_h[is.na(icd$stroke_h)] <- 0 
icd$stroke_count[is.na(icd$stroke_h_count)] <- 0 
icd$diabetes[is.na(icd$diabetes)] <- 0 
icd$hyperchol[is.na(icd$hyperchol)] <- 0 
icd$hypertension[is.na(icd$hypertension)] <- 0 
icd$AF[is.na(icd$AF)] <- 0 
icd$AD[is.na(icd$AD)] <- 0 
icd$dem_vascular[is.na(icd$dem_vascular)] <- 0 
icd$dem_other[is.na(icd$dem_other)] <- 0 
icd$dem_any[is.na(icd$dem_any)] <- 0 
icd$fracture_any[is.na(icd$fracture_any)] <- 0 

# export
write.csv(icd, 'diagnoses_inpatient_relevant.csv', row.names = FALSE)






### Add primary care diagnoses ###

## Import and prepare
meds_diagnoses <- read.csv('gp_clinical.txt', sep="\t", header=TRUE, quote="")

# rename columns
colnames(meds_diagnoses)[which(names(meds_diagnoses) == "eid")] <- "id"
colnames(meds_diagnoses)[which(names(meds_diagnoses) == "event_dt")] <- "date"
colnames(meds_diagnoses)[which(names(meds_diagnoses) == "read_3")] <- "diagnosis"
meds_diagnoses$read_2 <- NULL
meds_diagnoses$value1 <- NULL
meds_diagnoses$value2 <- NULL
meds_diagnoses$value3 <- NULL

# remove rows without dates or with invalid dates
meds_diagnoses <- filter(meds_diagnoses, date != '') # removed 163,207 rows and 0 participants
meds_diagnoses$date[meds_diagnoses$date=="01/01/1901" | meds_diagnoses$date=="02/02/1902" | meds_diagnoses$date=="03/03/1903" | meds_diagnoses$date=="07/07/2037"] <- NA
meds_diagnoses <- filter(meds_diagnoses, !is.na(id) & !is.na(date)) # removed 60,443 rows

# change class of all columns to character
meds_diagnoses <- as.data.frame(sapply(meds_diagnoses, as.character))




## Add a column for each relevant diagnosis

# dis_other
meds_diagnoses$dis_other <- 0
for (c in codes_gp$code[codes_gp$disorder=='dis_other']){
  meds_diagnoses$dis_other[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_dis_other <- meds_diagnoses$date; meds_diagnoses$date_dis_other[meds_diagnoses$dis_other==0] <- NA

# depression
meds_diagnoses$depression <- 0
for (c in codes_gp$code[codes_gp$disorder=='depression']){
  meds_diagnoses$depression[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_depression <- meds_diagnoses$date; meds_diagnoses$date_depression[meds_diagnoses$depression==0] <- NA

# fall
meds_diagnoses$fall <- 0
for (c in codes_gp$code[codes_gp$disorder=='fall']){
  meds_diagnoses$fall[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_fall <- meds_diagnoses$date; meds_diagnoses$date_fall[meds_diagnoses$fall==0] <- NA

# femur_fracture
meds_diagnoses$femur_fracture <- 0
for (c in codes_gp$code[codes_gp$disorder=='femur fracture']){
  meds_diagnoses$femur_fracture[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_femur_fracture <- meds_diagnoses$date; meds_diagnoses$date_femur_fracture[meds_diagnoses$femur_fracture==0] <- NA

# pelvic/lumbar fracture
meds_diagnoses$pelvic_fracture <- 0
for (c in codes_gp$code[codes_gp$disorder=='pelvic/lumbar fracture']){
  meds_diagnoses$pelvic_fracture[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_pelvic_fracture <- meds_diagnoses$date; meds_diagnoses$date_pelvic_fracture[meds_diagnoses$pelvic_fracture==0] <- NA

# shoulder/upper arm fracture
meds_diagnoses$shoulder_fracture <- 0
for (c in codes_gp$code[codes_gp$disorder=='shoulder/upper arm fracture']){
  meds_diagnoses$shoulder_fracture[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_shoulder_fracture <- meds_diagnoses$date; meds_diagnoses$date_shoulder_fracture[meds_diagnoses$shoulder_fracture==0] <- NA

# forearm fracture
meds_diagnoses$forearm_fracture <- 0
for (c in codes_gp$code[codes_gp$disorder=='forearm fracture']){
  meds_diagnoses$forearm_fracture[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_forearm_fracture <- meds_diagnoses$date; meds_diagnoses$date_forearm_fracture[meds_diagnoses$forearm_fracture==0] <- NA

# wrist fracture
meds_diagnoses$wrist_fracture <- 0
for (c in codes_gp$code[codes_gp$disorder=='wrist fracture']){
  meds_diagnoses$wrist_fracture[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_wrist_fracture <- meds_diagnoses$date; meds_diagnoses$date_wrist_fracture[meds_diagnoses$wrist_fracture==0] <- NA

# ischaemic stroke
meds_diagnoses$stroke_i <- 0
for (c in codes_gp$code[codes_gp$disorder=='stroke_i']){
  meds_diagnoses$stroke_i[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_stroke_i <- meds_diagnoses$date; meds_diagnoses$date_stroke_i[meds_diagnoses$stroke_i==0] <- NA

# haemorrhagic stroke
meds_diagnoses$stroke_h <- 0
for (c in codes_gp$code[codes_gp$disorder=='stroke_h']){
  meds_diagnoses$stroke_h[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_stroke_h <- meds_diagnoses$date; meds_diagnoses$date_stroke_h[meds_diagnoses$stroke_h==0] <- NA

# diabetes
meds_diagnoses$diabetes <- 0
for (c in codes_gp$code[codes_gp$disorder=='diabetes']){
  meds_diagnoses$diabetes[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_diabetes <- meds_diagnoses$date; meds_diagnoses$date_diabetes[meds_diagnoses$diabetes==0] <- NA

# hypercholesterolemia
meds_diagnoses$hyperchol <- 0
for (c in codes_gp$code[codes_gp$disorder=='hypercholesterolemia']){
  meds_diagnoses$hyperchol[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_hyperchol <- meds_diagnoses$date; meds_diagnoses$date_hyperchol[meds_diagnoses$hyperchol==0] <- NA

# hypertension
meds_diagnoses$hypertension <- 0
for (c in codes_gp$code[codes_gp$disorder=='hypertension']){
  meds_diagnoses$hypertension[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_hypertension <- meds_diagnoses$date; meds_diagnoses$date_hypertension[meds_diagnoses$hypertension==0] <- NA

# AF
meds_diagnoses$AF <- 0
for (c in codes_gp$code[codes_gp$disorder=='af']){
  meds_diagnoses$AF[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_AF <- meds_diagnoses$date; meds_diagnoses$date_AF[meds_diagnoses$AF==0] <- NA

# AD
meds_diagnoses$AD <- 0
for (c in codes_gp$code[codes_gp$disorder=='adem']){
  meds_diagnoses$AD[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_AD <- meds_diagnoses$date; meds_diagnoses$date_AD[meds_diagnoses$AD==0] <- NA

# VaD
meds_diagnoses$dem_vascular <- 0
for (c in codes_gp$code[codes_gp$disorder=='vad']){
  meds_diagnoses$dem_vascular[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_dem_vascular <- meds_diagnoses$date; meds_diagnoses$date_dem_vascular[meds_diagnoses$dem_vascular==0] <- NA

# Other dementia
meds_diagnoses$dem_other <- 0
for (c in codes_gp$code[codes_gp$disorder=='other dementia']){
  meds_diagnoses$dem_other[meds_diagnoses$diagnosis==c] <- 1 # label diagnosis as present
  codes_gp$n[codes_gp$code==c] <- length(unique(meds_diagnoses$id[meds_diagnoses$diagnosis==c])) # count the number of occurrences
}
meds_diagnoses$date_dem_other <- meds_diagnoses$date; meds_diagnoses$date_dem_other[meds_diagnoses$dem_other==0] <- NA

# diagnosis of any dementia
meds_diagnoses$dem_any <- rowSums(subset(meds_diagnoses, select=c(AD, dem_vascular, dem_other)), na.rm = TRUE)

# diagnosis of any fracture
meds_diagnoses$fracture_any <- rowSums(subset(meds_diagnoses, select=c(femur_fracture, pelvic_fracture, shoulder_fracture, 
                                                                       forearm_fracture, wrist_fracture)), na.rm = TRUE)
meds_diagnoses$date_fracture_any[meds_diagnoses$fracture_any==1] <- as.character(meds_diagnoses$date[meds_diagnoses$fracture_any==1])

# export
write.csv(meds_diagnoses, 'diagnoses_GP.csv', row.names = FALSE)





# combine counts of inpatient- and GP- codes and export
codes_new <- rbind(codes_gp, codes_inpatient)
codes_new <- filter(codes_new, n!=0)
write.csv(codes_new, 'diagnoses_counts.csv', row.names = FALSE)





## Remove duplicates 
fracture_any <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, fracture_any, date_fracture_any, femur_fracture, date_femur_fracture,
                                                       pelvic_fracture, date_pelvic_fracture, shoulder_fracture, date_shoulder_fracture,
                                                       forearm_fracture, date_forearm_fracture, wrist_fracture, date_wrist_fracture)), 
                       fracture_any==1) %>% arrange(date_fracture_any)
# treat multiple fractures in one individual on same day as duplicates (i.e., due to same incident) and remove
fracture_any <- distinct(fracture_any, id, diagnosis, fracture_any, date_fracture_any, .keep_all = TRUE)
fracture_any_count <- fracture_any %>% group_by(id) %>% summarize(fracture_any_count=sum(fracture_any))
# create a data frame with patients diagnosed with dis_other and arrange ascending by date of diagnosis 
dis_other <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, dis_other, date_dis_other)), dis_other==1) %>% arrange(date_dis_other)
dis_other <- distinct(dis_other, .keep_all = TRUE) # remove multiple occurrences on the same date
dis_other_count <- dis_other %>% group_by(id) %>% summarise(dis_other_count=sum(dis_other)) # count the occurrences for each participant
# create a data frame with patients diagnosed with depression and arrange ascending by date of diagnosis 
depression <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, depression, date_depression)), depression==1) %>% arrange(date_depression)
depression <- distinct(depression, .keep_all = TRUE) # remove multiple occurrences on the same date
depression_count <- depression %>% group_by(id) %>% summarize(depression_count=sum(depression)) # count the occurrences for each participant
# create a data frame with patients diagnosed with depression and arrange ascending by date of diagnosis 
fall <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, fall, date_fall)), fall==1) %>% arrange(date_fall)
fall <- distinct(fall, .keep_all = TRUE) # remove multiple occurrences on the same date
fall_count <- fall %>% group_by(id) %>% summarize(fall_count=sum(fall)) # count the occurrences for each participant
# create a data frame with patients diagnosed with femur fracture arrange ascending by date of diagnosis 
femur_fracture <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, femur_fracture, date_femur_fracture)), femur_fracture==1) %>% arrange(date_femur_fracture)
femur_fracture <- distinct(femur_fracture, .keep_all = TRUE)
femur_fracture_count <- femur_fracture %>% group_by(id) %>% summarize(femur_fracture_count=sum(femur_fracture))
# create a data frame with patients diagnosed with pelvic/lumbar fracture and arrange ascending by date of diagnosis 
pelvic_fracture <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, pelvic_fracture, date_pelvic_fracture)), pelvic_fracture==1) %>% arrange(date_pelvic_fracture)
pelvic_fracture <- distinct(pelvic_fracture, .keep_all = TRUE)
pelvic_fracture_count <- pelvic_fracture %>% group_by(id) %>% summarize(pelvic_fracture_count=sum(pelvic_fracture))
# create a data frame with patients diagnosed with shoulder/upper arm fracture and arrange ascending by date of diagnosis 
shoulder_fracture <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, shoulder_fracture, date_shoulder_fracture)), shoulder_fracture==1) %>% arrange(date_shoulder_fracture)
shoulder_fracture <- distinct(shoulder_fracture, .keep_all = TRUE)
shoulder_fracture_count <- shoulder_fracture %>% group_by(id) %>% summarize(shoulder_fracture_count=sum(shoulder_fracture))
# create a data frame with patients diagnosed with forearm fracture and arrange ascending by date of diagnosis 
forearm_fracture <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, forearm_fracture, date_forearm_fracture)), forearm_fracture==1) %>% arrange(date_forearm_fracture)
forearm_fracture <- distinct(forearm_fracture, .keep_all = TRUE)
forearm_fracture_count <- forearm_fracture %>% group_by(id) %>% summarize(forearm_fracture_count=sum(forearm_fracture))
# create a data frame with patients diagnosed with wrist and arrange ascending by date of diagnosis 
wrist_fracture <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, wrist_fracture, date_wrist_fracture)), wrist_fracture==1) %>% arrange(date_wrist_fracture)
wrist_fracture <- distinct(wrist_fracture, .keep_all = TRUE)
wrist_fracture_count <- wrist_fracture %>% group_by(id) %>% summarize(wrist_fracture_count=sum(wrist_fracture))
# create a data frame with patients diagnosed with ischaemic stroke and arrange ascending by date of diagnosis 
stroke_i <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, stroke_i, date_stroke_i)), stroke_i==1) %>% arrange(date_stroke_i)
stroke_i <- distinct(stroke_i, .keep_all = TRUE)
stroke_i_count <- stroke_i %>% group_by(id) %>% summarize(stroke_i_count=sum(stroke_i))
# create a data frame with patients diagnosed with haemorrhagic stroke and arrange ascending by date of diagnosis 
stroke_h <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, stroke_h, date_stroke_h)), stroke_h==1) %>% arrange(date_stroke_h)
stroke_h <- distinct(stroke_h, .keep_all = TRUE)
stroke_h_count <- stroke_h %>% group_by(id) %>% summarize(stroke_h_count=sum(stroke_h))
# create a data frame with patients diagnosed with diabetes and arrange ascending by date of diagnosis 
diabetes <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, diabetes, date_diabetes)), diabetes==1) %>% arrange(date_diabetes)
# create a data frame with patients diagnosed with hypercholesterolaemia and arrange ascending by date of diagnosis 
hyperchol <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, hyperchol, date_hyperchol)), hyperchol==1) %>% arrange(date_hyperchol)
# create a data frame with patients diagnosed with hypertension and arrange ascending by date of diagnosis 
hypertension <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, hypertension, date_hypertension)), hypertension==1) %>% arrange(date_hypertension)
# create a data frame with patients diagnosed with AF and arrange ascending by date of diagnosis 
AF <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, AF, date_AF)), AF==1) %>% arrange(date_AF)
# create a data frame with patients diagnosed with AD and arrange ascending by date of diagnosis
AD <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, AD, date_AD)), AD==1) %>% arrange(date_AD)
# create a data frame with patients diagnosed with vascular dementia and arrange ascending by date of diagnosis
dem_vascular <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, dem_vascular, date_dem_vascular)), dem_vascular==1) %>% arrange(date_dem_vascular)
# same for other dementias
dem_other <- filter(subset(meds_diagnoses, select=c(id, diagnosis, date, dem_other, date_dem_other)), dem_other==1) %>% arrange(date_dem_other) 

# remove all rows with found diagnoses
meds_diagnoses <- filter(meds_diagnoses, dis_other!=1 & depression!=1 & fall!=1 & femur_fracture!=1 & pelvic_fracture!=1 & 
                           shoulder_fracture!=1 & forearm_fracture!=1 & wrist_fracture!=1 & stroke_i!=1 & stroke_h!=1)
# add back only those rows that are not duplicates
meds_diagnoses <- rbind.fill(meds_diagnoses, dis_other, depression, fall, stroke_i, stroke_h, fracture_any)
# final cleaning of duplicates (i.e. "true" duplicates: identical rows)
meds_diagnoses <- distinct(meds_diagnoses)
# export
write.csv(meds_diagnoses, 'diagnoses_GP_cleaned.csv', row.names = FALSE)




# for all disorders, remove duplicates (retain the diagnosis on the earliest available date) and potentially add number of occurrences (for some)
dis_other$date <- NULL
dis_other$diagnosis <- NULL
dis_other <- dis_other[!duplicated(dis_other[,c('id')]),]
dis_other <- merge(dis_other, dis_other_count, by='id', all.x=TRUE)
depression$date <- NULL
depression$diagnosis <- NULL
depression <- depression[!duplicated(depression[,c('id')]),]
depression <- merge(depression, depression_count, by='id', all.x=TRUE)
fall$date <- NULL
fall$diagnosis <- NULL
fall <- fall[!duplicated(fall[,c('id')]),]
fall <- merge(fall, fall_count, by='id', all.x=TRUE)
femur_fracture$date <- NULL
femur_fracture$diagnosis <- NULL
femur_fracture <- femur_fracture[!duplicated(femur_fracture[,c('id')]),]
femur_fracture <- merge(femur_fracture, femur_fracture_count, by='id', all.x=TRUE)
pelvic_fracture$date <- NULL
pelvic_fracture$diagnosis <- NULL
pelvic_fracture <- pelvic_fracture[!duplicated(pelvic_fracture[,c('id')]),]
pelvic_fracture <- merge(pelvic_fracture, pelvic_fracture_count, by='id', all.x=TRUE)
shoulder_fracture$date <- NULL
shoulder_fracture$diagnosis <- NULL
shoulder_fracture <- shoulder_fracture[!duplicated(shoulder_fracture[,c('id')]),]
shoulder_fracture <- merge(shoulder_fracture, shoulder_fracture_count, by='id', all.x=TRUE)
forearm_fracture$date <- NULL
forearm_fracture$diagnosis <- NULL
forearm_fracture <- forearm_fracture[!duplicated(forearm_fracture[,c('id')]),]
forearm_fracture <- merge(forearm_fracture, forearm_fracture_count, by='id', all.x=TRUE)
wrist_fracture$date <- NULL
wrist_fracture$diagnosis <- NULL
wrist_fracture <- wrist_fracture[!duplicated(wrist_fracture[,c('id')]),]
wrist_fracture <- merge(wrist_fracture, wrist_fracture_count, by='id', all.x=TRUE)
stroke_i$date <- NULL
stroke_i$diagnosis <- NULL
stroke_i <- stroke_i[!duplicated(stroke_i[,c('id')]),]
stroke_i <- merge(stroke_i, stroke_i_count, by='id', all.x=TRUE)
stroke_h$date <- NULL
stroke_h$diagnosis <- NULL
stroke_h <- stroke_h[!duplicated(stroke_h[,c('id')]),]
stroke_h <- merge(stroke_h, stroke_h_count, by='id', all.x=TRUE)
diabetes$date <- NULL
diabetes$diagnosis <- NULL
diabetes <- diabetes[!duplicated(diabetes[,c('id')]),]
hyperchol <- hyperchol[!duplicated(hyperchol[,c('id')]),]
hyperchol$date <- NULL
hyperchol$diagnosis <- NULL
hypertension <- hypertension[!duplicated(hypertension[,c('id')]),]
hypertension$date <- NULL
hypertension$diagnosis <- NULL
AF <- AF[!duplicated(AF[,c('id')]),]
AF$date <- NULL
AF$diagnosis <- NULL
AD <- AD[!duplicated(AD[,c('id')]),]
AD$date <- NULL
AD$diagnosis <- NULL
dem_vascular <- dem_vascular[!duplicated(dem_vascular[,c('id')]),]
dem_vascular$date <- NULL
dem_vascular$diagnosis <- NULL
dem_other <- dem_other[!duplicated(dem_other[,c('id')]),]
dem_other$date <- NULL
dem_other$diagnosis <- NULL

# merge 
meds_diagnoses_diagnosed <- merge(dis_other, depression, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, femur_fracture, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, fall, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, pelvic_fracture, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, shoulder_fracture, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, forearm_fracture, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, wrist_fracture, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, stroke_i, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, stroke_h, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, diabetes, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, hyperchol, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, hypertension, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, AF, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, AD, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, dem_vascular, by='id', all=TRUE)
meds_diagnoses_diagnosed <- merge(meds_diagnoses_diagnosed, dem_other, by='id', all=TRUE)

# merge with original dataset that contains all participants (also those without the relevant diagnoses)
meds_diagnoses <- distinct(meds_diagnoses, id, .keep_all = TRUE) # keep only one entry for each participant
meds_diagnoses <- subset(meds_diagnoses, select=c(id)) # remove unnecessary columns
meds_diagnoses <- merge(meds_diagnoses, meds_diagnoses_diagnosed, all = TRUE)

# create column indicating presence of any dementia
meds_diagnoses$dem_any <- rowSums(subset(meds_diagnoses, select=c(AD, dem_vascular, dem_other)), na.rm = TRUE)
meds_diagnoses$dem_any[meds_diagnoses$dem_any > 0] <- 1

# create column indicating number of all fractures
# one incident could have caused several fractures; to avoid counting each of the latter as a separate fall,
# we bind the fractures into one data frame, remove duplicates based on date and id and then separate again
colnames(femur_fracture)[which(names(femur_fracture) == "date_femur_fracture")] <- "date_fracture" # change colname so that rbind doesn't complain
colnames(pelvic_fracture)[which(names(pelvic_fracture) == "date_pelvic_fracture")] <- "date_fracture"
colnames(shoulder_fracture)[which(names(shoulder_fracture) == "date_shoulder_fracture")] <- "date_fracture"
colnames(forearm_fracture)[which(names(forearm_fracture) == "date_forearm_fracture")] <- "date_fracture"
colnames(wrist_fracture)[which(names(wrist_fracture) == "date_wrist_fracture")] <- "date_fracture"
femur_fracture$femur_fracture_count <- NULL; femur_fracture$femur_fracture <- NULL # remove column with counts
pelvic_fracture$pelvic_fracture_count <- NULL; pelvic_fracture$pelvic_fracture <- NULL
shoulder_fracture$shoulder_fracture_count <- NULL; shoulder_fracture$shoulder_fracture <- NULL
forearm_fracture$forearm_fracture_count <- NULL; forearm_fracture$forearm_fracture <- NULL
wrist_fracture$wrist_fracture_count <- NULL; wrist_fracture$wrist_fracture <- NULL
fractures_all <- rbind(femur_fracture, pelvic_fracture, shoulder_fracture, forearm_fracture, wrist_fracture) # bind
fractures_all <- distinct(fractures_all, .keep_all = TRUE) # remove duplicates (i.e., multiple fractures due to same incident)
colnames(fractures_all)[which(names(fractures_all) == "date_fracture")] <- "date_fracture_any"
fractures_all$fracture_any_count <- 1
fractures_all_ids <- fractures_all %>% group_by(id) %>% summarize(fracture_any_count=sum(fracture_any_count)) # separate into an id-based data frame
fractures_all <- fractures_all[!duplicated(fractures_all[,c('id')]),] # remove all but the first date from the non-id-based data frame
fractures_all$fracture_any_count <- NULL
meds_diagnoses <- merge(meds_diagnoses, fractures_all, by='id', all = TRUE) # merge with main dataset
meds_diagnoses <- merge(meds_diagnoses, fractures_all_ids, by='id', all = TRUE) # merge with main dataset


# change NA's to 0's (indicating that the participant was not diagnosed with the relevant disorder)
meds_diagnoses$dis_other[is.na(meds_diagnoses$dis_other)] <- 0 
meds_diagnoses$dis_other_count[is.na(meds_diagnoses$dis_other_count)] <- 0 
meds_diagnoses$depression[is.na(meds_diagnoses$depression)] <- 0 
meds_diagnoses$depression_count[is.na(meds_diagnoses$depression_count)] <- 0 
meds_diagnoses$fall[is.na(meds_diagnoses$fall)] <- 0 
meds_diagnoses$fall_count[is.na(meds_diagnoses$fall_count)] <- 0 
meds_diagnoses$femur_fracture[is.na(meds_diagnoses$femur_fracture)] <- 0 
meds_diagnoses$femur_fracture_count[is.na(meds_diagnoses$femur_fracture_count)] <- 0 
meds_diagnoses$pelvic_fracture[is.na(meds_diagnoses$pelvic_fracture)] <- 0 
meds_diagnoses$pelvic_fracture_count[is.na(meds_diagnoses$pelvic_fracture_count)] <- 0 
meds_diagnoses$shoulder_fracture[is.na(meds_diagnoses$shoulder_fracture)] <- 0 
meds_diagnoses$shoulder_fracture_count[is.na(meds_diagnoses$shoulder_fracture_count)] <- 0 
meds_diagnoses$forearm_fracture[is.na(meds_diagnoses$forearm_fracture)] <- 0 
meds_diagnoses$forearm_fracture_count[is.na(meds_diagnoses$forearm_fracture_count)] <- 0 
meds_diagnoses$wrist_fracture[is.na(meds_diagnoses$wrist_fracture)] <- 0 
meds_diagnoses$wrist_fracture_count[is.na(meds_diagnoses$wrist_fracture_count)] <- 0 
meds_diagnoses$stroke_i[is.na(meds_diagnoses$stroke_i)] <- 0 
meds_diagnoses$stroke_i_count[is.na(meds_diagnoses$stroke_i_count)] <- 0 
meds_diagnoses$stroke_h[is.na(meds_diagnoses$stroke_h)] <- 0 
meds_diagnoses$stroke_count[is.na(meds_diagnoses$stroke_h_count)] <- 0 
meds_diagnoses$diabetes[is.na(meds_diagnoses$diabetes)] <- 0 
meds_diagnoses$hyperchol[is.na(meds_diagnoses$hyperchol)] <- 0 
meds_diagnoses$hypertension[is.na(meds_diagnoses$hypertension)] <- 0 
meds_diagnoses$AF[is.na(meds_diagnoses$AF)] <- 0 
meds_diagnoses$AD[is.na(meds_diagnoses$AD)] <- 0 
meds_diagnoses$dem_vascular[is.na(meds_diagnoses$dem_vascular)] <- 0 
meds_diagnoses$dem_other[is.na(meds_diagnoses$dem_other)] <- 0 
meds_diagnoses$dem_any[is.na(meds_diagnoses$dem_any)] <- 0 
meds_diagnoses$fracture_any[is.na(meds_diagnoses$fracture_any)] <- 0 

# export
write.csv(meds_diagnoses, 'diagnoses_GP_relevant.csv', row.names = FALSE)







### Combine inpatient and GP files ###

gp <- read.csv('diagnoses_GP_cleaned.csv')
inpatient <- read.csv('diagnoses_inpatient_cleaned.csv') #load ICD-diagnoses

gp[, c("date", "date_depression", "date_dis_other", "date_fall", "date_femur_fracture", "date_pelvic_fracture",
        "date_shoulder_fracture", "date_forearm_fracture", "date_wrist_fracture", "date_stroke_h",
        "date_stroke_i", "date_diabetes", "date_hypertension", "date_hyperchol", "date_AD", "date_AF",
        "date_dem_vascular", "date_dem_other", "date_fracture_any")] <- 
  lapply(gp[, c("date", "date_depression", "date_dis_other", "date_fall", "date_femur_fracture", "date_pelvic_fracture",
                "date_shoulder_fracture", "date_forearm_fracture", "date_wrist_fracture", "date_stroke_h",
                "date_stroke_i", "date_diabetes", "date_hypertension", "date_hyperchol", "date_AD", "date_AF", 
                "date_dem_vascular", "date_dem_other", "date_fracture_any")], as.Date, "%d/%m/%Y")

inpatient[, c("date", "date_depression", "date_dis_other", "date_fall", "date_femur_fracture", "date_pelvic_fracture",
       "date_shoulder_fracture", "date_forearm_fracture", "date_wrist_fracture", "date_stroke_h",
       "date_stroke_i", "date_diabetes", "date_hypertension", "date_hyperchol", "date_AD", "date_AF",
       "date_dem_vascular", "date_dem_other", "date_fracture_any")] <- 
  lapply(inpatient[, c("date", "date_depression", "date_dis_other", "date_fall", "date_femur_fracture", "date_pelvic_fracture",
                "date_shoulder_fracture", "date_forearm_fracture", "date_wrist_fracture", "date_stroke_h",
                "date_stroke_i", "date_diabetes", "date_hypertension", "date_hyperchol", "date_AD", "date_AF", 
                "date_dem_vascular", "date_dem_other", "date_fracture_any")], as.Date, "%Y-%m-%d")


# assign diagnosis specific dates to general date and remove the former
for (col in c("date_depression", "date_dis_other", "date_fall", "date_femur_fracture", "date_pelvic_fracture",
             "date_shoulder_fracture", "date_forearm_fracture", "date_wrist_fracture", "date_stroke_h",
             "date_stroke_i", "date_diabetes", "date_hypertension", "date_hyperchol", "date_AD", "date_AF",
             "date_dem_vascular", "date_dem_other", "date_fracture_any")){
  gp$date[!is.na(gp[[col]])] <- gp[[col]][!is.na(gp[[col]])]
  inpatient$date[!is.na(inpatient[[col]])] <- inpatient[[col]][!is.na(inpatient[[col]])]
}

gp <- subset(gp, select=-c(date_depression, date_dis_other, date_fall, date_femur_fracture, date_pelvic_fracture,
                           date_shoulder_fracture, date_forearm_fracture, date_wrist_fracture, date_stroke_h,
                           date_stroke_i, date_diabetes, date_hypertension, date_hyperchol, date_AD, date_AF,
                           date_dem_vascular, date_dem_other, date_fracture_any))
inpatient <- subset(inpatient, select=-c(date_depression, date_dis_other, date_fall, date_femur_fracture, date_pelvic_fracture,
                           date_shoulder_fracture, date_forearm_fracture, date_wrist_fracture, date_stroke_h,
                           date_stroke_i, date_diabetes, date_hypertension, date_hyperchol, date_AD, date_AF,
                           date_dem_vascular, date_dem_other, date_fracture_any))


## Create a prescriptions-based data frame
colnames(gp)[colnames(gp) %in% colnames(inpatient) == FALSE]
colnames(inpatient)[colnames(inpatient) %in% colnames(gp) == FALSE]

# remove unnecessary variables
gp$data_provider <- NULL
inpatient$version <- NULL

# create column indicating source of diagnoses
gp$source <- 'gp'
inpatient$source <-'inpatient'

diagnoses <- rbind(gp, inpatient) # 98,262,899

## Remove duplicates 
fracture_any <- filter(subset(diagnoses, select=c(id, diagnosis, date, fracture_any, femur_fracture, pelvic_fracture, shoulder_fracture,
                                                  forearm_fracture, wrist_fracture)), 
                       fracture_any==1) %>% arrange(date)
# treat multiple fractures in one individual on same day as duplicates (i.e., due to same incident) and remove
fracture_any <- distinct(fracture_any, id, diagnosis, date, fracture_any, .keep_all = TRUE)
fracture_any_count <- fracture_any %>% group_by(id) %>% summarize(fracture_any_count=sum(fracture_any))
# create separate data frames for each diagnosis and remove duplicates (same day, same id)
dis_other <- filter(subset(diagnoses, select=c(id, diagnosis, date, dis_other)), dis_other==1) %>% arrange(date)
dis_other <- distinct(dis_other, .keep_all = TRUE) # remove multiple occurrences on the same date
dis_other_count <- dis_other %>% group_by(id) %>% summarize(dis_other_count=sum(dis_other)) # count the occurrences for each participant
# create separate data frames for each diagnosis and remove duplicates (same day, same id)
depression <- filter(subset(diagnoses, select=c(id, diagnosis, date, depression)), depression==1) %>% arrange(date)
depression <- distinct(depression, .keep_all = TRUE) # remove multiple occurrences on the same date
depression_count <- depression %>% group_by(id) %>% summarize(depression_count=sum(depression)) # count the occurrences for each participant
# create a data frame with patients diagnosed with depression and arrange ascending by date of diagnosis 
fall <- filter(subset(diagnoses, select=c(id, diagnosis, date, fall)), fall==1) %>% arrange(date)
fall <- distinct(fall, .keep_all = TRUE) # remove multiple occurrences on the same date
fall_count <- fall %>% group_by(id) %>% summarize(fall_count=sum(fall)) # count the occurrences for each participant
# create a data frame with patients diagnosed with femur fracture arrange ascending by date of diagnosis 
femur_fracture <- filter(subset(diagnoses, select=c(id, diagnosis, date, femur_fracture)), femur_fracture==1) %>% arrange(date)
femur_fracture <- distinct(femur_fracture, .keep_all = TRUE)
femur_fracture_count <- femur_fracture %>% group_by(id) %>% summarize(femur_fracture_count=sum(femur_fracture))
# create a data frame with patients diagnosed with pelvic/lumbar fracture and arrange ascending by date of diagnosis 
pelvic_fracture <- filter(subset(diagnoses, select=c(id, diagnosis, date, pelvic_fracture)), pelvic_fracture==1) %>% arrange(date)
pelvic_fracture <- distinct(pelvic_fracture, .keep_all = TRUE)
pelvic_fracture_count <- pelvic_fracture %>% group_by(id) %>% summarize(pelvic_fracture_count=sum(pelvic_fracture))
# create a data frame with patients diagnosed with shoulder/upper arm fracture and arrange ascending by date of diagnosis 
shoulder_fracture <- filter(subset(diagnoses, select=c(id, diagnosis, date, shoulder_fracture)), shoulder_fracture==1) %>% arrange(date)
shoulder_fracture <- distinct(shoulder_fracture, .keep_all = TRUE)
shoulder_fracture_count <- shoulder_fracture %>% group_by(id) %>% summarize(shoulder_fracture_count=sum(shoulder_fracture))
# create a data frame with patients diagnosed with forearm fracture and arrange ascending by date of diagnosis 
forearm_fracture <- filter(subset(diagnoses, select=c(id, diagnosis, date, forearm_fracture)), forearm_fracture==1) %>% arrange(date)
forearm_fracture <- distinct(forearm_fracture, .keep_all = TRUE)
forearm_fracture_count <- forearm_fracture %>% group_by(id) %>% summarize(forearm_fracture_count=sum(forearm_fracture))
# create a data frame with patients diagnosed with wrist and arrange ascending by date of diagnosis 
wrist_fracture <- filter(subset(diagnoses, select=c(id, diagnosis, date, wrist_fracture)), wrist_fracture==1) %>% arrange(date)
wrist_fracture <- distinct(wrist_fracture, .keep_all = TRUE)
wrist_fracture_count <- wrist_fracture %>% group_by(id) %>% summarize(wrist_fracture_count=sum(wrist_fracture))
# create a data frame with patients diagnosed with ischaemic stroke and arrange ascending by date of diagnosis 
stroke_i <- filter(subset(diagnoses, select=c(id, diagnosis, date, stroke_i)), stroke_i==1) %>% arrange(date)
stroke_i <- distinct(stroke_i, .keep_all = TRUE)
stroke_i_count <- stroke_i %>% group_by(id) %>% summarize(stroke_i_count=sum(stroke_i))
# create a data frame with patients diagnosed with haemorrhagic stroke and arrange ascending by date of diagnosis 
stroke_h <- filter(subset(diagnoses, select=c(id, diagnosis, date, stroke_h)), stroke_h==1) %>% arrange(date)
stroke_h <- distinct(stroke_h, .keep_all = TRUE)
stroke_h_count <- stroke_h %>% group_by(id) %>% summarize(stroke_h_count=sum(stroke_h))
# create a data frame with patients diagnosed with diabetes and arrange ascending by date of diagnosis 
diabetes <- filter(subset(diagnoses, select=c(id, diagnosis, date, diabetes)), diabetes==1) %>% arrange(date)
# create a data frame with patients diagnosed with hypercholesterolaemia and arrange ascending by date of diagnosis 
hyperchol <- filter(subset(diagnoses, select=c(id, diagnosis, date, hyperchol)), hyperchol==1) %>% arrange(date)
# create a data frame with patients diagnosed with hypertension and arrange ascending by date of diagnosis 
hypertension <- filter(subset(diagnoses, select=c(id, diagnosis, date, hypertension)), hypertension==1) %>% arrange(date)
# create a data frame with patients diagnosed with AF and arrange ascending by date of diagnosis 
AF <- filter(subset(diagnoses, select=c(id, diagnosis, date, AF)), AF==1) %>% arrange(date)
# create a data frame with patients diagnosed with AD and arrange ascending by date of diagnosis
AD <- filter(subset(diagnoses, select=c(id, diagnosis, date, AD)), AD==1) %>% arrange(date)
# create a data frame with patients diagnosed with vascular dementia and arrange ascending by date of diagnosis
dem_vascular <- filter(subset(diagnoses, select=c(id, diagnosis, date, dem_vascular)), dem_vascular==1) %>% arrange(date)
# same for other dementias
dem_other <- filter(subset(diagnoses, select=c(id, diagnosis, date, dem_other)), dem_other==1) %>% arrange(date) 
# remove all rows with found diagnoses
diagnoses <- filter(diagnoses, depression!=1 & femur_fracture!=1 & pelvic_fracture!=1 & shoulder_fracture!=1 & 
                      forearm_fracture!=1 & wrist_fracture!=1 & stroke_i!=1 & stroke_h!=1 & fall!=1 & dis_other!=1)
# add back only those rows that are not duplicates
diagnoses <- rbind.fill(diagnoses, depression, stroke_i, stroke_h, fall, fracture_any, dis_other)



# export
saveRDS(diagnoses, file = "diagnoses_all_cleaned.rds")
write.csv(diagnoses, 'diagnoses_all_cleaned.csv', row.names = FALSE)