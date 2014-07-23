"""
Draw time line from list of images
Required:
    timeline.json files listing the files in the desired order
"""

from PIL import Image,ImageDraw, ImageFont
import json,os
import numpy as np


config_file = os.environ['fdm_config']
timeline_file = os.environ['fdm_timeline']


with open(config_file, 'r') as f:
    cfg = json.load(f)

with open(timeline_file, 'r') as f:
    timeline = json.load(f)

PID=cfg['PID']

BaseDir = cfg['parent_dir']
ImageDir = BaseDir+'/FDM/Outputs/Images/'
PlotDir = BaseDir+'/FDM/Outputs/Plots/'
MetricDir = BaseDir+'/FDM/Outputs/Metrics/'

Treatment = cfg['treatment']



##################################################################################

print "Creating Time Line"

baseline_scan_list = timeline['baseline']
serial_scan_list = timeline['serial']

baseline_list = ['scan_{0}-scan_{1}.png'.format(scan[5:7],scan[15:17]) for
                                       scan in baseline_scan_list]
serial_list = ['scan_{0}-scan_{1}.png'.format(scan[5:7],scan[15:17]) for
                                       scan in serial_scan_list]


baseline_time = [int(cfg[scan[:7]]['time']) for
                                        scan in baseline_scan_list]
serial_time = [int(cfg[scan[:7]]['time']) for
                                        scan in serial_scan_list]
if Treatment:
    basedate = int(cfg['v_days'])
    scans_before = np.size(np.where(np.array(baseline_time) < basedate))
else:
    scans_before = 0

p_width = 533
p_height = 400
m_width = 533
m_height = 400
vspace = 30
time_unit = 5 #pixels


basedate= int(basedate) * time_unit + p_width*(scans_before+1)
longest = np.max(np.vstack((serial_time, baseline_time)))

image_width=len(baseline_list)*(p_width) +int(longest)*time_unit + m_width+ 10
image_height=(p_height*4 + vspace*5) + 10

baseline_plot_files=[PlotDir+plot for plot in baseline_list]
baseline_plot_images=[Image.open(filename) for filename in baseline_plot_files]

baseline_map_files=[ImageDir+dmap for dmap in baseline_list]
baseline_map_images=[Image.open(filename) for filename in baseline_map_files]

serial_plot_files=[PlotDir+plot for plot in serial_list]
serial_plot_images=[Image.open(filename) for filename in serial_plot_files]

serial_map_files=[ImageDir+dmap for dmap in serial_list]
serial_map_images=[Image.open(filename) for filename in serial_map_files]

# create metrics file
baseline_metrics = [MetricDir+csv[:-3]+'csv' for csv in baseline_list]
serial_metrics = [MetricDir+csv[:-3]+ 'csv' for csv in serial_list]

def write_metrics(filelist, outfile):
    csvout = open(outfile, 'wb')
    with open(filelist[0], 'r') as f:
            csvout.write(f.read())
    for csv in filelist[1:]:
        with open(csv, 'r') as f:
            f.next()
            for line in f:
                csvout.write(line)
    csvout.close()

write_metrics(baseline_metrics, BaseDir+'/baseline.csv')
write_metrics(serial_metrics, BaseDir+'/serial.csv')


img = Image.new("RGB",(image_width,image_height), (255,255,255))   #w, h

#Lines

draw = ImageDraw.Draw(img)
draw.rectangle((0, p_height/2 + vspace+50,    #### First black line
            image_width,p_height/2 + vspace + 55),
            fill='#000000')  #x1,y1, x2,y2
draw.rectangle((0, 2.5*p_height + 3*vspace,     #### Second black line
           image_width, 2.5*p_height + 3*vspace + 5),
           fill='#000000')  #x1,y1, x2,y2
draw.rectangle((0, image_height/2 - 85,        #### Middle blue time line
           image_width,image_height/2 - 70),
           fill='#0000ff')  #x1,y1, x2,y2
if Treatment:
    draw.rectangle((basedate-5, 0,                  ##### Vertical baseline
           basedate-1,image_height),
           fill='#ff0000')  #x1,y1, x2,y2


    #WEIGHTS
weight_image = Image.open(ImageDir+PID+'_Weights.png')
w,h = weight_image.size
weight_image = weight_image.crop((int(w/2.5) , int(h/15), w - int(w/3), h - int(h/20) ))
WeightMap = weight_image.resize((int(p_width*1.2), p_height*3), Image.ANTIALIAS)
ImageDraw.floodfill(WeightMap, (0,0), (255,255,255))
img.paste(WeightMap, (0, vspace + 70))


fontpath='/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'
font = ImageFont.truetype(fontpath, 60)
draw.text((p_width, image_height/2-70), 'Days from first scan', fill='#0000ff', font=font)

if Treatment:
    draw.text((basedate+15,3), 'Baseline treatment', fill='#ff0000', font=font)


for i in range(len(baseline_map_images)):
    BasePlot = baseline_plot_images[i].resize((p_width,p_height), Image.ANTIALIAS)
    BaseMap = baseline_map_images[i].resize((m_width, m_height), Image.ANTIALIAS)
    ImageDraw.floodfill(BaseMap,(0,0),(255,255,255))

    SerialPlot = serial_plot_images[i].resize((p_width, p_height), Image.ANTIALIAS)
    SerialMap = serial_map_images[i].resize((m_width, m_height), Image.ANTIALIAS)
    ImageDraw.floodfill(SerialMap,(0,0), (255,255,255))


    img.paste(BaseMap, (time_unit*int(baseline_time[i]) + p_width*(i+1),
                        p_height+1*vspace-70))
    img.paste(SerialMap, (time_unit*int(serial_time[i])+ p_width*(i+1),
                         3*p_height+3*vspace-70))

    img.paste(BasePlot, (time_unit*int(baseline_time[i]) + p_width*(i+1),
                        vspace+50))
    img.paste(SerialPlot, (time_unit*int(serial_time[i])+ p_width*(i+1),
                        2*p_height+3*vspace))

    draw.text((time_unit*int(baseline_time[i]) + p_width*(i+1) + p_width/2 -20,
                image_height/2 - 160),
                str(baseline_time[i]), fill='#0000ff', font=font)



img.save(BaseDir+'/'+PID+'_w-timeline.png')
