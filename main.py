from __future__ import annotations 
from cmu_graphics import * # type: ignore
from logic import StateManager, RailManager, GameManager, StationManager, PassengerManager

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