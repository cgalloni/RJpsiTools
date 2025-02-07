import FWCore.ParameterSet.Config as cms

from GeneratorInterface.EvtGenInterface.EvtGenSetting_cff import *
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8GeneratorFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    pythiaHepMCVerbosity = cms.untracked.bool(True),
    comEnergy = cms.double(13000.0),

    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'SoftQCD:nonDiffractive = on',
            'PTFilter:filter = on', # this turn on the filter
            'PTFilter:quarkToFilter = 5', # PDG id of q quark
            'PTFilter:scaleToFilter = 2.0', 
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            'processParameters',
        ),
    ),

    ExternalDecays = cms.PSet(
        EvtGen130 = cms.untracked.PSet(
            decay_table = cms.string('GeneratorInterface/EvtGenInterface/data/DECAY_2014_NOLONGLIFE.DEC'),
            particle_property_file = cms.FileInPath('GeneratorInterface/EvtGenInterface/data/evt_2014.pdl'),
            user_decay_embedded = cms.vstring(
'''
Alias      MyJ/psi          J/psi
Alias      Mypsi(2S)        psi(2S)
Alias      Mypsi(3770)      psi(3770)
Alias      Mychi_c0         chi_c0
Alias      Mychi_c1         chi_c1
Alias      Mychi_c2         chi_c2
Alias      Myh_c            h_c
Alias      MyB+             B+
Alias      MyB-             B-
Alias      Myanti-B0        anti-B0
Alias      MyB0             B0
Alias      Myanti-Bs        anti-B_s0
Alias      MyBs             B_s0
Alias      MyBc+            B_c+
Alias      MyBc-            B_c-
Alias      MyB*+            B*+
Alias      MyB*-            B*-
Alias      MyB*0            B*0
Alias      Myanti-B*0       anti-B*0
Alias      MyBs*            B_s*0
Alias      Myanti-Bs*       anti-B_s*0
Alias      MyLambda_b0      Lambda_b0
Alias      MyXi_b-          Xi_b-
Alias      Myanti-Xi_b+     anti-Xi_b+
Alias      MyXi_b0          Xi_b0
Alias      Myanti-Xi_b0     anti-Xi_b0
Alias      MyOmega_b-       Omega_b-
Alias      Myanti-Omega_b+  anti-Omega_b+
ChargeConj MyB-             MyB+
ChargeConj Myanti-B0        MyB0
ChargeConj Myanti-Bs        MyBs
ChargeConj MyBc-            MyBc+
ChargeConj MyB*-            MyB*+
ChargeConj MyB*0            Myanti-B*0
ChargeConj MyBs*            Myanti-Bs*
ChargeConj MyXi_b-          Myanti-Xi_b+
ChargeConj MyXi_b0          Myanti-Xi_b0
ChargeConj MyOmega_b-       Myanti-Omega_b+


Decay MyJ/psi  # original total forced BR = 0.05930000
1.00000000 mu+ mu- PHOTOS  VLL;
Enddecay


Decay Mychi_c0  # original total forced BR = 0.01160000
1.00000000 gamma MyJ/psi PHSP;
Enddecay


Decay Mychi_c1  # original total forced BR = 0.34400000
1.00000000 MyJ/psi gamma VVP 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0;
Enddecay


Decay Mychi_c2  # original total forced BR = 0.19500000
1.00000000 gamma MyJ/psi PHSP;
Enddecay


Decay Mypsi(2S)  # original total forced BR = 0.82380000
0.56261153 MyJ/psi pi+ pi- VVPIPI;
0.29687805 MyJ/psi pi0 pi0 VVPIPI;
0.05492160 MyJ/psi eta PARTWAVE 0.0 0.0 1.0 0.0 0.0 0.0;
0.00217677 MyJ/psi pi0 PARTWAVE 0.0 0.0 1.0 0.0 0.0 0.0;
0.00186854 gamma Mychi_c0 PHSP;
0.05299265 gamma Mychi_c1 PHSP;
0.02853747 gamma Mychi_c2 PHSP;
0.00001340 Myh_c gamma PHSP;
Enddecay


Decay Mypsi(3770)  # original total forced BR = 0.00363000
0.53168044 MyJ/psi pi+ pi- PHSP;
0.22038567 MyJ/psi pi0 pi0 PHSP;
0.24793388 MyJ/psi eta PHSP;
Enddecay


Decay Myh_c  # original total forced BR = 0.01000000
1.00000000 MyJ/psi pi0 PHSP;
Enddecay


Decay MyB+  # original total forced BR = 0.01756960
0.09774322 MyJ/psi K+ SVS;
0.13784300 MyJ/psi K*+ SVV_HELAMP PKHplus PKphHplus PKHzero PKphHzero PKHminus PKphHminus;
0.00472329 MyJ/psi pi+ SVS;
0.00481969 MyJ/psi rho+ SVV_HELAMP PKHplus PKphHplus PKHzero PKphHzero PKHminus PKphHminus;
0.01927874 MyJ/psi K0 pi+ PHSP;
0.00963937 MyJ/psi K+ pi0 PHSP;
0.00963937 MyJ/psi K'_1+ SVV_HELAMP 0.5 0.0 1.0 0.0 0.5 0.0;
0.04819685 MyJ/psi K_2*+ PHSP;
0.17350868 MyJ/psi K_1+ SVV_HELAMP 0.5 0.0 1.0 0.0 0.5 0.0;
0.00501247 MyJ/psi phi K+ PHSP;
0.10314127 MyJ/psi K+ pi+ pi- PHSP;
0.01041052 MyJ/psi eta K+ PHSP;
0.03373780 MyJ/psi omega K+ PHSP;
0.00113745 MyJ/psi p+ anti-Lambda0 PHSP;
0.03718877 Mypsi(2S) K+ SVS;
0.03569201 Mypsi(2S) K*+ SVV_HELAMP PKHplus PKphHplus PKHzero PKphHzero PKHminus PKphHminus;
0.02302710 Mypsi(2S) K0 pi+ PHSP;
0.01151355 Mypsi(2S) K+ pi0 PHSP;
0.10937875 Mypsi(2S) K+ pi- pi+ PHSP;
0.00575678 Mypsi(2S) K+ pi0 pi0 PHSP;
0.00575678 Mypsi(2S) K0 pi+ pi0 PHSP;
0.02302710 Mypsi(2S) K_1+ PHSP;
0.00148525 Mypsi(2S) pi+ PHSP;
0.00017146 Mypsi(3770) K+ SVS;
0.00017495 Mypsi(3770) K*+ PHSP;
0.00010497 Mypsi(3770) K0 pi+ PHSP;
0.00006998 Mypsi(3770) K+ pi0 PHSP;
0.00006998 Mypsi(3770) K+ pi- pi+ PHSP;
0.00003499 Mypsi(3770) K+ pi0 pi0 PHSP;
0.00003499 Mypsi(3770) K0 pi+ pi0 PHSP;
0.00010497 Mypsi(3770) K_1+ PHSP;
0.00014872 Mychi_c0 K+ PHSP;
0.00044727 K*+ Mychi_c0 SVS;
0.00022363 Mychi_c0 K0 pi+ PHSP;
0.00011182 Mychi_c0 K+ pi0 PHSP;
0.00022363 Mychi_c0 K+ pi- pi+ PHSP;
0.00011182 Mychi_c0 K+ pi0 pi0 PHSP;
0.00011182 Mychi_c0 K0 pi+ pi0 PHSP;
0.01525334 Mychi_c1 K+ SVS;
0.00994783 Mychi_c1 K*+ SVV_HELAMP PKHplus PKphHplus PKHzero PKphHzero PKHminus PKphHminus;
0.01326377 Mychi_c1 K0 pi+ PHSP;
0.00663189 Mychi_c1 K+ pi0 PHSP;
0.01326377 Mychi_c1 K+ pi- pi+ PHSP;
0.00663189 Mychi_c1 K+ pi0 pi0 PHSP;
0.00663189 Mychi_c1 K0 pi+ pi0 PHSP;
0.00066319 Mychi_c1 pi+ PHSP;
0.00037594 Mychi_c2 K+ STS;
0.00037594 Mychi_c2 K*+ PHSP;
0.00375935 Mychi_c2 K0 pi+ PHSP;
0.00187968 Mychi_c2 K+ pi0 PHSP;
0.00375935 Mychi_c2 K+ pi- pi+ PHSP;
0.00187968 Mychi_c2 K+ pi0 pi0 PHSP;
0.00187968 Mychi_c2 K0 pi+ pi0 PHSP;
Enddecay
CDecay MyB-


Decay Myanti-B0  # original total forced BR = 0.01778030
0.07883916 MyJ/psi anti-K0 PHSP;
0.02805986 MyJ/psi omega anti-K0 PHSP;
0.00085990 MyJ/psi eta PHSP;
0.00171980 MyJ/psi pi- pi+ PHSP;
0.04163721 MyJ/psi anti-K0 pi- pi+ PHSP;
0.04887847 MyJ/psi anti-K0 rho0 PHSP;
0.07241254 MyJ/psi K*- pi+ PHSP;
0.05974035 MyJ/psi anti-K*0 pi- pi+ PHSP;
0.03941958 MyJ/psi K_S0 SVS;
0.03941958 MyJ/psi K_L0 SVS;
0.12038585 MyJ/psi anti-K*0 SVV_HELAMP PKHminus PKphHminus PKHzero PKphHzero PKHplus PKphHplus;
0.00159308 MyJ/psi pi0 SVS;
0.00244392 MyJ/psi rho0 SVV_HELAMP PKHminus PKphHminus PKHzero PKphHzero PKHplus PKphHplus;
0.00271547 MyJ/psi omega SVV_HELAMP PKHminus PKphHminus PKHzero PKphHzero PKHplus PKphHplus;
0.00000000 MyJ/psi K- pi+ PHSP;
0.00905157 MyJ/psi anti-K0 pi0 PHSP;
0.11767038 MyJ/psi anti-K_10 SVV_HELAMP 0.5 0.0 1.0 0.0 0.5 0.0;
0.00905157 MyJ/psi anti-K'_10 SVV_HELAMP 0.5 0.0 1.0 0.0 0.5 0.0;
0.04525784 MyJ/psi anti-K_2*0 PHSP;
0.00850847 MyJ/psi phi anti-K0 PHSP;
0.03351554 Mypsi(2S) anti-K0 PHSP;
0.01675777 Mypsi(2S) K_S0 SVS;
0.01675777 Mypsi(2S) K_L0 SVS;
0.03297496 Mypsi(2S) anti-K*0 SVV_HELAMP PKHminus PKphHminus PKHzero PKphHzero PKHplus PKphHplus;
0.02162293 Mypsi(2S) K- pi+ PHSP;
0.01081146 Mypsi(2S) anti-K0 pi0 PHSP;
0.01081146 Mypsi(2S) anti-K0 pi+ pi- PHSP;
0.00540573 Mypsi(2S) anti-K0 pi0 pi0 PHSP;
0.00540573 Mypsi(2S) K- pi+ pi0 PHSP;
0.02162293 Mypsi(2S) anti-K_10 PHSP;
0.00007886 Mypsi(3770) K_S0 SVS;
0.00007886 Mypsi(3770) K_L0 SVS;
0.00015771 Mypsi(3770) anti-K*0 SVV_HELAMP PKHplus PKphHplus PKHzero PKphHzero PKHminus PKphHminus;
0.00004600 Mypsi(3770) K- pi+ PHSP;
0.00004600 Mypsi(3770) anti-K0 pi0 PHSP;
0.00004600 Mypsi(3770) anti-K0 pi+ pi- PHSP;
0.00002300 Mypsi(3770) anti-K0 pi0 pi0 PHSP;
0.00002300 Mypsi(3770) K- pi+ pi0 PHSP;
0.00009529 Mypsi(3770) anti-K_10 PHSP;
0.00007350 Mychi_c0 K_S0 PHSP;
0.00007350 Mychi_c0 K_L0 PHSP;
0.00031499 anti-K*0 Mychi_c0 SVS;
0.00021000 Mychi_c0 K- pi+ PHSP;
0.00010500 Mychi_c0 anti-K0 pi0 PHSP;
0.00021000 Mychi_c0 anti-K0 pi+ pi- PHSP;
0.00010500 Mychi_c0 anti-K0 pi0 pi0 PHSP;
0.00010500 Mychi_c0 K- pi+ pi0 PHSP;
0.00014700 Mychi_c0 anti-K0 PHSP;
0.00607179 Mychi_c1 K_S0 SVS;
0.00607179 Mychi_c1 K_L0 SVS;
0.00691250 Mychi_c1 anti-K*0 SVV_HELAMP PKHminus PKphHminus PKHzero PKphHzero PKHplus PKphHplus;
0.01245496 Mychi_c1 K- pi+ PHSP;
0.00622748 Mychi_c1 anti-K0 pi0 PHSP;
0.01245496 Mychi_c1 anti-K0 pi+ pi- PHSP;
0.00622748 Mychi_c1 anti-K0 pi0 pi0 PHSP;
0.00622748 Mychi_c1 K- pi+ pi0 PHSP;
0.00034874 Mychi_c1 pi0 PHSP;
0.01214358 Mychi_c1 anti-K0 PHSP;
0.00491971 Mychi_c1 K+ pi- PHSP;
0.00088253 Mychi_c2 K_S0 STS;
0.00088253 Mychi_c2 K_L0 STS;
0.00052952 Mychi_c2 anti-K*0 PHSP;
0.00353011 Mychi_c2 K- pi+ PHSP;
0.00176506 Mychi_c2 anti-K0 pi0 PHSP;
0.00353011 Mychi_c2 anti-K0 pi+ pi- PHSP;
0.00176506 Mychi_c2 anti-K0 pi0 pi0 PHSP;
0.00176506 Mychi_c2 K- pi+ pi0 PHSP;
Enddecay
CDecay MyB0


Decay MyBs  # original total forced BR = 0.02298000
0.04783498 MyJ/psi eta' SVS;
0.02391749 MyJ/psi eta SVS;
0.09716481 MyJ/psi phi SVV_HELAMP  1.0 0.0 1.0 0.0 1.0 0.0;
0.00597937 MyJ/psi K0 SVS;
0.05231951 MyJ/psi K- K+ PHSP;
0.05231951 MyJ/psi anti-K0 K0 PHSP;
0.05231951 MyJ/psi K0 K- pi+ PHSP;
0.05231951 MyJ/psi anti-K0 K0 pi0 PHSP;
0.05231951 MyJ/psi K- K+ pi0 PHSP;
0.02914944 MyJ/psi phi pi+ pi- PHSP;
0.02914944 MyJ/psi phi pi0 pi0 PHSP;
0.01494843 MyJ/psi eta pi+ pi- PHSP;
0.01494843 MyJ/psi eta pi0 pi0 PHSP;
0.02989687 MyJ/psi eta' pi+ pi- PHSP;
0.02989687 MyJ/psi eta' pi0 pi0 PHSP;
0.01494843 MyJ/psi pi+ pi- PHSP;
0.01494843 MyJ/psi pi0 pi0 PHSP;
0.02075627 Mypsi(2S) eta' SVS;
0.01048973 Mypsi(2S) eta SVS;
0.03035325 Mypsi(2S) phi SVV_HELAMP  1.0 0.0 1.0 0.0 1.0 0.0;
0.01339114 Mypsi(2S) K- K+ PHSP;
0.01339114 Mypsi(2S) anti-K0 K0 PHSP;
0.01339114 Mypsi(2S) K0 K- pi+ PHSP;
0.01339114 Mypsi(2S) anti-K0 K0 pi0 PHSP;
0.01339114 Mypsi(2S) K- K+ pi0 PHSP;
0.01517663 Mypsi(2S) phi pi+ pi- PHSP;
0.01517663 Mypsi(2S) phi pi0 pi0 PHSP;
0.00892743 Mypsi(2S) eta pi+ pi- PHSP;
0.00892743 Mypsi(2S) eta pi0 pi0 PHSP;
0.01785485 Mypsi(2S) eta' pi+ pi- PHSP;
0.01785485 Mypsi(2S) eta' pi0 pi0 PHSP;
0.00892743 Mypsi(2S) pi+ pi- PHSP;
0.00892743 Mypsi(2S) pi0 pi0 PHSP;
0.00008670 Mychi_c0 eta' PHSP;
0.00004335 Mychi_c0 eta PHSP;
0.00017340 phi Mychi_c0 SVS;
0.00002601 Mychi_c0 K- K+ PHSP;
0.00002601 Mychi_c0 anti-K0 K0 PHSP;
0.00002601 Mychi_c0 K0 K- pi+ PHSP;
0.00002601 Mychi_c0 anti-K0 K0 pi0 PHSP;
0.00002601 Mychi_c0 K- K+ pi0 PHSP;
0.01799791 Mychi_c1 eta' SVS;
0.00771339 Mychi_c1 eta SVS;
0.03599583 Mychi_c1 phi SVV_HELAMP  1.0 0.0 1.0 0.0 1.0 0.0;
0.00668494 Mychi_c1 K- K+ PHSP;
0.00668494 Mychi_c1 anti-K0 K0 PHSP;
0.00668494 Mychi_c1 K0 K- pi+ PHSP;
0.00668494 Mychi_c1 anti-K0 K0 pi0 PHSP;
0.00668494 Mychi_c1 K- K+ pi0 PHSP;
0.01028452 Mychi_c1 phi pi+ pi- PHSP;
0.01028452 Mychi_c1 phi pi0 pi0 PHSP;
0.00257113 Mychi_c1 eta pi+ pi- PHSP;
0.00257113 Mychi_c1 eta pi0 pi0 PHSP;
0.00514226 Mychi_c1 eta' pi+ pi- PHSP;
0.00514226 Mychi_c1 eta' pi0 pi0 PHSP;
0.00677725 Mychi_c2 eta' STS;
0.00342506 Mychi_c2 eta STS;
0.00233196 Mychi_c2 K- K+ PHSP;
0.00233196 Mychi_c2 anti-K0 K0 PHSP;
0.00233196 Mychi_c2 K0 K- pi+ PHSP;
0.00233196 Mychi_c2 anti-K0 K0 pi0 PHSP;
0.00233196 Mychi_c2 K- K+ pi0 PHSP;
0.00034755 Myh_c eta' SVS;
0.00017564 Myh_c eta SVS;
0.00074742 Myh_c phi SVV_HELAMP  1.0 0.0 1.0 0.0 1.0 0.0;
0.00011959 Myh_c K- K+ PHSP;
0.00011959 Myh_c anti-K0 K0 PHSP;
0.00011959 Myh_c K0 K- pi+ PHSP;
0.00011959 Myh_c anti-K0 K0 pi0 PHSP;
0.00011959 Myh_c K- K+ pi0 PHSP;
Enddecay
CDecay Myanti-Bs


Decay MyBc+  # original total forced BR = 0.91097820
0.00232078 MyJ/psi mu+ nu_mu PHOTOS BC_VMN 1;
0.00006857 Mypsi(2S) mu+ nu_mu PHOTOS BC_VMN 1;
0.00000292 Mychi_c0 mu+ nu_mu PHOTOS BC_SMN 3;
0.00008646 Mychi_c1 mu+ nu_mu PHOTOS BC_VMN 3;
0.00004901 Mychi_c2 mu+ nu_mu PHOTOS BC_TMN 3;
0.00000357 Myh_c mu+ nu_mu PHOTOS PHSP;
0.00006586 MyBs mu+ nu_mu PHOTOS PHSP;
0.10422587 MyBs* mu+ nu_mu PHOTOS PHSP;
0.00700332 MyB0 mu+ nu_mu PHOTOS PHSP;
0.01194684 MyB*0 mu+ nu_mu PHOTOS PHSP;
0.00232078 MyJ/psi e+ nu_e PHOTOS BC_VMN 1;
0.00006857 Mypsi(2S) e+ nu_e PHOTOS BC_VMN 1;
0.00000292 Mychi_c0 e+ nu_e PHOTOS BC_SMN 3;
0.00008646 Mychi_c1 e+ nu_e PHOTOS BC_VMN 3;
0.00004901 Mychi_c2 e+ nu_e PHOTOS BC_TMN 3;
0.00000357 Myh_c e+ nu_e PHOTOS PHSP;
0.00006586 MyBs e+ nu_e PHOTOS PHSP;
0.10422587 MyBs* e+ nu_e PHOTOS PHSP;
0.00700332 MyB0 e+ nu_e PHOTOS PHSP;
0.01194684 MyB*0 e+ nu_e PHOTOS PHSP;
0.00058630 MyJ/psi tau+ nu_tau PHOTOS BC_VMN 1;
0.00000584 Mypsi(2S) tau+ nu_tau PHOTOS BC_VMN 1;
0.00015879 MyJ/psi pi+ SVS;
0.00048858 MyJ/psi rho+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00001344 MyJ/psi K+ SVS;
0.00002687 MyJ/psi K*+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00020765 MyJ/psi D_s+ SVS;
0.00081838 MyJ/psi D_s*+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00001099 MyJ/psi D+ SVS;
0.00003420 MyJ/psi D*+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00026801 MyBs pi+ PHSP;
0.00011766 rho+ MyBs SVS;
0.00001732 MyBs K+ PHSP;
0.00000000 K*+ MyBs SVS;
0.13388699 MyBs* pi+ SVS;
0.41607956 MyBs* rho+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00762126 MyBs* K+ SVS;
0.00000000 MyBs* K*+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.02183388 MyB0 pi+ PHSP;
0.01977408 rho+ MyB0 SVS;
0.00144186 MyB0 K+ PHSP;
0.00030897 K*+ MyB0 SVS;
0.01956810 MyB*0 pi+ SVS;
0.05293685 MyB*0 rho+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00113289 MyB*0 K+ SVS;
0.00119468 MyB*0 K*+ SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.00000047 MyB+ pi0 PHSP;
0.00000043 rho0 MyB+ SVS;
0.00002509 MyB+ anti-K0 PHSP;
0.00000545 K*0 MyB+ SVS;
0.00067973 MyB*+ pi0 SVS;
0.00185382 MyB*+ rho0 SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
0.03295680 MyB*+ anti-K0 SVS;
0.03439866 MyB*+ K*0 SVV_HELAMP 1.0 0.0 1.0 0.0 1.0 0.0;
Enddecay
CDecay MyBc-


Decay MyB*+  # original total forced BR = 1.00000000
1.00000000 MyB+ gamma VSP_PWAVE;
Enddecay
CDecay MyB*-


Decay MyB*0  # original total forced BR = 1.00000000
1.00000000 MyB0 gamma VSP_PWAVE;
Enddecay
CDecay Myanti-B*0


Decay MyBs*  # original total forced BR = 1.00000000
1.00000000 MyBs gamma VSP_PWAVE;
Enddecay
CDecay Myanti-Bs*


Decay MyLambda_b0  # original total forced BR = 0.00085000
0.67437494 Lambda0 MyJ/psi PHSP;
0.32562506 Lambda0 Mypsi(2S) PHSP;
Enddecay


Decay MyXi_b-  # original total forced BR = 0.00085000
0.67437494 Xi- MyJ/psi PHSP;
0.32562506 Xi- Mypsi(2S) PHSP;
Enddecay
CDecay Myanti-Xi_b+


Decay MyXi_b0  # original total forced BR = 0.00047000
1.00000000 Xi0 MyJ/psi PHSP;
Enddecay
CDecay Myanti-Xi_b0


Decay MyOmega_b-  # original total forced BR = 0.00085000
0.67437494 Omega- MyJ/psi PHSP;
0.32562506 Omega- Mypsi(2S) PHSP;
Enddecay
CDecay Myanti-Omega_b+

End
'''            
            ),
            list_forced_decays     = cms.vstring(
                'MyB+', #521
                'MyB-',
                'MyBc+', #541
                'MyBc-', 
                'Myanti-B0', #511
                'MyB0',
                'Myanti-Bs', #531
                'MyBs',
                'MyLambda_b0', #5122
                'MyXi_b-',     #20553 (xi_b1 ?)
                'Myanti-Xi_b+',
                'MyXi_b0',     #10551
                'Myanti-Xi_b0',
                'MyOmega_b-',  #5332
                'Myanti-Omega_b+',
            ),        
            operates_on_particles = cms.vint32(521,541,511,531,5122,10551,20553,5332),    
            convertPythiaCodes = cms.untracked.bool(False),
        ),
        parameterSets = cms.vstring('EvtGen130'),
    ),

)

