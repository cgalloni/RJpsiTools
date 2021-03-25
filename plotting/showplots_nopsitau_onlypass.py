import os
import copy
import ROOT
import numpy as np
from datetime import datetime
from bokeh.palettes import viridis, all_palettes
from histos import histos
from cmsstyle import CMS_lumi
from new_branches import to_define
from samples_wf import weights, sample_names, titles
from selections import preselection, preselection_mc, pass_id, fail_id
import pickle
from officialStyle import officialStyle
from create_datacard_bug import create_datacard_onlypass
import random
import time
from array import array
start_time = time.time()
#ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)

officialStyle(ROOT.gStyle, ROOT.TGaxis)

def make_directories(label):

    os.system('mkdir -p plots_ul/%s/pdf/lin/' %label)
    os.system('mkdir -p plots_ul/%s/pdf/log/' %label)
    os.system('mkdir -p plots_ul/%s/png/lin/' %label)
    os.system('mkdir -p plots_ul/%s/png/log/' %label)

    os.system('mkdir -p plots_ul/%s/fail_region/pdf/lin/' %label)
    os.system('mkdir -p plots_ul/%s/fail_region/pdf/log/' %label)
    os.system('mkdir -p plots_ul/%s/fail_region/png/lin/' %label)
    os.system('mkdir -p plots_ul/%s/fail_region/png/log/' %label)

    os.system('mkdir -p plots_ul/%s/datacards/' %label)

def save_yields(label, temp_hists):
    with open('plots_ul/%s/yields.txt' %label, 'w') as ff:
        total_expected = 0.
        for kk, vv in temp_hists['norm'].items(): 
            if 'data' not in kk:
                total_expected += vv.Integral()
            print(kk.replace(k, '')[1:], '\t\t%.1f' %vv.Integral(), file=ff)
        print('total expected', '\t%.1f' %total_expected, file=ff)

def save_selection(label, preselection):
    with open('plots_ul/%s/selection.py' %label, 'w') as ff:
        total_expected = 0.
        print("selection = ' & '.join([", file=ff)
        for isel in preselection.split(' & '): 
            print("    '%s'," %isel, file=ff)
        print('])', file=ff)

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
        leg.AddEntry(temp_hists[k]['%s_%s' %(k, kk)].GetValue(), titles[kk], 'F' if kk!='data' else 'EP')
    return leg

def create_datacard_prep(hists,flag,name,label):
    fout = ROOT.TFile.Open('plots_ul/%s/datacards/datacard_%s_%s.root' %(label,flag, name), 'recreate')
    fout.cd()
    myhists = dict()
    for k, v in hists.items():
        for isample in sample_names :
            if isample in k:
                hh = v.Clone()
                if isample == 'data':
                    hh.SetName(isample+'_obs')
                else:
                    hh.SetName(isample)
                hh.Write()
                myhists[isample] = hh.Clone()
                #print(myhists[isample],isample)

    #print(myhists['data'].Integral())
    if flag == 'pass':
        create_datacard_onlypass(myhists,name, label)
    #    else:
    #    create_datacard_fail(myhists,name, label)
    fout.Close()

                
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

##########################################################################################
##########################################################################################

if __name__ == '__main__':
    
    datacards = ['mu1pt', 'Q_sq', 'm_miss_sq', 'E_mu_star', 'E_mu_canc', 'bdt_tau', 'Bmass', 'mcorr']
    
    # timestamp
    #label = datetime.now().strftime('%d%b%Y_%Hh%Mm%Ss')
    label = datetime.now().strftime('%d%b%Y_%Hh%Mm%Ss')

    # create plot directories
    make_directories(label)

    # add normalisation factor from Jpsi pi MC
#     for k, v in weights.items():
#         if k not in ['data']:
#             v *= 1.25
#         if k in ['data', 'onia', 'fakes']:
#             continue
#         v *= 0.79

    # tweak selections, if you like

