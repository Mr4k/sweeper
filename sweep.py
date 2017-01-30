from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import PIL.ImageGrab as ImageGrab
import pyautogui
import time
import random
import profile
import math

#The size of the board
WIDTH = 30
HEIGHT = 16

#Screen Coords of Board
TOP = 178
LEFT = 222
RIGHT = 700
BOTTOM = 432

CELL_WIDTH = 16
CELL_HEIGHT = 16

#Important Colors
NUMBER_RED = [143, 14, 252, 2, 122, 16, 0, 123]
NUMBER_GREEN = [143, 122, 13, 11, 3, 123, 0, 123]
NUMBER_BLUE = [205, 17, 27, 121, 7, 122, 0, 123]

#Board definition and functions
board = [[9 for x in range(HEIGHT)] for y in range(WIDTH)]
tilesCleared = 0

def distSqColor(r1,g1,b1,r2,g2,b2):
	return (r1 - r2) * (r1 - r2) + (b1 - b2) * (b1 - b2) + (g1 - g2) * (g1 - g2)

def click(x, y):
	#print ("called:" + str(x) + ", " + str(y))
	#Assume we clicked a safe spot otherwise we've already lost so it doesn't matter
	global tilesCleared
	tilesCleared += 1
	#time.sleep(0.1)
	pyautogui.moveTo(x * CELL_WIDTH + LEFT + CELL_WIDTH / 2.0, y * CELL_HEIGHT + TOP + CELL_HEIGHT / 2.0, duration=0.001)
	time.sleep(0.001)
	#we might need to click twice to register sometimes
	pyautogui.click()
	pyautogui.click()
	captureBoard()
	floodFillZeros(x, y)

def captureBoard():
	img = ImageGrab.grab(bbox=(LEFT * 2,TOP * 2,RIGHT * 2,BOTTOM * 2))
	img = img.convert('RGB')
	centerX = CELL_WIDTH
	centerY = CELL_HEIGHT
	for xx in xrange(WIDTH):
		for yy in xrange(HEIGHT):
			if board[xx][yy] > 8:
				r, g, b = img.getpixel((int(centerX), int(centerY)))
				for i in xrange(8):
					if i == 0:
						print(r,g,b)
					if distSqColor(r,g,b,NUMBER_RED[i],NUMBER_GREEN[i],NUMBER_BLUE[i]) < 3000:
						board[xx][yy] = i + 1
						break
			centerY += CELL_HEIGHT * 2
		centerY = CELL_HEIGHT
		centerX += CELL_WIDTH * 2

def floodFillZeros(x, y):
	global tilesCleared
	if board[x][y] < 9:
		return
	else:
		tilesCleared += 1
		board[x][y] = 0
		for neighbor in getNeighbors(x, y):
			floodFillZeros(neighbor[0],neighbor[1])

def getNeighbors(x, y):
	neighbors = []
	for xx in xrange(-1,2):
		for yy in xrange(-1,2):
			if x + xx >= 0 and x + xx < WIDTH and y + yy >= 0 and y + yy < HEIGHT and not (xx == 0 and yy == 0):
				neighbors.append((x+xx,y+yy))
	return neighbors

def findAdjacentBombs(x, y):
	unknownBombsAdj = board[x][y]
	unknownNeighbors = len(getNeighbors(x,y))
	neighbors = getNeighbors(x, y)
	i = 0
	while i < len(neighbors): 
		xx, yy = neighbors[i]
		if board[xx][yy] == -1:
			unknownBombsAdj -= 1
		if board[xx][yy] < 9:
			unknownNeighbors -= 1
			del neighbors[i]
			i -= 1
		i += 1
	neighborsToUpdate = []
	if unknownNeighbors == unknownBombsAdj:
		for neighbor in neighbors:
			xx, yy = neighbor
			board[xx][yy] = -1
			for bombNeighbors in getNeighbors(xx, yy):
				if board[bombNeighbors[0]][bombNeighbors[1]] > 0 and board[bombNeighbors[0]][bombNeighbors[1]] < 9:
					neighborsToUpdate.append(bombNeighbors)
	for bombNeighbor in neighborsToUpdate:
		findAdjacentBombs(bombNeighbor[0],bombNeighbor[1])

