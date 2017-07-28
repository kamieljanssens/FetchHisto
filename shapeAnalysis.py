from ROOT import TCanvas, TPad, TH1F, TH1I, THStack, TLegend, TMath, gROOT, TPDF, TGraph, TFile
import argparse
import subprocess
import time
import os
import sys
sys.path.append('cfgs/')
sys.path.append('input/')

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'])


def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '%' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()


##Data card for Zprime -> ll analysis, created on %(date)s at %(time)s using revision %(hash)s of the package

cardTemplate='''
##Data card for CI interpretation of the Zprime -> ll analysis, created on %(date)s at %(time)s
imax 1  number of channels
jmax %(nBkgs)d  number of backgrounds
kmax *  number of nuisance parameters (sources of systematical uncertainties)
------------
#for background shapes
%(bkgShapes)s
#for signal shape
%(sigShape)s
#for data
%(data)s
------------
# we have just one channel, in which we observe 0 events
bin %(bin)s
observation -1.
------------
# now we list the expected events for signal and all backgrounds in that bin
# the second 'process' line must have a positive number for backgrounds, and 0 for signal
# then we list the independent sources of uncertainties, and give their effect (syst. error)
# on each process and bin
%(channels)s  
------------
%(systs)s
'''


def getChannelBlock(nBkgs,yields,signalScale,chan):

	result = "bin %s"%chan
	for i in range(0,nBkgs):
		result += " %s "%chan
	result+="\n"
	result += "process      sig"
	if nBkgs == 1:
		result+= "  bkg  "
	else:
		for i in range(0,nBkgs):
			result+= "  bkg_%d  "%i
	result +="\n"
	result +="process       0 "
	for i in range(0,nBkgs):
		result+=" %d"%(i+1)
	result +="\n"
	result += "rate         %.2f "%yields[1]
	#result += "rate         1 "
	for i in range (0, nBkgs):
		result+= " %.2f"%yields[0]
	return result
 


def getUncert(uncert, value, nBkgs, mass,channel,correlate,yields,signif):

	if uncert == "sigEff":
		if correlate:
			name = "sig_effUnc"
		else:
			name = "sig_effUnc_%s"%channel
	        if len(value) == 1:
	                result = "%s  lnN  %.2f"%(name,value[0])
	        else:
	                result = "%s  lnN  %.5f/%.2f"%(name, value[0], value[1] )

		for i in range(0,nBkgs):
	                result += "  -  "

	if uncert == "bkgUncert":
		#if value != 0:
		#	print "non-standard background uncertainties not supported yet"
		#	sys.exit()
		if correlate:
			name = "bkg_unc"
		else:
			name = "bkg_unc_%s"%channel
		result = "%s lnN   -  "%(name)  
		for i in range(0, nBkgs):
			#value = 0.8
			if not signif:

#				result += " %.2f"%(1.+yields[i]**0.5/bkgYields[i])
				result += "  %.2f  "%(value)
			#result += "  %.2f  "%(1.4)
			else:
				#result += " %.4f"%(1.+yields[i]**0.5/bkgYields[i])
				result += "  %.2f  "%(value)
	if uncert == "massScale":
		if correlate:
			name = "scale"
		else:
			name = "scale_%s"%channel
		result = "%s shape 1"%name
	        for i in range(0,nBkgs):
        		result += "  -  "
			
	
		result += "\n"		
	if uncert == "res":

		if correlate:
			name = "res"
		else:
			name = "res_%s"%channel
		result = "%s shape 1"%name
	        for i in range(0,nBkgs):
        		result += "  -  "
	


		result += "\n"		
        return result
		
	


def writeCard(card,fileName):

	text_file = open("%s.txt" % (fileName), "w")
	text_file.write(card)
	text_file.close()
	

def getDataset(fileName, chan):

	return "shapes data_obs %s %s dataHist" % (chan, fileName)