#     preselection = '1'
#     preselection_mc = preselection
#     pass_id = 'k_softID>0.5'
#     fail_id = 'k_tightID<0.5'
#     fail_id = '(!(%s))' % pass_id

    # access the samples, via RDataFrames
    samples = dict()
    
    tree_name = 'BTo3Mu'
    tree_dir_data = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_2021Mar15' #data
    tree_dir = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_2021Mar15' #Bc and Hb
    tree_hbmu = '/pnfs/psi.ch/cms/trivcat/store/user/friti/dataframes_2021Mar16' #Bc and Hb

    '''    for isample_name in sample_names:
        print(isample_name)
        samples[isample_name] = ROOT.RDataFrame(tree_name, '%s/BcToXToJpsi_is_%s_merged.root' %(tree_dir, isample_name))
        #        samples[isample_name] = ROOT.RDataFrame(tree_name, '%s/BcToXToJpsi_is_%s_enriched.root' %(tree_dir, isample_name))
    '''
    samples['jpsi_tau'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_jpsi_tau_merged.root' %(tree_dir))
    samples['jpsi_mu'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_jpsi_mu_trigger_hammer.root' %(tree_dir))
    samples['chic0_mu'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_chic0_mu_merged.root' %(tree_dir))
    samples['chic1_mu'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_chic1_mu_merged.root' %(tree_dir))
    samples['chic2_mu'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_chic2_mu_merged.root' %(tree_dir))
    samples['hc_mu'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_hc_mu_merged.root' %(tree_dir))
    samples['jpsi_hc'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_jpsi_hc_merged.root' %(tree_dir))
    samples['psi2s_mu'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_psi2s_mu_merged.root' %(tree_dir))
    #    samples['psi2s_tau'] = ROOT.RDataFrame(tree_name,'%s/BcToJPsiMuMu_is_psi2s_tau_merged.root' %(tree_dir))
    #samples['data'] = ROOT.RDataFrame(tree_name,'%s/data_ptmax_merged.root' %(tree_dir_data))
    samples['data'] = ROOT.RDataFrame(tree_name,'%s/data_flagtriggersel.root' %(tree_dir_data))
    #samples['onia'] = ROOT.RDataFrame(tree_name,'%s/HbToJPsiMuMu_ptmax_merged.root' %(tree_dir))
    #samples['onia'] = ROOT.RDataFrame(tree_name,'%s/HbToJPsiMuMu3MuFilter_ptmax_merged.root' %(tree_hbmu))
    samples['onia'] = ROOT.RDataFrame(tree_name,'%s/HbToJPsiMuMu3MuFilter_trigger_bcclean.root' %(tree_hbmu))
    samples['fakes'] = ROOT.RDataFrame(tree_name,'%s/HbToJPsiMuMu_trigger_bcclean.root' %(tree_dir))
    
    print("OK")
    # define total weights for the different samples and add new columns to RDFs

    #blind analysis-> random number between 0.5 and 2 (but always the same because it is fixed)
    random.seed(2)
    rand = random.randint(0, 10000)
    #blind = rand/10000 *1.5 +0.5
    blind = 1.
    rjpsi = 1.
    #rjpsi = 0.25/0.066 #SM
    #rjpsi = 0.71 #lhcb
    for k, v in samples.items():
        #print(k,v)
        samples[k] = samples[k].Define('br_weight', '%f' %weights[k])
        if k=='jpsi_tau':
            # HERE
            #samples[k] = samples[k].Define('total_weight', 'ctau_weight_central*br_weight*puWeight*290620./500805.')
           samples[k] = samples[k].Define('total_weight', 'ctau_weight_central*br_weight*puWeight*%f*%f' %(blind,rjpsi))
           
        elif k=='jpsi_mu':
            #samples[k] = samples[k].Define('total_weight', 'ctau_weight_central*br_weight*puWeight*hammer_clean')
            samples[k] = samples[k].Define('total_weight', 'ctau_weight_central*br_weight*puWeight')
        else:
            samples[k] = samples[k].Define('total_weight', 'ctau_weight_central*br_weight*puWeight' if k!='data' else 'br_weight') # weightGen is suposed to be the lifetime reweigh, but it's broken
        for new_column, new_definition in to_define: 
            if samples[k].HasColumn(new_column):
                continue
            samples[k] = samples[k].Define(new_column, new_definition)

    # apply filters on newly defined variables
    for k, v in samples.items():
        filter = preselection_mc if (k!='data' and k!='fakes') else preselection
        samples[k] = samples[k].Filter(filter)
        if k == 'fakes':
            hbx_filter = '!(abs(k_genpdgId)==13)'
            samples[k] = samples[k].Filter(hbx_filter)

    # better for categorical data
    # colours = list(map(ROOT.TColor.GetColor, all_palettes['Category10'][len(samples)]))
    colours = list(map(ROOT.TColor.GetColor, all_palettes['Spectral'][len(samples)-1]))

    # print ('user defined variables')
    # print ('='*80)
    # for i in samples['jpsi_mu'].GetDefinedColumnNames(): print(i)
    # print ('%'*80)

    # CREATE THE SMART POINTERS IN ONE GO AND PRODUCE RESULTS IN ONE SHOT,
    # SEE MAX GALLI PRESENTATION
    # https://github.com/maxgalli/dask-pyroot-tutorial/blob/master/2_rdf_basics.ipynb
    # https://indico.cern.ch/event/882824/contributions/3929999/attachments/2073718/3481850/PyROOT_PyHEP_2020.pdf

    # first create all the pointers
    print('====> creating pointers to histo')
    temp_hists      = {} # pass muon ID category
    temp_hists_fake = {} # fail muon ID category
    for k, v in histos.items():    
        temp_hists     [k] = {}
        temp_hists_fake[k] = {}
        for kk, vv in samples.items():
            #            try:
            temp_hists     [k]['%s_%s' %(k, kk)] = vv.Filter(pass_id).Histo1D(v[0], k, 'total_weight')
            temp_hists_fake[k]['%s_%s' %(k, kk)] = vv.Filter(fail_id).Histo1D(v[0], k, 'total_weight')
            #except:
            #    print("NO")
            #    pass
    
    #     import pdb ; pdb.set_trace()
    
    print('====> now looping')
    # loop on the histos
    for k, v in histos.items():
    
        c1.cd()
        leg = create_legend(temp_hists, sample_names, titles)

        main_pad.cd()
        main_pad.SetLogy(False)

        maxima = []
        data_max = 0.
        for i, kv in enumerate(temp_hists[k].items()):
            key = kv[0]
            ihist = kv[1]
            ihist.GetXaxis().SetTitle(v[1])
            ihist.GetYaxis().SetTitle('events')
            #         ihist.Scale(1./ihist.Integral())
            if(key == '%s_fakes'%k):
                ihist.SetLineColor(ROOT.kRed-4)
                ihist.SetFillColor(ROOT.kRed-4)
            else:
                ihist.SetLineColor(colours[i] if key!='%s_data'%k else ROOT.kBlack)
                ihist.SetFillColor(colours[i] if key!='%s_data'%k else ROOT.kWhite)
            if key!='%s_data'%k:
                maxima.append(ihist.GetMaximum())
            else:
                data_max = ihist.GetMaximum()
    
        ths1      = ROOT.THStack('stack', '')
        ths1_fake = ROOT.THStack('stack_fake', '')

        for i, kv in enumerate(temp_hists[k].items()):
            key = kv[0]
            if key=='%s_data'%k: continue
            ihist = kv[1]
            #if key == '%s_jpsi_mu'%k:ihist.Scale(48717.9/ihist.Integral())
            ihist.SetMaximum(2.*max(maxima))
            # ihist.SetMinimum(0.)
            ihist.Draw('hist' + 'same'*(i>0))
            #if key == '%s_fakes'%k:print(ihist.Integral())
            ths1.Add(ihist.GetValue())

        # apply same aestethics to pass and fail
        for kk in temp_hists[k].keys():
            temp_hists_fake[k][kk].GetXaxis().SetTitle(temp_hists[k][kk].GetXaxis().GetTitle())
            temp_hists_fake[k][kk].GetYaxis().SetTitle(temp_hists[k][kk].GetYaxis().GetTitle())
            temp_hists_fake[k][kk].SetLineColor(temp_hists[k][kk].GetLineColor())
            temp_hists_fake[k][kk].SetFillColor(temp_hists[k][kk].GetFillColor())
        print(k)
        '''
        print(temp_hists_fake[k]['%s_data' %k].Integral())
        temp_hists[k]['%s_fakes' %k] = temp_hists_fake[k]['%s_data' %k].Clone()
        fakes = temp_hists[k]['%s_fakes' %k]
        for i, kv in enumerate(temp_hists_fake[k].items()):
            if 'data' in kv[0]:
                kv[1].SetLineColor(ROOT.kBlack)
                continue
            else:
                fakes.Add(kv[1].GetPtr(), -1.)
                for j in range(fakes.GetNbinsX()):
                    if(fakes.GetBinContent(j) < 0):
                        fakes.SetBinContent(j,0.0001)  
        fakes.SetFillColor(ROOT.kRed)
        fakes.SetFillStyle(1001)
        fakes.SetLineColor(ROOT.kRed)
        fakes_forfail = fakes.Clone()
        fakes.Scale(weights['fakes'])
        ths1.Add(fakes)
        '''
        ths1.Draw('hist')
        try:
            ths1.GetXaxis().SetTitle(v[1])
        except:
            continue
        ths1.GetYaxis().SetTitle('events')
        ths1.SetMaximum(1.6*max(sum(maxima), data_max))
        print(1.6*max(sum(maxima), data_max))
        ths1.SetMinimum(0.)
        
        # statistical uncertainty
        stats = ths1.GetStack().Last().Clone()
        stats.SetLineColor(0)
        stats.SetFillColor(ROOT.kGray+1)
        stats.SetFillStyle(3344)
        stats.SetMarkerSize(0)
        stats.Draw('E2 SAME')
        #leg.AddEntry(fakes, 'fakes', 'F')    
        leg.AddEntry(stats, 'stat. unc.', 'F')
        leg.Draw('same')
    
        temp_hists[k]['%s_data'%k].Draw('EP SAME')
        
        CMS_lumi(main_pad, 4, 0, cmsText = 'CMS', extraText = ' Preliminary', lumi_13TeV = '')

        main_pad.cd()
        #print(temp_hists[k]['%s_jpsi_tau'%k].Integral())
        rjpsi_value = ROOT.TPaveText(0.7, 0.65, 0.88, 0.72, 'nbNDC')
        rjpsi_value.AddText('R(J/#Psi) = %.2f' %rjpsi)
        rjpsi_value.SetFillColor(0)
        rjpsi_value.Draw('EP')        
        #HERE comment rjpsi value
        #rjpsi_value = ROOT.TPaveText(0.7, 0.65, 0.88, 0.72, 'nbNDC')
        #rjpsi_value.AddText('R(J/#Psi) = %.2f' %(weights['jpsi_tau']/weights['jpsi_mu']))
        #rjpsi_value.SetFillColor(0)
        #rjpsi_value.Draw('EP')

        ratio_pad.cd()
        ratio = temp_hists[k]['%s_data'%k].Clone()
        ratio.SetName(ratio.GetName()+'_ratio')
        ratio.Divide(stats)
        ratio_stats = stats.Clone()
        ratio_stats.SetName(ratio.GetName()+'_ratiostats')
        ratio_stats.Divide(stats)
        ratio_stats.SetMaximum(1.999) # avoid displaying 2, that overlaps with 0 in the main_pad
        ratio_stats.SetMinimum(0.001) # and this is for symmetry
        ratio_stats.GetYaxis().SetTitle('obs/exp')
        ratio_stats.GetYaxis().SetTitleOffset(0.5)
        ratio_stats.GetYaxis().SetNdivisions(405)
        ratio_stats.GetXaxis().SetLabelSize(3.* ratio.GetXaxis().GetLabelSize())
        ratio_stats.GetYaxis().SetLabelSize(3.* ratio.GetYaxis().GetLabelSize())
        ratio_stats.GetXaxis().SetTitleSize(3.* ratio.GetXaxis().GetTitleSize())
        ratio_stats.GetYaxis().SetTitleSize(3.* ratio.GetYaxis().GetTitleSize())

        norm_stack = ROOT.THStack('norm_stack', '')
#         import pdb ; pdb.set_trace()
        for kk, vv in temp_hists[k].items():
            if 'data' in kk: continue
            hh = vv.Clone()
            hh.Divide(stats)
            norm_stack.Add(hh)
        norm_stack.Draw('hist same')


        line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1., ratio.GetXaxis().GetXmax(), 1.)
        line.SetLineColor(ROOT.kBlack)
        line.SetLineWidth(1)
        ratio_stats.Draw('E2')
        norm_stack.Draw('hist same')
        ratio_stats.Draw('E2 same')
        line.Draw('same')
        ratio.Draw('EP same')
    
        c1.Modified()
        c1.Update()
        c1.SaveAs('plots_ul/%s/pdf/lin/%s.pdf' %(label, k))
        c1.SaveAs('plots_ul/%s/png/lin/%s.png' %(label, k))
    
        ths1.SetMaximum(20*max(sum(maxima), data_max))
        ths1.SetMinimum(10)
        main_pad.SetLogy(True)

        
        c1.Modified()

        c1.Update()
        c1.SaveAs('plots_ul/%s/pdf/log/%s.pdf' %(label, k))
        c1.SaveAs('plots_ul/%s/png/log/%s.png' %(label, k))
        
        #print("pass region")
        #print(temp_hists[k])
        if k in datacards:
            create_datacard_prep(temp_hists[k],'pass',k,label)

        ##########################################################################################
        
        c1.cd()
        main_pad.cd()
        main_pad.SetLogy(False)


        for i, kv in enumerate(temp_hists_fake[k].items()):
            key = kv[0]
            if key=='%s_data'%k: 
                max_fake = kv[1].GetMaximum()
                continue
            ihist = kv[1]
            # ihist.SetMaximum(2.*max(maxima))
            # ihist.SetMinimum(0.)
            # ihist.Draw('hist' + 'same'*(i>0))
            ths1_fake.Add(ihist.GetValue())
        #        print(type(temp_hists_fake[k]['%s_data' %k]))
        #temp_hists_fake[k]['%s_fakes' %k] = fakes_forfail
        #print("fakes!",temp_hists_fake[k]['%s_fakes' %k])
        #ths1_fake.Add(fakes_forfail)
        ths1_fake.Draw('hist')
        ths1_fake.SetMaximum(1.6*max_fake)

#         try:
#             ths1_fake.GetXaxis().SetTitle(v[1])
#         except:
#             continue
        ths1_fake.GetYaxis().SetTitle('events')
#         ths1_fake.SetMaximum(1.5*max(sum(maxima), data_max))
#         ths1_fake.SetMinimum(0.)
        
        # statistical uncertainty
#         stats = ths1_fake.GetStack().Last().Clone()
#         stats.SetLineColor(0)
#         stats.SetFillColor(ROOT.kGray+1)
#         stats.SetFillStyle(3344)
#         stats.SetMarkerSize(0)
#         stats.Draw('E2 SAME')
    
        temp_hists_fake[k]['%s_data'%k].Draw('EP SAME')
        CMS_lumi(main_pad, 4, 0, cmsText = 'CMS', extraText = ' Preliminary', lumi_13TeV = '')
        leg.Draw('same')

#         import pdb ; pdb.set_trace()
        c1.Modified()
        c1.Update()
        c1.SaveAs('plots_ul/%s/fail_region/pdf/lin/%s.pdf' %(label, k))
        c1.SaveAs('plots_ul/%s/fail_region/png/lin/%s.png' %(label, k))
    
        ths1_fake.SetMaximum(20*max(sum(maxima), data_max))
        ths1_fake.SetMinimum(10)
        main_pad.SetLogy(True)
        c1.Modified()
        c1.Update()
        c1.SaveAs('plots_ul/%s/fail_region/pdf/log/%s.pdf' %(label, k))
        c1.SaveAs('plots_ul/%s/fail_region/png/log/%s.png' %(label, k))

        #        if k in datacards:
        #    create_datacard_prep(temp_hists_fake[k],'fail',k,label)
  


    save_yields(label, temp_hists)
    save_selection(label, preselection)

print("--- %s seconds ---" % (time.time() - start_time))
# save reduced trees to produce datacards
# columns = ROOT.std.vector('string')()
# for ic in ['Q_sq', 'm_miss_sq', 'E_mu_star', 'E_mu_canc', 'Bmass']:
#     columns.push_back(ic)
# for k, v in samples.items():
#     v.Snapshot('tree', 'plots_ul/%s/tree_%s_datacard.root' %(label, k), columns)
