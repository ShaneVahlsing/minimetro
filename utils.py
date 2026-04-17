from __future__ import annotations
import math
from enum import Enum

# translates and rotates x and y based on the rotation angle
# checks if the x and y are within the defined rectangle
# returns true if x and y are in boundary
# otherwise returns false
def rectInBoundary(pointX: float, pointY: float, rectX: float, rectY: float, 
                   width: float, height: float | None = None, 
                   rotateAngle: float = 0) -> bool:
    
    if height == None: 
        height = width

    angleInRadians: float = math.radians(90-rotateAngle)

    translatedPointX: float = pointX - rectX
    translatedPointY: float = pointY - rectY

    # formula found using 2d rotation matrix:
    # [ x ] * [cos(t), -sin(t)] = [x*cos(t) - y*sin(t)]
    # [ y ]   [sin(t), cos(t)]    [x*sin(t) + y*cos(t)] 

    rotatedPointX: float = rectX + translatedPointX * math.cos(
        angleInRadians) - translatedPointY * math.sin(angleInRadians)
    
    rotatedPointY: float = rectY + translatedPointX * math.sin(
        angleInRadians) + translatedPointY * math.cos(angleInRadians)

    xBoundary: float = width/2
    yBoundary: float = height/2
    
    inXBoundary: bool = abs(distance(rectX, 0, rotatedPointX, 0)) <= xBoundary
    inYBoundary: bool = abs(distance(0, rectY, 0, rotatedPointY)) <= yBoundary

    return inXBoundary and inYBoundary

# finds the x and y differences between the 2 points
# calculates arctangent of x/y as angle, uses atan2 to handle division by 0 errors
# returns angle
def findAngleOfLine(x1: float, y1: float, x2: float, y2:float) -> float:
    xDistance: float = abs(x1-x2)
    yDistance: float = abs(y1-y2)

    angleOfLine: float = math.atan2(xDistance, yDistance)
    return angleOfLine

# returns distance between 2 coordinates
def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x1-x2)**2 + (y1-y2)**2)**.5

# defines types of stations and their sizes as station | passenger
class StationType(Enum):
    CIRCLE = 'drawCircle 13 | 5'
    SQUARE = 'drawRect 22, 22 | 10, 10'
    TRIANGLE = 'drawRegularPolygon 17, 3 | 7, 3'
    STAR = 'drawStar 17, 5 | 7, 5'

    @staticmethod
    def getValue(passengerOrStation: str, stationType: StationType
                 ) -> tuple[str, list[int]]:
        
        functionName, rest = stationType.value.split(' ', 1)

        if passengerOrStation == 'station':
            restOfString = rest.split('|')[0]
        elif passengerOrStation == 'passenger':
            restOfString = rest.split('|')[1]

        parameters = [int(p) for p in restOfString.split(',')]

        return functionName, parameters