def getSignalShape(fileName,chan,scale,res):
	
	result =  "shapes sig %s %s sigHist" % (chan, fileName)
	if scale:
		#result += " sigHist_%s_scaleUp"%chan
		#result += " sigHist_%s_scaleDown"%chan
		result += " sigHist_%s_$SYSTEMATIC"%chan  
	if res:
		#result += " sigHist_%s_scaleUp"%chan
		#result += " sigHist_%s_scaleDown"%chan
		result += " sigHist_%s_$SYSTEMATIC"%chan  
	return result

def getBackgroundShapes(fileName,chan):

	return "shapes bkg %s %s bkgHist" % (chan, fileName)
def main():


	cardDir = "dataCards"
	if not os.path.exists(cardDir):
    		os.makedirs(cardDir)
	L=1
	#name = "%s/%s_%d" % (cardDir,args.chan, L)

	
	

	channels = ["dimuon_CI","dimuon_CI_BB","dimuon_CI_BE","dimuon_CI_CSPos","dimuon_CI_BB_CSPos","dimuon_CI_BE_CSPos","dimuon_CI_CSNeg","dimuon_CI_BB_CSNeg","dimuon_CI_BE_CSNeg"]

	for channel in channels:
		channelDict = {}

		channelDict["date"] = time.strftime("%d/%m/%Y")
		channelDict["time"] = time.strftime("%H:%M:%S")
		#channelDict["hash"] = get_git_revision_hash()	

		channelDict["bin"] = channel

		channelDict["nBkgs"] = 1

		location="/afs/cern.ch/user/k/kjanssen/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/DatacardTest/rootfiles/"
		varName="DimuonMassVertexConstrained"  #["DimuonMassVertexConstrained","DimuonMassVertexConstrained_CSPos","DimuonMassVertexConstrained_CSNeg","DimuonMassVertexConstrained_bb","DimuonMassVertexConstrained_bb_CSPos","DimuonMassVertexConstrained_bb_CSNeg","DimuonMassVertexConstrained_be","DimuonMassVertexConstrained_be_CSPos","DimuonMassVertexConstrained_be_CSNeg"]
		
		sigNameL=["CITo2Mu_Lam22TeVConLL","CITo2Mu_Lam22TeVConLR","CITo2Mu_Lam22TeVConRR","CITo2Mu_Lam22TeVDesLL","CITo2Mu_Lam22TeVDesLR","CITo2Mu_Lam22TeVDesRR"]


		for index, sigName in enumerate(sigNameL):

			rootName="%s"%location+"%s"%sigName+"_"+"%s"%varName
			tempName="%s"%sigName+"_"+"%s"%varName
			name = "%s/%s_%d" % (cardDir,tempName, L)

		

			channelDict["bkgShapes"] = getBackgroundShapes("%s.root"%rootName,channel)
			scale = False
			res = False

#### Add code here to open your histograms and get the integrals for the proper normalization

			InputFile=TFile("%s.root"%rootName,"read")
		
			bkgHisto=InputFile.Get("bkgHist")
			sigHisto=InputFile.Get("sigHist")

			bkgYield=bkgHisto.Integral(0,bkgHisto.GetSize())
			sigYield=sigHisto.Integral(0,sigHisto.GetSize())


			yields = []
			yields.append(bkgYield)
			yields.append(sigYield)

			channelDict["sigShape"] = getSignalShape("%s.root"%rootName,channel,scale,res)
			channelDict["data"] = getDataset("%s.root"%rootName,channel)

			channelDict["channels"]	= getChannelBlock(1,yields,1,channel)		

			uncertBlock = ""
#			uncerts = module.provideUncertainties(L)
#			for uncert in config.systematics:
#			uncertBlock += getUncert(uncert,uncerts[uncert],nBkg,L,args.chan,config.correlate,yields,args.signif)

			channelDict["systs"] = uncertBlock
	
			writeCard(cardTemplate % channelDict, name)
		
main()
