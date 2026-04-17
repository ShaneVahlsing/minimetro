from __future__ import annotations 
from cmu_graphics import *
from enum import Enum
from random import randint, choice
from itertools import cycle
import math
from typing import Iterator
import uuid

### --------------------------------
### HELPER FUNCTIONS AND CLASSES
### -----------------------------

# translates and rotates x and y based on the rotation angle
# checks if the x and y are within the defined rectangle
# returns true if x and y are in boundary
# otherwise returns false
def rectInBoundary(pointX: float, pointY: float, rectX: float, rectY: float, 
                   width: float, height: float = None, 
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

    def getValue(passengerOrStation: str, stationType: StationType
                 ) -> tuple[str, list[int]]:
        
        functionName, rest = stationType.value.split(' ', 1)

        if passengerOrStation == 'station':
            restOfString = rest.split('|')[0]
        elif passengerOrStation == 'passenger':
            restOfString = rest.split('|')[1]

        parameters = [int(p) for p in restOfString.split(',')]

        return functionName, parameters


### -----------
### MANAGERS
### --------

# handles input for all objects
# handles rendering of all sprites
class GameManager:
    allInteracts = []
    allSprites = []

    @staticmethod
    def addInteract(interact):
        GameManager.allInteracts.append(interact)

    @staticmethod
    def addSprite(sprite):
        GameManager.allSprites.append(sprite)

    @staticmethod
    def callMethodOnAll(objects: list, methodName: str, *args):
        for obj in objects:
            if methodName not in dir(obj):
                break
            
            getattr(obj, methodName)(*args)


# handles game data and resources
class StateManager:
    # the number of points equals this number
    passengersDelivered: int = 0
    gamePaused: bool = False

    gameTicks: int = 0
    clock: float = 0

    availableLocomotives: int = 3
    availableCarriages: int = 0

    # updates ticks
    # updates the number of seconds the game has been unpaused
    @staticmethod
    def updateClock(fps: int):
        StateManager.gameTicks += 1
        StateManager.clock = pythonRound(
            1 + StateManager.gameTicks / fps, 2)


# handles creating, deleting, and modifying rails
class RailManager:
    availableRails: int = 3
    rails: list[Rail] = []

    railColors: Iterator[str] = cycle(['red', 'blue', 'green', 'purple'])

    # the rail that is currently being created or modified
    activeRail: Rail = None

    # the stations that bookend the active rail segment
    activeRailSegment: tuple[Station] = None

    @staticmethod
    def createNewRail(station: Station):
        if RailManager.availableRails <= 0:
            print('Used all rails')
            return



    # checks if the mouse lands within any of the rectangles that cover each line segment
    # sets the active rail if it does
    @staticmethod
    def selectRail(rail: Rail, mouseX: float = 0, mouseY: float = 0):
        def mouseOnRailSegment(station1: Station, station2: Station) -> bool:
            x1, y1 = station1.getPosition()
            x2, y2 = station2.getPosition()
            
            angleOfSegment: float = findAngleOfLine(x1, y1, x2, y2)
            centerOfSegment: tuple[float] = ((x1+x2)/2, ((y1+y2)/2))
            lengthOfSegment: float = distance(x1, y1, x2, y2)
            
            mouseOnRailSegment: bool = rectInBoundary(mouseX, mouseY, 
                                    *centerOfSegment, lengthOfSegment,
                                    15, angleOfSegment)

            print(mouseOnRailSegment)
            return mouseOnRailSegment
        
    @staticmethod
    def modifyRail(rail: Rail, mouseX: float, mouseY: float):
        if RailManager.activeRail != rail:
            return
        
    @staticmethod
    def deleteRail(rail: Rail):
        RailManager.availableRails += 1
        RailManager.rails.pop(rail)

        del(rail)


# handles when and where stations are spawned
# handles drawing stations and its passengers
class StationManager:
    # percentage of screen from center that stations can spawn
    stationSpawnRange: int = 50
 
    # the number of seconds between stations spawning
    stationSpawnRate: float = 1

    # all the stations active in the game
    stations: list[Station] = []

    maxStationsReached: bool = False

    # assigns a random x and y position within spawn range and screen boundaries
    @staticmethod
    def assignPosition(maxScreenWidth: int = 1300, maxScreenHeight: int = 500
                       ) -> tuple[int]:
        
        xSpawnRange: int = pythonRound(
            maxScreenWidth*(StationManager.stationSpawnRange/100)/2)
        
        ySpawnRange: int = pythonRound(
            maxScreenHeight*(StationManager.stationSpawnRange/100)/2)

        xPosition: int = min(randint(-xSpawnRange, xSpawnRange) + 
                             (maxScreenWidth / 2), maxScreenWidth - 20)
        
        yPosition: int = min(randint(-ySpawnRange, ySpawnRange) + 
                             (maxScreenHeight / 2), maxScreenHeight - 20)

        return xPosition, yPosition

    # tries to assignPosition
    # if its to close to another station then it assigns a new x and y position
    # assigns a random station type
    # adds a station at that point with that type to the station list
    # changes the time variance for the next spawned station
    # returns that station
    @staticmethod
    def spawnStation() -> Station | None:
        xPosition, yPosition = StationManager.assignPosition()

        isSearching: bool = True
        attempts: int = 0
        while isSearching and attempts < 100:
            attempts += 1
            isSearching = False

            for preexistingStation in StationManager.stations:
                distanceToOtherStation: float = distance(preexistingStation.xPosition, 
                                                         preexistingStation.yPosition, 
                                                         xPosition, yPosition)
                
                if distanceToOtherStation < 100:
                    xPosition, yPosition = StationManager.assignPosition()
                    isSearching = True
                    break
            else:
                break
        else:
            print('max stations reached')
            StationManager.maxStationsReached = True
            return

        stationType: StationType = choice(list(StationType))
        station: Station = Station(xPosition, yPosition, stationType)

        return station

    @staticmethod
    def spawnStationsOnIntervals():
        if StateManager.clock % StationManager.stationSpawnRate == 0:
            station: Station = StationManager.spawnStation()

            if type(station) == Station:
                StationManager.stations.append(station)


# handles where passengers are spawned
class PassengerManager:
    # passengers spawn every this many seconds
    passengerSpawnRate: float = 1000

    # gets random station from the station manager
    # creates a random passenger
    # adds passenger to that station
    @staticmethod
    def spawnPassenger():
        if len(StationManager.stations) == 0:
            return

        stationToSpawnPassenger: Station = choice(StationManager.stations)
        passenger: Passenger = Passenger(choice(list(StationType)))

        stationToSpawnPassenger.passengers.append(passenger)

    @staticmethod
    def spawnPassengersOnIntervals():
        if StateManager.clock % PassengerManager.passengerSpawnRate == 0:
            PassengerManager.spawnPassenger()


### ----------------
### MAIN CLASSES
### -------------

# defines a rail that can be passed through stations and hold locomotives
class Rail():
    def __init__(self, color: str):
        GameManager.addInteract(self)
        GameManager.addSprite(self)

        self.connectedStations: list[Station] = []
        self.color: str = color

        self.id: str = str(uuid.uuid4())

    def __eq__(self, other) -> bool:
        if isinstance(other, Rail):
            return self.id == other.id
        
    def draw(self):
        for index, station in enumerate(self.connectedStations):
            if index == len(self.connectedStations)-1:
                break

            nextStation: Station = self.connectedStations[index+1]

            nextXPosition, nextYPosition = nextStation.getPosition()
            drawLine(station.xPosition, station.yPosition, 
                     nextXPosition, nextYPosition, fill=self.color, lineWidth=5)

            # draw T design at end of the rails

    def onPress(self, mouseX: float, mouseY: float):
        RailManager.selectRail(self, mouseX, mouseY)

    def onDrag(self, mouseX: float, mouseY: float):
        RailManager.modifyRail(self, mouseX, mouseY)


# defines a station that can be added to a rail and hold passengers
class Station():
    def __init__(self, xPosition: int, yPosition: int, stationType: StationType):
        GameManager.addInteract(self)
        GameManager.addSprite(self)

        self.xPosition: int = xPosition
        self.yPosition: int = yPosition

        self.stationType: StationType = stationType

        self.passengers: list[Passenger] = []

        self.id: str = str(uuid.uuid4())

    def __repr__(self):
        return f'Type: {self.stationType} at ({self.xPosition}, {self.yPosition})'

    def __eq__(self, other) -> bool:
        if isinstance(other, Station):
            return self.id == other.id

    def getPosition(self) -> tuple[int]:
        return self.xPosition, self.yPosition

    def addPassenger(self, passenger: Passenger):
        self.passengers.append(passenger)

    # loops through each passenger an displays there ...
    # destination on there current station
    def drawPassengers(self):
        for index, passenger in enumerate(self.passengers):

            xPosition: int = self.xPosition+(12*index)+20
            yPosition: int = self.yPosition-5

            functionName, parameters = StationType.getValue(
                'passenger', passenger.destinationType)

            globals()[functionName](xPosition, yPosition, *parameters, align='center')

    # draws the an inappropriate shape for the station
    # calls drawPassengers for the station
    def draw(self):
        functionName, parameters = StationType.getValue('station', self.stationType)

        # reduces border width by 1 if it is a star
        # (it looks better)
        borderWidthForStar = int(self.stationType==StationType.STAR)*-1

        globals()[functionName](self.xPosition, self.yPosition, *parameters, 
                                fill='white', border='black', 
                                borderWidth = 4 + borderWidthForStar,
                                  align='center')

        self.drawPassengers()

    def onPress(self, mouseX: float, mouseY: float):
        if rectInBoundary(mouseX, mouseY, *self.getPosition(), 30):
            RailManager.createNewRail(self)

# defines a locomotive that can collect and drop off ...
# passengers from different stations
class Locomotive():
    def __init__(self, rail: Rail):
        GameManager.addSprite(self)

        self.xPosition: float = 0
        self.yPosition: float = 0
        self.color: str = rail.color
        self.rail: Rail = rail

        self.maxPassengers: int = 6
        self.passengers: list[Passenger] = []

        self.isFull: bool = False

        self.currentStation: Station = self.rail[0]

        self.travelingForward: bool = True

    def findNextStation(self) -> Station:
        return self.rail.connectedStations[
            self.rail.connectedStations.index(
                self.currentStation)+int(self.travelingForward)]
    
    # find passengers with destination types in current direction of travel
    # sort passengers by their time waited
    # removes passengers from their current station and adds ...
    # them to the locomotive until it is full
    def pickUpPassengers(self):
        if len(self.passengers) == self.maxPassengers:
            self.isFull = True
            return

        self.isFull = False

        remainingStationTypes: list[StationType] = [
            station.stationType for station in 
            self.rail.connectedStations[
                self.rail.connectedStations.index(
                    self.currentStation)::int(self.travelingForward)]]

        passengersAvailable: list[Passenger] = [
            passenger for passenger in 
            self.currentStation.passengers if 
            passenger.destinationType in remainingStationTypes]

        while len(self.passengers) < self.maxPassengers or len(passengersAvailable) > 0:
            self.passengers.append(passengersAvailable.pop())

    # removes passengers who's destination type matches that of ...
    # the current station from the passenger list
    # returns the number of passengers removed
    def dropOffPassengers(self) -> int:
        numberOfPassengersBeforeDropOff: int = len(self.passengers)
        self.passengers = [
            passenger for passenger in self.passengers if 
            passenger.destinationType != self.currentStation.stationType]

        return numberOfPassengersBeforeDropOff - len(self.passengers)

    def drawPassengers(self):
        for passenger in self.passengers:
            ...

    def draw(self):
        nextStation: Station = self.findNextStation()

        _rotateAngle: float = findAngleOfLine(
            *self.currentStation.getPosition(), *nextStation.getPosition())

        drawRect(self.xPosition, self.yPosition, 
                 10, 15, rotateAngle=_rotateAngle, align='center')

    def addLocomotive():
        print('addLocomotive')


# defines a passenger with a destination station
class Passenger:
    def __init__(self, destinationType: StationType):
        self.destinationType: StationType = destinationType


### ---------------
### HUD CLASSES
### ------------ 

# defines a button that can be pressed or key bound
class Button():
    def __init__(self, xPosition: float, yPosition: float, size: float, 
                 action, icon: str = ' ', color: str = 'grey', 
                 keybinding: str = None):
        
        GameManager.addInteract(self)
        GameManager.addSprite(self)

        self.action = action
        self.icon: str = icon
        self.color: str = color

        self.size: float = size

        self.xPosition: float = xPosition
        self.yPosition: float = yPosition

        self.keybinding: str = keybinding

    # varies the size of the font
    # draws the button rectangle
    # draws the icon with the proper size
    def draw(self):
        size: float = self.size-2

        if len(self.icon)>1:
            size=self.size/len(self.icon)*1.5
        elif self.icon in '`~!@#$%^&*()-=_+[]\}|,./<>?;{:"':
            size=self.size+5

        drawRect(self.xPosition, self.yPosition, self.size, 
                 self.size, fill=self.color, align='center')
        
        drawLabel(self.icon.upper(), self.xPosition+self.size/2, 
                  self.yPosition+self.size/2, size=size, 
                  fill='white',bold=True,align='center')

    # performs button action if keybinding is pressed
    def keyPress(self, k: str):
        if k == self.keybinding:
            self.action()

    # performs button action if pressed
    def onPress(self, mouseX: float, mouseY:float):
        if rectInBoundary(mouseX,mouseY,self.xPosition,self.yPosition,self.size):
            self.action()


### -------
### HUD
### ----

### -------------------------
### CMU DEFINED FUNCTIONS
### ----------------------

def onKeyPress(app, key: str):
    if key == 'p':
        StateManager.gamePaused = not StateManager.gamePaused
    if key == 'x':
        print('rails:')
        for rail in RailManager.rails:
            print(rail.color, *rail.connectedStations)
            print()

def onMousePress(app, mouseX: float, mouseY: float):
    GameManager.callMethodOnAll(GameManager.allInteracts, 'onPress', mouseX, mouseY)

def onMouseDrag(app, mouseX: float, mouseY: float):
    GameManager.callMethodOnAll(GameManager.allInteracts, 'onDrag', mouseX, mouseY)

def onMouseRelease(app, mouseX: float, mouseY: float):
    GameManager.callMethodOnAll(GameManager.allInteracts, 'onRelease', mouseX, mouseY)

def onStep(app):
    if StateManager.gamePaused:
        return
    
    StateManager.updateClock(app.stepsPerSecond)

    if not StationManager.maxStationsReached:
        StationManager.spawnStationsOnIntervals()

    PassengerManager.spawnPassengersOnIntervals()

def onAppStart(app):
    # 30 fps
    app.stepsPerSecond = 30

    app.width = 1300
    app.height = 500

def redrawAll(app):
    GameManager.callMethodOnAll(GameManager.allSprites, 'draw')

def main():
    runApp()

main()