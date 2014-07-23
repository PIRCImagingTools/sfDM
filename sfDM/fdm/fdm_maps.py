'''
Created on Mar 11, 2013

@author: rafa
'''

import nipype.interfaces.fsl as fsl
import nipype.pipeline.engine as pe
import os
import json
from nipype.interfaces.utility import Function
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
import shutil
from sfDM.vis import colormaps
from sfDM.vis.map_maker import MapMaker
import re
from nipype import config

fsl.FSLCommand.set_default_output_type('NIFTI')


#Data set up
config_file = os.environ['fdm_config']
timeline_file = os.environ['fdm_timeline']

with open(config_file, 'r') as f:
    cfg = json.load(f)
parent = cfg['parent_dir']

config.set('execution','crashdump_dir',parent)

with open(timeline_file, 'r') as f:
    tmln = json.load(f)

outputdir=parent+'/FDM/Outputs/'

#-----------------------Begin Map Calculations--------------------------------------------------------------------#

fsl.FSLCommand.set_default_output_type('NIFTI')

scan_list = ["scan_{0:0>2d}".format(x+1) for x in range(cfg['number_of_scans'])]
print scan_list


Tumor=[outputdir+'Tumor/'+scan+'/'+(os.listdir(outputdir+'Tumor/'+scan)[0]) for scan in scan_list]
ADC=[outputdir+'ADC/'+scan+'/'+(os.listdir(outputdir+'ADC/'+scan)[0]) for scan in scan_list]
Normal=[outputdir+'Normal/'+scan+'/'+(os.listdir(outputdir+'Normal/'+scan)[0]) for scan in scan_list]


def getScans(ADClist,TumorValueList,NormalValueList, tmln):
    time1=[]
    time2=[]
    TumorValue1=[]
    TumorValue2=[]
    NormalValue1=[]
    NormalValue2=[]
    for scan in tmln['baseline']:
        time2.append(ADClist[int(scan[5:7])-1])
        time1.append(ADClist[int(scan[15:17])-1])
        NormalValue2.append(NormalValueList[int(scan[5:7])-1])
        NormalValue1.append(NormalValueList[int(scan[15:17])-1])
        TumorValue2.append(TumorValueList[int(scan[5:7])-1])
        TumorValue1.append(TumorValueList[int(scan[15:17])-1])
    for scan in tmln['serial']:
        time2.append(ADClist[int(scan[5:7])-1])
        time1.append(ADClist[int(scan[15:17])-1])
        NormalValue2.append(NormalValueList[int(scan[5:7])-1])
        NormalValue1.append(NormalValueList[int(scan[15:17])-1])
        TumorValue2.append(TumorValueList[int(scan[5:7])-1])
        TumorValue1.append(TumorValueList[int(scan[15:17])-1])

    return time1,TumorValue1,NormalValue1,time2,TumorValue2,NormalValue2

ScanSource=pe.Node(name='scansource',
                   interface=Function(input_names=['ADClist','TumorValueList','NormalValueList', 'tmln'],
                                      output_names=['time1','TumorValue1','NormalValue1',
                                                    'time2', 'TumorValue2','NormalValue2'],
                                      function=getScans))

ScanSource.inputs.tmln = tmln

outstring='-add %s '*(len(Tumor)-1)
outstring=outstring[:-1]

CreateTumorMask=pe.Node(interface=fsl.MultiImageMaths(), name='CreateTumorMask')
CreateTumorMask.inputs.in_file=Tumor[0]
CreateTumorMask.inputs.operand_files=Tumor[1:]
CreateTumorMask.inputs.op_string=outstring

ThresholdTumor=pe.Node(interface=fsl.Threshold(), name='ThresholdTumor')
ThresholdTumor.inputs.thresh=1


CreateNormalMask=pe.Node(interface=fsl.MultiImageMaths(), name='CreateNormalMask')
CreateNormalMask.inputs.in_file=Normal[0]
CreateNormalMask.inputs.operand_files=Normal[1:]
CreateNormalMask.inputs.op_string=outstring

ThresholdNormal=pe.Node(interface=fsl.Threshold(), name='ThresholdNormal')
ThresholdNormal.inputs.thresh=1

MaskTumorADC=pe.MapNode(interface=fsl.ApplyMask(), name='MaskTumorADC',iterfield=['in_file'])


