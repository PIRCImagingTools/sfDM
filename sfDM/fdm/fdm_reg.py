'''
Created on Mar 11, 2013

@author: rafa
'''
import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import os,sys
import json
import sfDM.fdm.afni_ext as afni_ext
from nipype import config


fsl.FSLCommand.set_default_output_type('NIFTI')


def determine_path():
    """
    determines the local path of the module on the OS
    """
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        print "No __file__ variable"
        print "Problem with installation?"
        sys.exit()

local_path = determine_path()
fnirt_config = os.path.abspath(local_path+'/../res/fdm_FNIRT.cnf')

config_file = os.environ['fdm_config']

with open(config_file, 'r') as f:
    cfg = json.load(f)

parent_dir = cfg['parent_dir']
HighRes = cfg['struct']
non_linear = cfg['non_linear']
use_adc = cfg['use_adc']
ref_space = cfg['ref_space']

scan_list = ["scan_{0:0>2d}".format(x+1) for x in range(cfg['number_of_scans'])]
print scan_list

config.set('execution','crashdump_dir',parent_dir)

def GetImages(scan_id, config):
    DWI = config[scan_id]['dwi']
    ADC = config[scan_id]['adc']
    REF = config[scan_id]['ref']
    Tumor = config[scan_id]['roi']
    Normal = config[scan_id]['roi']
    print "Tumor is" + Tumor

    return DWI,ADC,REF,Tumor,Normal

data = pe.Node(interface=util.Function(input_names=['scan_id', 'config'],
                                        output_names=['DWI','ADC','REF','Tumor','Normal'],
                                        function=GetImages),
                                        name = "data")
data.inputs.config = cfg
data.iterables = ('scan_id', scan_list)


betADC = pe.Node(interface=fsl.BET(),name='betADC')
betADC.inputs.frac=0.2
betADC.inputs.robust=True

betREF = pe.Node(interface=fsl.BET(),name='betREF')
betREF.inputs.frac=0.2
betREF.inputs.robust=True

REFlinHighRes = pe.Node(interface=fsl.FLIRT(), name='REFlinHighRes')
REFlinHighRes.inputs.reference=HighRes
REFlinHighRes.inputs.dof = 6
REFlinHighRes.inputs.searchr_x = [-45, 45]
REFlinHighRes.inputs.searchr_y = [-45, 45]
REFlinHighRes.inputs.searchr_z = [-45, 45]

TumorlinREF=pe.Node(interface=fsl.FLIRT(), name='TumorlinREF')
TumorlinREF.inputs.apply_xfm=True

TumorfftREF=pe.Node(interface=afni_ext.Allineate(), name='TumorfftREF')
TumorfftREF.inputs.outputtype='NIFTI'

NormallinREF=pe.Node(interface=fsl.FLIRT(), name='NormallinREF')
NormallinREF.inputs.apply_xfm=True

NormalfftREF=pe.Node(interface=afni_ext.Allineate(), name='NormalfftREF')
NormalfftREF.inputs.outputtype='NIFTI'

REFfftHighRes=pe.Node(interface=afni_ext.Volreg(), name='REFfftHighRes')
REFfftHighRes.inputs.basefile=HighRes
REFfftHighRes.inputs.args='-Fourier'
REFfftHighRes.inputs.outputtype='NIFTI'


ADClinHighRes=pe.Node(interface=fsl.FLIRT(), name='ADClinHighRes')
ADClinHighRes.inputs.apply_xfm=True
ADClinHighRes.inputs.reference=HighRes

TumorlinHighRes=pe.Node(interface=fsl.FLIRT(), name='TumorlinHighRes')
TumorlinHighRes.inputs.apply_xfm=True
TumorlinHighRes.inputs.reference=HighRes

NormallinHighRes=pe.Node(interface=fsl.FLIRT(), name='NormallinHighRes')
NormallinHighRes.inputs.apply_xfm=True
NormallinHighRes.inputs.reference=HighRes

ADCfftHighRes=pe.Node(interface=afni_ext.Allineate(), name='ADCfftHighRes')
ADCfftHighRes.inputs.outputtype='NIFTI'

TumorfftHighRes=pe.Node(interface=afni_ext.Allineate(), name='TumorfftHighRes')
TumorfftHighRes.inputs.outputtype='NIFTI'