generator.PythiaParameters.processParameters.extend(EvtGenExtraParticles)

jpsi_from_b_hadron_filter = cms.EDFilter(
    "PythiaFilterMultiAncestor",
    ParticleID      = cms.untracked.int32 (443),
    MinPt           = cms.untracked.double(0.),
    MinEta          = cms.untracked.double(-100.),
    MaxEta          = cms.untracked.double( 100.),
    MotherIDs       = cms.untracked.vint32([5]),
    DaughterIDs     = cms.untracked.vint32([-13, 13]),
    DaughterMinPts  = cms.untracked.vdouble([ 3.2 , 3.2  ]), 
    DaughterMaxPts  = cms.untracked.vdouble([ 1.e6,  1.e6]),
    DaughterMinEtas = cms.untracked.vdouble([-2.52 , -2.52 ]),
    DaughterMaxEtas = cms.untracked.vdouble([ 2.52 ,  2.52 ]),
)

three_mu_filter = cms.EDFilter(
    "MCMultiParticleFilter",
    NumRequired = cms.int32(3),
    AcceptMore  = cms.bool(True),
    ParticleID  = cms.vint32(13,13,13),
    PtMin       = cms.vdouble(3.2, 3.2, 3.2),
    EtaMax      = cms.vdouble(2.52, 2.52, 2.52),
    Status      = cms.vint32(1, 1, 1),
)


