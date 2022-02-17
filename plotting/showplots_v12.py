'''
This script does the final histograms for the fit for the rjpsi analysis
 - Computes the fakes from the fail region
 - Computes the shape uncertainties
 - Multiplies the vents for all the weights
 - Saves png, pdf and .root files with the histos in pass and fail regions + all the shape nuisances

Differnece from _v7:
- addition of hmlm_jpsi_x_mu_explicit option
  - for plots only
Difference from _v6:
- addition of renormalization with hammer weights from tau and mu
Difference from _v5:
- new option: add_hm_categories
  - it adds the high mass categories for the final fit
Difference from _v4:
- new option for jpsiXMu bkg to be splitted in the different contributions: 
   - FIXME: the datacard production gives an error: I will solve this when we have the new MC, because now we don't need that function

'''
#system
import os
import copy
from datetime import datetime
import random
import time
import sys
import multiprocessing as mp

# computation libraries
import ROOT
import pandas as pd
import numpy as np
from array import array
import pickle
import math 
from bokeh.palettes import viridis, all_palettes
from keras.models import load_model

# cms libs
from cmsstyle import CMS_lumi
from officialStyle import officialStyle

# personal libs
from histos import histos as histos_lm
from new_branches import to_define
from samples import weights, titles, colours
from selections import  prepreselection, triggerselection, preselection, preselection_mc, pass_id, fail_id
from create_datacard_v3 import create_datacard_ch1, create_datacard_ch2, create_datacard_ch3, create_datacard_ch4, create_datacard_ch1_onlypass, create_datacard_ch3_onlypass
from plot_shape_nuisances_v4 import plot_shape_nuisances

ROOT.ROOT.EnableImplicitMT()

shape_nuisances = True
flat_fakerate = False # false mean that we use the NN weights for the fr
compute_sf = False # compute scale factors SHAPE nuisances
compute_sf_onlynorm = False # compute only the sf normalisation (best case)
blind_analysis = True
rjpsi = 1

asimov = False
only_pass = False

if asimov:
    blind_analysis=False
    rjpsi = 1

add_hm_categories = True #true if you want to add also the high mass categories to normalise the jpsimu bkg

jpsi_x_mu_split_all = False #true if you want both hmlm and jpsimother divisions for jpsi_x_mu
jpsi_x_mu_split_jpsimother = True #true if you want to split the jpsimu bkg contributions depending on the jpsi mother
compress_xi_and_sigma = True # If jpsi_x_mu_split_jpsimother is True, this compress the xi and sigma contributes into 1 each
jpsi_x_mu_split_hmlm = False #true if you want to split the jpsimu bkg into contributions depending on hm or lm 
#jpsi_x_mu_split = False #automatic True if one of the previous is True

jpsi_x_mu_explicit_show_on_plots = True  #true if you want the divisions for jpsi_x_mu to be shown on plots

#from samples import  sample_names

if jpsi_x_mu_split_jpsimother:
    if compress_xi_and_sigma:
        from samples import sample_names_explicit_jpsimother_compressed as sample_names
        from samples import jpsi_x_mu_sample_jpsimother_splitting_compressed as jpsi_x_mu_samples
    else:
        from samples import  sample_names_explicit_jpsimother as sample_names
        from samples import  jpsi_x_mu_sample_jpsimother_splitting as jpsi_x_mu_samples
    jpsi_x_mu_split = True
elif jpsi_x_mu_split_hmlm:
    from samples import  sample_names_explicit_hmlm 
    jpsi_x_mu_split = True
elif jpsi_x_mu_split_all:
    from samples import  sample_names_explicit_all, jpsi_x_mu_sample_jpsimother_splitting 
    jpsi_x_mu_split = True
if add_hm_categories:
    from selections import preselection_hm, preselection_hm_mc
    from histos import histos_hm

dateTimeObj = datetime.now()
print(dateTimeObj.hour, ':', dateTimeObj.minute, ':', dateTimeObj.second, '.', dateTimeObj.microsecond)


ROOT.ROOT.EnableImplicitMT(mp.cpu_count())
ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)

officialStyle(ROOT.gStyle, ROOT.TGaxis)

def make_directories(label):

    if not add_hm_categories:
        channels = ['ch1','ch2']
    else:
        channels = ['ch1','ch2','ch3','ch4']
    
    print("Plots will be saved in %s"%label)
    for ch in channels:
        os.system('mkdir -p plots_ul/%s/%s/pdf/lin/' %(label,ch))
        os.system('mkdir -p plots_ul/%s/%s/pdf/log/' %(label,ch))
        os.system('mkdir -p plots_ul/%s/%s/png/lin/' %(label,ch))
        os.system('mkdir -p plots_ul/%s/%s/png/log/' %(label,ch))
            
    os.system('mkdir -p plots_ul/%s/datacards/' %label)

def save_yields(label, temp_hists):
    with open('plots_ul/%s/yields.txt' %label, 'w') as ff:
        total_expected = 0.
        for kk, vv in temp_hists['norm'].items(): 
            if 'data' not in kk:
                total_expected += vv.Integral()
            print(kk.replace(k, '')[1:], '\t\t%.1f' %vv.Integral(), file=ff)
        print('total expected', '\t%.1f' %total_expected, file=ff)

def save_weights(label, sample_names, weights):
    with open('plots_ul/%s/normalisations.txt' %label, 'w') as ff:
        for sname in sample_names: 
            print(sname+'\t\t%.2f' %weights[sname], file=ff)
        print("Flat fake rate weight %s" %str(flat_fakerate), file = ff)

def save_selection(label, preselection):
    with open('plots_ul/%s/selection.py' %label, 'w') as ff:
        total_expected = 0.
        print("selection = ' & '.join([", file=ff)
        for isel in preselection.split(' & '): 
            print("    '%s'," %isel, file=ff)
        print('])', file=ff)
        print('pass: %s'%pass_id, file=ff)
        print('fail: %s'%fail_id, file=ff)

def create_legend(temp_hists, sample_names, titles):
    # Legend gymnastics
    leg = ROOT.TLegend(0.24,.67,.95,.90)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.SetNColumns(3)
    k = list(temp_hists.keys())[0]
    for kk in sample_names:
        if jpsi_x_mu_split:
            if jpsi_x_mu_explicit_show_on_plots:
                if kk == 'jpsi_x_mu': continue
            else:
                if 'jpsi_x_mu_' in kk: continue
            
        leg.AddEntry(temp_hists[k]['%s_%s' %(k, kk)].GetValue(), titles[kk], 'F' if kk!='data' else 'EP')
            
    return leg

def create_datacard_prep(hists, shape_hists, shapes_names, sample_names, channel, name, label, which_sample_bbb_unc):
    '''
    Creates and saves the root file with the histograms of each contribution.
    Saves the histograms of the shape nuisances.
    Calls the 'create datacard' function, both for the pass and fail regions, 
    to write the text datacard for the fit in combine. 
    '''
    if only_pass and (channel == 'ch2' or channel == 'ch4'): #don't save the fail datacards
        return

    fout = ROOT.TFile.Open('plots_ul/%s/datacards/datacard_%s_%s.root' %(label, channel, name), 'UPDATE')
    fout.cd()
    myhists = dict()

    for k, v in hists.items():
        for isample in sample_names + ['fakes']:
            if k == '%s_%s'%(name,isample):
                #if jpsi_x_mu_split and isample == 'jpsi_x_mu':
                #    continue
                hh = v.Clone()
                if isample == 'data':
                    hh.SetName(isample+'_obs_'+channel)
                else:
                    hh.SetName(isample+'_'+channel)
                hh.Write()
                myhists[isample] = hh.Clone()
        
    # Creates the shape nuisances both for Pass and Fail regions
    for k,v in shape_hists.items():
        for sname in shapes_names:
            if k == '%s_%s'%(name,sname):
                #if jpsi_x_mu_split and sname == 'jpsi_x_mu':
                #    continue
                hh = v.Clone()
                hh.SetName(sname + '_'+channel)
                hh.Write()

    if only_pass: #the rate of fakes must be == integral in case of only pass category fit, while ==1 in case of two regions
        if channel == 'ch1' :
            create_datacard_ch1_onlypass(label, name, myhists, jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm, jpsi_x_mu_samples, which_sample_bbb_unc)
        else:
            create_datacard_ch3_onlypass(label, name,  myhists, jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm, jpsi_x_mu_samples, which_sample_bbb_unc)

    else:
        if channel == 'ch1' :
            create_datacard_ch1(label, name,  myhists,  jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm, jpsi_x_mu_samples, which_sample_bbb_unc)
        elif channel == 'ch2' :
            create_datacard_ch2(label, name,  myhists,  jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm, jpsi_x_mu_samples, which_sample_bbb_unc)
        elif channel == 'ch3' :
            create_datacard_ch3(label, name,  myhists,  jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm, jpsi_x_mu_samples, which_sample_bbb_unc)
        else:
            create_datacard_ch4(label, name,  myhists,  jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm, jpsi_x_mu_samples, which_sample_bbb_unc)
    fout.Close()

