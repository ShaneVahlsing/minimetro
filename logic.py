from __future__ import annotations
from models import Rail, Station, Passenger
from utils import * 
from itertools import cycle
from typing import Iterator 
from random import randint, choice

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
        StateManager.clock = round(
            1 + StateManager.gameTicks / fps, 2)


# handles creating, deleting, and modifying rails
class RailManager:
    availableRails: int = 3
    rails: list[Rail] = []

    railColors: Iterator[str] = cycle(['red', 'blue', 'green', 'purple'])

    # the rail that is currently being created or modified
    activeRail: Rail 

    # the stations that bookend the active rail segment
    activeRailSegment: tuple[Station] 

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
            x1: int
            y1: int
            x2: int
            y2: int
            x1, y1 = station1.getPosition()
            x2, y2 = station2.getPosition()
            
            angleOfSegment: float = findAngleOfLine(x1, y1, x2, y2)
            centerOfSegment: tuple[float, float] = ((x1+x2)/2, ((y1+y2)/2))
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
        RailManager.rails.remove(rail)

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
                       ) -> tuple[int, int]:
        
        xSpawnRange: int = round(
            maxScreenWidth*(StationManager.stationSpawnRange/100)/2)
        
        ySpawnRange: int = round(
            maxScreenHeight*(StationManager.stationSpawnRange/100)/2)

        xPosition: int = min(randint(-xSpawnRange, xSpawnRange) + 
                             round((maxScreenWidth / 2)), maxScreenWidth - 20)
        
        yPosition: int = min(randint(-ySpawnRange, ySpawnRange) + 
                             round((maxScreenHeight / 2)), maxScreenHeight - 20)

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
            station: Station | None = StationManager.spawnStation()

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
