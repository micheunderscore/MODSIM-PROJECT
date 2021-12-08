import random
import threading
import time
import tkinter as tk

import numpy as np
import pandas as pd

gridRows, gridCols = (50,50)
boxSize = 15
offset = 3 * boxSize
numEntities = 500
simTime, simEnd = 0, 16
lifespan = 80
seasonDuration = 20
lock = threading.Lock()

# Data Collection
femalesTotals = []
malesTotals = []
deathTotals = []
population = []
avgSpeed = []
avgSmarts = []
avgLifespan = []

# There is no god here
# Why? I created cows, then they started breeding with their own children because I forgot to code in sexual maturity
# It was a traumatizing experience
# Once I added consideration for cow reproduction age, the population reproduction rate dropped significantly.
# This greatly capped the cows' ability to keep a steady population.
# It is a sacrifice I'm willing to make as it is ultimately a good exchange of circumstances and...
# I would be allowed to enter god's kingdom of heaven once more.
# The awful version of this simulation has been logged as sim(OLD).py due to keeping history.

# Canvas Class =================================================================================
class Canvas(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.canvas = tk.Canvas(self, width=960, height=1080, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.rows = gridRows
        self.columns = gridCols
        self.cellsize = boxSize
        self.offset = offset
        self.turn = 0

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
                if self.turn == 0:
                    zaWarudo.growFertility(x, y)
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

        if self.turn == 0:
            self.turn = seasonDuration
        else:
            self.turn -= 1

        if zaWarudo.simTime < zaWarudo.simEnd and zaWarudo.entCount > 0:
            lock.acquire()
            zaWarudo.increment()
            # BROADCAST: Timekeeping
            print("t%r: %r live entities" % (zaWarudo.simTime, zaWarudo.entCount))
            lock.release()
            self.after(delay, lambda: self.redraw(delay, simTime, simEnd))
        else:
            self.title("SIMULATION DONE")
            data = {
                "Population": population,
                "Females": femalesTotals,
                "Males": malesTotals,
                "Deaths": deathTotals,
                "Average Speed": avgSpeed,
                "Average Smarts": avgSmarts,
                "Average Lifespan": avgLifespan
            }
            df = pd.DataFrame(data)
            df.to_csv("data.csv")

# Grid Class =================================================================================
class Grid():
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.entCount = 0
        self.femaleCount = 0
        self.maleCount = 0
        self.deathCount = 0
        self.speedTotal = 0
        self.smartsTotal = 0
        self.lifespanTotal = 0
        self.grid = np.zeros([width, height], dtype=object)
        self.fertility = np.random.randint(5, 10, size=(width, height))
        self.simTime = simTime
        self.simEnd = simEnd

    def record(self, entity):
        self.speedTotal += entity.speed
        self.smartsTotal += entity.smarts
        self.lifespanTotal += entity.lifespan

    def incrGender(self, gender):
        if gender == Entity.FEMALE:
            self.femaleCount += 1
        else:
            self.maleCount += 1

    def reduceGender(self, gender):
        if gender == Entity.FEMALE:
            self.femaleCount -= 1
        else:
            self.maleCount -= 1
    
    def resetRecord(self):
        self.speedTotal = 0
        self.smartsTotal = 0
        self.lifespanTotal = 0

    def add(self, entity, x, y):
        self.incrGender(entity.gender)
        self.grid[x, y] = entity
        self.entCount += 1
    
    def update(self, entity, x0, y0, x1, y1):
        self.grid[x0, y0] = 0
        self.grid[x1, y1] = entity
    
    def getRekt(self, x, y):
        return self.grid[x,y]
    
    def remove(self, x, y):
        self.grid[x,y] = 0
        self.entCount -= 1
        self.deathCount += 1

    def getRects(self):
        return self.grid()
    
    def getFertility(self, x, y):
        return self.fertility[x, y]

    def reduceFertility(self, x, y):
        self.fertility[x, y] -= 1

    def growFertility(self, x, y):
        self.fertility[x, y] += 1

    def increment(self):
        if self.simTime < self.simEnd:
            self.simTime += 1
        # Data Collection
        if self.entCount == 0:
            speedAvg = 0
            smartsAvg = 0
            lifespanAvg = 0
        else:
            speedAvg = self.speedTotal / self.entCount
            smartsAvg = self.smartsTotal / self.entCount
            lifespanAvg = self.lifespanTotal / self.entCount
        population.append(self.entCount)
        femalesTotals.append(self.femaleCount)
        malesTotals.append(self.maleCount)
        deathTotals.append(self.deathCount)
        avgSpeed.append(speedAvg)
        avgSmarts.append(smartsAvg)
        avgLifespan.append(lifespanAvg)
        self.resetRecord()
        

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
        self.lifespan = lifespan
        self.gender = gender
        self.hunger = 3                 # Max of 10
        self.speed = speed              # Max of 3
        self.smarts = smarts            # Max of 100

        # world
        self.grid = grid

        # Generated Stats
        self.delay = 5 - int(4 * (smarts / 100))
        self.currFertility = self.grid.getFertility(x, y)

    def getCoord(self):
        return [self.x, self.y]

    def getHexColor(self):
        r = int((self.speed / 3) * 255)
        g = 50
        b = int((self.smarts / 100) * 255)
        return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), g, clamp(b))

    def grow(self):
        if self.lifespan > 0:
            self.lifespan -= 1 + self.hunger
            if self.lifespan < 0:
                self.lifespan = 0

        self.grid.record(self)

    def run(self):
        hungryCounter = 0
        while self.grid.simTime < self.grid.simEnd:
            time.sleep(self.delay)
            neighbours = 0
            mates = []
            emptyPlaces = []
            fertilePlaces = []

            x0 = self.x
            y0 = self.y
            x1 = x0
            y1 = y0

            lock.acquire()
            
            # Check surroundings
            for i in range(self.speed):
                for j in range(self.speed):
                    nx = self.x + i - 1
                    ny = self.y + j - 1

                    # Evaluate nx, ny limits
                    if nx < self.grid.width and ny < self.grid.height:
                        agent = self.grid.getRekt(nx, ny)
                        # Check for empty spaces
                        if agent == 0:
                            # Keep note of empty coordinates (BIRTHING)
                            emptyPlaces.append([nx, ny])
                            # If coordinate is more fertile
                            nextFertility = self.grid.getFertility(nx, ny)
                            if nextFertility > self.currFertility:
                                # Keep note of fertile and empty coordinates if not already (MIGRATING)
                                fertilePlaces.append([nx, ny])

                        else:
                            # Considering areas within close proximity
                            if x0 - 1 <= nx <= x0 + 1 and y0 - 1 <= ny <= y0 + 1:
                                # Keep note of neighbours (SURVIVAL)
                                neighbours += 1
                                # If there is opposite gender neighbour
                                if agent.gender != self.gender:
                                    # Keep track of potential mates (REPRODUCTION)
                                    mates.append(agent)
            
            fertilePlaces = np.unique(fertilePlaces, axis=0)
            emptyPlaces = np.unique(emptyPlaces, axis=0)

            # Crowd Control
            # if neighbours > 8: self.lifespan -= 5
            # elif neighbours > 6: self.lifespan -= 2
            # elif neighbours > 4: self.lifespan -= 1
            
            # Make Decision
            decision = random.randint(0, self.smarts)

            # If current place is deteriorating and is hungry 
            if (self.currFertility < 5 and self.hunger > 0) or decision > 45:
                # If nowhere to go, stay put
                newBlock = [x1, y1]
                # If there are fertile places
                if len(fertilePlaces) > 0:
                    # Choose a random spot to migrate to
                    place = 0
                    if len(fertilePlaces > 1):
                        place = random.randint(0, len(fertilePlaces) - 1)
                    newBlock = fertilePlaces[place]
                    np.delete(fertilePlaces, place)
                # If no fertile places, find empty places
                elif len(emptyPlaces) > 0:
                    place = 0
                    if len(emptyPlaces) > 1:
                        place = random.randint(0, len(emptyPlaces) - 1)
                    newBlock = emptyPlaces[place]
                    np.delete(emptyPlaces, place)
                
                # New location to migrate to
                x1 = newBlock[0]
                y1 = newBlock[1]
            
            # If not too hungry and is sexually mature and has potential mates
            if self.hunger <= 1 and self.lifespan <= 65 and len(mates) > 0 and len(emptyPlaces) > 0:
                # Pick a random mate
                pick = 0
                if len(mates) > 1:
                    pick = random.randint(0, len(mates) - 1)
                mate = mates[pick]
                # BROADCAST: Mating
                print("%r (%r, %r) and %r (%r, %r) are mating" % (mate.getHexColor(), mate.x, mate.y, self.getHexColor(), self.x,  self.y))
                # Pick a place for birth
                place = 0
                if len(emptyPlaces) > 1:
                    place = random.randint(0, len(emptyPlaces) - 1)
                birthSpot = emptyPlaces[place]
                # Determine child specs
                nSpeed = int((mate.speed * 0.5) + (self.speed * 0.5))
                nSmarts = int((mate.smarts * 0.5) + (self.smarts * 0.5))
                if random.randint(0,1) == 0:
                    nGender = Entity.FEMALE
                else:
                    nGender = Entity.MALE

                # GIVE BIRTH
                child = Entity(birthSpot[0], birthSpot[1], zaWarudo, nSpeed, nSmarts, nGender)
                child.start()
                zaWarudo.add(child, birthSpot[0], birthSpot[1])

                self.lifespan -= 50
                mate.lifespan -= 50
                

            # Once observations have ended
            # If new location is different
            if (x0 != x1) or (y0 != y1):
                # BROADCAST: Migrating
                # print(x0, y0, "MOVING TO", x1, y1)
                # Migrate self
                self.x = x1
                self.y = y1
                self.grid.update(self, x0, y0, x1, y1)
                self.currFertility = self.grid.getFertility(self.x, self.y)

            lock.release()
            
            # HUNGER BEHAVIOR
            # If self is hungry
            if self.hunger > 0 and hungryCounter == 0:
                # and current area is fertile
                if self.currFertility > 0:
                    # EAT
                    self.hunger = 0
                    # Reduce ground fertility
                    self.grid.reduceFertility(self.x, self.y)
                    self.currFertility = self.grid.getFertility(self.x, self.y)
                    # If (after eating) not hungry anymore
                    if self.hunger == 0:
                        # FULL
                        hungryCounter = 5
                # if current area is ruined
                else:
                    self.hunger += 1
            elif self.hunger == 0 and hungryCounter > 0:
                hungryCounter -= 1
            elif hungryCounter == 0:
                self.hunger = 3
            
            # BROADCAST: STATS
            # print("TIME %r = (%r, %r) Life: %r\nSTATS: Sp%r, Sm%r H%r\nFert:%r, HC%r" %
            # (self.grid.simTime, self.x, self.y, self.lifespan, self.speed, self.smarts, self.hunger, self.currFertility, hungryCounter))

            if(self.lifespan <= 0):
                lock.acquire()
                self.grid.reduceGender(self.gender)
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
    speed = random.randint(1, 3)
    smarts = random.randint(1, 100)
    if random.randint(0,1) == 0:
        gender = Entity.FEMALE
        zaWarudo.femaleCount += 1
    else:
        gender = Entity.MALE
        zaWarudo.maleCount += 1
    agent = Entity(x, y, zaWarudo, speed, smarts, gender)
    agent.start()
    zaWarudo.add(agent, x, y)

if __name__ == "__main__":
    canvas = Canvas()
    canvas.mainloop()
