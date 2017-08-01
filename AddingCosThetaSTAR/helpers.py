import ROOT
import gc
from array import array
from ROOT import TCanvas, TPad, TH1F, TH2F, TH1I, THStack, TLegend, TMath
from ConfigParser import ConfigParser
from math import sqrt
from defs import defineMyColors, myColors, crossSections

config = ConfigParser()



	
def totalNumberOfGeneratedEvents(path):
	"""
	path: path to directory containing all sample files

	returns dict samples names -> number of simulated events in source sample
	"""
	from ROOT import TFile
	result = {}
	#~ print path

	for sampleName, filePath in getFilePathsAndSampleNames(path).iteritems():
			print sampleName
			rootFile = TFile(filePath, "read")
			result[sampleName] = rootFile.FindObjectAny("Events").GetBinContent(1)				
	return result
	
def loadHistoFromFile(fileName,histName,rebin):
	"""
	returns histogram from file
	"""
	from ROOT import TFile
	rootFile = TFile(fileName, "read")
	result = rootFile.Get("Our2016MuonsPlusMuonsMinusHistos/%s"%histName)
	result.Rebin(rebin)
	result.SetDirectory(0)	
	return result
	

def getFilePathsAndSampleNames(path):
	"""
	helper function
	path: path to directory containing all sample files

	returns: dict of smaple names -> path of .root file (for all samples in path)
	"""
	result = []
	from glob import glob
	from re import match
	result = {}

	for filePath in glob("%s/*.root"%(path)):
		if "ana_datamc" in filePath and not "SingleMuon" in filePath:
			sampleName = filePath.split("/")[-1].split("ana_datamc_")[-1].split(".root")[0]
			result[sampleName] = filePath
	return result


	

def createMyColors():
    iIndex = 2000

    containerMyColors = []
    for color in defineMyColors.keys():
        tempColor = ROOT.TColor(iIndex,
            float(defineMyColors[color][0]) / 255, float(defineMyColors[color][1]) / 255, float(defineMyColors[color][2]) / 255)
        containerMyColors.append(tempColor)

        myColors.update({ color: iIndex })
        iIndex += 1

    return containerMyColors
	
class Process:
	samples = []
	xsecs = []
	nEvents = []
	label = ""
	theColor = 0
	theStyle = 0
	theLineColor = 0 
	histo = None
	uncertainty = 0.
	scaleFac = 1.
	
	def __init__(self, process, counts, normalized = True):
		self.samples = process.subprocesses
		self.xsecs = []
		self.nEvents = []
		self.label = process.label
		self.theColor = process.fillcolor
		self.theStyle = process.fillstyle
		self.theLineColor = process.linecolor
		self.normalized = normalized
		for sample in self.samples:
			self.xsecs.append(crossSections[sample])
			self.nEvents.append(counts[sample])

		
	def loadHistogram(self,lumi,files,plot):
		
		for index, sample in enumerate(self.samples):
			tempHist = loadHistoFromFile(files[sample],plot.histName,plot.rebin)		
			tempHist.Scale(lumi*self.xsecs[index]/self.nEvents[index])
			
			#print sample
			#print lumi
			#print self.xsecs[index]
			#print self.nEvents[index]
			#print tempHist.Scale
			
			if self.histo == None:
				self.histo = tempHist.Clone()
			else:	
				self.histo.Add(tempHist.Clone())
		self.histo.SetFillColor(self.theColor)
		self.histo.SetFillStyle(self.theStyle)
		self.histo.SetLineColor(self.theLineColor)
		self.histo.GetXaxis().SetTitle(plot.xaxis) 
		self.histo.GetYaxis().SetTitle(plot.yaxis)	
				
		return self.histo

	
class TheStack:
	from ROOT import THStack
	theStack = THStack()	
	theHistogram = None	
	def  __init__(self,processes,lumi,plot,files):
		self.theStack = THStack()
			
		for process in processes:
			temphist = process.loadHistogram(lumi,files,plot)

			self.theStack.Add(temphist.Clone())
			if self.theHistogram == None:
				self.theHistogram = temphist.Clone()
			else:	
				self.theHistogram.Add(temphist.Clone())

def getDataHist(plot,files):
	histo = loadHistoFromFile(files["data"], plot.histName,plot.rebin)
	return histo	




