"""Patchwork to make AFNI outputs work in the pipeline"""

import warnings,os

from nipype.interfaces.afni.base import AFNICommand,AFNICommandInputSpec
from nipype.interfaces.base import traits, File, TraitedSpec, isdefined



warn = warnings.warn
warnings.filterwarnings('always', category=UserWarning)


class AllineateInputSpec(AFNICommandInputSpec):
    in_file = File(desc='input file to 3dAllineate',
                   argstr='-source %s',
                   position=-1,
                   mandatory=True,
                   exists=True,
                   copyfile=False)
    reference = File(
        exists=True,
        argstr='-base %s',
        desc="""file to be used as reference, the first volume will be used
if not given the reference will be the first volume of in_file.""")


    out_file = File(
        desc='output file from 3dAllineate',
        argstr='-prefix %s',
        position=-2,
        name_template='%s_allineate',
        name_source="in_file",
        genfile=True)
    out_param_file = File(
        argstr='-1Dparam_save %s',
        desc='Save the warp parameters in ASCII (.1D) format.')
    in_param_file = File(
        exists=True,
        argstr='-1Dparam_apply %s',
        desc="""Read warp parameters from file and apply them to
                  the source dataset, and produce a new dataset""")
    matrix = File(
        name_template='%s.aff12.1D',
        name_source="in_file",
        argstr='-1Dmatrix_save %s',
        keep_extension=True,
        desc='Save the transformation matrix for each volume.')

    in_matrix = File(desc='matrix to align input file',
                     argstr='-1Dmatrix_apply %s',
                     exists=True)

    _cost_funcs = [
        'leastsq', 'ls',
        'mutualinfo', 'mi',
        'corratio_mul', 'crM',
        'norm_mutualinfo', 'nmi',
        'hellinger', 'hel',
        'corratio_add', 'crA',
        'corratio_uns', 'crU']

    cost = traits.Enum(
        *_cost_funcs, argstr='-cost %s',
        desc="""Defines the 'cost' function that defines the matching
                between the source and the base""")
    _interp_funcs = [
        'nearestneighbour', 'linear', 'cubic', 'quintic', 'wsinc5']
    interpolation = traits.Enum(
        *_interp_funcs[:-1], argstr='-interp %s',
        desc='Defines interpolation method to use during matching')
    final_interpolation = traits.Enum(
        *_interp_funcs, argstr='-final %s',
        desc='Defines interpolation method used to create the output dataset')

    #   TECHNICAL OPTIONS (used for fine control of the program):
    nmatch = traits.Int(
        argstr='-nmatch %d',
        desc='Use at most n scattered points to match the datasets.')
    no_pad = traits.Bool(
        argstr='-nopad',
        desc='Do not use zero-padding on the base image.')
    zclip = traits.Bool(
        argstr='-zclip',
        desc='Replace negative values in the input datasets (source & base) with zero.')
    convergence = traits.Float(
        argstr='-conv %f',
        desc='Convergence test in millimeters (default 0.05mm).')
    usetemp = traits.Bool(argstr='-usetemp', desc='temporary file use')
    check = traits.List(
        traits.Enum(*_cost_funcs), argstr='-check %s',
        desc="""After cost functional optimization is done, start at the
                final parameters and RE-optimize using this new cost functions.
                If the results are too different, a warning message will be
                printed.  However, the final parameters from the original
                optimization will be used to create the output dataset.""")

    #      ** PARAMETERS THAT AFFECT THE COST OPTIMIZATION STRATEGY **
    one_pass = traits.Bool(
        argstr='-onepass',
        desc="""Use only the refining pass -- do not try a coarse
                resolution pass first.  Useful if you know that only
                small amounts of image alignment are needed.""")
    two_pass = traits.Bool(
        argstr='-twopass',
        desc="""Use a two pass alignment strategy for all volumes, searching
              for a large rotation+shift and then refining the alignment.""")
    two_blur = traits.Float(
        argstr='-twoblur',
        desc='Set the blurring radius for the first pass in mm.')
    two_first = traits.Bool(
        argstr='-twofirst',
        desc="""Use -twopass on the first image to be registered, and
               then on all subsequent images from the source dataset,
               use results from the first image's coarse pass to start
               the fine pass.""")
    two_best = traits.Int(
        argstr='-twobest %d',
        desc="""In the coarse pass, use the best 'bb' set of initial
               points to search for the starting point for the fine
               pass.  If bb==0, then no search is made for the best
               starting point, and the identity transformation is
               used as the starting point.  [Default=5; min=0 max=11]""")
    fine_blur = traits.Float(
        argstr='-fineblur %f',
        desc="""Set the blurring radius to use in the fine resolution
               pass to 'x' mm.  A small amount (1-2 mm?) of blurring at
               the fine step may help with convergence, if there is
               some problem, especially if the base volume is very noisy.
               [Default == 0 mm = no blurring at the final alignment pass]""")

    center_of_mass = traits.Str(
        argstr='-cmass%s',
        desc='Use the center-of-mass calculation to bracket the shifts.')
    autoweight = traits.Str(
        argstr='-autoweight%s',
        desc="""Compute a weight function using the 3dAutomask
               algorithm plus some blurring of the base image.""")
    automask = traits.Int(
        argstr='-automask+%d',
        desc="""Compute a mask function, set a value for dilation or 0.""")
    autobox = traits.Bool(
        argstr='-autobox',
        desc="""Expand the -automask function to enclose a rectangular
                box that holds the irregular mask.""")
    nomask = traits.Bool(
        argstr='-nomask',
        desc="""Don't compute the autoweight/mask; if -weight is not
                also used, then every voxel will be counted equally.""")
    weight_file = File(
        argstr='-weight %s', exists=True,
        desc="""Set the weighting for each voxel in the base dataset;
                larger weights mean that voxel count more in the cost function.
                Must be defined on the same grid as the base dataset""")
    out_weight_file = traits.File(
        argstr='-wtprefix %s',
        desc="""Write the weight volume to disk as a dataset""")

    source_mask = File(
        exists=True, argstr='-source_mask %s',
        desc='mask the input dataset')
    source_automask = traits.Int(
        argstr='-source_automask+%d',
        desc='Automatically mask the source dataset with dilation or 0.')
    warp_type = traits.Enum(
        'shift_only', 'shift_rotate', 'shift_rotate_scale', 'affine_general',
        argstr='-warp %s',
        desc='Set the warp type.')
    warpfreeze = traits.Bool(
        argstr='-warpfreeze',
        desc='Freeze the non-rigid body parameters after first volume.')
    replacebase = traits.Bool(
        argstr='-replacebase',
        desc="""If the source has more than one volume, then after the first
                volume is aligned to the base""")
    replacemeth = traits.Enum(
        *_cost_funcs,
        argstr='-replacemeth %s',
        desc="""After first volume is aligned, switch method for later volumes.
                For use with '-replacebase'.""")
    epi = traits.Bool(
        argstr='-EPI',
        desc="""Treat the source dataset as being composed of warped
                EPI slices, and the base as comprising anatomically
                'true' images.  Only phase-encoding direction image
                shearing and scaling will be allowed with this option.""")
    master = File(
        exists=True, argstr='-master %s',
        desc='Write the output dataset on the same grid as this file')
    newgrid = traits.Float(
        argstr='-newgrid %f',
        desc='Write the output dataset using isotropic grid spacing in mm')

    # Non-linear experimental
    _nwarp_types = ['bilinear',
                    'cubic', 'quintic', 'heptic', 'nonic',
                    'poly3', 'poly5', 'poly7',  'poly9']  # same non-hellenistic
    nwarp = traits.Enum(
        *_nwarp_types, argstr='-nwarp %s',
        desc='Experimental nonlinear warping: bilinear or legendre poly.')
    _dirs = ['X', 'Y', 'Z', 'I', 'J', 'K']
    nwarp_fixmot = traits.List(
        traits.Enum(*_dirs),
        argstr='-nwarp_fixmot%s',
        desc='To fix motion along directions.')
    nwarp_fixdep = traits.List(
        traits.Enum(*_dirs),
        argstr='-nwarp_fixdep%s',
        desc='To fix non-linear warp dependency along directions.')


