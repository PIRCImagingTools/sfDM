import warnings

from nipype.interfaces.base import TraitedSpec, traits, File
from nipype.interfaces.afni.base import AFNICommand, AFNICommandInputSpec


warn = warnings.warn
warnings.filterwarnings('always', category=UserWarning)


class VolregInputSpec(AFNICommandInputSpec):

    in_file = File(desc='input file to 3dvolreg',
                   argstr='%s',
                   position=-1,
                   mandatory=True,
                   exists=True)
    out_file = File("%s_volreg", desc='output image file name',
                    argstr='-prefix %s', name_source="in_file", usedefault=True)

    basefile = File(desc='base file for registration',
                    argstr='-base %s',
                    position=-6,
                    exists=True)
    zpad = traits.Int(desc='Zeropad around the edges' +
                      ' by \'n\' voxels during rotations',
                      argstr='-zpad %d',
                      position=-5)
    md1dfile = File(desc='max displacement output file',
                    argstr='-maxdisp1D %s',
                    position=-4)
    oned_file = File('%s.1D', desc='1D movement parameters output file',
                     argstr='-1Dfile %s',
                     name_source="in_file",
                     keep_extension=True,
                     usedefault=True)
    dfile = File("%s_dfile",desc='displacement output file',
        argstr='-dfile %s',
        name_source="in_file",
        usedefault=True,
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
    oned_file = File(desc='movement parameters info file', exists=True)
    dfile = File(desc='displacement file', exists=True)

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
    >>> volreg.cmdline
    '3dvolreg -Fourier -twopass -1Dfile functional.1D -prefix functional_volreg.nii -zpad 4 functional.nii'
    >>> res = volreg.run() # doctest: +SKIP

    """

    _cmd = '3dvolreg'
    input_spec = VolregInputSpec
    output_spec = VolregOutputSpec


class TransformInputSpec(AFNICommandInputSpec):

    in_file = File(desc='input file to 3drotate',
       argstr='%s',
       position=-1,
       mandatory=True,
       exists=True)
    out_file = File("%s_FFT", desc='output image file name',
        argstr='-prefix %s', name_source="in_file", usedefault=True)
    dfile = File(desc='displacement file',
        argstr='-dfile %s',
        position=1)


class TransformOutputSpec(TraitedSpec):
    out_file = File(desc='registered file', exists=True)


class Transform(AFNICommand):
    """3dRotate interface
    For complete details, see the `3drotate Documentation.
    <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dvolreg.html>`_

        """

    _cmd = '3drotate'
    input_spec = TransformInputSpec
    output_spec = TransformOutputSpec

