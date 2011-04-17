# -*- coding: utf-8 -*-
#-----------------------------------------------
# Filename: core.py
#  Purpose: Wrapper for mopad
#   Author: Tobias Megies, Moritz Beyreuther
#    Email: megies@geophysik.uni-muenchen.de
#
# Copyright (C) 2008-2011 ObsPy Development Team
#-----------------------------------------------
"""
ObsPy bindings to mopad
"""

from matplotlib import pyplot as plt, patches
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from mopad import BeachBall as mopad_BeachBall
from mopad import MomentTensor as mopad_MomentTensor


def Beach(fm, linewidth=2, facecolor='b', bgcolor='w', edgecolor='k',
          alpha=1.0, xy=(0, 0), width=200, size=100, nofill=False,
          zorder=100):
    """
    Return a beach ball as a collection which can be connected to an
    current matplotlib axes instance (ax.add_collection).
    
    S1, D1, and R1, the strike, dip and rake of one of the focal planes, can 
    be vectors of multiple focal mechanisms.
    
    :param fm: Focal mechanism that is either number of mechanisms (NM) by 3 
        (strike, dip, and rake) or NM x 6 (Mxx, Myy, Mzz, Mxy, Mxz, Myz - the 
        six independent components of the moment tensor). The strike is of the 
        first plane, clockwise relative to north. 
        The dip is of the first plane, defined clockwise and perpendicular to 
        strike, relative to horizontal such that 0 is horizontal and 90 is 
        vertical. The rake is of the first focal plane solution. 90 moves the 
        hanging wall up-dip (thrust), 0 moves it in the strike direction 
        (left-lateral), -90 moves it down-dip (normal), and 180 moves it 
        opposite to strike (right-lateral). 
    :param size: Controls the number of interpolation points for the
        curves. Minimum is automatically set to 100.
    :param facecolor: Color to use for quadrants of tension; can be a string, e.g. 
        'r', 'b' or three component color vector, [R G B].
    :param edgecolor: Color of the edges.
    :param bgcolor: The background color, usually white.
    :param alpha: The alpha level of the beach ball.
    :param xy: Origin position of the beach ball as tuple.
    :param width: Symbol size of beach ball.
    :param nofill: Do not fill the beach ball, but only plot the planes.
    :param zorder: Set zorder. Artists with lower zorder values are drawn
                   first.
    """
    mt = mopad_MomentTensor(fm, "USE")
    bb = mopad_BeachBall(mt)
    bb._setup_BB()
    
    res = width/2.0
    neg_nodalline = bb._nodalline_negative_final_US
    pos_nodalline = bb._nodalline_positive_final_US
    US             = bb._unit_sphere
    tension_colour = bb._plot_tension_colour
    pressure_colour = bb._plot_pressure_colour

    coll = []
    fc = []
    coll.append(xy2patch(US[0,:], US[1,:], res, xy))
    fc.append(tension_colour)
    coll.append(xy2patch(neg_nodalline[0,:], neg_nodalline[1,:], res, xy))
    fc.append(pressure_colour)
    coll.append(xy2patch(pos_nodalline[0,:], pos_nodalline[1,:], res, xy))
    fc.append(pressure_colour)
    if bb._plot_curve_in_curve != 0:
        coll.append(xy2patch(US[0,:], US[1,:], res, xy))
        fc.append(tension_colour)
        if bb._plot_curve_in_curve < 1 :
            coll.append(xy2patch(neg_nodalline[0,:], neg_nodalline[1,:], res, xy))
            fc.append(pressure_colour)
            coll.append(xy2patch(pos_nodalline[0,:], pos_nodalline[1,:], res, xy))
            fc.append(tension_colour)
        else:
            coll.append(xy2patch(neg_nodalline[0,:], neg_nodalline[1,:], res, xy))
            fc.append(pressure_colour)
            coll.append(xy2patch(pos_nodalline[0,:], pos_nodalline[1,:], res, xy))
            fc.append(tension_colour)
    collection = PatchCollection(coll, match_original=False)
    collection.set_facecolors(fc)
    collection.set_alpha(alpha)
    collection.set_linewidth(linewidth)
    collection.set_zorder(zorder)
    return collection

def Beachball(fm, size=200, linewidth=2, facecolor='b', edgecolor='k',
              bgcolor='w', alpha=1.0, xy=(0, 0), width=200, outfile=None,
              format=None, nofill=False, fig=None):
    """
    Draws a beach ball diagram of an earthquake focal mechanism. 
    
    S1, D1, and R1, the strike, dip and rake of one of the focal planes, can 
    be vectors of multiple focal mechanisms.

    :param size: Draw with this diameter.
    :param fig: Give an existing figure instance to plot into. New Figure if
                set to None.
    :param format: If specified the format in which the plot should be
                   saved. E.g. (pdf, png, jpg, eps)

    For info on the remaining parameters see the
    :func:`~obspy.imaging.beachball.Beach` function of this module.
    """
    mt = mopad_MomentTensor(fm, "USE")
    bb = mopad_BeachBall(mt)
    bb.ploBB({})

 
def xy2patch(x, y, res, xy): 
    # transform into the Path coordinate system  
    x = x * res + xy[0] 
    y = y * res + xy[1] 
    verts = zip(x.tolist(), y.tolist()) 
    codes = [Path.MOVETO] 
    codes.extend([Path.LINETO]*(len(x)-2)) 
    codes.append(Path.CLOSEPOLY) 
    path = Path(verts, codes)  
    return patches.PathPatch(path) 


if __name__ == '__main__':
    """
          [1.45, -6.60, 5.14, -2.67, -3.16, 1.36],
          [1, 1, 1, 0, 0, 0],
          [-1, -1, -1, 0, 0, 0],
    """
    mt = [
          [0.91, -0.89, -0.02, 1.78, -1.55, 0.47],
          [274, 13, 55],
          [130, 79, 98],
          [264.98, 45.00, -159.99],
          [160.55, 76.00, -46.78],
          [235, 80, 35],
          [138, 56, 168],
          [1, -2, 1, 0, 0, 0],
          [1, -1, 0, 0, 0, 0],
          [1, -1, 0, 0, 0, -1],
          [179, 55, -78],
          [10, 42.5, 90],
          [10, 42.5, 92],
          [150, 87, 1],
          [0.99, -2.00, 1.01, 0.92, 0.48, 0.15],
          [5.24, -6.77, 1.53, 0.81, 1.49, -0.05],
          [16.578, -7.987, -8.592, -5.515, -29.732, 7.517],
          [-2.39, 1.04, 1.35, 0.57, -2.94, -0.94],
          [150, 87, 1]
    ]


    # Initialize figure
    fig = plt.figure(1, figsize=(3, 3), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')

    # Plot the stations or borders
    ax.plot([-100, -100, 100, 100], [-100, 100, -100, 100], 'rv')

    x = -100
    y = -100
    for i, t in enumerate(mt):
        # add the beachball (a collection of two patches) to the axis
        ax.add_collection(Beach(t, size=100, width=30, xy=(x, y),
                                linewidth=.6))
        x += 50
        if (i + 1) % 5 == 0:
            x = -100
            y += 50

    # Set the x and y limits and save the output
    ax.axis([-120, 120, -120, 120])
    plt.show()