NormalfftHighRes=pe.Node(interface=afni_ext.Allineate(), name='NormalfftHighRes')
NormalfftHighRes.inputs.outputtype='NIFTI'


LowThreshREF=pe.Node(interface=fsl.maths.Threshold(), name='LowThreshREF')
LowThreshREF.inputs.thresh=0.2

LowThreshADC=pe.Node(interface=fsl.maths.Threshold(), name='LowThreshADC')
LowThreshADC.inputs.thresh=0.2

LowThreshTumor=pe.Node(interface=fsl.maths.Threshold(), name='LowThreshTumor')
LowThreshTumor.inputs.thresh=0.2

LowThreshNormal=pe.Node(interface=fsl.maths.Threshold(), name='LowThreshNormal')
LowThreshNormal.inputs.thresh=0.2

MaskREF=pe.Node(interface=fsl.maths.ApplyMask(), name='MaskREF')
MaskREF.inputs.mask_file=HighRes

MaskADC=pe.Node(interface=fsl.maths.ApplyMask(), name='MaskADC')
MaskADC.inputs.mask_file=HighRes

MaskTumor=pe.Node(interface=fsl.maths.ApplyMask(), name='MaskTumor')
MaskTumor.inputs.mask_file=HighRes

MaskNormal=pe.Node(interface=fsl.maths.ApplyMask(), name='MaskNormal')
MaskNormal.inputs.mask_file=HighRes

if use_adc and not ref_space:

    ADClinREF = pe.Node(interface=fsl.FLIRT(), name='ADClinREF')
    ADClinREF.inputs.dof = 6

    ADCfftREF=pe.Node(interface=afni_ext.Volreg(), name='ADCfftREF')
    ADCfftREF.inputs.args='-Fourier'
    ADCfftREF.inputs.outputtype='NIFTI'

    Reg = pe.Workflow(name='Reg')
    Reg.base_dir=parent_dir+'/FDM'
    Reg.connect([
                           (data, betADC, [('ADC','in_file')]),
                           (data, betREF, [('REF','in_file')]),
                      (betADC, ADClinREF, [('out_file','in_file')]),
                      (betREF, ADClinREF, [('out_file','reference')]),
                 (ADClinREF, TumorlinREF, [('out_matrix_file','in_matrix_file')]),
                    (betREF, TumorlinREF, [('out_file','reference')]),
                       (data,TumorlinREF, [('Tumor','in_file')]),
                (ADClinREF, NormallinREF, [('out_matrix_file','in_matrix_file')]),
                   (betREF, NormallinREF, [('out_file','reference')]),
                      (data,NormallinREF, [('Normal','in_file')]),
                   (ADClinREF, ADCfftREF, [('out_file','in_file')]),
                      (betREF, ADCfftREF, [('out_file','basefile')]),
                (TumorlinREF,TumorfftREF, [('out_file','in_file')]),
                    (betREF, TumorfftREF, [('out_file','master')]),
                  (ADCfftREF,TumorfftREF, [('out_matrix_file','in_matrix')]),
              (NormallinREF,NormalfftREF, [('out_file','in_file')]),
                   (betREF, NormalfftREF, [('out_file','master')]),
                 (ADCfftREF,NormalfftREF, [('out_matrix_file','in_matrix')]),
                  (betREF, REFlinHighRes, [('out_file','in_file')]),
           (REFlinHighRes, REFfftHighRes, [('out_file','in_file')]),
           (REFlinHighRes, ADClinHighRes, [('out_matrix_file', 'in_matrix_file')]),
         (REFlinHighRes, TumorlinHighRes, [('out_matrix_file', 'in_matrix_file')]),
        (REFlinHighRes, NormallinHighRes, [('out_matrix_file', 'in_matrix_file')]),
               (ADCfftREF, ADClinHighRes, [('out_file','in_file')]),
           (TumorfftREF, TumorlinHighRes, [('out_file','in_file')]),
         (NormalfftREF, NormallinHighRes, [('out_file','in_file')]),
           (ADClinHighRes, ADCfftHighRes, [('out_file','in_file')]),
           (REFfftHighRes, ADCfftHighRes, [('out_matrix_file','in_matrix')]),
       (TumorlinHighRes, TumorfftHighRes, [('out_file','in_file')]),
     (NormallinHighRes, NormalfftHighRes, [('out_file','in_file')]),
         (REFfftHighRes, TumorfftHighRes, [('out_matrix_file','in_matrix')]),
        (REFfftHighRes, NormalfftHighRes, [('out_matrix_file','in_matrix')]),
                 (REFfftHighRes, MaskREF, [('out_file','in_file')]),
                 (ADCfftHighRes, MaskADC, [('out_file','in_file')]),
             (TumorfftHighRes, MaskTumor, [('out_file','in_file')]),
           (NormalfftHighRes, MaskNormal, [('out_file','in_file')])

    ])


