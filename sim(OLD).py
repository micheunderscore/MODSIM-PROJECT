import random
import threading
import time
import tkinter as tk

import numpy as np

gridRows, gridCols = (50,50)
boxSize = 15
offset = 3 * boxSize
numEntities = 100
simTime, simEnd = 0, 150
avgLifespan = 100
lock = threading.Lock() # GET BACK TO THIS WHEN THE SIM IS UP AND RUNNING

# Data Collection

# There is no god here
# Why? I created cows, then they started breeding the children because I forgot to code in sexual maturity
# It was a traumatizing experience

# Canvas Class =================================================================================
class Canvas(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.canvas = tk.Canvas(self, width=1080, height=1080, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.rows = gridRows
        self.columns = gridCols
        self.cellsize = boxSize
        self.offset = offset

        self.rect = {}
        self.ruler = {max: 20}
        self.number = {max: 20}
        for column in range(self.columns):
            # Creating the ruler
            b = calcBoxDims(0, column, self.cellsize, self.offset, mode="x")
            a = calcBoxDims(column, 0, self.cellsize, self.offset, mode="y")
            c = calcBoxDims(column, 0, self.cellsize, self.offset, mode="ruler")
            self.ruler[column] = self.canvas.create_rectangle(a[0], a[1], a[2], a[3], fill="white", tags="ruler")
            self.ruler[column + 10] = self.canvas.create_rectangle(b[0], b[1], b[2], b[3], fill="white", tags="ruler")
            self.number[column] = self.canvas.create_text(c[0], c[1], text=column)
            self.number[column + 10] = self.canvas.create_text(c[2], c[3], text=column)
            for row in range(self.rows):
                d = calcBoxDims(column, row, self.cellsize, self.offset)
                self.rect[row,column] = self.canvas.create_rectangle(d[0], d[1], d[2], d[3], fill="white", tags="rect")
                
        self.canvas.bind("<Motion>", self.moved)
        self.canvas.create_text(0, 0, text="(0, 0)", anchor="nw", tags="tag")

        self.redraw(1000, simTime, simEnd)
    
    def moved(self, event):
        x = int((event.x / self.cellsize) - (self.offset / self.cellsize))
        y = int((event.y / self.cellsize) - (self.offset / self.cellsize))
        if (self.rows > x >= 0) and (self.rows > y >= 0):
            self.canvas.itemconfig(self.canvas.find_withtag("tag"), text="(%r, %r)" % (x, y))

    def redraw(self, delay, simTime, simEnd):
        for x in range(self.rows):
            for y in range(self.columns):
                block = zaWarudo.getRekt(x, y)
                item_id = self.rect[x,y]
                color="white"
                outline="black"
                if (block != 0):
                    color = block.getHexColor()
                    outline = "yellow"
                    block.grow()
                    self.canvas.tag_raise(item_id)
                else:
                    fert = int((zaWarudo.getFertility(x, y) / 10) * 150)
                    color = "#{0:02x}{1:02x}{2:02x}".format(50, clamp(fert, 50, 150), 50)
                self.canvas.itemconfig(item_id, fill=color, outline=outline)
        
        if zaWarudo.simTime < zaWarudo.simEnd:
            lock.acquire()
            zaWarudo.increment()
            print("t%r: %r live entities" % (zaWarudo.simTime, zaWarudo.entCount))
            lock.release()
            self.after(delay, lambda: self.redraw(delay, simTime, simEnd))
        else:
            self.title("SIMULATION DONE")

# Grid Class =================================================================================
class Grid():
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.entCount = 0
        self.grid = np.zeros([width, height], dtype=object)
        self.fertility = np.random.randint(5, 10, size=(width, height))
        self.simTime = simTime
        self.simEnd = simEnd
    
    def add(self, entity, x, y):
        self.grid[x, y] = entity
        self.entCount += 1
    
    def update(self, entity, x0, y0, x1, y1):
        self.grid[x0, y0] = 0
        self.grid[x1, y1] = entity
    
    def getRekt(self, x, y):
        return self.grid[x,y]
    
    def remove(self, x, y):
        self.grid[x, y] = 0
        self.entCount -= 1

    def getRects(self):
        return self.grid()
    
    def getFertility(self, x, y):
        return self.fertility[x, y]

    def reduceFertility(self, x, y):
        self.fertility[x, y] -= 1

    def increment(self):
        if self.simTime < self.simEnd:
            self.simTime += 1

# Entity Class =================================================================================
class Entity(threading.Thread):
    FEMALE = 0
    MALE = 1
    def __init__(self, x, y, grid, speed, smarts, gender):
        threading.Thread.__init__(self)
        # Pos
        self.x = x
        self.y = y

        # Stats
        self.lifespan = avgLifespan
        self.gender = gender
        self.hunger = 3                 # Max of 10
        self.speed = speed              # Max of 3
        self.smarts = smarts            # Max of 100

        # world
        self.grid = grid

        # Generated Stats
        self.delay = 5 - int(4 * (smarts / 100))
        self.currFertility = self.grid.getFertility(x, y)
        # print("Delay =", self.delay)

    def getCoord(self):
        return [self.x, self.y]

    def getHexColor(self):
        r = int((self.speed / 3) * 255)
        g = 50
        b = int((self.smarts / 100) * 255)
        return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), g, clamp(b))

    def grow(self):
        self.lifespan -= 1 + self.hunger

    def run(self):
        gridLimX = self.grid.width - 1
        gridLimY = self.grid.height - 1

        while self.grid.simTime < self.grid.simEnd:
            time.sleep(self.delay)
            hungryCounter = 0
            neighbours = 0
            x0 = self.x
            y0 = self.y

            # If nothing can be done, move to a random location
            x1 = clamp(self.x + random.randint(-self.speed, self.speed), 0, gridLimX)
            y1 = clamp(self.y + random.randint(-self.speed, self.speed), 0, gridLimY)

            lock.acquire()
            
            if self.currFertility < 5 and self.hunger > 0:
                # Make decision
                decision = random.randint(0, self.smarts)

                # Do decision
                if decision >= 50:
                    x1 = self.x
                    y1 = self.y
                    agentFertility = self.currFertility
                    # Informed Decision Making
                    for i in range(3):
                        for j in range(3):
                            nx = clamp(self.x + i - 1, 0, gridLimX)
                            ny = clamp(self.y + j - 1, 0, gridLimY)

                            # Evaluate nx, ny fert and replace x1, y1 if fitting
                            if nx < self.grid.width and ny < self.grid.height:
                                nextFertility = self.grid.getFertility(nx, ny)
                                if agentFertility < nextFertility:
                                    agent = self.grid.getRekt(nx, ny)
                                    if agent == 0:
                                        x1 = nx
                                        y1 = ny
                                        agentFertility = nextFertility
            elif self.hunger == 0 and self.lifespan <= 75:
                mate = None
                emptyPlaces = []
                for i in range(3):
                    for j in range(3):
                        nx = clamp(self.x + i - 1, 0, gridLimX)
                        ny = clamp(self.y + j - 1, 0, gridLimY)

                        # Evaluate nx, ny fert and replace x1, y1 if fitting
                        if nx < self.grid.width and ny < self.grid.height:
                            agent = self.grid.getRekt(nx, ny)
                            if agent == 0:
                                emptyPlaces.append([nx, ny])
                            if agent != 0 and agent.gender != self.gender:
                                print("%r (%r, %r) and %r (%r, %r) are mating" % (agent.getHexColor(), agent.x, agent.y, self.getHexColor(), self.x,  self.y))
                                mate = agent
                
                if mate != None:
                    nSpeed = int((mate.speed * 0.5) + (self.speed * 0.5))
                    nSmarts = int((mate.smarts * 0.5) + (self.smarts * 0.5))
                    if random.randint(0,1) == 0:
                        nGender = Entity.FEMALE
                    else:
                        nGender = Entity.MALE
                    if len(emptyPlaces) == 0:
                        for mx in range(3):
                            for my in range(3):
                                if (mx == self.x and my == self.y) or (mx == mate.x and my == mate.y):
                                    continue
                                area = self.grid.getRekt(mx, my)
                                if area == 0:
                                    emptyPlaces.append([mx, my])
                    child = Entity(emptyPlaces[0][0], emptyPlaces[0][1], zaWarudo, nSpeed, nSmarts, nGender)
                    child.start()
                    zaWarudo.add(child, emptyPlaces[0][0], emptyPlaces[0][1])

            if (x0 != x1) or (y0 != y1):
                print(x0, y0, "MOVING TO", x1, y1)
                self.x = x1
                self.y = y1
                self.grid.update(self, x0, y0, x1, y1)
                self.currFertility = self.grid.getFertility(self.x, self.y)

            lock.release()
            
            # If self is hungry
            if self.hunger > 0 and hungryCounter == 0:
                # and current area is fertile
                if self.currFertility > 0:
                    # EAT
                    self.hunger -= 1
                    # Reduce ground fertility
                    self.grid.reduceFertility(self.x, self.y)
                    self.currFertility = self.grid.getFertility(self.x, self.y)
                    # If (after eating) not hungry anymore
                    if self.hunger == 0:
                        # FULL
                        hungryCounter = 3
                # if current area is ruined
                else:
                    self.hunger += 1
            elif self.hunger == 0 and hungryCounter > 0:
                hungryCounter -= 1
            elif hungryCounter == 0:
                self.hunger = 3
            
            print("TIME %r = (%r, %r) Life: %r\nSTATS: Sp%r, Sm%r H%r\nFert:%r, HC%r" %
            (self.grid.simTime, self.x, self.y, self.lifespan, self.speed, self.smarts, self.hunger, self.currFertility, hungryCounter))

            if(self.lifespan < 0):
                lock.acquire()
                self.grid.remove(self.x, self.y)
                lock.release()
                break

