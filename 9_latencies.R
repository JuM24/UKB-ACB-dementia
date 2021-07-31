# different period ranges
library(tidyverse)
library(lubridate)
library(Hmisc)

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
id_years$bmi_class[id_years$bmi >= 25 & id_years$bmi < 30] <- '25-40'
id_years$bmi_class[id_years$bmi >= 30 & id_years$bmi < 35] <- '30-35'
id_years$bmi_class[id_years$bmi >= 35 & id_years$bmi < 40] <- '35-40'
id_years$bmi_class[id_years$bmi >= 40] <- '>40'
id_years$bmi_class <- as.factor(id_years$bmi_class)

# remove outliers
cols <- c("meds_count", "aa_duran", "deprivation")
for (col in cols){
  avg <- mean(id_years[[col]][id_years[[col]] != 0], na.rm = TRUE) # calculate mean of non-zero rows
  SD <- sd(id_years[[col]][id_years[[col]] != 0], na.rm = TRUE) # calculate sd of non-zero rows
  prev_na <- sum(is.na(id_years[[col]]))
  id_years[[col]][id_years[[col]] > (avg + 3*SD)] <- NA
  new_na <- sum(is.na(id_years[[col]])) - prev_na # calculate number of NA'd rows
  print(paste(col, new_na))
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

# define periods of dementia diagnosis
id_years$dem_period <- as.numeric(difftime(id_years$date_dementia, as.Date(parse_date_time(2000, "Y")), units = 'weeks')/52.25)
id_years <- filter(id_years, dem_period>0 | is.na(dem_period))
id_years$dem_period_class <- as.factor(sapply(cut2(id_years$dem_period, g=5), as.character))
id_years$dementia <- 0
id_years$dementia[!is.na(id_years$date_dementia)] <- 1
id_years$dem_1 <- 0
id_years$dem_1[id_years$dementia == 1 & id_years$dem_period > 0 & id_years$dem_period <= 12] <- 1
id_years$dem_2 <- 0
id_years$dem_2[id_years$dementia == 1 & id_years$dem_period > 12 & id_years$dem_period <= 14] <- 1
id_years$dem_3 <- 0
id_years$dem_3[id_years$dementia == 1 & id_years$dem_period > 14 & id_years$dem_period <= 16] <- 1
id_years$dem_4 <- 0
id_years$dem_4[id_years$dementia == 1 & id_years$dem_period > 16 & id_years$dem_period <= 18] <- 1
id_years$dem_5 <- 0
id_years$dem_5[id_years$dementia == 1 & id_years$dem_period > 18] <- 1

# change variable types
id_years$dem_1 <- as.factor(id_years$dem_1)
id_years$dem_2 <- as.factor(id_years$dem_2)
id_years$dem_3 <- as.factor(id_years$dem_3)
id_years$dem_4 <- as.factor(id_years$dem_4)
id_years$dem_5 <- as.factor(id_years$dem_5)



model_1 <- glm(data=id_years, dem_1 ~ scale(aa_duran) + aa_duran_poly + sex  + med_age + data_provider + education + 
               deprivation + bmi + smoking + alc_freq + activity + comorbidity + depression + stroke + 
                 diabetes + hyperchol + hypertension + apoe_carrier, family = binomial, na.action = 'na.exclude')
model_2 <- glm(data=id_years, dem_2 ~ scale(aa_duran) + aa_duran_poly + sex  + med_age + data_provider + education + 
                 deprivation + bmi + smoking + alc_freq + activity + comorbidity + depression + stroke + 
                 diabetes + hyperchol + hypertension + apoe_carrier, family = binomial, na.action = 'na.exclude')
model_3 <- glm(data=id_years, dem_3 ~ scale(aa_duran) + aa_duran_poly + sex  + med_age + data_provider + education + 
                 deprivation + bmi + smoking + alc_freq + activity + comorbidity + depression + stroke + 
                 diabetes + hyperchol + hypertension + apoe_carrier, family = binomial, na.action = 'na.exclude')
model_4 <- glm(data=id_years, dem_4 ~ scale(aa_duran) + aa_duran_poly + sex  + med_age + data_provider + education + 
                 deprivation + bmi + smoking + alc_freq + activity + comorbidity + depression + stroke + 
                 diabetes + hyperchol + hypertension + apoe_carrier, family = binomial, na.action = 'na.exclude')
model_5 <- glm(data=id_years, dem_5 ~ scale(aa_duran) + aa_duran_poly + sex  + med_age + data_provider + education + 
                 deprivation + bmi + smoking + alc_freq + activity + comorbidity + depression + stroke + 
                 diabetes + hyperchol + hypertension + apoe_carrier, family = binomial, na.action = 'na.exclude')