# pass the jpsi_x_mu hists chi, sigma, lambda
def make_single_binbybin(hists, channel, label, name):
    if only_pass and (channel == 'ch2' or channel == 'ch4'):
        return
    fout = ROOT.TFile.Open('plots_ul/%s/datacards/datacard_%s_%s.root' %(label, channel, name), 'UPDATE')
    
    which_sample = []
    # loop over the bins of the hist
    for i in range(1,hists['sigma'].GetValue().GetNbinsX()+1):
        # compute the quadratic sum of the stat unc of the 3 
        stat_unc = math.sqrt(hists['sigma'].GetValue().GetBinError(i)*hists['sigma'].GetValue().GetBinError(i)+hists['xi'].GetValue().GetBinError(i)*hists['xi'].GetValue().GetBinError(i)+ hists['lambdazero_b'].GetValue().GetBinError(i)*hists['lambdazero_b'].GetValue().GetBinError(i))
        #find the bin with highest uncertainty amongst the 3 contributes
        highest_stat = max(hists, key = lambda x:hists[x].GetValue().GetBinError(i))
        #print(i,hists['sigma'].GetValue().GetBinError(i),hists['xi'].GetValue().GetBinError(i),hists['lambdazero_b'].GetValue().GetBinError(i), stat_unc)
        which_sample.append(highest_stat)

        #define histo up and down
        histo_up = ROOT.TH1D('jpsi_x_mu_from_'+highest_stat+'_'+'jpsi_x_mu_from_'+highest_stat+'_single_bbb'+str(i)+channel+'Up_'+channel,'',hists[highest_stat].GetValue().GetNbinsX(),hists[highest_stat].GetValue().GetBinLowEdge(1), hists[highest_stat].GetValue().GetBinLowEdge(hists[highest_stat].GetValue().GetNbinsX() + 1))
        histo_down = ROOT.TH1D('jpsi_x_mu_from_'+highest_stat+'_'+'jpsi_x_mu_from_'+highest_stat+'_single_bbb'+str(i)+channel+'Down_'+channel,'',hists[highest_stat].GetValue().GetNbinsX(),hists[highest_stat].GetValue().GetBinLowEdge(1), hists[highest_stat].GetValue().GetBinLowEdge(hists[highest_stat].GetValue().GetNbinsX() + 1))

        for nbin in range(1,hists[highest_stat].GetValue().GetNbinsX()+1):
            if nbin == i:
                histo_up.SetBinContent(nbin,hists[highest_stat].GetValue().GetBinContent(nbin) + stat_unc)
                histo_up.SetBinError(nbin,stat_unc + math.sqrt(stat_unc))
                histo_down.SetBinContent(nbin,hists[highest_stat].GetValue().GetBinContent(nbin) - stat_unc)
                histo_down.SetBinError(nbin,stat_unc +math.sqrt( stat_unc))
            else:
                histo_up.SetBinContent(nbin,hists[highest_stat].GetValue().GetBinContent(nbin))
                histo_up.SetBinError(nbin,hists[highest_stat].GetValue().GetBinError(nbin))
                histo_down.SetBinContent(nbin,hists[highest_stat].GetValue().GetBinContent(nbin))
                histo_down.SetBinError(nbin,hists[highest_stat].GetValue().GetBinError(nbin))
        fout.cd()
        histo_up.Write()
        histo_down.Write()
    fout.Close()
    return which_sample


def make_binbybin(hist, sample, channel, label, name):
    if only_pass and (channel == 'ch2' or channel == 'ch4'):
        return

    fout = ROOT.TFile.Open('plots_ul/%s/datacards/datacard_%s_%s.root' %(label, channel, name), 'UPDATE')
    for i in range(1,hist.GetValue().GetNbinsX()+1):
        #histo_up = ROOT.TH1D('jpsi_x_mu_bbb'+str(i)+flag+'Up','jpsi_x_mu_bbb'+str(i)+flag+'Up',hist.GetValue().GetNbinsX(),hist.GetValue().GetBinLowEdge(1), hist.GetValue().GetBinLowEdge(hist.GetValue().GetNbinsX() + 1))
        #histo_down = ROOT.TH1D('jpsi_x_mu_bbb'+str(i)+flag+'Down','jpsi_x_mu_bbb'+str(i)+flag+'Down',hist.GetValue().GetNbinsX(),hist.GetValue().GetBinLowEdge(1), hist.GetValue().GetBinLowEdge(hist.GetValue().GetNbinsX() + 1))
        histo_up = ROOT.TH1D(sample+'_'+sample+'_bbb'+str(i)+channel+'Up_'+channel,'',hist.GetValue().GetNbinsX(),hist.GetValue().GetBinLowEdge(1), hist.GetValue().GetBinLowEdge(hist.GetValue().GetNbinsX() + 1))
        histo_down = ROOT.TH1D(sample+'_'+sample+'_bbb'+str(i)+channel+'Down_'+channel,'',hist.GetValue().GetNbinsX(),hist.GetValue().GetBinLowEdge(1), hist.GetValue().GetBinLowEdge(hist.GetValue().GetNbinsX() + 1))
        for nbin in range(1,hist.GetValue().GetNbinsX()+1):
            if nbin == i:
                histo_up.SetBinContent(nbin,hist.GetValue().GetBinContent(nbin) + hist.GetValue().GetBinError(nbin))
                histo_up.SetBinError(nbin,hist.GetValue().GetBinError(nbin) + math.sqrt(hist.GetValue().GetBinError(nbin)))
                histo_down.SetBinContent(nbin,hist.GetValue().GetBinContent(nbin) - hist.GetValue().GetBinError(nbin))
                histo_down.SetBinError(nbin,hist.GetValue().GetBinError(nbin) - math.sqrt(hist.GetValue().GetBinError(nbin)))
            else:
                histo_up.SetBinContent(nbin,hist.GetValue().GetBinContent(nbin))
                histo_up.SetBinError(nbin,hist.GetValue().GetBinError(nbin))
                histo_down.SetBinContent(nbin,hist.GetValue().GetBinContent(nbin))
                histo_down.SetBinError(nbin,hist.GetValue().GetBinError(nbin))
        fout.cd()
        histo_up.Write()
        histo_down.Write()
    fout.Close()

def define_shape_nuisances(sname, shapes, samples, nuisance_name, central_value, up_value, down_value, central_weights_string):
    shapes[sname + '_' + nuisance_name + 'Up'] = samples[sname]
    if sname == 'jpsi_mu':
        shapes[sname + '_' + nuisance_name + 'Up'] = shapes[sname + '_' + nuisance_name + 'Up'].Define('shape_weight_tmp', central_weights_string.replace(central_value,up_value)+'*hammer_bglvar')
    elif sname == 'jpsi_tau':
        shapes[sname + '_' + nuisance_name + 'Up'] = shapes[sname + '_' + nuisance_name + 'Up'].Define('shape_weight_tmp', central_weights_string.replace(central_value,up_value)+'*hammer_bglvar*%f*%f' %(blind,rjpsi))
    elif  'jpsi_x_mu' in sname: #this works both for jpsi_x_mu and for its subsamples
        shapes[sname + '_' + nuisance_name + 'Up'] = shapes[sname + '_' + nuisance_name + 'Up'].Define('shape_weight_tmp', central_weights_string.replace(central_value,up_value)+'*jpsimother_weight')

    else:
        shapes[sname + '_' + nuisance_name + 'Up'] = shapes[sname + '_' + nuisance_name + 'Up'].Define('shape_weight_tmp', central_weights_string.replace(central_value,up_value))

    shapes[sname + '_' + nuisance_name + 'Down'] = samples[sname]
    if sname == 'jpsi_mu':
        shapes[sname + '_' + nuisance_name + 'Down'] = shapes[sname + '_' + nuisance_name + 'Down'].Define('shape_weight_tmp', central_weights_string.replace(central_value,down_value)+'*hammer_bglvar')
    elif sname == 'jpsi_tau':
        shapes[sname + '_' + nuisance_name + 'Down'] = shapes[sname + '_' + nuisance_name + 'Down'].Define('shape_weight_tmp', central_weights_string.replace(central_value,down_value)+'*hammer_bglvar*%f*%f' %(blind,rjpsi))
    elif 'jpsi_x_mu' in sname:
        shapes[sname + '_' + nuisance_name + 'Down'] = shapes[sname + '_' + nuisance_name + 'Down'].Define('shape_weight_tmp', central_weights_string.replace(central_value,down_value)+'*jpsimother_weight')

    else:
        shapes[sname + '_' + nuisance_name + 'Down'] = shapes[sname + '_' + nuisance_name + 'Down'].Define('shape_weight_tmp', central_weights_string.replace(central_value,down_value))
    return shapes[sname + '_' + nuisance_name + 'Up'], shapes[sname + '_' + nuisance_name + 'Down']

# Canvas and Pad gymnastics
c1 = ROOT.TCanvas('c1', '', 700, 700)
c1.Draw()
c1.cd()
main_pad = ROOT.TPad('main_pad', '', 0., 0.25, 1. , 1.  )
main_pad.Draw()
c1.cd()
ratio_pad = ROOT.TPad('ratio_pad', '', 0., 0., 1., 0.25)
ratio_pad.Draw()
main_pad.SetTicks(True)
main_pad.SetBottomMargin(0.)
# main_pad.SetTopMargin(0.3)   
# main_pad.SetLeftMargin(0.15)
# main_pad.SetRightMargin(0.15)
# ratio_pad.SetLeftMargin(0.15)
# ratio_pad.SetRightMargin(0.15)
ratio_pad.SetTopMargin(0.)   
ratio_pad.SetGridy()
ratio_pad.SetBottomMargin(0.45)

