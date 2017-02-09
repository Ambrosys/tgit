
colors = [
    "#2c3e50",
    "#c0392b",
    "#27ae60",
    "#f39c12",
    "#2980b9",
    "#8e44ad",
    "#16a085",
    "#e74c3c",
    "#2ecc71",
    "#f1c40f",
    "#3498db",
    "#2AA198",
    "#ecf0f1"
    ]

from PyQt5 import QtGui
import skimage.color
import numpy as np

def optimizeForBackground( color ):
    return _specificDistanceInLabToReferenceColor( color, QtGui.QColor( 255, 255, 255 ), 9.0 )

def _specificDistanceInLabToReferenceColor( color, referenceColor, distance ):
    [[lab]] = skimage.color.rgb2lab( [[[ color.redF(), color.greenF(), color.blueF() ]]] )
    [[lab_reference]] = skimage.color.rgb2lab( [[[ referenceColor.redF(), referenceColor.greenF(), referenceColor.blueF() ]]] )
    lab_fromReference = lab - lab_reference
    lab_normalized = lab_fromReference / np.linalg.norm( lab_fromReference ) * distance + lab_reference
    [[rgb]] = skimage.color.lab2rgb( [[ lab_normalized ]] )
    for i in range(3):
        rgb[i] = min( 1.0, max( 0.0, rgb[i] ) )
    result = QtGui.QColor()
    result.setRedF( rgb[0] )
    result.setGreenF(rgb[1] )
    result.setBlueF( rgb[2] )
    return result
