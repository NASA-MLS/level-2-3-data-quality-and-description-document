library(hdf5)
source("l2gpzm.R")
hcn<-hdf5load("../inspdat/MLS-Aura_L2GP-HCN_v01-51-c04_2005d029.he5",
              load=FALSE,tidy=TRUE)

zm<-l2gpzm(hcn$HDFEOS$SWATHS[["HCN"]])

zeta<-10.0^(-zm$Geolocation.Fields$Pressure)
bogo<-(3+zeta)*16