def get_DiMuonBkg(selection):
    
    tree_name = 'BTo3Mu'
    tree_dir = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_Dec2021/'
        
    dataframe = {}
    dataframe["SR"] = ROOT.RDataFrame(tree_name,'%s/data_ptmax_merged_fakerate.root'%(tree_dir))
    #dataframe["ResonantTrg"] = ROOT.RDataFrame(tree_name,'%s/data_ptmax_merged_fakerate.root'%(tree_dir)) 
    #dataframe["NonResonantTrg"] = ROOT.RDataFrame(tree_name,'%s/datalowmass_ptmax_merged_fakerate.root'%(tree_dir))
    dataframe["SBs"] = ROOT.RDataFrame(tree_name,{'%s/datalowmass_ptmax_merged_fakerate_2.root'%(tree_dir), '%s/data_ptmax_merged_fakerate.root'%(tree_dir)})
    regions = list(dataframe.keys())
    
    print("==================================")
    print("==== Dimuon Combinatorial Bkg ====")
    print("==================================")
    print("regions: ", regions)

    sanitycheck             = False
    
    #hists                  = {}
    Q2hist                  = {}
    Q2_extrap_hist          = {}
    JpsimassShape           = {}
    Jpsimass                = {}
    JpsimassSB              = {}
    JpsimassLSB             = {}
    Q2LSBcanvas             = {}
    Q2_extrapcanvas         = {}
    Q2_DimuonShape          = {}
    
    ######################
    ##### Defintions #####
    ######################
    
    LSB_min = 2.89
    LSB_max = 3.02
    RSB_min = 3.18
    RSB_max = 3.32
    SR_min  = 2.95
    SR_max  = 3.23
    Bkgshape_min   = 2.695
    Bkgshape_max   = 2.83
    
    '''for s in ["SBs"]:
    filterLSB = ' & '.join([preselectionLSB, pass_id])
    hists[s] = dataframe[s].Filter(filterLSB).Histo1D(('Q2LSB%s'%s,"Q2LSB;  q^{2} [GeV^{2}]; Events/0.5 GeV",24,0,10.5),"Q_sq")'''
    
    ### Get the relevant histos and information from the DataFrames  ###
    
    ### Get the histo with the full invariant-mass distribution to extract the Dimuon shape ###
    #filterSBsShape = ' & '.join([prepreselection,'Bmass<6.3', pass_id])
    filterSBsShape = ' & '.join([prepreselection,selection])
    JpsimassShape["SBs"] = dataframe["SBs"].Filter(filterSBsShape).Histo1D(("mJpsiSBShape","mJpsiSBShape;  m_{#mu#mu} [GeV]; Events/0.01 GeV", 200, 2, 4), "jpsi_mass")
    HJpsimassSB = JpsimassShape["SBs"].GetValue()
    if(sanitycheck):
        SBMasscanvas = TCanvas("SBMassc", "SBMassc")
        SBMasscanvas.cd()
        JpsimassShape["SBs"].Draw("pe")
        SBMasscanvas.Print('SBMasscanvas.png')
        
    ### LSB ###
    #filterLSB = ' & '.join([preselectionLSB, pass_id])
    filterLSB = ' & '.join([prepreselection, 'jpsi_mass>%s'%LSB_min, 'jpsi_mass<%s'%LSB_max, selection])
    Q2hist["SBs"] = dataframe["SBs"].Filter(filterLSB).Histo1D(("Q2LSB","Q2LSB;  q^{2} [GeV^{2}]; Events/0.5 GeV",24,0,10.5),"Q_sq")
            
    ### Get the scale factor to extrapolate the LSB to the SR ###
    JpsimassLSB["SBs"] = dataframe["SBs"].Filter(filterLSB).Histo1D(("mJpsiLSB","mJpsiLSB;  m_{#mu#mu} [GeV]; Events/0.01 GeV", 200, 2, 4), "jpsi_mass")
    HJpsimassLSB = JpsimassLSB["SBs"].GetValue()
    Jpsi_scale = 3.0969/HJpsimassLSB.GetMean()
    dataframe["SBs"] = dataframe["SBs"].Filter(filterLSB).Define("Jpsi_scale", "{}".format(Jpsi_scale))
    if(sanitycheck):
        print("Mean For Jpsi_scale: ", HJpsimassLSB.GetMean())
        Q2LSBcanvas = TCanvas("Q2LSBcan", "Q2LSBcan")
        Q2LSBcanvas.cd()
        Q2hist["SBs"].Draw("pe")
        Q2LSBcanvas.Print('Q2LSBcan.png') 
                
        '''for s in ["SBs"]:
        Q2LSBcanvas[s] = TCanvas("Q2LSBc", "Q2LSBc")
        Q2LSBcanvas[s].cd()
        hists[s].Draw("pe")
        Q2LSBcanvas[s].Print('Q2LSB%s.png'%s)'''
   
    ### Get the histo in the SR with the SR selection to perform the fit to get the Dimuon normalization ###
    #filterSR = ' & '.join([preselectionSRForSB, pass_id])
    filterSR = ' & '.join([prepreselection, triggerselection, selection])
    Jpsimass["SR"] = dataframe["SR"].Filter(filterSR).Histo1D(("mJpsiSR","mJpsiSR;  m_{#mu#mu} [GeV]; Events/0.01 GeV", 200, 2, 4), "jpsi_mass")
    HJpsimassSR = Jpsimass["SR"].GetValue()
    #SRdataset = ROOT.RooDataSet('SRdataset', 'SRdataset', tree_name, filterSR)
    if(sanitycheck):
        SRMasscanvas = TCanvas("SRMassc", "SRMassc")
        SRMasscanvas.cd()
        Jpsimass["SR"].Draw("pe")
        SRMasscanvas.Print('SRMasscanvas.png')

    ############################# 
    ####### Dimuon Shape  #######
    #############################
                
                
    ROOT.gInterpreter.Declare(
        """
        using Vec_t = const ROOT::VecOps::RVec<float>;
        float SB_extrap(float B_pt_reco, float scale,
        float pt1, float eta1, float phi1, float m1, 
        float pt2, float eta2, float phi2, float m2, 
        float pt3, float eta3, float phi3, float m3) {
        float Bc_MASS_PDG = 6.275;
        //cout<<pt1<<" "<<eta1<<" "<<phi1<<" "<<m1<<" "<<endl;
        //cout<<pt2<<" "<<eta2<<" "<<phi2<<" "<<m2<<" "<<endl;
        //cout<<pt3<<" "<<eta3<<" "<<phi3<<" "<<m3<<" "<<endl;
        //cout<<scale<<endl;
        TLorentzVector mu1_p4, mu2_p4, mu3_p4, B_coll_p4, Jpsi_p4_extrap;
        mu1_p4.SetPtEtaPhiM(pt1, eta1, phi1, m1);
        mu2_p4.SetPtEtaPhiM(pt1, eta2, phi2, m2);
        mu3_p4.SetPtEtaPhiM(pt3, eta3, phi3, m3);
        B_coll_p4.SetPtEtaPhiM(B_pt_reco, (mu1_p4 + mu2_p4 + mu3_p4).Eta(), (mu1_p4 + mu2_p4 + mu3_p4).Phi(), Bc_MASS_PDG);
        Jpsi_p4_extrap.SetPtEtaPhiM((mu1_p4 + mu2_p4).Pt(), (mu1_p4 + mu2_p4).Eta(), (mu1_p4 + mu2_p4).Phi(), (mu1_p4 + mu2_p4).M()*scale);
        Float_t Q_2 = (B_coll_p4 - Jpsi_p4_extrap)*(B_coll_p4 - Jpsi_p4_extrap);
        return Q_2;
        }
        """)
    
    dataframe["SBs"] = dataframe["SBs"].Filter(filterLSB).Define("Q_sq_extrap", "SB_extrap(Bpt_reco, Jpsi_scale, mu1pt, mu1eta, mu1phi, mu1mass, mu2pt, mu2eta, mu2phi, mu2mass, kpt, keta, kphi, kmass)")
    Q2_extrap_hist["SBs"] = dataframe["SBs"].Filter(filterLSB).Histo1D(("Q2LSB_extrap","Q2LSB_extrap;  q^{2} [GeV^{2}]; Events/0.5 GeV",24,0,10.5),"Q_sq_extrap")
    Q2_DimuonShape = Q2_extrap_hist["SBs"].GetValue()
    if(sanitycheck):
        Q2_extrapcanvas = TCanvas("Q2_extrapcanvasc", "Q2_extrapcanvasc")
        Q2_extrapcanvas.cd()
        Q2_extrap_hist["SBs"].Draw("pe")
        Q2_extrapcanvas.Print('Q2_extrapcanvas.png')
        
    #################################### 
    ####### Dimuon Normalization #######
    ####################################

    # Shape defintion # 
                    
    mass                   = ROOT.RooRealVar     ("mass",           "mass",                  SR_min,        SR_max                               )
    massSB                 = ROOT.RooRealVar     ("massSB",         "massSB",                Bkgshape_min,  Bkgshape_max                         )
    
    mass.setRange  ('LSB',       LSB_min,       LSB_max      )
    mass.setRange  ('RSB',       RSB_min,       RSB_max      )
    mass.setRange  ('SR',        SR_min,        SR_max       )
    massSB.setRange('Bkgshape',  Bkgshape_min,  Bkgshape_max )
    
    #####    Signal    #####
    MassJpsi               = ROOT.RooRealVar     ("MassJpsi",       "MassJpsi",     3.0969                                                       )
    scale                  = ROOT.RooRealVar     ("scale",          "scale",        1.,      0.,   2.                                            )
    sigma                  = ROOT.RooRealVar     ("sigma",          "sigma",        0.03,    0.,   0.5                                           )
    ResSigma               = ROOT.RooRealVar     ("ResSigma",       "ResSigma",     1.5,     0.,   3.                                            )
    alphaCB                = ROOT.RooRealVar     ("alphaCB",        "alphaCB",      1.5,     0.,   10.                                           )
    nCB                    = ROOT.RooRealVar     ("nCB",             "nCB",         1.5,     0.,   100.                                          )
    fraGauss               = ROOT.RooRealVar     ("fraGauss",       "fraGauss",     0.01,    0.,   0.35                                          )
    
    MeanMassJpsi           = ROOT.RooFormulaVar  ("MeanMassJpsi",   "MassJpsi*scale", ROOT.RooArgList(MassJpsi, scale))
    sigmaGauss             = ROOT.RooFormulaVar  ("sigmaGauss",     "sigma*ResSigma", ROOT.RooArgList(sigma, ResSigma))
    
    #####   Background   #####
    bkgSlope               = ROOT.RooRealVar     ("bkgSlope",        "bkgSlope",    1.,     -5., 5.                                              )
    
    ##### Fit Normalizations #####
    NSgl                   = ROOT.RooRealVar     ("NSgl",            "NSgl",        50000,    0.,  200000.                                       )
    NBkg                   = ROOT.RooRealVar     ("NBkg",            "NBkg",        500,      0.,  1000.                                         )
    NBkgSB                 = ROOT.RooRealVar     ("NBkgSB",          "NBkgSB",      1000,     0.,  1000000.                                      )
    
    #####################
    #####   PDFs    #####
    #####################
    CBall                  = ROOT.RooCBShape     ("CBall",            "CBall",      mass, MeanMassJpsi, sigma, alphaCB, nCB                      )
    Gauss                  = ROOT.RooGaussian    ("Gauss",            "Gauss",      mass, MeanMassJpsi, sigmaGauss                               )
    SigPDF                 = ROOT.RooAddPdf      ("SigPDF",           "SigPDF",     ROOT.RooArgList(Gauss, CBall), ROOT.RooArgList(fraGauss)     )
    
    Expo                   = ROOT.RooExponential ("Expo",             "Expo",       mass,   bkgSlope                                             )
    SBExpo                 = ROOT.RooExponential ("SBExpo",           "SBExpo",     massSB, bkgSlope                                             )
    
    shapes                 = ROOT.RooArgList     (SigPDF, Expo)
    yields                 = ROOT.RooArgList     (NSgl,   NBkg)
    
    PDFSB                  = ROOT.RooAddPdf      ("PDFSB",        "PDFSB",          ROOT.RooArgList(SBExpo), ROOT.RooArgList(NBkgSB)             )
    CompletePDF            = ROOT.RooAddPdf      ("CompletePDF",  "CompletePDF",    ROOT.RooArgList(shapes), ROOT.RooArgList(yields)             )
    
    
    # Fit to the invariant mass in the SB to extract ths background shape #
    SBdataset   = ROOT.RooDataHist("SBdataset", "SBdataset", ROOT.RooArgList(massSB), HJpsimassSB)
    framemassSB = massSB.frame(ROOT.RooFit.Name(""), ROOT.RooFit.Title(""), ROOT.RooFit.Bins(200))
    SBdataset.plotOn(framemassSB,ROOT.RooFit.Binning(200, 2, 4),ROOT.RooFit.MarkerSize(1.5))
    PDFSB.fitTo(SBdataset,ROOT.RooFit.Save())
    PDFSB.plotOn(framemassSB)
    if(sanitycheck):
        JpsiMassSBCanvas = TCanvas("FitShapeJpsiMassSB", "FitShapeJpsiMassSB")
        JpsiMassSBCanvas.cd()
        framemassSB.Draw()
        JpsiMassSBCanvas.Print('FitShapeJpsiMassSB.png')
        
    BkgShapetoFix = bkgSlope.getVal()                                       
    if(sanitycheck):
        print("Shape slope for the dimuon from SB fit:", BkgShapetoFix)
                    
    # Fit to the invariant mass in the SR (defined with all the analysis selections, but the invariant-mass cut) #
    SRdataset = ROOT.RooDataHist("SRdataset", "SRdataset", mass, HJpsimassSR)
    framemass = mass.frame(ROOT.RooFit.Name("SRFit"), ROOT.RooFit.Title(""), ROOT.RooFit.Bins(200))    
    SRdataset.plotOn(framemass,ROOT.RooFit.Name("data"),ROOT.RooFit.Binning(200, 2, 4))
    bkgSlope.setConstant(ROOT.kTRUE)
    bkgSlope.setVal(BkgShapetoFix)
    CompletePDF.fitTo(SRdataset,ROOT.RooFit.Save())
    CompletePDF.plotOn(framemass)
    CompletePDF.plotOn(framemass,ROOT.RooFit.Components("Expo"),ROOT.RooFit.LineColor(ROOT.kGreen),ROOT.RooFit.FillColor(ROOT.kGreen),ROOT.RooFit.DrawOption("F"),ROOT.RooFit.MoveToBack())
    CompletePDF.plotOn(framemass,ROOT.RooFit.Components("CBall"),ROOT.RooFit.LineColor(ROOT.kGray),ROOT.RooFit.FillColor(ROOT.kGray),ROOT.RooFit.DrawOption("F"),ROOT.RooFit.MoveToBack())
    CompletePDF.plotOn(framemass,ROOT.RooFit.Components("Gauss"),ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kDashed));
    framemass.GetXaxis().SetTitleSize(0.1)
    framemass.GetXaxis().SetLabelSize(0.05)
    framemass.GetYaxis().SetTitleOffset(0.85)
    framemass.GetYaxis().SetTitleSize(0.05)
    framemass.GetYaxis().SetNdivisions(505)
    framemass.SetYTitle("Events/0.01 GeV")
    framemass.SetTitle(" ")
    
    #################
    ## Pulls study ##
    #################
    SRdatasetPulls = framemass.pullHist()
    framemassPulls = mass.frame(ROOT.RooFit.Title(""))
    framemassPulls.addPlotable(SRdatasetPulls,"P") 
    framemassPulls.GetXaxis().SetTitleSize(0.08)
    framemassPulls.GetXaxis().SetLabelSize(0.05)
    framemassPulls.GetYaxis().SetTitleOffset(0.5)
    framemassPulls.GetYaxis().CenterTitle(1)
    framemassPulls.GetYaxis().SetTitle("#Delta/#sigma")
    framemassPulls.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
    framemassPulls.GetYaxis().SetTitleSize(0.08)
    framemassPulls.GetYaxis().SetLabelSize(0.05)
    framemassPulls.GetYaxis().SetNdivisions(505)
    #§framemassPulls.GetYaxis().SetRangeUser(-10.52, 10.52)
    
    ##############
    ## Plotting ##
    ##############
    JpsiMassSRCanvas = TCanvas("JpsiMassSR", "JpsiMassSR", 0, 0, 700, 700)
    JpsiMassSRCanvas.SetTicks()
    JpsiMassSRCanvas.SetTopMargin(0.015);
    JpsiMassSRCanvas.SetRightMargin(0.020);
    JpsiMassSRCanvas.SetBottomMargin(0.15);
    JpsiMassSRCanvas.SetLeftMargin(0.12);
    JpsiMassSRCanvas.cd()
    Plot = TPad("Plot", "Plot", 0, 0.4, 1, 1)
    Pulls = TPad("Pulls", "Pulls", 0, 0, 1, 0.4)
    Plot.SetRightMargin(0.02)
    Plot.SetLeftMargin(0.16)
    Plot.SetTopMargin(0.02)
    Plot.SetBottomMargin(0.001)
    Pulls.SetRightMargin(0.02)
    Pulls.SetTopMargin(0)
    Pulls.SetBottomMargin(0.45)
    Pulls.SetLeftMargin(0.16)
    Plot.SetTicks()
    Pulls.SetTicks()
    Plot.Draw()
    Pulls.Draw()
    
    cms = TLatex()
    cms.SetTextSize(0.07)
    leg = TLegend(0.18,0.7,0.4,0.2)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.05)
    leg.SetTextFont(42)
    leg.AddEntry(framemass.getObject(2),"Data","PLE")
    leg.AddEntry(framemass.getObject(3),"Fit pdf","L")
    leg.AddEntry(framemass.getObject(0),"Crystall Ball","FL")
    leg.AddEntry(framemass.getObject(4),"Gaussian","L")
    leg.AddEntry(framemass.getObject(1),"Background","FL")
    
    if(sanitycheck):
        Plot.cd()
        framemass.Draw()
        cms.DrawLatexNDC(0.2, 0.85, "#it{CMS} #bf{Internal}")
        leg.Draw()
        Pulls.cd()
        framemassPulls.Draw()
        #framemass.Draw()
        #Jpsimass["SR"].Draw("pe")
        JpsiMassSRCanvas.Print('FitJpsiMassSR.png')
        #CompletePDF.Draw("SAME")
        
    Normalization = NBkg.getVal()/NSgl.getVal()
    Q2_DimuonShape.Scale(Normalization)
    if(sanitycheck):
        print("Dimuon Normalization: ",  Normalization)
        DiMuonShapeCanvas = TCanvas("DiMuonShapeCanvas", "DiMuonShapeCanvas", 0, 0, 700, 700)
        DiMuonShapeCanvas.cd()
        Q2_DimuonShape.Draw("pe")
        DiMuonShapeCanvas.Print('NormalizedDiMuonShape.png')
                        
    return Q2_DimuonShape
                    