# UTILS =========================================================================================
def calcBoxDims(x, y, size, offset, mode="normal"):
    if (mode == "normal"):
        x1 = x * size + offset
        y1 = y * size + offset
    elif (mode == "y"):
        x1 = x * size + offset
        y1 = size
    elif (mode == "x"):
         x1 = size
         y1 = y * size + offset
    elif (mode == "ruler"):
        shift = size / 2
        x1 = x * size + shift + offset
        y1 = size + shift
        x2 = size + shift
        y2 = x * size + shift + offset
        return [x1, y1, x2, y2]
    x2 = x1 + size
    y2 = y1 + size
    return [x1, y1, x2, y2]

def clamp(x, mini=0, maxi=255): 
  return max(mini, min(x, maxi))

# Simulation Initialization =====================================================================
zaWarudo = Grid(gridRows, gridCols)
for agent in range(numEntities):
    while True:
        x = random.randint(0, zaWarudo.width - 1)
        y = random.randint(0, zaWarudo.height - 1)
        block = zaWarudo.getRekt(x, y)
        if block == 0: break
    speed = random.randint(0, 3)
    smarts = random.randint(0, 100)
    if random.randint(0,1) == 0:
        gender = Entity.FEMALE
    else:
        gender = Entity.MALE
    agent = Entity(x, y, zaWarudo, speed, smarts, gender)
    agent.start()
    zaWarudo.add(agent, x, y)

    # print(x, y)

if __name__ == "__main__":
    canvas = Canvas()
    canvas.mainloop()
