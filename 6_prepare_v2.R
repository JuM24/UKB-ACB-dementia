###
#
#
# Cleans the data to prepare them for transformations.
#
#
###

library(zoo)
library(tidyverse)
library(car)
library(reshape2)




## read in the files
meds <- read.csv('6_demographics_v2.csv', sep="|", header=TRUE)



# remove unnecessary columns
meds <- subset(meds, select=-c(prescription_old, quantity, prescription, aa_count, combo_drug, month_len,
                               date_1, date_2, date_3, scale_name))

# assign to all topical, ophthalmic, nasal, or otic drugs an anticholinergic value of 0
meds$aa_ancelin[meds$admin_oral==0] <- 0
meds$aa_bishara[meds$admin_oral==0] <- 0
meds$aa_boustani[meds$admin_oral==0] <- 0
meds$aa_briet[meds$admin_oral==0] <- 0
meds$aa_cancelli[meds$admin_oral==0] <- 0
meds$aa_carnahan[meds$admin_oral==0] <- 0
meds$aa_chew[meds$admin_oral==0] <- 0
meds$aa_duran[meds$admin_oral==0] <- 0
meds$aa_ehrt[meds$admin_oral==0] <- 0
meds$aa_han[meds$admin_oral==0] <- 0
meds$aa_kiesel[meds$admin_oral==0] <- 0
meds$aa_rudolph[meds$admin_oral==0] <- 0
meds$aa_sittironnarit[meds$admin_oral==0] <- 0



## miscelaneous formatting etc.
meds$birth_year <- format(as.Date(meds$birth_date), "%Y")
meds$id <- as.character(meds$id)
meds$data_provider <- as.factor(meds$data_provider)
meds$date <- as.Date(meds$date,"%Y-%m-%d")
meds$sex <- as.factor(meds$sex)
meds$education <- as.factor(meds$education)
meds$deprivation <- as.numeric(meds$deprivation)
meds$smoking <- as.factor(meds$smoking)
meds$alc_freq <- as.factor(meds$alc_freq)
meds$activity <- as.factor(meds$activity)
meds$bmi <- as.numeric(meds$bmi)
meds$aa_ancelin <- as.numeric(meds$aa_ancelin)
meds$aa_boustani <- as.numeric(meds$aa_boustani)
meds$aa_carnahan <- as.numeric(meds$aa_carnahan)
meds$aa_cancelli <- as.numeric(meds$aa_cancelli)
meds$aa_chew <- as.numeric(meds$aa_chew)
meds$aa_han <- as.numeric(meds$aa_han)
meds$aa_ehrt <- as.numeric(meds$aa_ehrt)
meds$aa_sittironnarit <- as.numeric(meds$aa_sittironnarit)
meds$aa_briet <- as.numeric(meds$aa_briet)
meds$aa_duran <- as.numeric(meds$aa_duran)
meds$aa_kiesel <- as.numeric(meds$aa_kiesel)
meds$aa_duran <- as.numeric(meds$aa_duran)
meds$aa_name <- as.character(meds$aa_name)


## export
save.image("meds_v2.RData")
write.csv(meds, 'meds_v2.csv', row.names = FALSE)


## add drug classes


load("meds_v2.RData")
class <- read.csv('drug_groups.csv')

# remove rows with no anticholinergic drugs (so everything below runs faster)
meds <- filter(meds, aa_duran > 0)


# convert everything to lower-case character and trim leading/trailing white spaces
class <- as.data.frame(lapply(class, as.character))
class <- as.data.frame(lapply(class, tolower))
class <- as.data.frame(lapply(class, trimws))
colnames(class)[which(names(class) == "drug")] <- "aa_name"
class <- subset(class, select=-c(several_categories, in_sample))

# merge and subset
meds <- merge(meds, class, by='aa_name', all.x = TRUE)
meds <- subset(meds, select=c(id, aa_name, aa_duran, data_provider, date, body_system, lower))

# spaces to NA's
meds[meds==''] <- NA

# transform to wide format by category
meds_wide <- dcast(meds, id + aa_name + aa_duran + data_provider + date ~ body_system, length)
meds_wide_lower <- dcast(meds, id + aa_name + aa_duran + data_provider + date ~ lower, length)

# calculate aa-burden of category
meds_wide[,6:length(meds_wide)] <- meds_wide[,6:length(meds_wide)]*meds_wide$aa_duran
meds_wide_lower[,6:length(meds_wide_lower)] <- meds_wide_lower[,6:length(meds_wide_lower)]*meds_wide_lower$aa_duran

write.csv(meds_wide, 'meds_v2_body_system.csv', row.names = FALSE)
write.csv(meds_wide_lower, 'meds_v2_class_lower.csv', row.names = FALSE)

