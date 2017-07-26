import argparse	
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import TCanvas, TPad, TH1F, TH1I, THStack, TLegend, TMath, gROOT, TPDF, TGraph, TFile
import ratios
from setTDRStyle import setTDRStyle
gROOT.SetBatch(True)
from helpers import *
from defs import getPlot, Backgrounds, Signals, DYsignals
import math
import os
from array import array



def plotDataMC(args,plot):
	

	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	if args.ratio:
		plotPad = ROOT.TPad("plotPad","plotPad",0,0.3,1,1)
		ratioPad = ROOT.TPad("ratioPad","ratioPad",0,0.,1,0.3)
		setTDRStyle()		
		plotPad.UseCurrentStyle()
		ratioPad.UseCurrentStyle()
		plotPad.Draw()	
		ratioPad.Draw()	
		plotPad.cd()
	else:
		plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
		setTDRStyle()
		plotPad.UseCurrentStyle()
		plotPad.Draw()	
		plotPad.cd()	
		
	colors = createMyColors()	


	
	
	eventCounts = totalNumberOfGeneratedEvents("/afs/cern.ch/work/j/jschulte/public/filesM300/mc/")	
	mcFiles = getFilePathsAndSampleNames("/afs/cern.ch/work/j/jschulte/public/filesM300/mc/")
	eventCountsDY=totalNumberOfGeneratedEvents("/afs/cern.ch/work/j/jschulte/public/filesM300/mc/mcSignDY/")
	SignDYFiles = getFilePathsAndSampleNames("/afs/cern.ch/work/j/jschulte/public/filesM300/mc/mcSignDY/")
	dataFile = getFilePathsAndSampleNames("/afs/cern.ch/work/j/jschulte/public/filesM300/")

	print eventCounts
	
	
	processes = []
	for background	 in args.backgrounds:
		processes.append(Process(getattr(Backgrounds,background),eventCounts))
		
	
	signals = []
	for signal in args.signals:
		signals.append(Process(getattr(Signals,signal),eventCounts))

	DYSignals=[]
	for DYsignal in args.DYSignals:
		DYSignals.append(Process(getattr(DYsignals,DYsignal),eventCountsDY))
		
	legend = TLegend(0.475, 0.65, 0.925, 0.925)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)
	legend.SetTextFont(42)
	#~ legend.SetNColumns(2)

	#legendEta = TLegend(0.15, 0.75, 0.7, 0.9)
	#legendEta.SetFillStyle(0)
	#legendEta.SetBorderSize(0)
	#legendEta.SetTextFont(42)

	

	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.06)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.045)
	latexCMSExtra.SetNDC(True)	
	legendHists = []
	


	legendHistData = ROOT.TH1F()
	if args.data:	
		legend.AddEntry(legendHistData,"Data","pe")	
		#legendEta.AddEntry(legendHistData,"Data","pe")	


	for process in reversed(processes):
		temphist = ROOT.TH1F()
		temphist.SetFillColor(process.theColor)
		temphist.SetFillStyle(process.theStyle)
		temphist.SetLineColor(process.theLineColor)
		legendHists.append(temphist.Clone)
		legend.AddEntry(temphist,process.label,"f")
		#legendEta.AddEntry(temphist,process.label,"f")



	
	if args.signals !=0:
		processesWithSignal = []
		for process in processes:
			processesWithSignal.append(process)
		for Signal in signals:
			processesWithSignal.append(Signal)
			temphist = ROOT.TH1F()
			temphist.SetFillColor(Signal.theColor)
			temphist.SetFillStyle(process.theStyle)
			temphist.SetLineColor(Signal.theLineColor)
			legendHists.append(temphist.Clone)		
			legend.AddEntry(temphist,Signal.label,"l")
			#legendEta.AddEntry(temphist,Signal.label,"l")
	
	


	nEvents=-1

	
	ROOT.gStyle.SetOptStat(0)
	
	intlumi = ROOT.TLatex()
	intlumi.SetTextAlign(12)
	intlumi.SetTextSize(0.045)
	intlumi.SetNDC(True)
	intlumi2 = ROOT.TLatex()
	intlumi2.SetTextAlign(12)
	intlumi2.SetTextSize(0.07)
	intlumi2.SetNDC(True)
	scalelabel = ROOT.TLatex()
	scalelabel.SetTextAlign(12)
	scalelabel.SetTextSize(0.03)
	scalelabel.SetNDC(True)
	metDiffLabel = ROOT.TLatex()
	metDiffLabel.SetTextAlign(12)
	metDiffLabel.SetTextSize(0.03)
	metDiffLabel.SetNDC(True)
	chi2Label = ROOT.TLatex()
	chi2Label.SetTextAlign(12)
	chi2Label.SetTextSize(0.03)
	chi2Label.SetNDC(True)
	hCanvas.SetLogy()




	
	plotPad.cd()
	plotPad.SetLogy(0)
	logScale = plot.log
	
	if logScale == True:
		plotPad.SetLogy()

	datahist = getDataHist(plot,dataFile)	
	print datahist.GetEntries()
	lumi = 36400
	print "-----"
	stack = TheStack(processes,lumi,plot,mcFiles)

	if args.data:
		yMax = datahist.GetBinContent(datahist.GetMaximumBin())
		yMin = 0.1
		xMax = datahist.GetXaxis().GetXmax()
		xMin = datahist.GetXaxis().GetXmin()
	else:	
		yMax = stack.theHistogram.GetBinContent(datahist.GetMaximumBin())
		yMin = 0.1
		xMax = stack.theHistogram.GetXaxis().GetXmax()
		xMin = stack.theHistogram.GetXaxis().GetXmin()	
	print yMax, yMin, xMax, xMin
	if plot.yMax == None:
		if logScale:
			yMax = yMax*1000
		else:
			yMax = yMax*1.5
	
	else: yMax = plot.yMax
	print plot.xMin, plot.xMax
	if not plot.yMin == None:
		yMin = plot.yMin
	if not plot.xMin == None:
		xMin = plot.xMin
	if not plot.xMax == None:
		xMax = plot.xMax
	print yMax, yMin, xMax, xMin
	plotPad.DrawFrame(xMin,yMin,xMax,yMax,"; %s ; %s" %(plot.xaxis,plot.yaxis))
	
	

 
	drawStack = stack

	if len(args.signals) != 0:
		signalhists = []
		SignalName = []
		for Signal in signals:
			
			signalhist = Signal.loadHistogram(lumi,mcFiles,plot)
			signalhist.SetLineWidth(2)
	#		signalhist.Add(stack.theHistogram)
			signalhist.SetMinimum(0.1)
			signalhist.Draw("samehist")
			signalhists.append(signalhist)	

	if len(args.DYSignals) != 0:
		DYSignalhists = []
		DYSignalName = []
		for DYSignal in DYSignals:
			
			DYSignalhist = DYSignal.loadHistogram(lumi,mcFiles,plot)
			DYSignalhist.SetLineWidth(2)
	#		DYSignalhist.Add(stack.theHistogram)
			DYSignalhist.SetMinimum(0.1)
			DYSignalhist.Draw("samehist")
			DYSignalhists.append(DYSignalhist)	

	 
	

	drawStack.theStack.Draw("samehist")							


	
	

	datahist.SetMinimum(0.1)
	if args.data:
		datahist.Draw("samep")	


	legend.Draw()


	
	latex.DrawLatex(0.95, 0.96, "%.2f fb^{-1} (13 TeV)"%(lumi/1000,))
	yLabelPos = 0.85
	cmsExtra = "Private Work"
	if not args.data:
		cmsExtra = "#splitline{Private Work}{Simulation}"
		yLabelPos = 0.82	
	latexCMS.DrawLatex(0.19,0.89,"CMS")
	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))
	
	if args.ratio:
		try:
			ratioPad.cd()
		except AttributeError:
			print "Plot fails. Look up in errs/failedPlots.txt"
			outFile =open("errs/failedPlots.txt","a")
			outFile.write('%s\n'%plot.filename%("_"+run.label+"_"+dilepton))
			outFile.close()
			plot.cuts=baseCut
			return 1
		ratioGraphs =  ratios.RatioGraph(datahist,drawStack.theHistogram, xMin=xMin, xMax=xMax,title="Data / MC",yMin=0.0,yMax=2,ndivisions=10,color=ROOT.kBlack,adaptiveBinning=0.25)
		ratioGraphs.draw(ROOT.gPad,True,False,True,chi2Pos=0.8)
					

	ROOT.gPad.RedrawAxis()
	plotPad.RedrawAxis()
	if args.ratio:

		ratioPad.RedrawAxis()
	if not os.path.exists("NplotsCI"):
		os.makedirs("NplotsCI")	
	print plot.fileName
	hCanvas.Print("NplotsCI/"+plot.fileName+".png")



	##
	## Get the histograms
	##

	## Background processes:

	HistoB=stack.theHistogram
	
	##DY to subract from signal
	
	

	for index, DYSignal in enumerate(DYSignals):
	
		if index is 0:
			HistoSDY=DYSignalhists[index]
		else:
			HistoSDY.Add(DYSignalhists[index]) #loadHistoFromFile("/afs/cern.ch/work/j/jschulte/public/filesM300/ana_datamc_DYTo2Mu_M300.root",plot.histName,plot.rebin)

	##Signals


	for index, signal in enumerate(signals):
     		HistoS = signalhists[index]
		SignalName.append(signal.label)

		binning = [400,500,700,1100,1900,3500]

		newHistoB = TH1F("dataHist","bkgHist",len(binning)-1,array("f",binning))	
		for index, binBoundary in enumerate(binning):
    			if index < len(binning)-1:
     				newHistoB.SetBinContent(index+1,HistoB.Integral(binBoundary,binning[index+1]))

		for index, binBoundary in enumerate(binning):
    			if index < len(binning)-1:
     				newHistoS.SetBinContent(index+1,HistoS.Integral(binBoundary,binning[index+1])-HistoSDY.Integral(binBoundary,binning[index+1]))

		for index, binBoundary in enumerate(binning):
    			if index < len(binning)-1:
     				newHistoD.SetBinContent(index+1,newHistoB.Integral(binBoundary,binning[index+1])+newHistoS.Integral(binBoundary,binning[index+1]))

		OutputFile=TFile("%s"+"_"+"%s"+".root"%(signal,plot.histName))
		OutputFile.Write()

					
