import ROOT
from array import array
import awkward 
from parquet_to_root import parquet_to_root

# GJets1=ROOT.TFile.Open("/eos/user/s/shsong/HHWWgg/root/cat2/GJet.root")
# GJets1_tree=GJets1.Get("cat2")
GJets1=ROOT.TFile.Open("/eos/user/s/shsong/HHWWgg/root/cat7/GJet.root")
GJets1_tree=GJets1.Get("cat7")
# GJets1=ROOT.TFile.Open("/eos/user/s/shsong/combined_WWgg/root/datadriven/category3/raw/GJet_e.root")
# GJets1_tree=GJets1.Get("cat2")
cuts="(Diphoton_mass<115 || Diphoton_mass>135)*(minID_genPartFlav!=1)"
h_minphotonID=ROOT.TH1F("h_minphotonID_gjet","h_minphotonID_gjet",19,-0.9,1)
GJets1_tree.Project("h_minphotonID_gjet","Diphoton_minID","weight_central*"+cuts)
photonIDPDF_fake=ROOT.TF1("photonIDPDF_fake","pol7",-0.9,1.)
h_minphotonID.Fit(photonIDPDF_fake,"R")
c1=ROOT.TCanvas("c1","c1",600,800)
h_minphotonID.Draw("E1")
# c1.SaveAs("fakephoton_pdf_cat2.png")
c1.SaveAs("fakephoton_pdf_cat7.png")

# Data=ROOT.TFile.Open("/eos/user/s/shsong/HHWWgg/root/cat2/Data_2017.root")
# Data_tree=Data.Get("cat2")
# 
Data=ROOT.TFile.Open("/eos/user/s/shsong/HHWWgg/root/cat7/Data_2017.root")
Data_tree=Data.Get("cat7")
# Data=ROOT.TFile.Open("/eos/user/s/shsong/combined_WWgg/root/datadriven/category3/raw/Data_e.root")
nevents=Data_tree.GetEntries()

new_weight=-999
weights=[]

minID=[]
maxID=[]
hasMaxLead=[]
originalminID=[]
print(nevents)
for i in range(0,nevents):
    Data_tree.GetEntry(i)
    # weights.append(1)
    if(Data_tree.LeadPhoton_mvaID < Data_tree.SubleadPhoton_mvaID):
        hasleadIDmin=True
        original_Photon_MVA_min = Data_tree.LeadPhoton_mvaID
        Photon_MVA_max = Data_tree.SubleadPhoton_mvaID
    else:
        hasleadIDmin=False
        original_Photon_MVA_min = Data_tree.SubleadPhoton_mvaID
        Photon_MVA_max = Data_tree.LeadPhoton_mvaID
    originalminID.append(original_Photon_MVA_min)
    maxID.append(Photon_MVA_max)
    # weights.append(1)
    if(not (original_Photon_MVA_min<-0.7 and Photon_MVA_max>-0.7)):
        new_weight=-999
        minID.append(-999)
        hasMaxLead.append(-999)
    else:
        if(hasleadIDmin):
            hasMaxLead.append(0)
            LeadPhoton_mvaID=photonIDPDF_fake.GetRandom(-0.7,Photon_MVA_max)
            PhotonID_min=LeadPhoton_mvaID
        else:
            SubleadPhoton_mvaID=photonIDPDF_fake.GetRandom(-0.7,Photon_MVA_max)
            PhotonID_min=SubleadPhoton_mvaID
            hasMaxLead.append(1)
        minID.append(PhotonID_min)
        new_weight = photonIDPDF_fake.Integral(-0.7,Photon_MVA_max) / photonIDPDF_fake.Integral(-0.9,-0.7);
    weights.append(new_weight)
    if(i%100000==0):
        print("Read entry:",i,new_weight)

print(sum(weights))
d={"new_weight":weights,"minID":minID,"maxID":maxID,"originalminID":originalminID,"hasMaxLead":hasMaxLead}
import pandas
dataframe=pandas.DataFrame(d) 

# DataFile=awkward.from_parquet("/eos/user/s/shsong/HHWWgg/parquet/cat2/Data_2017.parquet")
DataFile=awkward.from_parquet("/eos/user/s/shsong/HHWWgg/parquet/cat7/Data_2017.parquet")
# DataFile=DataFile[DataFile.weight!=-999]
DataFile["Diphoton_maxID"]=dataframe.maxID
DataFile["Diphoton_minID"]=dataframe.minID
DataFile["originalminID"]=dataframe.originalminID
DataFile["weight_central"]=dataframe.new_weight
DataFile=DataFile[DataFile.weight_central!=-999]
# awkward.to_parquet(DataFile,"/eos/user/s/shsong/HHWWgg/parquet/cat2/DatadrivenQCD_usingcat7Gjet.parquet")
# parquet_to_root("/eos/user/s/shsong/HHWWgg/parquet/cat2/DatadrivenQCD_usingcat7Gjet.parquet","/eos/user/s/shsong/HHWWgg/root/cat2/DatadrivenQCD_usingcat7Gjet.root",treename="cat2",verbose=False)
awkward.to_parquet(DataFile,"/eos/user/s/shsong/HHWWgg/parquet/cat7/DatadrivenQCD.parquet")
parquet_to_root("/eos/user/s/shsong/HHWWgg/parquet/cat7/DatadrivenQCD.parquet","/eos/user/s/shsong/HHWWgg/root/cat7/DatadrivenQCD.root",treename="cat7",verbose=False)

# dataframe("data_weight.csv")