from __future__ import annotations
from logic import GameManager
from utils import *
from cmu_graphics import * # type: ignore

# defines a button that can be pressed or key bound
class Button():
    def __init__(self, xPosition: float, yPosition: float, size: float, 
                 action, icon: str = ' ', color: str = 'grey', 
                 keybinding: str | None = None):
        
        from logic import GameManager
        GameManager.addInteract(self)
        GameManager.addSprite(self)

        self.action = action
        self.icon: str = icon
        self.color: str = color

        self.size: float = size

        self.xPosition: float = xPosition
        self.yPosition: float = yPosition

        self.keybinding: str | None = keybinding

    # varies the size of the font
    # draws the button rectangle
    # draws the icon with the proper size
    def draw(self):
        size: float = self.size-2

        if len(self.icon)>1:
            size=self.size/len(self.icon)*1.5
        elif self.icon in '`~!@#$%^&*()-=_+[]\\}|,./<>?;{:"':
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