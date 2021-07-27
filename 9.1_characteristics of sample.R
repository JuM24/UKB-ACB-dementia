# demographic data

load("id_years_cleaned_v2.RData")
load("meds_v2.RData")

# prescription data are inaccurate after 2015, so remove those
id_years <- filter(id_years, year<=2015)

# remove years with <100 id's
id_years$year[id_years$year>2016] <- NA

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


# dates, ages, years
min(id_years$date_dementia, na.rm = TRUE)
max(id_years$date_dementia, na.rm = TRUE)
id_years$dementia_age <- as.numeric(difftime(id_years$date_dementia, id_years$birth_date))/365.25
median(id_years$dementia_age, na.rm = TRUE); IQR(id_years$dementia_age, na.rm = TRUE)
median(id_years$med_age)
IQR(id_years$med_age)
quantile(id_years$med_age, prob=c(.25,.5,.75))
median(id_years$year)
IQR(id_years$year)

# demography
prop.table(table(id_years$sex))
prop.table(table(id_years$data_provider))
prop.table(table(id_years$bmi_class))
prop.table(table(id_years$education))
prop.table(table(id_years$alc_freq))
prop.table(table(id_years$smoking))
prop.table(table(id_years$activity))
prop.table(table(id_years$dementia))
hist(id_years$deprivation)
median(id_years$deprivation)
IQR(id_years$deprivation)


# diseases
table(id_years$dementia); prop.table(table(id_years$dementia))
hist(id_years$comorbidity)
median(id_years$comorbidity)
IQR(id_years$comorbidity)
prop.table(table(id_years$depression_count)) # is - despite the name - a binary variable
prop.table(table(id_years$stroke))
prop.table(table(id_years$diabetes))
prop.table(table(id_years$hyperchol))
prop.table(table(id_years$hypertension))
prop.table(table(id_years$apoe_carrier))


# drugs
meds$year <- format(as.Date(meds$date), "%Y")
# remove unused id's
meds <- filter(meds, id %in% id_years$id)
# remove unused years
meds <- filter(meds, year>=2000 & year<=2015)

vars <- c("aa_ancelin", "aa_boustani", 
          "aa_carnahan", "aa_cancelli", "aa_chew", "aa_rudolph", "aa_ehrt", "aa_han", "aa_sittironnarit", "aa_briet", 
          "aa_bishara", "aa_duran", "aa_kiesel")
print("% or anticholinergics in the sample:")
for (var in vars){
  print(paste(var, 100*sum(meds[[var]]>0,na.rm = TRUE)/nrow(meds)))
}
vars <- c("aa_ancelin_n", "aa_boustani_n", 
          "aa_carnahan_n", "aa_cancelli_n", "aa_chew_n", "aa_rudolph_n", "aa_ehrt_n", "aa_han_n", "aa_sittironnarit_n", "aa_briet_n", 
          "aa_bishara_n", "aa_duran_n", "aa_kiesel_n")
print("Number of anticholinergics per person in year_0 in the sample:")
for (var in vars){
 print(sum(id_years[[var]],na.rm = TRUE)/length(unique(id_years$id)))
}