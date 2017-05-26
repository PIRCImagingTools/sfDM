#!/bin/python
import os
import json
import shlex
import subprocess
import sys
try:
#    import wxversion
#    wxversion.select('3.0')
    import wx
    import wx.lib.scrolledpanel as scrolled
except ImportError:
    raise ImportError,"wxPython module is required."

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

class Top_Panel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.frame = parent

        box = wx.StaticBox(self, -1, "Patient Info")
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer = wx.GridBagSizer(5, 5)

#------------------------------------------------------------------------#
        pid_label = wx.StaticText(self, -1, label=u"PID")
        self.pid_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)

        sizer.Add(pid_label, (0,0), (1,1),
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL ,5)
        sizer.Add(self.pid_field, (0, 1), (1, 2),
                        wx.ALIGN_LEFT, 10)

#------------------------------------------------------------------------#
        parent_dir_label = wx.StaticText(self, -1, label =u"Parent Dir")
        self.parent_dir_field = wx.TextCtrl(self, -1, value="",
                                                 style=wx.TE_PROCESS_ENTER)
        parent_dir_button = wx.Button(self, -1, label=u"...")
        sizer.Add(parent_dir_label, (1,0), (1,1),
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.parent_dir_field, (1,1), (1,2),
                                             wx.EXPAND|wx.ALIGN_LEFT,5)
        sizer.Add(parent_dir_button, (1,3), (1,1),
                    wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        self.Bind(wx.EVT_BUTTON, self.OnParDirButtonClick, parent_dir_button)

#---------------------------------------------------------------------------#
        struct_label = wx.StaticText(self, -1, label =u"Struct Brain")
        self.struct_field = wx.TextCtrl(self, -1, value="",
                                                 style=wx.TE_PROCESS_ENTER)
        struct_button = wx.Button(self, -1, label=u"...")

        tumor_center_label = wx.StaticText(self, -1, label=u"Tumor Center  ")

        tumor_center_x_label = wx.StaticText(self, -1, label=u"X ")
        self.tumor_center_x_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        tumor_center_y_label = wx.StaticText(self, -1, label=u" Y ")
        self.tumor_center_y_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        tumor_center_z_label = wx.StaticText(self, -1, label=u" Z ")
        self.tumor_center_z_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)

        sizer.Add(struct_label, (2,0), (1,1),
                  wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.struct_field, (2,1), (1,2),
                                             wx.EXPAND|wx.ALIGN_LEFT,5)
        sizer.Add(struct_button, (2,3), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        self.Bind(wx.EVT_BUTTON, self.OnStructButtonClick, struct_button)

        coord_sizer = wx.BoxSizer(wx.HORIZONTAL)

        coord_sizer.Add(tumor_center_label,0,
                         wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer.Add(tumor_center_x_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer.Add(self.tumor_center_x_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer.Add(tumor_center_y_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer.Add(self.tumor_center_y_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer.Add(tumor_center_z_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer.Add(self.tumor_center_z_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        sizer.Add(coord_sizer, (3,1), (1,2),
                                           wx.ALIGN_CENTER_VERTICAL,5)

#---------------------------------------------------------------------------#
        self.treatment = wx.CheckBox(self, -1, label=u"Treatment",
                                   style=wx.ALIGN_RIGHT)

        vaccine_label = wx.StaticText(self, -1,
                    label=u"Days post baseline", style=wx.ALIGN_LEFT)

        self.vaccine_field = wx.TextCtrl(self, -1, value="",
                                      style=wx.TE_PROCESS_ENTER)

        self.grid = wx.CheckBox(self, -1, label=u"Use GridEngine",
                                style=wx.ALIGN_RIGHT)

        self.nonlinear = wx.CheckBox(self, -1, label=u"Nonlinear Reg",
                                   style=wx.ALIGN_RIGHT)

        self.use_adc = wx.CheckBox(self, -1, label=u"Use ADC for Reg",
                                   style=wx.ALIGN_RIGHT)

        self.ref_space = wx.CheckBox(self, -1, label=u"ROI in Ref Space",
                                   style=wx.ALIGN_RIGHT)

        sizer.Add(self.treatment, (4,0), (1,1),
                 wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        sizer.Add(vaccine_label, (4,1), (1,1),
                wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        sizer.Add(self.vaccine_field, (4,2),(1,1),
                wx.ALIGN_LEFT,5)

        sizer.Add(self.grid, (5,0), (1,1),
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        sizer.Add(self.nonlinear, (5,1), (1,1),
                 wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        sizer.Add(self.ref_space, (5,2), (1,1),
                 wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        sizer.Add(self.use_adc, (5,3), (1,1),
                 wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
#--------------------------------------------------------------------------#
        sizer.AddGrowableCol(1)
        box_sizer.Add(sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        self.SetSizer(box_sizer)


    def OnParDirButtonClick(self, event):
            dir_picker = wx.DirDialog(self,
                    u"Choose dir", self.frame.default_dir)
            if dir_picker.ShowModal() == wx.ID_OK:
                self.parent_dir_field.SetValue(dir_picker.GetPath())
                self.parent_dir_field.SetFocus()
                self.frame.default_dir = dir_picker.GetPath()
            dir_picker.Destroy()

    def OnStructButtonClick(self, event):
            wildcard = "NIFTI image {*.nii}|*.nii|"\
                       "Compressed NIFTI {*.nii.gz}|*.nii.gz|"\
                       "All files {*.*}|*.*"
            file_picker = wx.FileDialog(self, "Choose file", self.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
            if file_picker.ShowModal() == wx.ID_OK:
                self.struct_field.SetValue(file_picker.GetPath())
                self.struct_field.SetFocus()
            file_picker.Destroy()


class Scan_Panel(scrolled.ScrolledPanel):

    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                 style=wx.SIMPLE_BORDER)
        self.frame = parent
        self.number_of_scans = 2
        self.time_points = []

        self.scans_sizer = wx.BoxSizer(wx.VERTICAL)


        self.scans_sizer.Add(Time_Point(self,'Scan 01'), 0,
                       wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        self.scans_sizer.Add(Time_Point(self,'Scan 02'), 0,
                        wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        self.SetSizerAndFit(self.scans_sizer)
        self.SetupScrolling(scroll_x=False)
        self.Layout()



    def OnAddScan(self, event):
        self.number_of_scans += 1
        new_tp_name = "Scan {0:0>2d}".format(self.number_of_scans)
        new_tp = Time_Point(self, new_tp_name)
        self.scans_sizer.Add(new_tp, 0,
                      wx.RIGHT|wx.LEFT|wx.EXPAND, 10)
        self.frame.Layout()


    def OnRmvScan(self,event):
        if self.number_of_scans > 2:
            self.number_of_scans -= 1
            self.time_points.pop()
            self.scans_sizer.Hide(self.number_of_scans)
            self.scans_sizer.Remove(self.number_of_scans)
            self.frame.Layout()


class Scan_Buttons(wx.Panel):

    def __init__(self,parent,top_panel,scan_panel):
        wx.Panel.__init__(self,parent,style=wx.NO_BORDER)
        self.frame = parent
        self.top = top_panel
        self.scans = scan_panel

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_scan_button = wx.Button(self,  label=u"+ Scan")
        self.rmv_scan_button = wx.Button(self,  label=u"- Scan")
        self.load = wx.Button(self,  label=u"Load Config")
        self.save = wx.Button(self,  label=u"Save Config")

        buttons_sizer.Add(self.rmv_scan_button, 0, wx.ALIGN_LEFT, 10)
        buttons_sizer.Add(self.add_scan_button, 0, wx.ALIGN_LEFT, 10)
        buttons_sizer.Add(self.load, 1, wx.ALIGN_RIGHT, 5)
        buttons_sizer.Add(self.save, 1, wx.ALIGN_RIGHT, 5)

        self.Bind(wx.EVT_BUTTON, self.OnLoad, self.load)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)
        self.Bind(wx.EVT_BUTTON, self.scans.OnAddScan, self.add_scan_button)
        self.Bind(wx.EVT_BUTTON, self.scans.OnRmvScan, self.rmv_scan_button)

        self.SetSizerAndFit(buttons_sizer)

    def OnLoad(self, event):
        wildcard = "Config file {*.json}|*.json|"\
                       "All files {*.*}|*.*"
        file_picker = wx.FileDialog(self, "Choose file", self.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
        if file_picker.ShowModal() == wx.ID_OK:
            config_file = file_picker.GetPath()
            with open(config_file, 'r') as f:
                config = json.loads(f.read())
            self.top.pid_field.SetValue(config['PID'])
            self.top.parent_dir_field.SetValue(config['parent_dir'])
            self.top.struct_field.SetValue(config['struct'])
            self.top.tumor_center_x_field.SetValue(config['tumor_center'][0])
            self.top.tumor_center_y_field.SetValue(config['tumor_center'][1])
            self.top.tumor_center_z_field.SetValue(config['tumor_center'][2])
            self.top.treatment.SetValue(config['treatment'])
            self.top.vaccine_field.SetValue(config['v_days'])
            self.top.grid.SetValue(config['grid_eng'])
            self.top.nonlinear.SetValue(config['non_linear'])
            self.top.use_adc.SetValue(config['use_adc'])
            self.top.ref_space.SetValue(config['ref_space'])

            if int(config['number_of_scans']) > self.scans.number_of_scans:
                diff = int(config['number_of_scans']) - self.scans.number_of_scans
                for x in range(diff):
                    self.scans.scans_sizer.Add(Time_Point(self.scans,
                        'Scan {0:0>2d}'.format((x+self.scans.number_of_scans+1))),
                        0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
                self.scans.number_of_scans += diff
                self.frame.Layout()

            elif int(config['number_of_scans']) < self.scans.number_of_scans:
                diff = self.scans.number_of_scans - int(config['number_of_scans'])
                for x in range(diff):
                    self.scans.number_of_scans -= 1
                    self.scans.time_points.pop()
                    self.scans.scans_sizer.Hide(self.scans.number_of_scans)
                    self.scans.scans_sizer.Remove(self.scans.number_of_scans)
                    self.frame.Layout()

            for x in range(int(config['number_of_scans'])):
                sid='scan_{0:0>2d}'.format((x+1))
                self.scans.time_points[x].dwi_field.SetValue(config[sid]['dwi'])
                self.scans.time_points[x].adc_field.SetValue(config[sid]['adc'])
                self.scans.time_points[x].ref_field.SetValue(config[sid]['ref'])
                self.scans.time_points[x].roi_field.SetValue(config[sid]['roi'])
                self.scans.time_points[x].time_field.SetValue(config[sid]['time'])

        file_picker.Destroy()


    def OnSave(self, event):
        config = {}
        pid = self.top.pid_field.GetValue()
        parent_dir = self.top.parent_dir_field.GetValue()
        struct = self.top.struct_field.GetValue()
        tumor_center_x = self.top.tumor_center_x_field.GetValue()
        tumor_center_y = self.top.tumor_center_y_field.GetValue()
        tumor_center_z = self.top.tumor_center_z_field.GetValue()
        tumor_center = [tumor_center_x,tumor_center_y,tumor_center_z]
        treatment = self.top.treatment.IsChecked()
        v_days = self.top.vaccine_field.GetValue()
        grid_eng = self.top.grid.IsChecked()
        non_linear = self.top.nonlinear.IsChecked()
        use_adc = self.top.use_adc.IsChecked()
        ref_space = self.top.ref_space.IsChecked()

        if os.path.isdir(parent_dir):
            config['PID'] = pid
            config['parent_dir'] = parent_dir
            config['struct'] = struct
            config['tumor_center'] = tumor_center
            config['treatment'] = treatment
            config['v_days'] = v_days
            config['grid_eng'] = grid_eng
            config['number_of_scans'] = self.scans.number_of_scans
            config['non_linear'] = non_linear
            config['use_adc'] = use_adc
            config['ref_space'] = ref_space

            for x in range(self.scans.number_of_scans):
                sid = 'scan_{0:0>2d}'.format((x+1))
                dwi = self.scans.time_points[x].dwi_field.GetValue()
                adc = self.scans.time_points[x].adc_field.GetValue()
                ref = self.scans.time_points[x].ref_field.GetValue()
                roi = self.scans.time_points[x].roi_field.GetValue()
                time = self.scans.time_points[x].time_field.GetValue()
                config[sid] = {}
                config[sid]['dwi'] = dwi
                config[sid]['adc'] = adc
                config[sid]['ref'] = ref
                config[sid]['roi'] = roi
                config[sid]['time'] = time

            if os.path.isfile(parent_dir+'/'+pid+'_config.json'):

                file_overwrite = wx.MessageDialog(self, "Overwrite Config?",
                                                "Config File Exists",  wx.YES_NO)
                if file_overwrite.ShowModal() == wx.ID_YES:
                    with open(parent_dir+'/'+pid+'_config.json', 'w') as f:
                        json.dump(config, f,sort_keys=True,ensure_ascii=False,
                                           indent=4,separators=(',',': '))
            else:
                with open(parent_dir+'/'+pid+'_config.json', 'w') as f:
                        json.dump(config, f,sort_keys=True,ensure_ascii=False,
                                           indent=4,separators=(',',': '))


        else:
            print "Parent directory does not exist!"



class Time_Point(wx.Panel):
    def __init__(self, parent, tp_name):
        wx.Panel.__init__(self,parent)
        self.parent = parent
        self.tp_name = tp_name
        self.parent.time_points.append(self)

        box = wx.StaticBox(self, -1, self.tp_name)
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        sizer = wx.GridBagSizer(3, 3)
##------------------------------------------------------------------------------
        self.dwi_label = wx.StaticText(self, -1, label=u'DWI')
        self.dwi_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)
        dwi_button = wx.Button(self, -1, label=u"...")

        sizer.Add(self.dwi_label, (0,0), (1,1),
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.dwi_field, (0, 1), (1, 1),
                        wx.EXPAND|wx.ALIGN_RIGHT, 5)
        sizer.Add(dwi_button, (0,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        self.Bind(wx.EVT_BUTTON, self.OnDWIButton, dwi_button)
##------------------------------------------------------------------------------
        self.adc_label = wx.StaticText(self, -1, label=u'ADC')
        self.adc_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)
        adc_button = wx.Button(self, -1, label=u"...")

        sizer.Add(self.adc_label, (1,0), (1,1),
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.adc_field, (1, 1), (1, 1),
                        wx.EXPAND|wx.ALIGN_RIGHT, 5)
        sizer.Add(adc_button, (1,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        self.Bind(wx.EVT_BUTTON, self.OnADCButton, adc_button)


##------------------------------------------------------------------------------------------------
        self.ref_label = wx.StaticText(self, -1, label=u'REF')
        self.ref_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)
        ref_button = wx.Button(self, -1, label=u"...")

        sizer.Add(self.ref_label, (2,0), (1,1),
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.ref_field, (2, 1), (1, 1),
                        wx.EXPAND|wx.ALIGN_RIGHT, 5)
        sizer.Add(ref_button, (2,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        self.Bind(wx.EVT_BUTTON, self.OnRefButton, ref_button)

##------------------------------------------------------------------------------------------------
        self.roi_label = wx.StaticText(self, -1, label=u'ROI')
        self.roi_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)
        roi_button = wx.Button(self, -1, label=u"...")

        sizer.Add(self.roi_label, (3,0), (1,1),
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.roi_field, (3, 1), (1, 1),
                        wx.EXPAND|wx.ALIGN_RIGHT, 5)
        sizer.Add(roi_button, (3,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        self.Bind(wx.EVT_BUTTON, self.OnROIButton, roi_button)

##------------------------------------------------------------------------------------------------
        time_label = wx.StaticText(self, -1, label=u"Time (Days)")
        self.time_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)

        sizer.Add(time_label, (4,0), (1,1),
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL ,5)
        sizer.Add(self.time_field, (4, 1), (1, 5),
                        wx.ALIGN_LEFT, 5)

##------------------------------------------------------------------------------------------------


        sizer.AddGrowableCol(1)
        box_sizer.Add(sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(box_sizer)


    def OnDWIButton(self, event):
        wildcard = "NIFTI image {*.nii}|*.nii|"\
                   "Compressed NIFTI {*.nii.gz}|*.nii.gz|"\
                   "All files {*.*}|*.*"
        file_picker = wx.FileDialog(self, "Choose file", self.parent.frame.default_dir,
                                            "", wildcard, wx.FD_OPEN)
        if file_picker.ShowModal() == wx.ID_OK:
            self.dwi_field.SetValue(file_picker.GetPath())
            self.dwi_field.SetFocus()
        file_picker.Destroy()

    def OnADCButton(self, event):
        wildcard = "NIFTI image {*.nii}|*.nii|"\
                   "Compressed NIFTI {*.nii.gz}|*.nii.gz|"\
                   "All files {*.*}|*.*"
        file_picker = wx.FileDialog(self, "Choose file", self.parent.frame.default_dir,
                                            "", wildcard, wx.FD_OPEN)
        if file_picker.ShowModal() == wx.ID_OK:
            self.adc_field.SetValue(file_picker.GetPath())
            self.adc_field.SetFocus()
        file_picker.Destroy()

    def OnRefButton(self, event):
            wildcard = "NIFTI image {*.nii}|*.nii|"\
                       "Compressed NIFTI {*.nii.gz}|*.nii.gz|"\
                       "All files {*.*}|*.*"
            file_picker = wx.FileDialog(self, "Choose file",
                                         self.parent.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
            if file_picker.ShowModal() == wx.ID_OK:
                self.ref_field.SetValue(file_picker.GetPath())
                self.ref_field.SetFocus()
            file_picker.Destroy()

    def OnROIButton(self, event):
            wildcard = "NIFTI image {*.nii}|*.nii|"\
                       "Compressed NIFTI {*.nii.gz}|*.nii.gz|"\
                       "All files {*.*}|*.*"
            file_picker = wx.FileDialog(self, "Choose file",
                                         self.parent.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
            if file_picker.ShowModal() == wx.ID_OK:
               self.roi_field.SetValue(file_picker.GetPath())
               self.roi_field.SetFocus()
            file_picker.Destroy()


class Run_Buttons(wx.Panel):
    def __init__(self,parent, top, scans):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.frame = parent
        self.top = top
        self.scans = scans

        sizer = wx.BoxSizer(wx.VERTICAL)


        self.reg = wx.Button(self,  label=u"Reg")
        sizer.Add(self.reg, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnReg, self.reg)

        self.time_points = wx.Button(self,  label=u"Time Points")
        sizer.Add(self.time_points, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnTimePoints, self.time_points)


        self.maps = wx.Button(self,  label=u"Maps")
        sizer.Add(self.maps, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnMaps, self.maps)

        self.time_line= wx.Button(self,  label=u"Time Line")
        sizer.Add(self.time_line, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnTimeLine, self.time_line)


        self.view = wx.Button(self,  label=u"View")
        sizer.Add(self.view, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnView, self.view)

        self.SetSizerAndFit(sizer)


    def OnReg(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        config_file = parent+'/'+pid+'_config.json'
        if os.path.isfile(config_file):
            env = os.environ.copy()
            env['fdm_config'] = config_file
            reg = os.path.abspath(local_path+'/../fdm/fdm_reg.py')
            cmd = 'ipython '+ reg
            task = shlex.split(cmd)
            subprocess.call(task, env=env)
            print "Reg done!\n"+\
            'Please check:\n'+\
            parent + '/FDM/Outputs/MergedRegs.nii.gz\n'+\
            'For any registration errors'
        else:
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'



    def OnMaps(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        config_file = parent+'/'+pid+'_config.json'
        timeline_file = parent+'/timeline.json'

        if not os.path.isfile(config_file):
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'

        elif not os.path.isfile(timeline_file):
            print 'timeline file: \n'+\
                     config_file+\
                     '\n Not Found!'

        else:
            env = os.environ.copy()
            env['fdm_config'] = config_file
            env['fdm_timeline'] = timeline_file
            maps = os.path.abspath(local_path+'/../fdm/fdm_maps.py')
            cmd = 'python '+ maps
            task = shlex.split(cmd)
            subprocess.call(task, env=env)
            print "Maps created!\n"



    def OnTimePoints(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        config_file = parent+'/'+pid+'_config.json'
        if os.path.isfile(config_file):
            map_dir = parent+'/FDM/Outputs/Plots'
            map_list = []
            scan_list = range(self.scans.number_of_scans)
            for tp1 in scan_list:
                for tp2 in scan_list:
                    if not tp1 == tp2:
                        map_list.append('scan_{0:0>2d} - scan_{1:0>2d}'\
                                        .format(tp2+1,tp1+1))
                scan_list = scan_list[1:]

            new_tl_window = Time_Line_Frame(self.top, map_list)
            new_tl_window.Show()
        else:
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'

    def OnTimeLine(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        config_file = parent+'/'+pid+'_config.json'
        timeline_file = parent+'/timeline.json'

        if not os.path.isfile(config_file):
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'

        elif not os.path.isfile(timeline_file):
            print 'timeline file: \n'+\
                     config_file+\
                     '\n Not Found!'
        else:
            env = os.environ.copy()
            env['fdm_config'] = config_file
            env['fdm_timeline'] = timeline_file
            pmaps = os.path.abspath(local_path+'/../fdm/fdm_timeline.py')
            cmd = 'python '+ pmaps
            task = shlex.split(cmd)
            subprocess.call(task, env=env)
            print "Time line created!\n"


    def OnView(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        config_file = parent+'/'+pid+'_config.json'
        map_list = []
        if os.path.isfile(config_file):
            if os.path.isfile(parent+'/FDM/Outputs/MergedRegs.nii.gz'):
                map_list.append('MergedRegs.nii.gz')
            map_dir = parent+'/FDM/Outputs/Maps'
            if os.path.isdir(map_dir):
                for pmap in os.listdir(map_dir):
                    map_list.append(pmap)
            new_view_window = View_Frame(self.top, map_list)
            new_view_window.Show()
        else:
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'


class Time_Line_Frame(wx.Frame):
    def __init__(self, parent, map_list):
        wx.Frame.__init__(self, parent, title="Time Line Selection")
        self.parent = parent
        self.map_list = map_list
        self.focused_window = None
        self.serial = []
        self.baseline =[]

        parent_dir = self.parent.parent_dir_field.GetValue()

        if os.path.isfile(parent_dir+'/timeline.json'):
            with open(parent_dir+'/timeline.json') as f:
                timeline = json.load(f)
            self.serial = timeline['serial']
            self.baseline = timeline['baseline']


        timeline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        baseline_sizer = wx.BoxSizer(wx.VERTICAL)
        serial_sizer = wx.BoxSizer(wx.VERTICAL)

        self.add_serial_button = wx.Button(self, label=u"+ Serial")
        self.add_baseline_button = wx.Button(self, label=u"+ Baseline")
        self.remove_serial_button = wx.Button(self,  label=u"Remove")
        self.remove_baseline_button = wx.Button(self,  label=u"Remove")
        self.save_button = wx.Button(self, label=u"Save")
        self.done_button = wx.Button(self, label=u"Done")
        baseline_label = wx.StaticText(self, -1, label =u"Baseline")
        serial_label = wx.StaticText(self, -1, label=u"Serial")

        buttons_sizer.Add(self.add_serial_button, 0, wx.EXPAND|wx.TOP, 5)
        buttons_sizer.Add(self.add_baseline_button, 0, wx.EXPAND, 5)
        buttons_sizer.Add(self.save_button, 0, wx.EXPAND|wx.TOP, 30)
        buttons_sizer.Add(self.done_button, 0, wx.EXPAND, 5)


        self.all_maps_list = wx.ListBox(choices=self.map_list,parent=self, name="All Maps",
                      style=wx.LB_EXTENDED|wx.LB_ALWAYS_SB, size=wx.Size(225,300))
        self.serial_list = wx.ListBox(choices=self.serial,parent=self, name="Serial List",
                      style=wx.LB_EXTENDED|wx.LB_ALWAYS_SB, size=wx.Size(225,300))
        self.baseline_list = wx.ListBox(choices=self.baseline,parent=self, name="Baseline List",
                      style=wx.LB_EXTENDED|wx.LB_ALWAYS_SB, size=wx.Size(225,300))

        self.Bind(wx.EVT_BUTTON, self.OnAddSerial, self.add_serial_button)
        self.Bind(wx.EVT_BUTTON, self.OnAddBaseline, self.add_baseline_button)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveSerial, self.remove_serial_button)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveBaseline, self.remove_baseline_button)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.OnDone, self.done_button)

        baseline_sizer.Add(self.baseline_list, 1, wx.EXPAND, 5)
        baseline_sizer.Add(self.remove_baseline_button, 0, wx.ALIGN_CENTER, 4)
        baseline_sizer.Add(baseline_label, 0, wx.ALIGN_CENTER, 4)

        serial_sizer.Add(self.serial_list, 1, wx.EXPAND, 5)
        serial_sizer.Add(self.remove_serial_button, 0, wx.ALIGN_CENTER, 4)
        serial_sizer.Add(serial_label, 0, wx.ALIGN_CENTER, 4)


        timeline_sizer.Add(self.all_maps_list, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5)
        timeline_sizer.Add(buttons_sizer, 0, wx.ALIGN_RIGHT|wx.EXPAND, 5)
        timeline_sizer.Add(serial_sizer, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5)
        timeline_sizer.Add(baseline_sizer, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5)

        self.SetSizerAndFit(timeline_sizer)

    def OnAddSerial(self,event):
        [self.serial_list.Append(self.map_list[i]) for
                                 i in self.all_maps_list.GetSelections()]


    def OnAddBaseline(self, event):
        [self.baseline_list.Append(self.map_list[i]) for
                                 i in self.all_maps_list.GetSelections()]


    def OnRemoveSerial(self, event):
        [self.serial_list.Delete(i) for i in self.serial_list.GetSelections()[::-1]]

    def OnRemoveBaseline(self, event):
        [self.baseline_list.Delete(i) for i in self.baseline_list.GetSelections()[::-1]]

    def OnSave(self, event):
        scan_list = {}
        serial = self.serial_list.GetStrings()
        baseline = self.baseline_list.GetStrings()
        parent_dir = self.parent.parent_dir_field.GetValue()

        if os.path.isdir(parent_dir):
            scan_list['serial'] = serial
            scan_list['baseline'] = baseline

            if os.path.isfile(parent_dir+'/timeline.json'):

                file_overwrite = wx.MessageDialog(self, "Overwrite Time Line List?",
                                                "Time Line List File Exists",  wx.YES_NO)
                if file_overwrite.ShowModal() == wx.ID_YES:
                    with open(parent_dir+'/timeline.json', 'w') as f:
                        json.dump(scan_list, f,sort_keys=True,ensure_ascii=False,
                                           indent=4,separators=(',',': '))
            else:
                with open(parent_dir+'/timeline.json', 'w') as f:
                        json.dump(scan_list, f,sort_keys=True,ensure_ascii=False,
                                           indent=4,separators=(',',': '))

    def OnDone(self, event):
        self.Close()

class View_Frame(wx.Frame):
    def __init__(self, parent, map_list):
        wx.Frame.__init__(self, parent, title="View Map")
        self.parent = parent
        self.map_list = map_list
        self.focused_window = None

        parent_dir = self.parent.parent_dir_field.GetValue()

        view_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.view_button = wx.Button(self, label=u"View")
        self.done_button = wx.Button(self, label=u"Done")

        buttons_sizer.Add(self.view_button, 0, wx.EXPAND, 5)
        buttons_sizer.Add(self.done_button, 0, wx.EXPAND, 5)


        self.all_maps_list = wx.ListBox(choices=self.map_list,parent=self, name="All Maps",
                      style=wx.LB_SINGLE|wx.LB_ALWAYS_SB, size=wx.Size(225,300))

        self.Bind(wx.EVT_BUTTON, self.OnView, self.view_button)
        self.Bind(wx.EVT_BUTTON, self.OnDone, self.done_button)


        view_sizer.Add(self.all_maps_list, 1, wx.ALIGN_RIGHT|wx.EXPAND, 5)
        view_sizer.Add(buttons_sizer, 0, wx.ALIGN_RIGHT|wx.EXPAND, 5)
        self.SetSizerAndFit(view_sizer)

    def OnView(self, event):
        scan_idx = self.all_maps_list.GetSelection()
        parent_dir = self.parent.parent_dir_field.GetValue()
        struct = self.parent.struct_field.GetValue()
        pid = self.parent.pid_field.GetValue()

        if self.map_list[scan_idx] == 'MergedRegs.nii.gz':
            image = parent_dir+'/FDM/Outputs/MergedRegs.nii.gz'
            cmd = 'fslview -m ortho '+struct+' -l GreyScale '+\
                image +' -l "GreyScale"'
        elif self.map_list[scan_idx] == pid+'_Tumor_Mask.nii':
            image = parent_dir+'/FDM/Outputs/Maps/'+pid+'_Tumor_Mask.nii'
            cmd = 'fslview -m ortho '+struct+' -l GreyScale '+\
                image +' -l "Hot"'


        else:
            image = parent_dir+'/FDM/Outputs/Maps/'+self.map_list[scan_idx]
            mask = parent_dir+'/FDM/Outputs/Maps/'+pid+'_Tumor_Mask.nii'
            cmd = 'fslview -m ortho '+struct+' -l GreyScale '+\
                mask+' -l "Green" -b 0,1 -t 0.4 '+image+\
                ' -l "Red" -b 400,1000 -t 0.8 ' +image+\
                ' -l "Blue" -b -400,-1000 -t 0.8'
        print "VIEW "+ image

        if os.path.isfile(image):
            env = os.environ.copy()
            task = shlex.split(cmd)
            subprocess.call(task, env=env)
        else:
            print 'Map file: \n'+\
                     image+\
                     '\n Not Found!'
    def OnDone(self, event):
        self.Close()

class SplashScreen(wx.SplashScreen):
    def __init__(self, parent=None):
        splash_bit = wx.Image(name=local_path+'/Splash.png').ConvertToBitmap()
        splash_style = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splash_duration = 2500
        wx.SplashScreen.__init__(self, splash_bit, splash_style,
                                 splash_duration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, evt):
        self.Hide()
        frame = fDM_Frame()
        frame.Show(True)
        evt.Skip()

class fDM_Frame(wx.Frame):

   def __init__(self):
        wx.Frame.__init__(self, parent=None, title="fDM GUI")
        self.default_dir = os.path.expanduser("~")
        self.frame_sizer = wx.GridBagSizer(5,5)

        top = Top_Panel(self)
        scans = Scan_Panel(self)
        scan_buttons = Scan_Buttons(self, top, scans)
        run_buttons = Run_Buttons(self, top, scans)

        self.frame_sizer.Add(top,(0,0),wx.DefaultSpan,
                             wx.ALL|wx.EXPAND,5)
        self.frame_sizer.Add(scan_buttons, (1,0), wx.DefaultSpan,
                           wx.ALL|wx.EXPAND,5)
        self.frame_sizer.Add(scans,(2,0),wx.DefaultSpan,
                             wx.ALL|wx.EXPAND,5)
        self.frame_sizer.Add(run_buttons,(0,1),(3,1),
                             wx.ALL|wx.EXPAND,5)

        self.frame_sizer.AddGrowableCol(0)
        self.frame_sizer.AddGrowableRow(2)

        self.SetSizerAndFit(self.frame_sizer)
        self.Show()


def start():
    app = wx.App(False)
    frame = SplashScreen()
    app.MainLoop()


if __name__ ==  "__main__":
    start()