elif use_adc and ref_space:

    ADClinREF = pe.Node(interface=fsl.FLIRT(), name='ADClinREF')
    ADClinREF.inputs.dof = 6

    ADCfftREF=pe.Node(interface=afni_ext.Volreg(), name='ADCfftREF')
    ADCfftREF.inputs.args='-Fourier'
    ADCfftREF.inputs.outputtype='NIFTI'

    Reg = pe.Workflow(name='Reg')
    Reg.base_dir=parent_dir+'/FDM'
    Reg.connect([
                           (data, betADC, [('ADC','in_file')]),
                           (data, betREF, [('REF','in_file')]),
                      (betADC, ADClinREF, [('out_file','in_file')]),
                      (betREF, ADClinREF, [('out_file','reference')]),
                   (ADClinREF, ADCfftREF, [('out_file','in_file')]),
                      (betREF, ADCfftREF, [('out_file','basefile')]),
                  (betREF, REFlinHighRes, [('out_file','in_file')]),
           (REFlinHighRes, REFfftHighRes, [('out_file','in_file')]),
           (REFlinHighRes, ADClinHighRes, [('out_matrix_file', 'in_matrix_file')]),
         (REFlinHighRes, TumorlinHighRes, [('out_matrix_file', 'in_matrix_file')]),
        (REFlinHighRes, NormallinHighRes, [('out_matrix_file', 'in_matrix_file')]),
               (ADCfftREF, ADClinHighRes, [('out_file','in_file')]),
                  (data, TumorlinHighRes, [('Tumor','in_file')]),
                 (data, NormallinHighRes, [('Normal','in_file')]),
           (ADClinHighRes, ADCfftHighRes, [('out_file','in_file')]),
           (REFfftHighRes, ADCfftHighRes, [('out_matrix_file','in_matrix')]),
       (TumorlinHighRes, TumorfftHighRes, [('out_file','in_file')]),
     (NormallinHighRes, NormalfftHighRes, [('out_file','in_file')]),
         (REFfftHighRes, TumorfftHighRes, [('out_matrix_file','in_matrix')]),
        (REFfftHighRes, NormalfftHighRes, [('out_matrix_file','in_matrix')]),
                 (REFfftHighRes, MaskREF, [('out_file','in_file')]),
                 (ADCfftHighRes, MaskADC, [('out_file','in_file')]),
             (TumorfftHighRes, MaskTumor, [('out_file','in_file')]),
           (NormalfftHighRes, MaskNormal, [('out_file','in_file')])
    ])



