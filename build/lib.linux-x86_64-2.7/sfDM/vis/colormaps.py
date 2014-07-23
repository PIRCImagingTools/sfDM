
from matplotlib.colors import LinearSegmentedColormap


def blue():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 1.0))
            }
    return  LinearSegmentedColormap('Blue', cdict)


def blue_r():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 1.0))
            }
    return  LinearSegmentedColormap('Blue_r', cdict)

def darkgreen():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.2),
                      (1.0, 0.5, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Green', cdict)

def darkgreen_r():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.5),
                      (1.0, 0.2, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Green_r', cdict)


def green():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 1.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Green', cdict)

def green_r():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 1.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Green_r', cdict)

def lightblue():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.2),
                      (1.0, 0.9, 1.0)),
             'blue': ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 0.0))
            }
    return  LinearSegmentedColormap('Green', cdict)

def lightblue_r():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.9),
                      (1.0, 0.2, 1.0)),
             'blue': ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 0.0))
            }
    return  LinearSegmentedColormap('Green_r', cdict)


def orange():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 0.0)),
            'green': ((0.0, 0.0, 0.2),
                      (1.0, 0.5, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Green', cdict)

def orange_r():

    cdict = {'red':  ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 0.0)),
            'green': ((0.0, 0.0, 0.5),
                      (1.0, 0.2, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Green_r', cdict)

def purple():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 1.0)),
             'blue': ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 0.0))
            }
    return  LinearSegmentedColormap('Green', cdict)

def purple_r():

    cdict = {'red':  ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 0.0))
            }
    return  LinearSegmentedColormap('Green_r', cdict)


def red():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 1.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Red', cdict)

def red_r():

    cdict = {'red':  ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 1.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('Red_r', cdict)

def yellow():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 0.0)),
            'green': ((0.0, 0.0, 0.3),
                      (1.0, 1.0, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('yellow_green', cdict)



def yellow_r():

    cdict = {'red':  ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 0.0)),
            'green': ((0.0, 0.0, 1.0),
                      (1.0, 0.3, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('yellow_green_r', cdict)


def yellow_green():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.9, 0.0)),
            'green': ((0.0, 0.0, 0.4),
                      (1.0, 0.8, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('yellow_green', cdict)



def yellow_green_r():

    cdict = {'red':  ((0.0, 0.0, 0.9),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.8),
                      (1.0, 0.4, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('yellow_green_r', cdict)


################################################
### SEGMENTATION COLORS
################################################
def brainstem():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0))
            }
    return  LinearSegmentedColormap('brainstem', cdict)

def cerebellum():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0)),
             'blue': ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0))
            }
    return  LinearSegmentedColormap('cerebellum', cdict)

def cortex():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('cortex', cdict)

def csf():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0)),
            'green': ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('csf', cdict)

def dgm():

    cdict = {'red':  ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0))
            }
    return  LinearSegmentedColormap('csf', cdict)


def wm():

    cdict = {'red':  ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
            'green': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'blue': ((0.0, 0.0, 0.3),
                      (1.0, 0.9, 0.0))
            }
    return  LinearSegmentedColormap('wm', cdict)

if __name__ =='__main__':
    from matplotlib import pyplot, mpl

    fig = pyplot.figure(figsize=(8,3))
    ax1 = fig.add_axes([0.05,0.8,0.9,0.15])

    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=green_r(),
                                    orientation='horizontal')
    pyplot.show()