ThresholdADC=pe.MapNode(interface=fsl.Threshold(), name='ThresholdADC',iterfield=['in_file'])
ThresholdADC.inputs.in_file=ADC
ThresholdADC.inputs.thresh=10


MaskNormalADC=pe.MapNode(interface=fsl.ApplyMask(), name='MaskNormalADC',iterfield=['in_file'])
MaskNormalADC.inputs.in_file=ADC


ExtractTumorValue=pe.MapNode(interface=fsl.ImageMeants(), name='ExtractTumorValues',iterfield=['in_file'])
ExtractTumorValue.inputs.show_all=True
ExtractTumorValue.inputs.transpose=True

ExtractNormalValue=pe.MapNode(interface=fsl.ImageMeants(), name='ExtractNormalValues',iterfield=['in_file'])
ExtractNormalValue.inputs.show_all=True
ExtractNormalValue.inputs.transpose=True


ExtractMaskValue=pe.Node(interface=fsl.ImageMeants(), name='ExtractMaskValues')
ExtractMaskValue.inputs.show_all = True
ExtractMaskValue.inputs.transpose = True


ImageSubtract=pe.MapNode(interface=fsl.BinaryMaths(), name='ImageSubtract', iterfield=['operand_file','in_file'])
ImageSubtract.inputs.operation='sub'


def ConfInt(value1,value2, thresh):
   # import numpy as np
   # from scipy.stats.distributions import t
    if len(value1)==len(value2):
   #     n=len(value1)
   #     dof=n-1
        #Using empirical value from literature
        pos_thresh = thresh
        neg_thresh = -thresh
        return pos_thresh, neg_thresh

    else:
        return 0

ConfidenceInterval=pe.Node(name='ConfidenceInterval',
                   interface=Function(input_names=['value1','value2', 'thresh'],
                                      output_names=['pos_thresh','neg_thresh'],
                                      function=ConfInt))
ConfidenceInterval.inputs.thresh = 400



Maps = pe.Workflow(name='Maps')
Maps.base_dir=parent+'/FDM/'
Maps.connect([
               (ThresholdADC, MaskTumorADC, [('out_file','in_file')]),
          (CreateTumorMask, ThresholdTumor, [('out_file','in_file')]),
         (ThresholdTumor, ExtractMaskValue, [('out_file', 'in_file')]),
         (ThresholdTumor, ExtractMaskValue, [('out_file','mask')]),
             (ThresholdTumor, MaskTumorADC, [('out_file','mask_file')]),
        (CreateNormalMask, ThresholdNormal, [('out_file','in_file')]),
           (ThresholdNormal, MaskNormalADC, [('out_file','mask_file')]),
      (ThresholdNormal, ExtractNormalValue, [('out_file','mask')]),
        (MaskNormalADC, ExtractNormalValue, [('out_file','in_file')]),
        (ThresholdTumor, ExtractTumorValue, [('out_file','mask')]),
           (MaskTumorADC, ExtractTumorValue, [('out_file','in_file')]),
                  (MaskTumorADC, ScanSource, [('out_file','ADClist')]),
             (ExtractTumorValue, ScanSource, [('out_file','TumorValueList')]),
            (ExtractNormalValue, ScanSource, [('out_file','NormalValueList')]),
                 (ScanSource, ImageSubtract, [('time1','operand_file'),
                                              ('time2','in_file')]),
            (ScanSource, ConfidenceInterval, [('NormalValue1','value1'),
                                              ('NormalValue2','value2')])
])


#----------------------Begin Image creating and stats --------------------------------#

def getname(s):
    """
    Helper function to get time point from log files
    """
    try:
        Times=re.findall('_MaskTumorADC.{1,2}/',s)
        time2 = Times[0][13:-1]
        time1 = Times[1][13:-1]

        return int(time1)+1, int(time2)+1
    except ValueError:
       return "string error"

def create_image(bg,mask, overlay, X , Y , Z , savefile):
    """
    Generates 3-plane image fDM at specified coordinates
    using the map maker class given background, mask and overlay
    """
    image = MapMaker(bg)
    image.add_overlay(mask, .1, 1, colormaps.green(), alpha=0.4)
    image.add_overlay(overlay, -400, -1000, colormaps.blue_r())
    image.add_overlay(overlay, 400, 1000, colormaps.red())
    image.save_3plane(X, Y, Z, savefile)