if __name__ == "__main__":
	
	
	parser = argparse.ArgumentParser(description='Process some integers.')
	
	parser.add_argument("-d", "--data", action="store_true", dest="data", default=False,
						  help="plot data points.")
	parser.add_argument("-m", "--mc", action="store_true", dest="mc", default=False,
						  help="plot mc backgrounds.")
	parser.add_argument("-p", "--plot", dest="plot", nargs=1, default="",
						  help="plot to plot.")
	parser.add_argument("-n", "--norm", action="store_true", dest="norm", default=False,
						  help="normalize to data.")
	parser.add_argument("-r", "--ratio", action="store_true", dest="ratio", default=False,
						  help="plot ratio plot")
	parser.add_argument("-l", "--log", action="store_true", dest="log", default=False,
						  help="plot with log scale for y axis")
	parser.add_argument("-s", "--signal", dest="signals", action="append", default=[],
						  help="signals to plot.")
	parser.add_argument("-b", "--backgrounds", dest="backgrounds", action="append", default=[],
						  help="backgrounds to plot.")
	parser.add_argument("-dy", "--drellyansign", dest="DYSignals", action="append", default=[],
						  help="DYSignals to plot.")


	args = parser.parse_args()
	if len(args.backgrounds) == 0:
		args.backgrounds = ["DYTo2Mu_M300","OtherPrompt","NonPrompt"]

	if len(args.DYSignals) == 0:
		args.DYSignals = ["DYTo2Mu_M300"]

	#if len(args.signals) == 0:
	#	args.signals = ["SimplifiedModel_mB_225_mn2_150_mn1_80","CITo2Mu_Lam22TeVConLL"]

	#if len(args.signals) != 0:
	#	args.plotSignal = True

	if args.plot == "":
	        ## Normal plots
 	        #args.plot = ["massPlot","massPlot2","massPlot3"]
		
		## CI plots
		args.plot = ["massPlot","massCSPosPlot","massCSNegPlot","massPlotBB","massCSPosPlotBB","massCSNegPlotBB","massPlotBE","massCSPosPlotBE","massCSNegPlotBE"]
		
	for plot in args.plot:
		plotObject = getPlot(plot)
		plotDataMC(args,plotObject)
	