elif not use_adc and not ref_space:
    betb0 = pe.Node(interface=fsl.BET(),name='betb0')
    betb0.inputs.frac=0.2
    betb0.inputs.robust=True

    b0linREF = pe.Node(interface=fsl.FLIRT(), name='b0linREF')
    b0linREF.inputs.dof = 6

    b0fftREF=pe.Node(interface=afni_ext.Volreg(), name='b0fftREF')
    b0fftREF.inputs.args='-Fourier'
    b0fftREF.inputs.outputtype='NIFTI'

    ADClinREF=pe.Node(interface=fsl.FLIRT(), name='ADClinREF')
    ADClinREF.inputs.apply_xfm=True

    ADCfftREF=pe.Node(interface=afni_ext.Allineate(), name='ADCfftREF')
    ADCfftREF.inputs.outputtype='NIFTI'

    extract_b0 = pe.Node(interface=fsl.ExtractROI(), name = 'extract_b0')
    extract_b0.inputs.t_size = 1

    def get_high_signal(DWI):
        import numpy as np
        from nipy import load_image

        img = load_image(DWI)
        if img.ndim == 3:
            return 0
        else:
            x = [np.mean(img[:,:,:,_]) for _ in xrange(img.shape[3])]
            return np.argmax(x)


    find_b0 = pe.Node(name='find_b0',
                        interface = util.Function(input_names=['DWI'],
                                             output_names=['index'],
                                             function = get_high_signal))
    Reg = pe.Workflow(name='Reg')
    Reg.base_dir=parent_dir+'/FDM'
    Reg.connect([
                       (data, find_b0, [('DWI', 'DWI')]),
                 (find_b0, extract_b0, [('index', 't_min')]),
                    (data, extract_b0, [('DWI','in_file')]),
                   (extract_b0, betb0, [('roi_file', 'in_file')]),
                        (data, betREF, [('REF','in_file')]),
                     (betb0, b0linREF, [('out_file','in_file')]),
                    (betREF, b0linREF, [('out_file','reference')]),
               (b0linREF, TumorlinREF, [('out_matrix_file','in_matrix_file')]),
                 (betREF, TumorlinREF, [('out_file','reference')]),
                    (data,TumorlinREF, [('Tumor','in_file')]),
              (b0linREF, NormallinREF, [('out_matrix_file','in_matrix_file')]),
                (betREF, NormallinREF, [('out_file','reference')]),
                   (data,NormallinREF, [('Normal','in_file')]),
                 (b0linREF, ADClinREF, [('out_matrix_file','in_matrix_file')]),
                   (betREF, ADClinREF, [('out_file','reference')]),
                      (data,ADClinREF, [('ADC','in_file')]),
                  (b0linREF, b0fftREF, [('out_file','in_file')]),
                    (betREF, b0fftREF, [('out_file','basefile')]),
             (TumorlinREF,TumorfftREF, [('out_file','in_file')]),
                 (betREF, TumorfftREF, [('out_file','reference')]),
                (b0fftREF,TumorfftREF, [('out_matrix_file','in_matrix')]),
           (NormallinREF,NormalfftREF, [('out_file','in_file')]),
                (betREF, NormalfftREF, [('out_file','reference')]),
               (b0fftREF,NormalfftREF, [('out_matrix_file','in_matrix')]),
                 (ADClinREF,ADCfftREF, [('out_file','in_file')]),
                   (betREF, ADCfftREF, [('out_file','reference')]),
                  (b0fftREF,ADCfftREF, [('out_matrix_file','in_matrix')]),
               (betREF, REFlinHighRes, [('out_file','in_file')]),
        (REFlinHighRes, REFfftHighRes, [('out_file','in_file')]),
        (REFlinHighRes, ADClinHighRes, [('out_matrix_file', 'in_matrix_file')]),
      (REFlinHighRes, TumorlinHighRes, [('out_matrix_file', 'in_matrix_file')]),
     (REFlinHighRes, NormallinHighRes, [('out_matrix_file', 'in_matrix_file')]),
            (ADCfftREF, ADClinHighRes, [('out_file','in_file')]),
        (TumorfftREF, TumorlinHighRes, [('out_file','in_file')]),
      (NormalfftREF, NormallinHighRes, [('out_file','in_file')]),
        (ADClinHighRes, ADCfftHighRes, [('out_file','in_file')]),
        (REFfftHighRes, ADCfftHighRes, [('out_matrix_file','in_matrix')]),
    (TumorlinHighRes, TumorfftHighRes, [('out_file','in_file')]),
  (NormallinHighRes, NormalfftHighRes, [('out_file','in_file')]),
      (REFfftHighRes, TumorfftHighRes, [('out_matrix_file','in_matrix')]),
     (REFfftHighRes, NormalfftHighRes, [('out_matrix_file','in_matrix')]),
              (REFfftHighRes, MaskREF, [('out_file','in_file')]),
              (ADCfftHighRes, MaskADC, [('out_file','in_file')]),
          (TumorfftHighRes, MaskTumor, [('out_file','in_file')]),
        (NormalfftHighRes, MaskNormal, [('out_file','in_file')])

    ])