# two OS muons make the Jpsi, so, if  there's an additional muon around
# it must have the same charge as that of to one of the Jpsi muons.
# In addition, the invariant mass of these two can't be too large 
mu_mu_same_charge_filter = cms.EDFilter(
    "MCParticlePairFilter",
    ParticleID1    = cms.untracked.vint32(13), # mu
    ParticleID2    = cms.untracked.vint32(13), # mu
    ParticleCharge = cms.untracked.int32(1), # same charge
    MaxInvMass     = cms.untracked.double(10.),
    MinPt          = cms.untracked.vdouble(3.2, 3.2), 
    MinEta         = cms.untracked.vdouble(-2.52, -2.52),
    MaxEta         = cms.untracked.vdouble( 2.52,  2.52),
    Status         = cms.untracked.vint32(1, 1),
)

configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('\$Revision$'),
    name = cms.untracked.string('\$Source$'),
    annotation = cms.untracked.string(
        'QCD bbbar production, '\
        'Jpsi from any b-hadron (either directly or feeddown), '\
        'Jpsi->mumu, mu pt>3.2, mu |eta|<2.52, '\
        'additional mu with pt>3.2 and |eta|<2.52, '\
        'invariant mass(Jpsi, mu)<10, '\
        '13 TeV, '\
        'TuneCP5'
    )
)

ProductionFilterSequence = cms.Sequence(generator*jpsi_from_b_hadron_filter*three_mu_filter*mu_mu_same_charge_filter)
