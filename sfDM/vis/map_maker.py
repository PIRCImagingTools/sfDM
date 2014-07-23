
from nipy import load_image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import colormaps
import matplotlib.pylab as pylab


def get_crop(mat):
    """ find first slice with non-zero voxels in each dimension""" 
    for i in xrange(mat.shape[0]):
        xmin = i
        if np.sum(mat[i, :, :]) > 0:
                break
    for i in xrange(mat.shape[0]-1, 0, -1):
        xmax = i
        if np.sum(mat[i, :, :]) > 0:
                break 
    for i in xrange(mat.shape[1]):
        ymin = i
        if np.sum(mat[:, i, :]) > 0:
                break 
    for i in xrange(mat.shape[1]-1, 0, -1):
        ymax = i
        if np.sum(mat[:, i, :]) > 0:
                break 
    for i in xrange(mat.shape[2]):
        zmin = i
        if np.sum(mat[:, :, i]) > 0:
                break 
    for i in xrange(mat.shape[2]-1, 0, -1):
        zmax = i
        if np.sum(mat[:, :, i]) > 0:
                break 
    return xmin,xmax,ymin,ymax,zmin,zmax

def normalize_dims(data, diag):
    x,y,z = 1,1,1
    if diag[0] < 0:
        x = -1
    if diag[1] < 0:
        y = -1
    if diag[2] < 0:
        z = -1

    return data[::x,::y,::z]

