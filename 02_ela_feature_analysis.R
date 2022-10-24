#rm(list = ls())
wd = dirname(rstudioapi::getActiveDocumentContext()$path)
setwd(wd)

library(tidyverse)
library(doParallel)

# Load data and transform from wide to long
data = read_csv('data/00_ela_features.csv') %>%
  gather("feature", "value", ela_distr.skewness:disp.costs_runtime) %>%
  arrange(fid, dim, iid, stan, rep)
#########################################################################################

library(smoof)
library(flacco)

cl = makeCluster(detectCores())
registerDoParallel(cl)
result = foreach(fid = 1:24, .combine = rbind) %:%
  foreach(dim = c(2, 3, 5, 10, 20), .combine = rbind) %:%
  foreach(iid = 1:5, .combine = rbind) %dopar% {
    library(smoof)
    fun = makeBBOBFunction(dim, fid, iid)
    res = matrix(runif(1000*dim*dim, min = -5, max = 5), ncol = dim)
    y = apply(res, 1, fun)
    data.frame(FID = fid, DIM = dim, IID = iid, y = y)
  }
stopCluster(cl)

result = result %>%
  mutate(IID = as.factor(IID)) %>%
  #mutate(FID = as.factor(FID)) %>%
  mutate(GRP = ifelse(FID < 6, 1,
                      ifelse(FID < 10, 2,
                             ifelse(FID < 15, 3, 
                                    ifelse(FID < 20, 4, 5)))))

foreach(grp = unique(result$GRP)) %do% {
  plt = ggplot(filter(result, GRP %in% grp), aes(x = IID, y = y, fill = IID)) +
    geom_boxplot() +
    theme_light() + 
    facet_wrap(. ~ FID, scales = "free", nrow = 1, labeller = label_both)
  ggsave(paste("Function_Group_", grp, ".pdf", sep = ""), plt, device = cairo_pdf(), path = file.path(wd, "figures"), width = 42, height = 30, units = "cm")
}

#####


ggplot(result, aes(y = y)) +
  geom_boxplot() +
  theme_light() + 
  facet_wrap(FID ~ ., scales = "free", nrow = 5, labeller = label_both)

####################################################################################
# Check for missing values
summary(data)
unique(filter(data, is.na(value))$feature)
unique(filter(data, is.na(value))$fid)
unique(filter(data, is.na(value))$dim)
unique(filter(data, is.na(value))$iid)
# Only F7 in D2 suffers from missing values for some dispersion features

####################################################################################
feature_groups = c("ela_distr", "ela_meta", "ic", "nbc", "disp")
dir.create(file.path(wd, "figures"), showWarnings = FALSE)

# Create violin plots for each feature group
for(colname in feature_groups) {
  pl = ggplot(filter(data, grepl(colname, feature)), aes(stan, value, fill = stan)) +
    geom_violin() +
    facet_wrap(. ~ feature, scales = "free_y")
  ggsave(paste(colname, ".pdf"), pl, device = cairo_pdf(), path = file.path(wd, "figures"))
  
}
####################################################################################

library(rpart)
library(rpart.plot)

data = read_csv('data/00_ela_features.csv')


for (tdim in unique(data$dim)) {
  train = filter(data, dim == tdim)
  test = filter(data, dim != tdim)
  
  X_train = train %>%
    filter(stan == F, dim == tdim) %>%
    select(ela_distr.skewness:disp.costs_runtime)
  
  y_train = train$fid
}




