elif not use_adc and ref_space:

    betb0 = pe.Node(interface=fsl.BET(),name='betb0')
    betb0.inputs.frac=0.2
    betb0.inputs.robust=True

    b0linREF = pe.Node(interface=fsl.FLIRT(), name='b0linREF')
    b0linREF.inputs.dof = 6

    b0fftREF=pe.Node(interface=afni_ext.Volreg(), name='b0fftREF')
    b0fftREF.inputs.args='-Fourier'
    b0fftREF.inputs.outputtype='NIFTI'

    ADClinREF=pe.Node(interface=fsl.FLIRT(), name='ADClinREF')
    ADClinREF.inputs.apply_xfm=True

    ADCfftREF=pe.Node(interface=afni_ext.Allineate(), name='ADCfftREF')
    ADCfftREF.inputs.outputtype='NIFTI'

    extract_b0 = pe.Node(interface=fsl.ExtractROI(), name = 'extract_b0')
    extract_b0.inputs.t_size = 1

    def get_high_signal(DWI):
        import numpy as np
        from nipy import load_image

        img = load_image(DWI)
        if img.ndim == 3:
            return 0
        else:
            x = [np.mean(img[:,:,:,_]) for _ in xrange(img.shape[3])]
            return np.argmax(x)


    find_b0 = pe.Node(name='find_b0',
                        interface = util.Function(input_names=['DWI'],
                                             output_names=['index'],
                                             function = get_high_signal))
    Reg = pe.Workflow(name='Reg')
    Reg.base_dir=parent_dir+'/FDM'
    Reg.connect([
                       (data, find_b0, [('DWI', 'DWI')]),
                 (find_b0, extract_b0, [('index', 't_min')]),
                    (data, extract_b0, [('DWI','in_file')]),
                   (extract_b0, betb0, [('roi_file', 'in_file')]),
                        (data, betREF, [('REF','in_file')]),
                     (betb0, b0linREF, [('out_file','in_file')]),
                    (betREF, b0linREF, [('out_file','reference')]),
                 (b0linREF, ADClinREF, [('out_matrix_file','in_matrix_file')]),
                   (betREF, ADClinREF, [('out_file','reference')]),
                      (data,ADClinREF, [('ADC','in_file')]),
                  (b0linREF, b0fftREF, [('out_file','in_file')]),
                    (betREF, b0fftREF, [('out_file','basefile')]),
                 (ADClinREF,ADCfftREF, [('out_file','in_file')]),
                   (betREF, ADCfftREF, [('out_file','reference')]),
                  (b0fftREF,ADCfftREF, [('out_matrix_file','in_matrix')]),
               (betREF, REFlinHighRes, [('out_file','in_file')]),
        (REFlinHighRes, REFfftHighRes, [('out_file','in_file')]),
        (REFlinHighRes, ADClinHighRes, [('out_matrix_file', 'in_matrix_file')]),
      (REFlinHighRes, TumorlinHighRes, [('out_matrix_file', 'in_matrix_file')]),
     (REFlinHighRes, NormallinHighRes, [('out_matrix_file', 'in_matrix_file')]),
            (ADCfftREF, ADClinHighRes, [('out_file','in_file')]),
               (data, TumorlinHighRes, [('Tumor','in_file')]),
              (data, NormallinHighRes, [('Normal','in_file')]),
        (ADClinHighRes, ADCfftHighRes, [('out_file','in_file')]),
        (REFfftHighRes, ADCfftHighRes, [('out_matrix_file','in_matrix')]),
    (TumorlinHighRes, TumorfftHighRes, [('out_file','in_file')]),
  (NormallinHighRes, NormalfftHighRes, [('out_file','in_file')]),
      (REFfftHighRes, TumorfftHighRes, [('out_matrix_file','in_matrix')]),
     (REFfftHighRes, NormalfftHighRes, [('out_matrix_file','in_matrix')]),
              (REFfftHighRes, MaskREF, [('out_file','in_file')]),
              (ADCfftHighRes, MaskADC, [('out_file','in_file')]),
          (TumorfftHighRes, MaskTumor, [('out_file','in_file')]),
        (NormalfftHighRes, MaskNormal, [('out_file','in_file')])
    ])

