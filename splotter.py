import ROOT
import os
from cmsstyle import CMS_lumi
from officialStyle import officialStyle
officialStyle(ROOT.gStyle)
ROOT.gStyle.SetTitleOffset(1.5, "Y")
ROOT.gStyle.SetTitleOffset(0.85, "X")
ROOT.gStyle.SetPadLeftMargin(0.20)

ROOT.EnableImplicitMT()
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)   



# tree_data = ROOT.RDataFrame('tree'   , ['jpsi_pi_splots.root'])
# tree_mc   = ROOT.RDataFrame('tree_mc', ['jpsi_pi_splots.root'])

ff = ROOT.TFile.Open('jpsi_pi_splots.root')
tree = ff.Get('tree')
treemc = ff.Get('treemc')

plot_outdir = 'sPlots'
if not os.path.isdir(plot_outdir):
   os.mkdir(plot_outdir)

histos = dict()
histos['Bpt'     ] = (ROOT.TH1F('Bpt'     , '', 15, 15,  60), '3#mu p_{T} (GeV)'                          )
histos['Blxy_sig'] = (ROOT.TH1F('Blxy_sig', '', 20,  0, 100), 'L_{xy}/#sigma_{L_{xy}}'                    )
histos['Bsvprob' ] = (ROOT.TH1F('Bsvprob' , '', 10,  0,   1), 'vtx(#mu_{1}, #mu_{2}, #mu_{3}) probability')

c1 = ROOT.TCanvas('c1', '', 700, 700)
c1.Draw()

for k, v in histos.items():

    v[0].GetXaxis().SetTitle(v[1])
    v[0].GetYaxis().SetTitle('events')
    v[0].SetMinimum(0.)
    
    h_all = v[0].Clone()
    h_sig = v[0].Clone()
    h_bkg = v[0].Clone()
    h_mc  = v[0].Clone()

    h_all.SetName( '_'.join([h_all.GetName(), 'all']))
    h_sig.SetName( '_'.join([h_sig.GetName(), 'sig']))
    h_bkg.SetName( '_'.join([h_bkg.GetName(), 'bkg']))
    h_mc .SetName( '_'.join([h_mc .GetName(), 'mc' ]))

    tree.Draw('%s >> %s' %(k, h_all.GetName()), ''       , 'hist')
    tree.Draw('%s >> %s' %(k, h_sig.GetName()), 'nsig_sw', 'hist')
    tree.Draw('%s >> %s' %(k, h_bkg.GetName()), 'nbkg_sw', 'hist')

    h_sig.SetLineColor(ROOT.kRed)
    h_bkg.SetLineColor(ROOT.kBlue)

    h_sig.SetFillColor(ROOT.kRed)
    h_bkg.SetFillColor(ROOT.kBlue)

    h_all.SetMarkerStyle(8)

    ths = ROOT.THStack('ths', '')
    ths.Add(h_sig)
    ths.Add(h_bkg)

    ths.Draw('hist')
    h_all.Draw('EP same')

    # place this after THStack is drawn, else nullptr
    ths.GetXaxis().SetTitle(v[1])
    ths.GetYaxis().SetTitle('events')

    CMS_lumi(c1, 4, 0, cmsText = 'CMS', extraText = '   Preliminary', lumi_13TeV = '')

    leg = ROOT.TLegend(0.6,.7,.88,.88)
    leg.SetHeader('sPlot fits', 'C')
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.AddEntry(h_sig, 'signal', 'F')
    leg.AddEntry(h_bkg, 'background', 'F')
    leg.AddEntry(h_all, 'observed', 'EP')
    leg.Draw('same')

    c1.Modified()
    c1.Update()
    
    c1.SaveAs('%s/%s_splot.pdf' %(plot_outdir, k))

    # now compare signal from data (via sPlot) and MC
    treemc.Draw('%s >> %s' %(k, h_mc.GetName()), '', 'hist')

    h_mc.SetLineColor(ROOT.kGreen-2)
    h_mc.SetFillColor(ROOT.kGreen-2)
    h_mc.SetFillStyle(3345)
    h_sig.SetFillStyle(3354)

    h_mc .Scale(1./h_mc .Integral())
    h_sig.Scale(1./h_sig.Integral())
    
    h_mc .Draw('hist')
    h_sig.Draw('hist same')
    
    mymax = 1.2*max(map(ROOT.TH1.GetMaximum, [h_mc, h_sig]))
    
    h_mc .SetMaximum(mymax)
    h_sig.SetMaximum(mymax)
    h_mc .SetMinimum(0.)
    h_sig.SetMinimum(0.)
    h_mc.GetYaxis().SetTitle('a.u.')
    
    CMS_lumi(c1, 4, 0, cmsText = 'CMS', extraText = '   Preliminary', lumi_13TeV = '')
    
    leg = ROOT.TLegend(0.6,.7,.88,.88)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.AddEntry(h_sig, 'signal from sPlot', 'F')
    leg.AddEntry(h_mc , 'signal MC'        , 'F')
    leg.Draw('same')

    c1.Modified()
    c1.Update()
    
    c1.SaveAs('%s/%s_shapes_splot.pdf' %(plot_outdir, k))