class AllineateOutputSpec(TraitedSpec):
    out_file = File(desc='output image file name', exists=True)
    matrix = File(desc='matrix to align input file')



class Allineate(AFNICommand):
    """Program to align one dataset (the 'source') to a base dataset

    For complete details, see the `3dAllineate Documentation.
    <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dAllineate.html>`_

    Examples
    ========

    >>> from nipype.interfaces import afni as afni
    >>> allineate = afni.Allineate()
    >>> allineate.inputs.in_file = 'functional.nii'
    >>> allineate.inputs.out_file= 'functional_allineate.nii'
    >>> allineate.inputs.in_matrix= 'cmatrix.mat'
    >>> res = allineate.run() # doctest: +SKIP

    """

    _cmd = '3dAllineate'
    input_spec = AllineateInputSpec
    output_spec = AllineateOutputSpec



class VolregInputSpec(AFNICommandInputSpec):

    in_file = File(desc='input file to 3dvolreg',
                   argstr='%s',
                   position=-1,
                   mandatory=True,
                   exists=True,
                   copyfile=False)
    out_file = File(name_template="%s_volreg", desc='output image file name',
                    argstr='-prefix %s', name_source="in_file")

    basefile = File(desc='base file for registration',
                    argstr='-base %s',
                    position=-6,
                    exists=True)
    zpad = traits.Int(desc='Zeropad around the edges' +
                      ' by \'n\' voxels during rotations',
                      argstr='-zpad %d',
                      position=-5)
    md1d_file = File(name_template='%s_md.1D', desc='max displacement output file',
                    argstr='-maxdisp1D %s', name_source="in_file",
                    keep_extension=True, position=-4)
    out_matrix_file = File(name_template='%s.aff12.1D', desc='motion parameters output matrix',
                     argstr='-1Dmatrix_save %s',
                     name_source="in_file",
                     keep_extension=True)
    verbose = traits.Bool(desc='more detailed description of the process',
                          argstr='-verbose')
    timeshift = traits.Bool(desc='time shift to mean slice time offset',
                            argstr='-tshift 0')
    copyorigin = traits.Bool(desc='copy base file origin coords to output',
                             argstr='-twodup')


class VolregOutputSpec(TraitedSpec):
    out_file = File(desc='registered file', exists=True)
    md1d_file = File(desc='max displacement info file', exists=True)
    out_matrix_file = File(desc='motion parameters matrix file', exists=True)


class Volreg(AFNICommand):
    """Register input volumes to a base volume using AFNI 3dvolreg command

    For complete details, see the `3dvolreg Documentation.
    <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dvolreg.html>`_

    Examples
    ========

    >>> from nipype.interfaces import afni as afni
    >>> volreg = afni.Volreg()
    >>> volreg.inputs.in_file = 'functional.nii'
    >>> volreg.inputs.args = '-Fourier -twopass'
    >>> volreg.inputs.zpad = 4
    >>> volreg.inputs.outputtype = "NIFTI"
    >>> volreg.cmdline #doctest: +ELLIPSIS
    '3dvolreg -Fourier -twopass -1Dfile functional.1D -prefix functional_volreg.nii -zpad 4 -maxdisp1D functional_md.1D functional.nii'
    >>> res = volreg.run() # doctest: +SKIP

    """

    _cmd = '3dvolreg'
    input_spec = VolregInputSpec
    output_spec = VolregOutputSpec