if non_linear:
    def get_ADC(LinADC):
        """
        in the future, users will be able to specify which time point
        to use as reference
        """
        return LinADC[0]

    get_Ref = pe.JoinNode(interface = util.Function(input_names=['LinADC'],
                          output_names=['REF'], function=get_ADC),
                          name='get_Ref', joinsource='data',joinfield='LinADC')

    ADCwarpHighRes=pe.Node(interface=fsl.FNIRT(), name='ADCwarpHighRes')
    ADCwarpHighRes.inputs.field_file=True
    ADCwarpHighRes.inputs.config_file=fnirt_config

    TumorwarpHighRes=pe.Node(interface=fsl.ApplyWarp(), name='TumorwarpHighRes')

    REFwarpHighRes=pe.Node(interface=fsl.ApplyWarp(), name='REFwarpHighRes')


    NormalwarpHighRes=pe.Node(interface=fsl.ApplyWarp(), name='NormalwarpHighRes')


    Warp = pe.Workflow(name='Warp')
    Warp.base_dir=parent_dir+'/FDM'
    Warp.connect([

                (get_Ref, ADCwarpHighRes, [('REF', 'ref_file')]),
                (get_Ref, REFwarpHighRes, [('REF', 'ref_file')]),
              (get_Ref, TumorwarpHighRes, [('REF', 'ref_file')]),
             (get_Ref, NormalwarpHighRes, [('REF', 'ref_file')]),
         (ADCwarpHighRes, REFwarpHighRes, [('field_file','field_file')]),
       (ADCwarpHighRes, TumorwarpHighRes, [('field_file','field_file')]),
      (ADCwarpHighRes, NormalwarpHighRes, [('field_file','field_file')]),
           (ADCwarpHighRes, LowThreshADC, [('warped_file','in_file')]),
           (REFwarpHighRes, LowThreshREF, [('out_file','in_file')]),
       (TumorwarpHighRes, LowThreshTumor, [('out_file','in_file')]),
     (NormalwarpHighRes, LowThreshNormal, [('out_file','in_file')])
                                ])

    datasink=pe.Node(interface=nio.DataSink(), name="datasink")
    datasink.inputs.base_directory= parent_dir+'/FDM/Outputs'
    datasink.inputs.substitutions = [('_scan_id_',''),
                                    ('_brain_flirt_volreg_masked_warp_thresh', '_highres'),
                                    ('_flirt_allineate_flirt_allineate_masked_warp_thresh','_highres'),
                                    ('_brain_flirt_volreg_flirt_allineate_masked_warped_thresh','_highres')]


else:
    def do_nothing(LinADC):
        print LinADC

    get_Ref = pe.Node(name='get_Ref',
                        interface = util.Function(input_names=['LinADC'],
                                             output_names=['REF'],
                                             function = do_nothing))

    REFwarpHighRes=pe.Node(interface=afni_ext.Allineate(), name='REFwarpHighRes')
    REFwarpHighRes.inputs.cost='hel'
    REFwarpHighRes.inputs.reference=HighRes
    REFwarpHighRes.inputs.two_pass=False
    REFwarpHighRes.inputs.outputtype='NIFTI'

    ADCwarpHighRes=pe.Node(interface=afni_ext.Allineate(), name='ADCwarpHighRes')
    ADCwarpHighRes.inputs.outputtype='NIFTI'
    ADCwarpHighRes.inputs.master=HighRes
    ADCwarpHighRes.inputs.reference=HighRes

    TumorwarpHighRes=pe.Node(interface=afni_ext.Allineate(), name='TumorwarpHighRes')
    TumorwarpHighRes.inputs.outputtype='NIFTI'
    TumorwarpHighRes.inputs.master=HighRes
    TumorwarpHighRes.inputs.reference=HighRes

    NormalwarpHighRes=pe.Node(interface=afni_ext.Allineate(), name='NormalwarpHighRes')
    NormalwarpHighRes.inputs.outputtype='NIFTI'
    NormalwarpHighRes.inputs.master=HighRes
    NormalwarpHighRes.inputs.reference=HighRes

    Warp = pe.Workflow(name='Warp')
    Warp.base_dir=parent_dir+'/FDM'
    Warp.add_nodes([get_Ref])
    Warp.connect([
         (REFwarpHighRes, ADCwarpHighRes, [('matrix','in_matrix')]),
       (REFwarpHighRes, TumorwarpHighRes, [('matrix','in_matrix')]),
      (REFwarpHighRes, NormalwarpHighRes, [('matrix','in_matrix')]),
           (REFwarpHighRes, LowThreshREF, [('out_file','in_file')]),
           (ADCwarpHighRes, LowThreshADC, [('out_file','in_file')]),
       (TumorwarpHighRes, LowThreshTumor, [('out_file','in_file')]),
     (NormalwarpHighRes, LowThreshNormal, [('out_file','in_file')])
                                ])

    datasink=pe.Node(interface=nio.DataSink(), name="datasink")
    datasink.inputs.base_directory= parent_dir+'/FDM/Outputs'
    datasink.inputs.substitutions = [('_scan_id_',''),
                                    ('_brain_flirt_volreg_masked_allineate_thresh','_highres'),
                                    ('_brain_flirt_volreg_flirt_allineate_masked_allineate_thresh','_highres'),
                                    ('_flirt_allineate_flirt_allineate_masked_allineate_thresh','_highres')]

