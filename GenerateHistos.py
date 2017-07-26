from ROOT import TCanvas, TPad, TH1F, TH1I, THStack, TLegend, TMath, gROOT, TPDF, TGraph, TFile
import math
import os
from array import array


def FetchHisto(location,variable,signal):

	BackgroundL= ["dyInclusive50","dy50to120","dy120to200","dy200to400","dy400to800","dy800to1400","dy1400to2300","dy2300to3500","dy3500to4500","dy4500to6000","tW","Wantitop","Wjets","WW200to600","WW600to1200","WW1200to2500","WW2500","WWinclusive","WZ","WZ_ext","ZZ_ext","ZZ","ttbar_lep","ttbar_lep50to500","ttbar_lep_500to800","ttbar_lep_800to1200","ttbar_lep_1200to1800","ttbar_lep1800toInf","qcd50to80","qcd80to120","qcd120to170","qcd170to300","qcd300to470","qcd470to600","qcd600to800","qcd800to1000","qcd1000to1400","qcd1400to1800","qcd1800to2400","qcd2400to3200","qcd3200"]
	
	binning = [400,500,700,1100,1900,3500]
	histoB = TH1F("dataHist","bkgHist",len(binning)-1,array("f",binning))
# ????????????? does this binning need to happen only once before you fill the histo of only once at the end ????????????? #

	for index,background in enumerate(BackgroundL):

		if index != 0:
			temphist=histoB


		#tempString="%s"+"ana_datamc_"+"%s"+".root"%(location,background)
		InputFile=TFile("%s"%(location)+"ana_datamc_"+"%s"%(background)+".root","read")
		
		histoB=InputFile.Get("Our2016MuonsPlusMuonsMinusHistos/%s"%variable)
		histoB.Add(temphist)

	histoS=	TH1F("dataHist","bkgHist",len(binning)-1,array("f",binning))
	tempString="%s"+"ana_datamc_"+"%s"+".root"%(location,signal)
	InputFile=TFile(tempString)
	histoS=InputFile.Get("Our2016MuonsPlusMuonsMinusHistos/%s"%variable)

	histoD= TH1F("dataHist","bkgHist",len(binning)-1,array("f",binning))
	histoD=histoS.Clone()
	histoD.Add(histoB)

	OutputFile=TFile("%s"+"%s"+"_"+"%s"+".root")%(location,signal,variable)
	OutputFile.Write()

	

def main():

	signalL=["CITo2Mu_Lam22TeVConLL","CITo2Mu_Lam22TeVConLR","CITo2Mu_Lam22TeVConRR","CITo2Mu_Lam22TeVDesLL","CITo2Mu_Lam22TeVDesLR","CITo2Mu_Lam22TeVDesRR"]
	location="/afs/cern.ch/work/j/jschulte/public/filesM300/mc/"
	variableL=["DimuonMassVertexConstrained","DimuonMassVertexConstrained_CSPos","DimuonMassVertexConstrained_CSNeg","DimuonMassVertexConstrained_bb","DimuonMassVertexConstrained_bb_CSPos","DimuonMassVertexConstrained_bb_CSNeg","DimuonMassVertexConstrained_be","DimuonMassVertexConstrained_be_CSPos","DimuonMassVertexConstrained_be_CSNeg"]
	
	for index,sig in enumerate(signalL):

		for indexx,var in enumerate(variableL):

			FetchHisto("%s","%s","%s")%(location,var,sig)



main()