def create_weight_image(bg, mask, X, Y, Z, savefile):
    """
    Creates the gradient image from the weighted mask
    """
    image = MapMaker(bg)
    image.add_overlay(mask, .1, 'max',colormaps.green_r(), alpha= 0.9 )
    image.save_3plane_vertical(X,Y,Z,savefile)

def output_metrics(Time1, Time2, SN1, SN2, vectors, weights=[], se=400):
    """
    Calculates fDM metrics given two time points, where Time1,2 are vectors of ADC values,
    SN1,2 are string values of the time point names, vectors are PCA eigenvectors, and
    weights is a vector of weights (must match Time points)
    """
    valuedict = {}
    valuedict['timepoint'] = SN2+' - '+SN1

    weights = weights / np.max(weights)
    mn_weights = np.copy(weights)
    mn_weights[mn_weights < 1] = 0

    mx_iADC, mn_iADC, wt_iADC = 0.0, 0.0, 0.0
    mx_dADC, mn_dADC, wt_dADC = 0.0, 0.0, 0.0

    for i in np.arange(0,len(Time1)):
        if Time2[i]-Time1[i] > se:
            mx_iADC += 1
            mn_iADC += mn_weights[i]
            wt_iADC += weights[i]

        elif Time2[i]-Time1[i] < -se:
            mx_dADC += 1
            wt_dADC += weights[i]
            mn_dADC += mn_weights[i]


    mx_fiADC = mx_iADC/len(Time1)
    mx_fdADC = mx_dADC/len(Time1)
    mx_ADCratio = mx_fiADC/(0.01+mx_fdADC)


    wt_fiADC = wt_iADC/np.sum(weights)
    wt_fdADC = wt_dADC/np.sum(weights)
    wt_ADCratio = wt_fiADC / (0.01+wt_fdADC)

    mn_fiADC = mn_iADC/np.sum(mn_weights)
    mn_fdADC = mn_dADC/np.sum(mn_weights)
    mn_ADCratio = mn_fiADC / (0.01+mn_fdADC)

    mx_slope = np.arctan(vectors[0,1]/vectors[0,0]) * 180 / np.pi


    valuedict = {}
    valuedict['timepoint'] = SN2+'-'+SN1
    valuedict['mx_fiADC'] = mx_fiADC
    valuedict['mx_fdADC'] = mx_fdADC
    valuedict['mx_FDMratio'] = mx_ADCratio
    valuedict['mn_fiADC'] = mn_fiADC
    valuedict['mn_fdADC'] = mn_fdADC
    valuedict['mn_FDMratio'] = mn_ADCratio
    valuedict['wt_fiADC'] = wt_fiADC
    valuedict['wt_fdADC'] = wt_fdADC
    valuedict['wt_FDMratio'] = wt_ADCratio
    valuedict['vectors'] = vectors
    valuedict['slope'] = mx_slope
    valuedict['out_string'] = 'Timepoints,mx_fiADC,mx_fdADC,mx_fDMratio,'+\
                                         'mn_fiADC,mn_fd_ADC,mn_fDMratio,'+\
                                         'wt_fiADC,wt_fdADC,wt_fDMratio \n'+\
                                 valuedict['timepoint'] +','+\
            str(mx_fiADC) +','+ str(mx_fdADC) +','+ str(mx_ADCratio) +','+\
            str(mn_fiADC) +','+ str(mn_fdADC) +','+ str(mn_ADCratio) +','+\
            str(wt_fiADC) +','+ str(wt_fdADC) +','+ str(wt_ADCratio) +'\n'


    return valuedict