def sweep():
	for yy in xrange(HEIGHT):
		for xx in xrange(WIDTH):
			if board[xx][yy] > 0 and board[xx][yy] < 9:
				findAdjacentBombs(xx, yy)

def getSafeUnknownNeighbors(x, y):
	unknownBombsAdj = board[x][y]
	unknownNeighbors = 8
	neighbors = getNeighbors(x, y)
	i = 0
	while i < len(neighbors): 
		xx, yy = neighbors[i]
		if board[xx][yy] == -1:
			unknownBombsAdj -= 1
		if board[xx][yy] < 9:
			unknownNeighbors -= 1
			del neighbors[i]
			i -= 1
		i += 1
	if unknownBombsAdj == 0:
		return neighbors
	else:
		return []

def getUnknownNeighbors(x, y):
	unknownNeighbors = 8
	neighbors = getNeighbors(x, y)
	i = 0
	while i < len(neighbors): 
		xx, yy = neighbors[i]
		if board[xx][yy] < 9:
			unknownNeighbors -= 1
			del neighbors[i]
			i -= 1
		i += 1
	return neighbors

def findNextClick():
	for yy in xrange(HEIGHT):
		for xx in xrange(WIDTH):
			if board[xx][yy] > 0 and board[xx][yy] < 9:
				safeClicks = getSafeUnknownNeighbors(xx, yy)
				if len(safeClicks) > 0:
					click(safeClicks[0][0], safeClicks[0][1])
					#time.sleep(0.2)
					return
	#no safe bet we will guess
	bestRatio = 1
	coords = (0,0)
	numUnknownTiles = 0
	numBombs = 99
	leastSuspiciousTile = 9999

	for yy in xrange(HEIGHT):
		for xx in xrange(WIDTH):
			if board[xx][yy] == -1:
				numBombs -=1
			if board[xx][yy] == 9:
				numUnknownTiles += 1

	for yy in xrange(HEIGHT):
		for xx in xrange(WIDTH):
			
			
			if board[xx][yy] > 0 and board[xx][yy] < 9:
				l = len(getUnknownNeighbors(xx, yy))
				if l == 0:
					continue
				ratio = float(board[xx][yy]) / float(l)
				if ratio < bestRatio:
					bestRatio = ratio
					coords = (xx, yy)
			"""tileSuspecion = 0
			if board[xx][yy] == 9:
				neighbors = getNeighbors(xx,yy)
				for neighbor in neighbors:
					nx,ny = neighbor
					if board[nx][ny] >= 0 and board[nx][ny] < 9:
						tileSuspecion += board[nx][ny] * board[nx][ny]
					else:
						#below is an approximation
						tileSuspecion +=  (2 * float(numBombs) / float(numUnknownTiles)) * (2 * float(numBombs) / float(numUnknownTiles)) * 30
				tileSuspecion = tileSuspecion
				if tileSuspecion < leastSuspiciousTile:
					leastSuspiciousTile = tileSuspecion
					coords = (xx, yy)"""

	click(coords[0], coords[1])

	if bestRatio < float(numBombs) / float(numUnknownTiles):
		x,y = getUnknownNeighbors(coords[0], coords[1])[0]
		click(x, y)
	else:
		num = random.randint(0, numUnknownTiles)
		for yy in xrange(HEIGHT):
			for xx in xrange(WIDTH):
				if board[xx][yy] == 9:
					num -= 1
					if num <= 1:
						click(xx, yy)
						return
	#time.sleep(0.2)


def printBoard():
	for yy in xrange(HEIGHT):
		for xx in xrange(WIDTH):
			if board[xx][yy] >= 0:
				if board[xx][yy] == 9:
					print("? ", end="")
				else:
					print(str(board[xx][yy]) + " ", end="")
			else:
				print("* ", end="")
		print('\n',end = "")

pyautogui.click()
click(3,3)
sweep()
printBoard()

"""profile.run(
	'findNextClick()')
profile.run(
	'sweep()')"""

while tilesCleared < 381:
	findNextClick()
	sweep()
	print ("HMMMmmm...")
	printBoard()
