from __future__ import annotations
from utils import *
from uuid import uuid4
from cmu_graphics import * # type: ignore

# defines a rail that can be passed through stations and hold locomotives
class Rail():
    def __init__(self, color: str):
        from logic import GameManager
        GameManager.addInteract(self)
        GameManager.addSprite(self)

        self.connectedStations: list[Station] = []
        self.color: str = color

        self.id: str = str(uuid4())

    def __eq__(self, other) -> bool:
        if isinstance(other, Rail):
            return self.id == other.id
        
        return False
        
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
        from logic import RailManager
        RailManager.selectRail(self, mouseX, mouseY)

    def onDrag(self, mouseX: float, mouseY: float):
        from logic import RailManager
        RailManager.modifyRail(self, mouseX, mouseY)


# defines a station that can be added to a rail and hold passengers
class Station():
    def __init__(self, xPosition: int, yPosition: int, stationType: StationType):
        from logic import GameManager
        GameManager.addInteract(self)
        GameManager.addSprite(self)

        self.xPosition: int = xPosition
        self.yPosition: int = yPosition

        self.stationType: StationType = stationType

        self.passengers: list[Passenger] = []

        self.id: str = str(uuid4())

    def __repr__(self):
        return f'Type: {self.stationType} at ({self.xPosition}, {self.yPosition})'

    def __eq__(self, other) -> bool:
        if isinstance(other, Station):
            return self.id == other.id

        return False

    def getPosition(self) -> tuple[int, int]:
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
            from logic import RailManager
            RailManager.createNewRail(self)

# defines a locomotive that can collect and drop off ...
# passengers from different stations
class Locomotive():
    def __init__(self, rail: Rail):
        from logic import GameManager
        GameManager.addSprite(self)

        self.xPosition: float = 0
        self.yPosition: float = 0
        self.color: str = rail.color
        self.rail: Rail = rail

        self.maxPassengers: int = 6
        self.passengers: list[Passenger] = []

        self.isFull: bool = False

        self.currentStation: Station = self.rail.connectedStations[0]

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

    def addLocomotive(self):
        print('addLocomotive')


# defines a passenger with a destination station
class Passenger:
    def __init__(self, destinationType: StationType):
        self.destinationType: StationType = destinationType