def plot_adc(results,Val1,Val2,TP1,TP2,weights,se=400,sfile='Time1Time2'):
    X=np.arange(0,len(Val1))
    Scale=np.zeros((len(Val1), 3)) # matrix of RGB colors matching each voxel
    iADC = 0.0
    dADC = 0.0
    for i in X:
        if Val2[i]-Val1[i] > se:
            Scale[i] = [1,0,0]
            iADC += 1
        elif Val2[i]-Val1[i] < -se:
            Scale[i] = [0, 0, 1]
            dADC += 1
        else:
            Scale[i] = [0, 1, 0]

    weights = (weights/np.max(weights)).reshape([len(Val1),1])
    colorscale = np.hstack([Scale, weights]) # weights become the alpha channel

    fig1=plt.figure()
    ax=fig1.add_subplot(111)
    plt.scatter(Val1,Val2,c=colorscale, edgecolors='none', zorder=1)
    plt.plot(X,X,lw=3,ls='-', color='Green',alpha=0.8)
    plt.plot(X,X-se,lw=3,ls='--', color='Green',alpha=0.8)
    plt.plot(X,X+se,lw=3,ls='--', color='Green',alpha=0.8)
    plt.plot([0,-results['vectors'][0,0]*3000]+Val1.mean(),
             [0,-results['vectors'][0,1]*3000]+Val2.mean(),lw=3,color='Yellow')
    plt.plot([0,results['vectors'][0,0]*3000]+Val1.mean(),
             [0,results['vectors'][0,1]*3000]+Val2.mean(),lw=3,color='Yellow')
    fig1.set_facecolor([1,1,1])
    ax.patch.set_alpha(0.25)
    textstr = 'mx_fiADC = {:.2f} mx_fdADC = {:.2f} mx_fDMratio = {:.2f}  Slope = {:.2f}$^\circ$\n'.format(
      results['mx_fiADC'],results['mx_fdADC'],results['mx_FDMratio'],results['slope']) + \
              'mn_fiADC = {:.2f} mn_fdADC = {:.2f} mn_fDMratio = {:.2f} \n'.format(
      results['mn_fiADC'],results['mn_fdADC'],results['mn_FDMratio'])+ \
              ' wt_fiADC = {:.2f}  wt_fdADC = {:.2f}  wt_fDMratio = {:.2f}'.format(
      results['wt_fiADC'],results['wt_fdADC'],results['wt_FDMratio'])

    #ax.text(10,10, textstr, bbox={'facecolor':'white','alpha':'0.8','pad':10})
    ax.set_xlim(0,3000)
    ax.set_ylim(0,3000)
    ax.set_xlabel('Scan '+TP1,fontsize=14,fontweight='bold')
    ax.set_ylabel('Scan '+TP2,fontsize=14,fontweight='bold')
    #fig1.suptitle(results['timepoint'], fontsize=14, fontweight='bold')
    #ax.set_title(textstr, fontsize = 10)
    fig1.suptitle(textstr, fontsize = 10)
    plt.savefig(sfile,dpi=900, facecolor=fig1.get_facecolor(), edgecolor='w',
                orientation='landscape', bbox_inches=None, pad_inches=0.3)
    plt.close(fig1)


def get_pca(data):

    """
    compute PCA between row vectors, where each row is an observation,
    columns are samples (subjects, voxel intensity across time)
    """
    M = (data.T-np.mean(data,axis=1)).T ###subtract sample means at each observation
                                        ### observation==Time, or Slice
    [vals, vecs] = np.linalg.eig(np.cov(M)) # get eigenvales, vectors of Cov.matrix
    idx = np.argsort(vals)  #sort eigenvalues
    idx = idx[::-1]   #switch to descending order
    vecs = vecs[:,idx] #sort eigenvectors according eigenvalue order
    vals = vals[idx] #same for vals

    score = np.dot(vecs.T,M) #projection data
    return vecs, vals, score


PID=cfg['PID']
Xsl, Ysl, Zsl  = cfg['tumor_center']
charlen=len(PID)

MainDir = cfg['parent_dir']
BaseDir = MainDir+'/FDM/'
MapSearchDir = BaseDir+'Maps/ImageSubtract/mapflow/'
MapOutputDir = BaseDir+'Outputs/Maps/'
ValueSearchDir = BaseDir+'Maps/ExtractTumorValues/mapflow/'
PlotOutputDir = BaseDir+'Outputs/Plots/'
ImageOutputDir = BaseDir+'Outputs/Images/'
MaskVals= BaseDir + 'Maps/ExtractMaskValues/'
MetricsOutputDir = BaseDir+'Outputs/Metrics/'

#----------------------- Execution ---------------------------------------#
os.chdir(MainDir)
Maps.write_graph()
Maps.run()

if not os.path.isdir(MapOutputDir):
    os.makedirs(MapOutputDir)
if not os.path.isdir(PlotOutputDir):
    os.makedirs(PlotOutputDir)
