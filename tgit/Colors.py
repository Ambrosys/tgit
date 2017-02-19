from PyQt5 import QtGui
import skimage.color
import numpy

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


class ColorGroup:
    def __init__( self ):
        self.map_name_color = {}
        self.colors = []

    def addColor( self, name, color ):
        """
        :type color: Color
        """
        color = Color( name, color )
        self.map_name_color[name] = color
        self.colors.append( color )

    def getColor( self, name ):
        return self.map_name_color[name]

    def optimize( self ):
        circleCenter = rgb2lab( qt2rgb( QtGui.QColor( 255, 255, 255 ) ) )
        circleR = 8.0
        def correct( lab ):
            return projectToCircle( lab, circleCenter, circleR )

        for color in self.colors:
            color.lab = rgb2lab( qt2rgb( color.getOriginalColor() ) )
            color.lab = correct( color.lab )
            color.force = numpy.zeros( 3 )

        isBalanced = False
        while not isBalanced:
            isBalanced = True
            for subject in self.colors:
                for color in self.colors:
                    if color == subject:
                        continue
                    colorToSubject = subject.lab - color.lab
                    distance = numpy.linalg.norm( colorToSubject )
                    accurateDistance = skimage.color.deltaE_ciede2000( color.lab, subject.lab )
                    assert accurateDistance >= 0.0
                    if accurateDistance < 3.0:
                        if accurateDistance == 0.0:
                            subject.force += [numpy.random.random(), numpy.random.random(), numpy.random.random()]
                        else:
                            subject.force += 0.5 * (colorToSubject / distance)
            for subject in self.colors:
                if numpy.count_nonzero( subject.force ):
                    isBalanced = False
                    subject.lab += subject.force
                    subject.lab = correct( subject.lab )
                    subject.lab = rgb2lab( limitToRgb( lab2rgb( subject.lab ) ) )
                    subject.force = numpy.zeros( 3 )

        for color in self.colors:
            color.optimized = rgb2qt( limitToRgb( lab2rgb( color.lab ) ) )


class Color:
    def __init__( self, name, color ):
        """
        :type color: QtGui.QColor
        """
        self.name = name
        self.original = color
        self.optimized = None

    def getOriginalColor( self ):
        return self.original

    def getOptimizedColor( self ):
        assert self.optimized is not None
        return self.optimized



def optimizeForBackground( color ):
    return _specificDistanceInLabToReferenceColor( color, QtGui.QColor( 255, 255, 255 ), 9.0 )

def _specificDistanceInLabToReferenceColor( color, referenceColor, distance ):
    lab_subject = rgb2lab( qt2rgb( color ) )
    lab_reference = rgb2lab( qt2rgb( referenceColor ) )
    lab_referenceToSubject = lab_subject - lab_reference
    lab = normalized( lab_referenceToSubject ) * distance + lab_reference
    return rgb2qt( limitToRgb( lab2rgb( lab ) ) )

def projectToCircle( point, center, r ):
    centerToPoint = point - center
    return normalized( centerToPoint ) * r + center

def limitToRgb( rgb ):
    #for i in range( len( rgb ) ):
    #    rgb[i] = min( 1.0, max( 0.0, rgb[i] ) )
    return [min( 1.0, max( 0.0, value ) ) for value in rgb]

def normalized( vector ):
    return vector / numpy.linalg.norm( vector )

def qt2rgb( qt ):
    return [qt.redF(), qt.greenF(), qt.blueF()]

def rgb2qt( rgb ):
    qt = QtGui.QColor()
    qt.setRedF( rgb[0] )
    qt.setGreenF( rgb[1] )
    qt.setBlueF( rgb[2] )
    return qt

def rgb2lab( rgb ):
    [[lab]] = skimage.color.rgb2lab( [[rgb]] )
    return lab

def lab2rgb( lab ):
    [[rgb]] = skimage.color.lab2rgb( [[lab]] )
    return rgb