TumorBin = pe.Node(interface=fsl.UnaryMaths(), name='TumorBin')
TumorBin.inputs.operation = 'bin'

FDM = pe.Workflow(name='FDM')
FDM.base_dir=parent_dir
FDM.connect([
              (Reg, Warp, [('MaskADC.out_file','get_Ref.LinADC')]),
              (Reg, Warp, [('MaskADC.out_file', 'ADCwarpHighRes.in_file')]),
              (Reg, Warp, [('MaskREF.out_file', 'REFwarpHighRes.in_file')]),
              (Reg, Warp, [('MaskTumor.out_file', 'TumorwarpHighRes.in_file')]),
              (Reg, Warp, [('MaskNormal.out_file', 'NormalwarpHighRes.in_file')]),
         (Warp, TumorBin, [('LowThreshTumor.out_file', 'in_file')]),
         (Warp, datasink, [('LowThreshREF.out_file','Ref.@ref')]),
          (Warp,datasink, [('LowThreshADC.out_file','ADC.@adc')]),
      (TumorBin,datasink, [('out_file','Tumor.@tumor')]),
          (Warp,datasink, [('LowThreshNormal.out_file','Normal.@normal')])

])


def Merge(scan_list,out_reg_dir, out_file):
    import subprocess
    import shlex
    ADC_list=[out_reg_dir+scan+'/'+(os.listdir(out_reg_dir+scan)[0])
          for scan in scan_list]
    MergeRegs = fsl.utils.Merge()
    MergeRegs.inputs.in_files=ADC_list
    MergeRegs.inputs.dimension='t'
    MergeRegs.inputs.merged_file = out_file
    print MergeRegs.cmdline
    command = shlex.split( MergeRegs.cmdline)
    subprocess.call(command)

def Get_Volume(timepoint):
    infile = parent_dir+'/FDM/Outputs/Tumor/'+timepoint+'/'+\
    os.listdir( parent_dir+'/FDM/Outputs/Tumor/'+timepoint)[0]
    Volume = fsl.ImageStats()
    Volume.inputs.in_file = infile
    Volume.inputs.op_string = '-V'
    Vout = Volume.run()
    return Vout.outputs.out_stat

def Get_Mean_ADC(timepoint):
    infile = parent_dir+'/FDM/Outputs/ADC/'+timepoint+'/'+\
    os.listdir( parent_dir+'/FDM/Outputs/ADC/'+timepoint)[0]
    maskfile = parent_dir+'/FDM/Outputs/Tumor/'+timepoint+'/'+\
    os.listdir( parent_dir+'/FDM/Outputs/Tumor/'+timepoint)[0]
    ADC = fsl.ImageStats()
    ADC.inputs.in_file = infile
    ADC.inputs.op_string = '-k %s -M'
    ADC.inputs.mask_file = maskfile
    ADCout = ADC.run()
    return ADCout.outputs.out_stat


def Out_Stats(out_file, scan_list):
    with open(out_file, 'wb') as f:
        f.write('Time_Point,Volume(voxels),Volume(mm3),Mean_ADC,\n')
        for scan in scan_list:
              Vol = Get_Volume(scan)
              MADC = Get_Mean_ADC(scan)
              f.write(scan+','+str(Vol[0])+','
                              +str(Vol[1])+','
                              +str(MADC)+'\n')


out_reg_dir = parent_dir+'/FDM/Outputs/ADC/'
merge_out = parent_dir+'/FDM/Outputs/MergedRegs.nii'
out_file = parent_dir+'/stats.csv'



if not os.path.isdir(parent_dir+'/FDM'):
    print 'creating FDM directory'
    os.makedirs(parent_dir+'/FDM')



FDM.write_graph()
if cfg['grid_eng']:
    FDM.run(plugin='SGE',plugin_args=dict(qsub_args='-V -q long.q'))
    Merge(scan_list, out_reg_dir, merge_out)
    Out_Stats(out_file, scan_list)
    print 'Merge done'
else:
    FDM.run()
    Merge(scan_list, out_reg_dir, merge_out)
    Out_Stats(out_file, scan_list)
    print 'Merge done'