##########################################################################################
##########################################################################################

if __name__ == '__main__':
    
    #datacards = ['mu1pt', 'Q_sq', 'm_miss_sq', 'E_mu_star', 'E_mu_canc', 'bdt_tau', 'Bmass', 'mcorr', 'decay_time_ps','k_raw_db_corr_iso04_rel']
    datacards = ['Q_sq','jpsiK_mass','Bmass','bdt_tau']

    # timestamp
    label = datetime.now().strftime('%d%b%Y_%Hh%Mm%Ss')

    # create plot directories
    make_directories(label)
    
    central_weights_string = 'ctau_weight_central*br_weight*puWeight*sf_reco_total*sf_id_jpsi*sf_id_k'

    # access the samples, via RDataFrames
    samples_orig = dict()
    samples_pres = dict()
    samples_lm = dict()

    tree_name = 'BTo3Mu'
    #Different paths depending on the sample
    #tree_dir = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_2021May31_nn'
    #tree_dir = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_Oct2021'
    #tree_dir = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_Dec2021/smaller/'
    tree_dir = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_Dec2021/'

    print("=============================")
    print("====== Loading Samples ======")
    print("=============================")

    #load the samples (jpsi_x_mu even if I want it splitted)
    for k in sample_names:
        samples_orig[k] = ROOT.RDataFrame(tree_name,'%s/%s_fakerate_only_iso.root'%(tree_dir,k)) 
        #samples_orig[k] = ROOT.RDataFrame(tree_name,'%s/%s_prepresel.root'%(tree_dir,k)) 
        #samples_orig[k] = ROOT.RDataFrame(tree_name,'%s/%s_bdt_comb.root'%(tree_dir,k)) 
        #if k!='data':
        #    samples_orig[k] = ROOT.RDataFrame(tree_name,'%s/%s_sf_werrors.root'%(tree_dir,k)) 
        #else: 
        #    samples_orig[k] = ROOT.RDataFrame(tree_name,'%s/%s_fakerate.root'%(tree_dir,k)) 
        #print("Loading sample %s/%s_prepresel.root"%(tree_dir,k))    

    #Blind analysis: hide the value of rjpsi for the fit
    if blind_analysis:
        random.seed(2)
        rand = random.randint(0, 10000)
        blind = rand/10000 *1.5 +0.5
        #blind = 1.
    else:
        blind = 1.

    
    #################################################
    ####### Weights ################################
    #################################################

    for k, v in samples_orig.items():
        #print(k)
        samples_orig[k] = samples_orig[k].Define('br_weight', '%f' %weights[k])
        if k=='jpsi_tau':
            samples_orig[k] = samples_orig[k].Define('tmp_weight', central_weights_string +'*hammer_bglvar*%f*%f' %(blind,rjpsi))
        elif k=='jpsi_mu':
            samples_orig[k] = samples_orig[k].Define('tmp_weight', central_weights_string +'*hammer_bglvar')
        elif 'jpsi_x_mu' in k: #works both if splitted or not
            samples_orig[k] = samples_orig[k].Define('tmp_weight', central_weights_string +'*jpsimother_weight')
        else:
            samples_orig[k] = samples_orig[k].Define('tmp_weight', central_weights_string  if k!='data' else 'br_weight') 

        #define new columns   
        for new_column, new_definition in to_define: 
            if samples_orig[k].HasColumn(new_column):
                continue       
            samples_orig[k] = samples_orig[k].Define(new_column, new_definition)

    if flat_fakerate == False:
        for sample in samples_orig:
            #samples_orig[sample] = samples_orig[sample].Define('total_weight_wfr', 'tmp_weight') 
            #samples_orig[sample] = samples_orig[sample].Define('total_weight_wfr', 'tmp_weight*nn/(1-nn)') 
            #samples_orig[sample] = samples_orig[sample].Define('total_weight_wfr', 'tmp_weight*fakerate_weight_w_weights_qsq_gen') 
            #if sample == 'data':
            samples_orig[sample] = samples_orig[sample].Define('total_weight_wfr', 'tmp_weight*fakerate_data') 
            #else:
            #    samples_orig[sample] = samples_orig[sample].Define('total_weight_wfr', 'tmp_weight*fakerate_bcmu') 
                
    # the scale factor on the id on the third muon only for the PASS region
    for sample in samples_orig:
        #samples_orig[sample] = samples_orig[sample].Define('total_weight', 'tmp_weight*sf_id_k' if sample!='data' else 'tmp_weight')
        samples_orig[sample] = samples_orig[sample].Define('total_weight', 'tmp_weight' if sample!='data' else 'tmp_weight')
            
    ##############################################
    ##### Preselection ###########################
    ##############################################
    print("===================================")
    print("====== Applying Preselection ======")
    print("===================================")

    #Apply preselection for ch1 and ch2
    for k, v in samples_orig.items():
        filter = preselection_mc if k!='data' else preselection
        samples_lm[k] = samples_orig[k].Filter(filter)
        #print("Sample "+k +" with "+str(samples_lm[k].Count().GetValue())+" events")
        print("Sample "+k )
        
    histos_dictionaries = [histos_lm]
    #Apply preselection for ch3 and ch4 (high mass regions)
    if add_hm_categories:
        samples_hm = dict()
        print("############################")
        for k, v in samples_orig.items():
            if not (k=='data' or 'jpsi_x_mu' in k): #only those samples are different from zero in the high mass region
                continue
            filter = preselection_hm_mc if k!='data' else preselection_hm
            samples_hm[k] = samples_orig[k].Filter(filter)
            #print("Sample "+k +" with "+str(samples_hm[k].Count().GetValue())+" events")
            print("Sample "+k )

        histos_dictionaries = [histos_lm, histos_hm]
    
    '''
    # request to divide jpsi_x_mu into all its contributions 
    if jpsi_x_mu_split:
        f_histo = ROOT.TFile.Open("decay_weight.root")
        histo = f_histo.Get('weight')
        jpsimother = {
            'other': histo.GetBinContent(1),
            'bzero': histo.GetBinContent(2),
            'bplus': histo.GetBinContent(3),
            'bzero_s': histo.GetBinContent(4),
            #'bplus_c': histo.GetBinContent(5),
            'sigmaminus_b': histo.GetBinContent(6),
            'lambdazero_b': histo.GetBinContent(7),
            'ximinus_b': histo.GetBinContent(8),
            'sigmazero_b': histo.GetBinContent(9),
            'xizero_b': histo.GetBinContent(10),
        }
        
        #division of jpsi_x_mu sample in different jpsi mother contributes
        for bkg_sample in jpsi_x_mu_sample_jpsimother_splitting:
            mother_name = bkg_sample.replace("jpsi_x_mu_from_","")
            
            filter_jpsi = ' & '.join(['jpsimother_weight == %s'%jpsimother[mother_name] ])
            # also split jpsi_x_mu for hm and lm if required
            if jpsi_x_mu_split_all or jpsi_x_mu_split_hmlm: 
                jpsi_x_mu_hmlm_dic = {'hm':'hmlm_flag == 0','lm':'hmlm_flag == 1'}
                for opt in jpsi_x_mu_hmlm_dic:
                    filter = ' & '.join([filter_jpsi,'%s'%(jpsi_x_mu_hmlm_dic[opt])])
                    samples_lm[bkg_sample + '_' + opt] = samples_lm['jpsi_x_mu'].Filter(filter) 
                    samples_hm[bkg_sample + '_' + opt] = samples_hm['jpsi_x_mu'].Filter(filter)
                    print("Splitting jpsi_x_mu in %s_%s; events %d for m<6.3 and %d for m>6.3"%(bkg_sample,opt,samples_lm[bkg_sample + '_' + opt].Count().GetValue(),samples_hm[bkg_sample + '_' + opt].Count().GetValue()))
                    #print("Splitting jpsi_x_mu in %s_%s"%(bkg_sample,opt))
                    
            else:
                print("Splitting jpsi_x_mu in %s"%bkg_sample)
                samples_lm[bkg_sample] = samples_lm['jpsi_x_mu'].Filter(filter_jpsi)
                #print("Splitting jpsi_x_mu in %s; events %d for m<6.3"%(bkg_sample,samples_lm[bkg_sample].Count().GetValue()))
                if add_hm_categories:
                    samples_hm[bkg_sample] = samples_hm['jpsi_x_mu'].Filter(filter_jpsi)
                    #print("Splitting jpsi_x_mu in %s; events %d for m>6.3"%(bkg_sample,samples_hm[bkg_sample].Count().GetValue()))

    '''
    samples_dictionaries = [samples_lm]
    if add_hm_categories:
        samples_dictionaries = [samples_lm, samples_hm]

    dateTimeObj = datetime.now()
    print(dateTimeObj.hour, ':', dateTimeObj.minute, ':', dateTimeObj.second, '.', dateTimeObj.microsecond)

    ###########################################################
    ######### NUISANCES Defininition ##########################
    ###########################################################

    # Shape nuisances definition
    # Create a new disctionary "shapes", similar to the "samples" one defined for the datasets
    # Each entry of the dic is a nuisance for a different dataset
    if shape_nuisances :
        shapes_lm = dict()
        shapes_dictionaries = [shapes_lm]
        if add_hm_categories:
            shapes_hm = dict()
            shapes_dictionaries = [shapes_lm, shapes_hm]

        for iter,(shapes,samples) in enumerate(zip(shapes_dictionaries, samples_dictionaries)):

            ############################
            ########  CTAU  ############
            ############################
            for sname in samples:
                if ('jpsi_x_mu' not in sname and sname != 'data' ):    #Only Bc samples want this nuisance
                    shapes[sname + '_ctauUp'], shapes[sname + '_ctauDown'] = define_shape_nuisances(sname, shapes, samples, 'ctau', 'ctau_weight_central', 'ctau_weight_up', 'ctau_weight_down', central_weights_string)

                ###############################
                ########  PILE UP  ############
                ###############################

                if (sname != 'data'): # all MC samples
                    shapes[sname + '_puWeightUp'], shapes[sname + '_puWeightDown'] = define_shape_nuisances(sname,shapes, samples, 'puWeight', 'puWeight', 'puWeightUp', 'puWeightDown', central_weights_string)

                if compute_sf:
                    ###############################
                    ########  SF RECO  ############
                    ###############################
                    if (sname != 'data'):

                        for ireco in range(0, 16):
                            shapes[sname + '_sfReco_'+str(ireco)+'Up'], shapes[sname + '_sfReco_'+str(ireco)+'Down'] = define_shape_nuisances(sname,shapes, samples,  'sfReco_'+str(ireco), 'sf_reco_total', 'sf_reco_'+str(ireco)+'_up', 'sf_reco_'+str(ireco)+'_down', central_weights_string)

                    ###############################
                    ########  SF ID  ##############
                    ###############################
		
                    # Only jpsi for now, bc the sf_id for the third muon is only in the pass region!
                    if (sname != 'data'):
                        for iid in range(0, 16):
                            shapes[sname + '_sfId_'+str(iid)+'Up'], shapes[sname + '_sfId_'+str(iid)+'Down'] = define_shape_nuisances(sname, shapes, samples, 'sfId_'+str(iid), 'sf_id_jpsi', 'sf_id_'+str(iid)+'_jpsi_up', 'sf_id_'+str(iid)+'_jpsi_down', central_weights_string)

                if compute_sf_onlynorm:
                    ###############################
                    ########  SF RECO  ############
                    ###############################
                    if (sname != 'data'):
                        shapes[sname + '_sfRecoUp'], shapes[sname + '_sfRecoDown'] = define_shape_nuisances(sname,shapes, samples,  'sfReco', 'sf_reco_total', 'sf_reco_all_up', 'sf_reco_all_down', central_weights_string)

                    ###############################
                    ########  SF ID  ##############
                    ###############################
		
                    # Only jpsi for now, bc the sf_id for the third muon is only in the pass region!
                    if (sname != 'data'):
                        shapes[sname + '_sfIdJpsiUp'], shapes[sname + '_sfIdJpsiDown'] = define_shape_nuisances(sname, shapes, samples, 'sfIdJpsi', 'sf_id_jpsi', 'sf_id_all_jpsi_up', 'sf_id_all_jpsi_down', central_weights_string)
                        shapes[sname + '_sfIdkUp'], shapes[sname + '_sfIdkDown'] = define_shape_nuisances(sname, shapes, samples, 'sfIdk', 'sf_id_k', 'sf_id_all_k_up', 'sf_id_all_k_down', central_weights_string)

            ######################################
            ########  FORM FACTORS  ##############
            #####################################
            
            if not iter: #iter == 0
                # form factor shape nuisances for jpsi mu and jpsi tau datasets
                hammer_branches = ['hammer_bglvar_e0up',
                                   'hammer_bglvar_e0down',
                                   'hammer_bglvar_e1up',
                                   'hammer_bglvar_e1down',
                                   'hammer_bglvar_e2up',
                                   'hammer_bglvar_e2down',
                                   'hammer_bglvar_e3up',
                                   'hammer_bglvar_e3down',
                                   'hammer_bglvar_e4up',
                                   'hammer_bglvar_e4down',
                                   'hammer_bglvar_e5up',
                                   'hammer_bglvar_e5down',
                                   'hammer_bglvar_e6up',
                                   'hammer_bglvar_e6down',
                                   'hammer_bglvar_e7up',
                                   'hammer_bglvar_e7down',
                                   'hammer_bglvar_e8up',
                                   'hammer_bglvar_e8down',
                                   'hammer_bglvar_e9up',
                                   'hammer_bglvar_e9down',
                                   'hammer_bglvar_e10up',
                                   'hammer_bglvar_e10down'
                               ]

                for ham in hammer_branches:
                    new_name = ham.replace('hammer_','')
                    # Redefinition of the name for combine requests
                    if 'up' in ham:
                        new_name = new_name.replace('up','Up')
                    elif 'down' in ham:
                        new_name = new_name.replace('down','Down')
            
                    shapes['jpsi_mu_'+new_name] = samples['jpsi_mu']
                    shapes['jpsi_mu_'+new_name] = shapes['jpsi_mu_'+new_name].Define('shape_weight_tmp', central_weights_string+'*'+ham)
                    shapes['jpsi_tau_'+new_name] = samples['jpsi_tau']
                    shapes['jpsi_tau_'+new_name] = shapes['jpsi_tau_'+new_name].Define('shape_weight_tmp', central_weights_string+'*'+ham+'*%f*%f' %(blind,rjpsi))
                    

            if flat_fakerate == False:
                for name in shapes:
                    #shapes[name] = shapes[name].Define('shape_weight_wfr','shape_weight_tmp') #fail region
                    #shapes[name] = shapes[name].Define('shape_weight_wfr','shape_weight_tmp*nn/(1-nn)') #fail region
                    #shapes[name] = shapes[name].Define('shape_weight_wfr','shape_weight_tmp*fakerate_weight_w_weights_qsq_gen') #fail region
                    #if 'data' in name:
                    shapes[name] = shapes[name].Define('shape_weight_wfr','shape_weight_tmp*fakerate_data') #fail region
                    #else:
                    #    shapes[name] = shapes[name].Define('shape_weight_wfr','shape_weight_tmp*fakerate_bcmu') #fail region

            # it has to be defined before I multiply the pass region weight for sf_id_k
            # it's the pass region because shape_Weight is used for the pass region onyl
            '''for sname in samples:
                if (sname != 'data'):
                    shapes[sname + '_sfIdkUp'] = samples[sname]
                    shapes[sname + '_sfIdkUp'] = shapes[sname + '_sfIdkUp'].Define('shape_weight', 'tmp_weight*sf_id_all_k_up')
                    shapes[sname + '_sfIdkDown'] = samples[sname]
                    shapes[sname + '_sfIdkDown'] = shapes[sname + '_sfIdkDown'].Define('shape_weight', 'tmp_weight*sf_id_all_k_down')
            '''
            # For the Pass region we add the sf_id_k and its shape uncetrtainty
            # it's the pass region because I use shape_weight, while for the fail region I use shape_weight_wfr
            for name in shapes:
                # this is to anticorrelate
                #if 'sfIdk' not in name:
                #    shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp*sf_id_k')
                shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp')
            

            '''
            for name in shapes:
                if 'sfId' not in name:
                    shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp*sf_id_k')
                elif (compute_sf):
                    if 'Up' in name:
                        number = name.split('_')[-1].strip('Up')
                        shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp*sf_id_'+number+'_k_up')
                    elif 'Down' in name:
                        number = name.split('_')[-1].strip('Down')
                        shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp*sf_id_'+number+'_k_down')
                elif (compute_sf_onlynorm):
                    if 'Up' in name:
                        shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp*sf_id_all_k_up')
                    elif 'Down' in name:
                        shapes[name] = shapes[name].Define('shape_weight','shape_weight_tmp*sf_id_all_k_down')
            '''

    ##################################
    ###### HISTOS ###################
    ##################################

    for iteration,(shapes,samples,histos) in enumerate(zip(shapes_dictionaries, samples_dictionaries, histos_dictionaries)):
        
        if not iteration: #iteration==0
            channels = ['ch1','ch2']
        else:
            channels = ['ch3','ch4']


        # first create all the pointers
        print('====> creating pointers to histo')
        temp_hists      = {} # pass muon ID category
        temp_hists_fake = {} # fail muon ID category
    
        for k, v in histos.items():    
            temp_hists     [k] = {}
            temp_hists_fake[k] = {}
            for kk, vv in samples.items():
                temp_hists     [k]['%s_%s' %(k, kk)] = vv.Filter(pass_id).Histo1D(v[0], k, 'total_weight')
                if flat_fakerate:
                    temp_hists_fake[k]['%s_%s' %(k, kk)] = vv.Filter(fail_id).Histo1D(v[0], k, 'total_weight')
                else:
                    temp_hists_fake[k]['%s_%s' %(k, kk)] = vv.Filter(fail_id).Histo1D(v[0], k, 'total_weight_wfr')
    
        # Create pointers for the shapes histos 
        if shape_nuisances:
            print('====> shape uncertainties histos')
            unc_hists      = {} # pass muon ID category
            unc_hists_fake = {} # pass muon ID category
            for k, v in histos.items():    
                # Compute them only for the variables that we want to fit
                if (k not in datacards and iteration == 0) or (k!='Bmass' and iteration):
                    continue
                unc_hists     [k] = {}
                unc_hists_fake[k] = {}
                for kk, vv in shapes.items():
                    unc_hists     [k]['%s_%s' %(k, kk)] = vv.Filter(pass_id).Histo1D(v[0], k, 'shape_weight')
                    #if 'sfIdk' in kk: #no shape unc for SF k for fail region
                    #    continue
                    if flat_fakerate:
                        unc_hists_fake[k]['%s_%s' %(k, kk)] = vv.Filter(fail_id).Histo1D(v[0], k, 'shape_weight')
                    else:
                        unc_hists_fake[k]['%s_%s' %(k, kk)] = vv.Filter(fail_id).Histo1D(v[0], k, 'shape_weight_wfr')

        print('====> now looping')
        for k, v in histos.items():
            print("Histo %s"%k)
            single_bbb_histos = {}
            single_bbb_histos_fake = {}
            for sample,sample_item in samples.items():
                if "jpsi_x_mu" in sample:
                    make_binbybin(temp_hists[k]['%s_%s'%(k,sample)],sample,channels[0], label, k)
                    make_binbybin(temp_hists_fake[k]['%s_%s'%(k,sample)],sample,channels[1], label, k)
                    if 'sigma' in sample or 'xi' in sample or 'lambda' in sample:
                        single_bbb_histos[sample.replace("jpsi_x_mu_from_","")]=temp_hists[k]['%s_%s'%(k,sample)]
                        single_bbb_histos_fake[sample.replace("jpsi_x_mu_from_","")]=temp_hists_fake[k]['%s_%s'%(k,sample)]

            which_sample_bbb_unc = make_single_binbybin(single_bbb_histos, channels[0], label, k)
            which_sample_bbb_unc_fake = make_single_binbybin(single_bbb_histos_fake, channels[1], label, k)

            #check that bins are not zero (if they are, correct)
            for i, kv in enumerate(temp_hists[k].items()):
                key = kv[0]
                ihist = kv[1]
                sample_name = key.split(k+'_')[1]
                for i in range(1,ihist.GetNbinsX()+1):
                    if ihist.GetBinContent(i) <= 0:
                        ihist.SetBinContent(i,0.0001)

            for i, kv in enumerate(temp_hists_fake[k].items()):
                key = kv[0]
                ihist = kv[1]
                sample_name = key.split(k+'_')[1]
                for i in range(1,ihist.GetNbinsX()+1):
                    if ihist.GetBinContent(i) <= 0:
                        ihist.SetBinContent(i,0.0001)

            if shape_nuisances and ((k in datacards and  iteration==0) or (k == 'Bmass' and iteration)):
                
                for i, kv in enumerate(unc_hists[k].items()):
                    key = kv[0]
                    ihist = kv[1]
                    sample_name = key.split(k+'_')[1]
                    for i in range(1,ihist.GetNbinsX()+1):
                        if ihist.GetBinContent(i) <= 0:
                            ihist.SetBinContent(i,0.0001)

                    for i, kv in enumerate(unc_hists_fake[k].items()):
                        key = kv[0]
                        ihist = kv[1]
                        sample_name = key.split(k+'_')[1]
                    for i in range(1,ihist.GetNbinsX()+1):
                        if ihist.GetBinContent(i) <= 0:
                            ihist.SetBinContent(i,0.0001)

            c1.cd()
            
            leg = create_legend(temp_hists, [str(k) for k,v in samples.items()], titles)
            main_pad.cd()
            main_pad.SetLogy(False)
        
            # some look features
            maxima = [] 
            data_max = 0.
            for i, kv in enumerate(temp_hists[k].items()):
                key = kv[0]
                ihist = kv[1]
                sample_name = key.split(k+'_')[1]
                    
                ihist.GetXaxis().SetTitle(v[1])
                ihist.GetYaxis().SetTitle('events')                
                ihist.SetLineColor(colours[sample_name])
                ihist.SetFillColor(colours[sample_name] if key!='%s_data'%k else ROOT.kWhite)
                if key!='%s_data'%k:
                    maxima.append(ihist.GetMaximum())
                else:
                    data_max = ihist.GetMaximum()
    
            # Definition of stack histos
            ths1      = ROOT.THStack('stack', '') #what I want to show
            ths1_fake = ROOT.THStack('stack_fake', '')

            for i, kv in enumerate(temp_hists[k].items()):
                key = kv[0]
                if key=='%s_data'%k: continue
                ihist = kv[1]
                ihist.SetMaximum(1.6*max(maxima))
                ihist.Draw('hist' + 'same'*(i>0))
                #print("Integral %s %f"%(key,ihist.Integral()))
                if not jpsi_x_mu_split:
                    ths1.Add(ihist.GetValue())
                else:
                    # if I want to explicitly see the splitting in the plots, I save them in ths1
                    if jpsi_x_mu_explicit_show_on_plots: 
                        if key=='%s_jpsi_x_mu'%k: continue
                        ths1.Add(ihist.GetValue())
                    else: # If I don't want to explicitely see the splitting, I use 
                        if key=='%s_jpsi_x_mu'%k: 
                            ths1.Add(ihist.GetValue())
                        elif 'jpsi_x_mu_' in key:
                            continue
                        else:
                            ths1.Add(ihist.GetValue())
            
            # apply same aestethics to pass and fail
            for kk in temp_hists[k].keys():
                temp_hists_fake[k][kk].GetXaxis().SetTitle(temp_hists[k][kk].GetXaxis().GetTitle())
                temp_hists_fake[k][kk].GetYaxis().SetTitle(temp_hists[k][kk].GetYaxis().GetTitle())
                temp_hists_fake[k][kk].SetLineColor(temp_hists[k][kk].GetLineColor())
                temp_hists_fake[k][kk].SetFillColor(temp_hists[k][kk].GetFillColor())
                

            # fakes for the fail contribution
            # subtract data to MC
            temp_hists[k]['%s_fakes' %k] = temp_hists_fake[k]['%s_data' %k].Clone()
            fakes = temp_hists[k]['%s_fakes' %k]
            # Subtract to fakes all the contributions of other samples in the fail region

            for i, kv in enumerate(temp_hists_fake[k].items()):
                if 'data' in kv[0]:
                    kv[1].SetLineColor(ROOT.kBlack)
                    continue
                #elif 'jpsi_x_mu_' in kv[0]: #if one of the splittings of jpsi_x_mu
                #    continue
                else:
                    fakes.Add(kv[1].GetPtr(), -1.)
            #check fakes do not have <= 0 bins
            for b in range(1,fakes.GetNbinsX()+1):
                if fakes.GetBinContent(b)<=0.:
                    fakes.SetBinContent(b,0.0001)

            fakes.SetFillColor(colours['fakes'])
            fakes.SetFillStyle(1001)
            fakes.SetLineColor(colours['fakes'])
            fakes_forfail = fakes.Clone()
            if flat_fakerate:
                fakes.Scale(weights['fakes'])

            ths1.Add(fakes)
            print(k,fakes.Integral())
            maxima.append(fakes.GetMaximum())
            ths1.Draw('hist')
            try:
                ths1.GetXaxis().SetTitle(v[1])
            except:
                continue
            ths1.GetYaxis().SetTitle('events')
            ths1.SetMaximum(1.6*max(sum(maxima), data_max))
            ths1.SetMinimum(0.0001)

        
            # statistical uncertainty
            stats = ths1.GetStack().Last().Clone()
            stats.SetLineColor(0)
            stats.SetFillColor(ROOT.kGray+1)
            stats.SetFillStyle(3344)
            stats.SetMarkerSize(0)
            stats.Draw('E2 SAME')
            
            if flat_fakerate:
                leg.AddEntry(fakes, 'fakes flat', 'F')    
            else:
                leg.AddEntry(fakes, 'fakes nn', 'F')    
            leg.AddEntry(stats, 'stat. unc.', 'F')
            leg.Draw('same')
    
            #temp_hists[k]['%s_data'%k].GetXaxis().SetRange(0,14)
            if not asimov:
                temp_hists[k]['%s_data'%k].Draw('EP SAME')
            CMS_lumi(main_pad, 4, 0, cmsText = 'CMS', extraText = ' Work in Progress', lumi_13TeV = 'L = 59.7 fb^{-1}')
            main_pad.cd()
            # if the analisis if blind, we don't want to show the rjpsi prefit value
            if not blind_analysis:
                rjpsi_value = ROOT.TPaveText(0.7, 0.65, 0.88, 0.72, 'nbNDC')
                rjpsi_value.AddText('R(J/#Psi) = %.2f' %rjpsi)
                rjpsi_value.SetFillColor(0)
                rjpsi_value.Draw('EP')
        
            # Ratio for pass region
            ratio_pad.cd()
            ratio = temp_hists[k]['%s_data'%k].Clone()
            ratio.SetName(ratio.GetName()+'_ratio')
            ratio.Divide(stats)
            ratio_stats = stats.Clone()
            ratio_stats.SetName(ratio.GetName()+'_ratiostats')
            ratio_stats.Divide(stats)
            ratio_stats.SetMaximum(1.999) # avoid displaying 2, that overlaps with 0 in the main_pad
            ratio_stats.SetMinimum(0.0001) # and this is for symmetry
            ratio_stats.GetYaxis().SetTitle('obs/exp')
            ratio_stats.GetYaxis().SetTitleOffset(0.5)
            ratio_stats.GetYaxis().SetNdivisions(405)
            ratio_stats.GetXaxis().SetLabelSize(3.* ratio.GetXaxis().GetLabelSize())
            ratio_stats.GetYaxis().SetLabelSize(3.* ratio.GetYaxis().GetLabelSize())
            ratio_stats.GetXaxis().SetTitleSize(3.* ratio.GetXaxis().GetTitleSize())
            ratio_stats.GetYaxis().SetTitleSize(3.* ratio.GetYaxis().GetTitleSize())
            
            norm_stack = ROOT.THStack('norm_stack', '')
            
            for kk, vv in temp_hists[k].items():
                if 'data' in kk: continue
                hh = vv.Clone()
                hh.Divide(stats)

                if not jpsi_x_mu_split:
                    norm_stack.Add(hh)
                else:
                    # if I want to explicitly see the splitting in the plots
                    if jpsi_x_mu_explicit_show_on_plots: 
                        if kk=='%s_jpsi_x_mu'%k: continue
                        norm_stack.Add(hh)
                    else: # If I don't want to explicitely see the splitting
                        if kk=='%s_jpsi_x_mu'%k: 
                            norm_stack.Add(hh)
                        elif 'jpsi_x_mu_' in kk:
                            continue
                        else:
                            norm_stack.Add(hh)

            norm_stack.Draw('hist same')


            line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1., ratio.GetXaxis().GetXmax(), 1.)
            line.SetLineColor(ROOT.kBlack)
            line.SetLineWidth(1)
            ratio_stats.Draw('E2')
            norm_stack.Draw('hist same')
            ratio_stats.Draw('E2 same')
            line.Draw('same')
            if not asimov:
                ratio.Draw('EP same')
    
            c1.Modified()
            c1.Update()

            c1.SaveAs('plots_ul/%s/%s/pdf/lin/%s.pdf' %(label, channels[0], k))
            c1.SaveAs('plots_ul/%s/%s/png/lin/%s.png' %(label, channels[0], k))
                    
            ths1.SetMaximum(20*max(sum(maxima), data_max))
            ths1.SetMinimum(10)
            main_pad.SetLogy(True)
            c1.Modified()
            c1.Update()

            c1.SaveAs('plots_ul/%s/%s/pdf/log/%s.pdf' %(label, channels[0], k))
            c1.SaveAs('plots_ul/%s/%s/png/log/%s.png' %(label, channels[0], k))
        
            if shape_nuisances and ((k in datacards and  iteration==0) or (k == 'Bmass' and iteration)):
                create_datacard_prep(temp_hists[k], unc_hists[k], shapes, [name for name,v in samples.items()], channels[0], k, label, which_sample_bbb_unc)
                plot_shape_nuisances(label, k, channels[0], [name for name,v in samples.items()], which_sample_bbb_unc, compute_sf = compute_sf, compute_sf_onlynorm = compute_sf_onlynorm)

            #####################################################
            # Now creating and saving the stack of the fail region

            c1.cd()
            main_pad.cd()
            main_pad.SetLogy(False)
            max_fake = []
            for i, kv in enumerate(temp_hists_fake[k].items()):
                key = kv[0]
                if key=='%s_data'%k: 
                    max_fake.append(kv[1].GetMaximum())
                    continue
                ihist = kv[1]
                #print("Integral %s %f"%(key,ihist.Integral()))
                if not jpsi_x_mu_split:
                    ths1_fake.Add(ihist.GetValue())
                else:
                    # if I want to explicitly see the splitting in the plots, I save them in ths1_fake
                    if jpsi_x_mu_explicit_show_on_plots: 
                        if key=='%s_jpsi_x_mu'%k: continue
                        ths1_fake.Add(ihist.GetValue())
                    else: # If I don't want to explicitely see the splitting
                        if key=='%s_jpsi_x_mu'%k: 
                            ths1_fake.Add(ihist.GetValue())
                        elif 'jpsi_x_mu_' in key:
                            continue
                        else:
                            ths1_fake.Add(ihist.GetValue())

            temp_hists_fake[k]['%s_fakes' %k] = fakes_forfail
            ths1_fake.Add(fakes_forfail)
            ths1_fake.Draw('hist')
            ths1_fake.SetMaximum(2.*sum(max_fake))
            ths1_fake.SetMinimum(0.0001)
            ths1_fake.GetYaxis().SetTitle('events')
            
            stats_fake = ths1_fake.GetStack().Last().Clone()
            stats_fake.SetLineColor(0)
            stats_fake.SetFillColor(ROOT.kGray+1)
            stats_fake.SetFillStyle(3344)
            stats_fake.SetMarkerSize(0)
            stats_fake.Draw('E2 SAME')
            
            if not asimov:
                temp_hists_fake[k]['%s_data'%k].Draw('EP SAME')
            CMS_lumi(main_pad, 4, 0, cmsText = 'CMS', extraText = ' Preliminary', lumi_13TeV = '')
            leg.Draw('same')

            # Ratio for pass region
            
            ratio_pad.cd()
            ratio_fake = temp_hists_fake[k]['%s_data'%k].Clone()
            ratio_fake.SetName(ratio_fake.GetName()+'_ratio')
            ratio_fake.Divide(stats_fake)
            ratio_stats_fake = stats_fake.Clone()
            ratio_stats_fake.SetName(ratio.GetName()+'_ratiostats_fake')
            ratio_stats_fake.Divide(stats_fake)
            ratio_stats_fake.SetMaximum(1.999) # avoid displaying 2, that overlaps with 0 in the main_pad
            ratio_stats_fake.SetMinimum(0.001) # and this is for symmetry
            ratio_stats_fake.GetYaxis().SetTitle('obs/exp')
            ratio_stats_fake.GetYaxis().SetTitleOffset(0.5)
            ratio_stats_fake.GetYaxis().SetNdivisions(405)
            ratio_stats_fake.GetXaxis().SetLabelSize(3.* ratio_fake.GetXaxis().GetLabelSize())
            ratio_stats_fake.GetYaxis().SetLabelSize(3.* ratio_fake.GetYaxis().GetLabelSize())
            ratio_stats_fake.GetXaxis().SetTitleSize(3.* ratio_fake.GetXaxis().GetTitleSize())
            ratio_stats_fake.GetYaxis().SetTitleSize(3.* ratio_fake.GetYaxis().GetTitleSize())
            
            norm_stack_fake = ROOT.THStack('norm_stack', '')

            for kk, vv in temp_hists_fake[k].items():
                if 'data' in kk: continue
                hh = vv.Clone()
                hh.Divide(stats_fake)
                if not jpsi_x_mu_split:
                    norm_stack_fake.Add(hh)
                else:
                    # if I want to explicitly see the splitting in the plots
                    if jpsi_x_mu_explicit_show_on_plots: 
                        if kk=='%s_jpsi_x_mu'%k: continue
                        norm_stack_fake.Add(hh)
                    else: # If I don't want to explicitely see the splitting, I use 
                        if kk=='%s_jpsi_x_mu'%k: 
                            norm_stack_fake.Add(hh)
                        elif 'jpsi_x_mu' in kk:
                            continue
                        else:
                            norm_stack_fake.Add(hh)

            norm_stack_fake.Draw('hist same')

            line = ROOT.TLine(ratio_fake.GetXaxis().GetXmin(), 1., ratio_fake.GetXaxis().GetXmax(), 1.)
            line.SetLineColor(ROOT.kBlack)
            line.SetLineWidth(1)
            ratio_stats_fake.Draw('E2')
            norm_stack_fake.Draw('hist same')
            ratio_stats_fake.Draw('E2 same')
            line.Draw('same')
            if not asimov:
                ratio_fake.Draw('EP same')

            c1.Modified()
            c1.Update()

            c1.SaveAs('plots_ul/%s/%s/pdf/lin/%s.pdf' %(label, channels[1], k))
            c1.SaveAs('plots_ul/%s/%s/png/lin/%s.png' %(label, channels[1], k))

            ths1_fake.SetMaximum(20*max(sum(maxima), data_max))
            ths1_fake.SetMinimum(10)
            main_pad.SetLogy(True)
            c1.Modified()
            c1.Update()

            c1.SaveAs('plots_ul/%s/%s/pdf/log/%s.pdf' %(label, channels[1], k))
            c1.SaveAs('plots_ul/%s/%s/png/log/%s.png' %(label, channels[1], k))

            if shape_nuisances and ((k in datacards and  iteration==0) or (k == 'Bmass' and iteration)):
                create_datacard_prep(temp_hists_fake[k], unc_hists_fake[k], shapes, [name for name,v in samples.items()], channels[1], k, label, which_sample_bbb_unc_fake)
                #create_datacard_prep(temp_hists_fake[k],unc_hists_fake[k],shapes,'fail',k,label)
                if not only_pass:
                    plot_shape_nuisances(label, k, channels[1], [name for name,v in samples.items()], which_sample_bbb_unc_fake, compute_sf = compute_sf, compute_sf_onlynorm = compute_sf_onlynorm)

        save_yields(label, temp_hists)
        save_selection(label, preselection)
        save_weights(label, [k for k,v in samples.items()], weights)

dateTimeObj = datetime.now()
print(dateTimeObj.hour, ':', dateTimeObj.minute, ':', dateTimeObj.second, '.', dateTimeObj.microsecond)


# save reduced trees to produce datacards
# columns = ROOT.std.vector('string')()
# for ic in ['Q_sq', 'm_miss_sq', 'E_mu_star', 'E_mu_canc', 'Bmass']:
#     columns.push_back(ic)
# for k, v in samples.items():
#     v.Snapshot('tree', 'plots_ul/%s/tree_%s_datacard.root' %(label, k), columns)