class MapMaker(object):

    def __init__(self, background):
        self.background = load_image(background)
        data = self.background.get_data()
        self.diag = self.background.affine.diagonal()[:3]
        self.x_trans, self.y_trans, self.z_trans = np.abs(self.diag)

        bg = normalize_dims(data, self.diag)

        vmax = bg.max()*.70
        vmin = bg.min()*.95

        self.xmin,self.xmax, self.ymin,self.ymax, self.zmin,self.zmax = get_crop(bg)
        self.image_list = []
        self.image_list.append((bg,cm.Greys_r, vmax, vmin, 1))


    def add_overlay(self, overlay, thr, limit, cmap, alpha=0.8):
        overlay = load_image(overlay)
        data = overlay.get_data()
        ovl = normalize_dims(data,self.diag)

        if limit == 'max':
            vmin = thr
            vmax = np.max(ovl)
            print 'using image max of ' + str(vmax) +' as threshold'
            ovl = np.ma.masked_less(ovl, thr)



        elif thr > limit:
            print "One or more overlays have inverse ranges,"
            print "beware of correct colormap!"
            ovl = np.ma.masked_greater(ovl, thr)
            vmax = thr
            vmin = limit

        else:
            ovl = np.ma.masked_less(ovl, thr)
            vmax = limit
            vmin = thr
        self.image_list.append((ovl, cmap, vmax, vmin, alpha))


    def display_Z(self, cut):
        for image in self.image_list:
            plt.imshow(np.rot90(image[0][:,:,cut],3), cmap=image[1],
                        vmax=image[2], vmin=image[3], alpha=image[4],
                        origin='lower',
                        extent=[0, self.x_trans*(self.xmax - self.xmin),
                                0, self.y_trans*(self.ymax - self.ymin)])
        plt.show()


    def save_Z(self, cut, savefile):
        for image in self.image_list:
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, cut],3),
                        cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                        origin='lower',
                        extent=[0, self.x_trans*(self.xmax - self.xmin),
                                0, self.y_trans*(self.ymax - self.ymin)])
        plt.savefig(savefile, dpi=300, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0.1)
        plt.close()

    def save_Y(self, cut, savefile):
        for image in self.image_list:
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, cut,self.zmin:self.zmax],3),
                       cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                        origin='lower',
                        extent=[0, self.x_trans*(self.xmax - self.xmin),
                                0, self.z_trans*(self.zmax - self.zmin)])
        plt.savefig(savefile, dpi=300, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0.1)
        plt.close()

    def save_X(self, cut, savefile):
        for image in self.image_list:
            plt.imshow(np.rot90(image[0][cut,self.ymin:self.ymax,self.zmin:self.zmax],3),
                        cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                        origin='lower',
                        extent=[0,self.y_trans*(self.ymax - self.ymin),
                                0, self.z_trans*(self.zmax - self.zmin)])
        plt.savefig(savefile, dpi=300, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0.1)
        plt.close()

    def save_3plane(self, X_cut, Y_cut, Z_cut, savefile):
        fig = pylab.figure(figsize=(4,3))
        for image in self.image_list:
            fig.add_subplot(1,3,1) ##### AXIAL
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, Z_cut],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.y_trans*(self.ymax - self.ymin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(1,3,2) ##### COR
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, Y_cut,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(1,3,3) #### SAG
            plt.imshow(np.rot90(image[0][X_cut,self.ymin:self.ymax,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0,self.y_trans*(self.ymax - self.ymin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')

        plt.savefig(savefile, dpi=500, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0)
        plt.close()

    def save_3plane_vertical(self, X_cut, Y_cut, Z_cut, savefile):
        fig = pylab.figure(figsize=(4,3))
        for image in self.image_list:
            fig.add_subplot(3,1,1) ##### AXIAL
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, Z_cut],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.y_trans*(self.ymax - self.ymin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(3,1,2) ##### COR
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, Y_cut,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(3,1,3) #### SAG
            plt.imshow(np.rot90(image[0][X_cut,self.ymin:self.ymax,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0,self.y_trans*(self.ymax - self.ymin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')

        plt.savefig(savefile, dpi=500, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0)
        plt.close()

    def save_3plane_crosshair(self, X_cut, Y_cut, Z_cut, savefile):
        fig = pylab.figure(figsize=(4,4))
        for image in self.image_list:
            fig.add_subplot(1,3,1) ##### AXIAL
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, Z_cut],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.y_trans*(self.ymax - self.ymin)],
                    origin='lower')
            plt.axhline(y=self.y_trans*(Y_cut-self.ymin),
                                        xmax=0.05, color='green') #A-P Marker
            plt.axhline(y=self.y_trans*(Y_cut-self.ymin),
                                        xmin=0.95, color='green') #A-P Marker 
            plt.axvline(x=self.x_trans*(X_cut-self.xmin),
                                        ymax=0.05, color='red') #R-L Marker
            plt.axvline(x=self.x_trans*(X_cut-self.xmin),
                                        ymin=0.95, color='red') #R-L Marker 
            plt.axis('off')

            fig.add_subplot(1,3,2) ##### COR
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, Y_cut,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axhline(y=self.z_trans*(Z_cut-self.zmin),
                                          xmax=0.05,color='blue') #I-S Marker OK
            plt.axhline(y=self.z_trans*(Z_cut-self.zmin),
                                          xmin=0.95,color='blue') #I-S Marker OK
            plt.axvline(x=self.x_trans*(X_cut-self.xmin),
                                          ymax=0.05, color='red') # R-L Marker
            plt.axvline(x=self.x_trans*(X_cut-self.xmin),
                                          ymin=0.95, color='red') # R-L Marker
            plt.axis('off')

            fig.add_subplot(1,3,3) #### SAG SPECIFIC TO STANDARD SPACE (ROTATE ABOUT Z AXIS )
            plt.imshow(np.rot90(image[0][-X_cut,self.ymin:self.ymax,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0,self.y_trans*(self.ymax - self.ymin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axhline(y=self.z_trans*(Z_cut-self.zmin),
                                       xmax=0.05,color='blue') #I-S Marker OK
            plt.axhline(y=self.z_trans*(Z_cut-self.zmin),
                                       xmin=0.95,color='blue') #I-S Marker OK
            plt.axvline(x=self.y_trans*(self.ymax-Y_cut),
                                       ymax=0.05, color='green')  #A-P Marker
            plt.axvline(x=self.y_trans*(self.ymax-Y_cut),
                                       ymin=0.95, color='green')  #A-P Marker THIS MAY BE A HACK
            plt.axis('off')

        plt.savefig(savefile, dpi=600, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0)
        plt.close()

    def save_strip(self, X_cut, Y_cut, Z_cut, Skip, savefile):
        fig = pylab.figure(figsize=(4,3))
        for image in self.image_list:
            fig.add_subplot(3,3,1) ##### AXIAL - SKIP
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, Z_cut-Skip],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.y_trans*(self.ymax - self.ymin)],
                    origin='lower')
            plt.axis('off')
            fig.add_subplot(3,3,2) ##### COR - SKIP
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, Y_cut-Skip,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')
            fig.add_subplot(3,3,3) #### SAG - SKIP
            plt.imshow(np.rot90(image[0][X_cut-Skip,self.ymin:self.ymax,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0,self.y_trans*(self.ymax - self.ymin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')
############################################
            fig.add_subplot(3,3,4) ##### AXIAL
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, Z_cut],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.y_trans*(self.ymax - self.ymin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(3,3,5) ##### COR
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, Y_cut,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(3,3,6) #### SAG
            plt.imshow(np.rot90(image[0][X_cut,self.ymin:self.ymax,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0,self.y_trans*(self.ymax - self.ymin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')
###########################################
            fig.add_subplot(3,3,7) ##### AXIAL + SKIP
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax,self.ymin:self.ymax, Z_cut+Skip],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.y_trans*(self.ymax - self.ymin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(3,3,8) ##### COR + SKIP
            plt.imshow(np.rot90(image[0][self.xmin:self.xmax, Y_cut+Skip,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0, self.x_trans*(self.xmax - self.xmin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off')

            fig.add_subplot(3,3,9) #### SAG + SKIP
            plt.imshow(np.rot90(image[0][X_cut+Skip,self.ymin:self.ymax,self.zmin:self.zmax],3),
                    cmap=image[1], vmax=image[2], vmin=image[3], alpha=image[4],
                    extent=[0,self.y_trans*(self.ymax - self.ymin),
                            0, self.z_trans*(self.zmax - self.zmin)],
                    origin='lower')
            plt.axis('off') 
        plt.savefig(savefile, dpi=500, facecolor=[0,0,0], bbox_inches=None,
                    pad_inches=0)
        plt.close()


if __name__ == '__main__':
    import getpass
    user = getpass.getuser()
    testdir = '/home/'+user+'/Desktop/layer/'
    bgimg = testdir+'HighResBrain.nii.gz'
    overlay = testdir+'TV005_02-TV005_01.nii'
    mask = testdir+'TV005_Tumor_Mask.nii'
    savefile = testdir+'screenshot.png'
    savefile2 = testdir+'screenshot2.png'
    savefile3 = testdir+'screenshot3.png'
    Testimage = MapMaker(bgimg)
    Testimage.add_overlay(mask, .1, 1, colormaps.green(), alpha=.4)
    Testimage.add_overlay(overlay, -400, -1000, colormaps.blue_r())
    Testimage.add_overlay(overlay, 400, 1000, colormaps.red())
    Testimage.save_Z(212, savefile)
    Testimage.save_Y(212, savefile2)
    Testimage.save_3plane(91, 212, 212, savefile3)

    #Testimage.display_axial(212)