if not os.path.isdir(ImageOutputDir):
    os.makedirs(ImageOutputDir)
if not os.path.isdir(MetricsOutputDir):
    os.makedirs(MetricsOutputDir)


### Copy mask into directory for easier access and viewing

for file in os.listdir(BaseDir+'Maps/CreateTumorMask'):
    if fnmatch.fnmatch(file, '*.nii'):
        shutil.copy2(BaseDir+'Maps/CreateTumorMask/'+file, MapOutputDir+PID+'_Tumor_Mask.nii')
Mask = MapOutputDir+PID+'_Tumor_Mask.nii'
BG = cfg['struct']
create_weight_image(BG, Mask, Xsl, Ysl, Zsl, ImageOutputDir+PID+'_Weights' )



#Organize and copy maps into output directory, create slice images

map_list = os.listdir(MapSearchDir)
for mapdir in map_list:
    log = MapSearchDir+mapdir+'/command.txt'
    if os.path.isfile(log):
        with open(log, 'r') as f:
            string = f.read()
        time1,time2 = getname(string)
        print 'time 2 is: scan_{0:0>2d}'.format(time2)
        print 'time 1 is: scan_{0:0>2d}'.format(time1)
        for file in os.listdir(MapSearchDir+mapdir):
            if fnmatch.fnmatch(file, '*.nii'):
                outmap = file
        print 'outmap: '+outmap
        FDM = MapOutputDir+'scan_{0:0>2d}-scan_{1:0>2d}.nii'.format(time2,time1)
        shutil.copy2(MapSearchDir+'/'+mapdir+'/'+outmap,
             FDM)
        create_image(BG, Mask, FDM, Xsl, Ysl, Zsl,\
                     ImageOutputDir+'/scan_{0:0>2d}-scan_{1:0>2d}.png'.format(time2,time1))

    else:
        print mapdir +' missing log'

def get_int(match):
    """
    Returns int value of folder name (listdir is alphabetical,not numerical )
    """
    return int(match[19:])

#### fetch text values and create plot

value_dirs = sorted(os.listdir(ValueSearchDir), key = get_int)
val_list = []
for valdir in value_dirs:
    for file in os.listdir(ValueSearchDir+valdir):
        if fnmatch.fnmatch(file, '*masked_ts.txt'):
            timepoint = file
    outval = ValueSearchDir+valdir+'/'+timepoint
    val_list.append(outval)
    print outval

for txtfile in os.listdir(MaskVals):
    if fnmatch.fnmatch(txtfile, '*_thresh_ts.txt'):
        maskvals = txtfile

weights = np.loadtxt(MaskVals+maskvals)[:,3]

#Iterate over scan time points
#calc PCA, get results dict and plot

for scan in tmln['baseline']:
    time2 = scan[5:7]
    time1 = scan[15:17]
    print 'scan {0} - scan {1}'.format(time2,time1)
    val2=np.loadtxt(val_list[int(time2)-1])[:,3]
    val1=np.loadtxt(val_list[int(time1)-1])[:,3]
    pca=get_pca(np.vstack((val1, val2)))[0]
    results=output_metrics(val1, val2, time1, time2, pca, weights)
    with open(MetricsOutputDir+'scan_{0}-scan_{1}.csv'.format(time2,time1),'wb') as f:
        f.write(results['out_string'])
    plot_adc(results,val1, val2,time1,time2,weights,
                sfile=PlotOutputDir+'scan_{0}-scan_{1}'.format(time2,time1))

for scan in tmln['serial']:
    time2 = scan[5:7]
    time1 = scan[15:17]
    print 'scan {0} - scan {1}'.format(time2,time1)
    val2=np.loadtxt(val_list[int(time2)-1])[:,3]
    val1=np.loadtxt(val_list[int(time1)-1])[:,3]
    pca=get_pca(np.vstack((val1, val2)))[0]
    results=output_metrics(val1, val2, time1, time2, pca, weights)
    with open(MetricsOutputDir+'scan_{0}-scan_{1}.csv'.format(time2,time1),'wb') as f:
        f.write(results['out_string'])
    plot_adc(results,val1, val2,time1,time2,weights,
                sfile=PlotOutputDir+'scan_{0}-scan_{1}'.format(time2,time1))

print 'Maps done'



