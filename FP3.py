import pygame
import sys
import time
import random 
from pygame.locals import *
import keyboard
import math

class Map():
	def __init__(self):
		self.mapWidth = 1800
		self.mapHeight = 1000
		self.floors = [[(0,self.mapWidth), self.mapHeight], [(200,self.mapWidth - 200),500] , [(200,self.mapWidth - 200), 740], [(0,self.mapWidth), 0]]
		self.walls = [[0, (self.mapHeight, 0)] , [self.mapWidth,(self.mapHeight,0)], [200, (500, 740)] , [self.mapWidth-200, (500,740)]]
		self.grapplePlaces = [[(400,self.mapWidth - 400), 0]]
	def drawBackground(self, data):
		picture = pygame.image.load("download.jpg")
		picture = pygame.transform.scale(picture, (self.mapWidth, self.mapHeight))
		data.screen.blit(picture,(-data.screenX,-data.screenY))
	def drawGrapplePlaces(self, data):
		for grap in self.grapplePlaces:
			y,x1,x2 = grap[1] - data.screenY, grap[0][0]-data.screenX, grap[0][1] - data.screenX
			pygame.draw.line(data.screen, (0,0,255) , (x1,y), (x2,y), 5)
	def drawWalls(self,data):
		for wall in self.walls:
			x,y1,y2 = wall[0] - data.screenX, wall[1][0] - data.screenY, wall[1][1] - data.screenY
			pygame.draw.line(data.screen, (255,255,255), (x,y1), (x,y2), 2)
	def drawFloors(self,data):
		for floor in self.floors:
			x1,y,x2 = floor[0][0] - data.screenX, floor[1] - data.screenY, floor[0][1] - data.screenX
			pygame.draw.line(data.screen, (255,255,255), (x1,y), (x2,y), 2)
	def drawMap(self, data):
		self.drawBackground(data)
		self.drawWalls(data)
		self.drawFloors(data)
		self.drawGrapplePlaces(data)
class Player():
	def __init__(self):
		self.x = 300
		self.y = 0
		self.width = 100
		self.height = 100
		self.xSpeed = 0
		self.ySpeed = 0
		self.color = (255,0,0)
		self.jumpStrength = 35
		self.runningSpeed = 15
		self.djUsed = False
		self.djkeyLifted = False
		self.wjUsed = False
		self.squatHeight = 50
		self.stadningHeight = 100
		self.grappleState = 0 #0 is not grappling, 1 is extending, 2 is swining, 3 is retracting
		self.grappleAngle = 60
		self.grapplingHook = [[self.x + self.width/2, self.y],[self.x + self.width/2, self.y]]
		self.grappleExtendSpeed = 25
		self.direction = 1
		self.isGrappling = False
	def grappleHit(self,data):
		for pad in data.map.grapplePlaces:
			px1, px2, py= pad[0][0], pad[0][1], pad[1]
			if self.grapplingHook[1][1] > py:
				return (False,0,0)
			gx1,gy1,gx2,gy2 = self.grapplingHook[0][0], self.grapplingHook[0][1], self.grapplingHook[1][0], self.grapplingHook[1][1]
			try:
				slope = (gx2 - gx1)/(gy1 - gy2) #negative
			except:
				slope = 0
			tx = (slope * (gy1 - py)) + gx1
			if tx < max(px1,px2) and tx > min(px1,px2):
				print("fuck")
				return (True, tx, py)
		return (False,0,0)
	def extendGrapple(self,data):
		g = self.grapplingHook
		newLen = ((g[0][0] - g[1][0])**2 + (g[0][1] - g[1][1])**2)**0.5 + self.grappleExtendSpeed
		x2,y2 = g[0][0] + newLen*math.cos(math.radians(self.grappleAngle))*(self.direction), g[0][1] - newLen*math.sin(math.radians(self.grappleAngle))
		self.grapplingHook[1] = [x2,y2]
		self.grapplingHook[0] = [self.x, self.y]
		if self.grappleHit(data)[0]:
			self.grappleState = 2
			self.grapplingHook[1] = list(self.grappleHit(data)[1:])
		elif g[1][1] < 0:
			self.grappleState = 3
	def swingFromGrapple(self, data):
		if self.isOnFloor(data) or self.isOnWall(data):
			self.grappleState = 3
			return
		self.isGrappling = True
		g = self.grapplingHook
		length = ((g[0][0] - g[1][0])**2 + (g[0][1] - g[1][1])**2)**.5
		angle = math.atan((g[0][0] - g[1][0])/(g[0][1] - g[1][1]))
		newAngle = angle + self.direction/8
		self.xSpeed = (g[1][0] - g[0][0]) + math.sin(newAngle)*length
		self.ySpeed =  -(math.cos(newAngle)*length - (g[0][1] - g[1][1]))

		
	def retractGrapple(self,data):
		self.isGrappling = False
		self.grapplingHook[1] = [self.x + self.width/2, self.y]
		self.grappleState = 0
	def updateGrappleLocation(self,data):
		if self.grappleState == 0:
			self.grapplingHook[1] = [self.x + self.width/2, self.y]
		self.grapplingHook[0] = [self.x + self.width/2, self.y]
		if self.grappleState == 1:
			self.extendGrapple(data)
		elif self.grappleState == 2:
			self.swingFromGrapple(data)
		elif self.grappleState == 3:
			self.retractGrapple(data)
		if self.grappleState == 0:
			self.grapplingHook[1] = [self.x + self.width/2, self.y]
		self.grapplingHook[0] = [self.x + self.width/2, self.y]
	def grapple(self,data):
		if self.grappleState == 0:
			self.grappleState = 1	
	def endGrapple(self,data):
		if self.grappleState == 1 or self.grappleState == 2:
			self.grappleState = 3
	def jump(self,data):
		if self.isOnFloor(data):
			self.ySpeed = self.jumpStrength
		elif self.djkeyLifted and not self.djUsed and not self.isGrappling:
			self.ySpeed = self.jumpStrength
			self.djUsed = True
		if self.isOnWall(data) and self.djkeyLifted and not self.wjUsed:
			self.ySpeed = self.jumpStrength
			self.wjUsed = True
	def moveRight(self,data):
		if self.isOnFloor(data):
			self.xSpeed = self.runningSpeed
		if self.isOnWall(data):
			self.xSpeed = self.runningSpeed
	def moveLeft(self, data):
		if self.isOnFloor(data):
			self.xSpeed = -self.runningSpeed
		if self.isOnWall(data):
			self.xSpeed = -self.runningSpeed
	def stop(self,data):
		if self.isOnFloor(data):
			self.xSpeed = 0
	def isOnWall(self, data):
		for wall in data.map.walls:
			y1, y2 = wall[1][0], wall[1][1]
			if self.x <= wall[0] and self.x + self.width >= wall[0]:
				if self.y < max(y1,y2) and self.y + self.height > min(y1,y2):
					return True
		return False
	def isOnFloor(self, data):
		for floor in data.map.floors:
			x1,x2,y = floor[0][1], floor[0][0], floor[1]
			if self.x < max(x1,x2) and self.x + self.width > min(x1,x2):
				if self.y <= y and self.y + self.height >= y:
					return True
		return False
	def fixFloorCollision(self, data):
		for floor in data.map.floors:
			x1,x2,y = floor[0][1], floor[0][0], floor[1]
			if self.x < max(x1,x2) and self.x + self.width > min(x1,x2):
				if self.y <= y and self.y + self.height >= y:
					if self.ySpeed < 0:
						self.y = y - self.height
					elif self.ySpeed > 0:
						self.y = y+1
					else:
						self.y = y - self.height
					self.ySpeed = 0
	def fixWallCollision(self,data):
		for wall in data.map.walls:
			y1, y2 = wall[1][0], wall[1][1]
			if self.x <= wall[0] and self.x + self.width >= wall[0]:
				if self.y < max(y1,y2) and self.y + self.height > min(y1,y2):
					if self.xSpeed > 0:
						self.x = wall[0] - self.width
					if self.xSpeed < 0:
						self.x = wall[0]
					self.xSpeed = 0
	def fixDoubleCollision(self,data):
		wallHit = []
		floorHit = []
		for wall in data.map.walls:
			y1, y2 = wall[1][0], wall[1][1]
			if self.x <= wall[0] and self.x + self.width >= wall[0]:
				if self.y < max(y1,y2) and self.y + self.height > min(y1,y2):
					wallHit = wall
		for floor in data.map.floors:
			x1,x2,y = floor[0][1], floor[0][0], floor[1]
			if self.x < max(x1,x2) and self.x + self.width > min(x1,x2):
				if self.y <= y and self.y + self.height >= y:
					floorHit = floor
		xC, yC = self.x, self.y
		self.x, self.y = wallHit[0], floorHit[1]-data.player1.height
		if self.isOnWall(data) or self.isOnFloor(data):
			self.xSpeed, self.ySpeed = 0,0
		else:
			print("trip")
			self.x,self.y = xC, yC
		


	def move(self,data):
		self.updateGrappleLocation(data)
		if self.isOnWall(data) and self.ySpeed < 0:
			self.ySpeed -= data.wallGravity
		elif not self.isGrappling:
			self.ySpeed -= data.gravity
		self.y -= self.ySpeed
		self.x += self.xSpeed
		if self.isOnFloor(data) and self.isOnWall(data):
			self.fixDoubleCollision(data)
		elif self.isOnFloor(data):
			self.fixFloorCollision(data)
			self.djUsed = False
		elif self.isOnWall(data):
			self.fixWallCollision(data)
			self.wjUsed = False
	def drawGrapplingHook(self,data):
		x1,y1 = self.grapplingHook[0][0] - data.screenX, self.grapplingHook[0][1] - data.screenY
		x2,y2 = self.grapplingHook[1][0] - data.screenX, self.grapplingHook[1][1] - data.screenY	
		pygame.draw.line(data.screen, (255,0,0), (x1,y1), (x2,y2), 5)
	def drawPlayer(self, data):
		x,y,sx, sy = self.x, self.y, self.width, self.height
		x -= data.screenX
		y -= data.screenY
		pygame.draw.rect(data.screen, self.color, [x, y, sx, sy])
		self.drawGrapplingHook(data)
def init(data):
	data.screenWidth, data.screenHeight = 600, 800
	data.fps = 60
	pygame.init()
	data.fpsClock = pygame.time.Clock()
	data.screen = pygame.display.set_mode((data.screenWidth, data.screenHeight),0,32)
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1)
	data.player1 = Player()
	data.gravity = 2
	data.map = Map()
	data.screenX, data.screenY = 0,0
	data.wallGravity = 1
	data.fpsActual = 0
	pygame.font.init()
def userInteractions(data):
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	if keyboard.is_pressed("up"):
		data.player1.jump(data)
		data.player1.djkeyLifted = False
	else:
		data.player1.djkeyLifted = True
	if keyboard.is_pressed("left"):
		data.player1.direction = -1
		data.player1.moveLeft(data)
	elif keyboard.is_pressed("right"):
		data.player1.direction = 1
		data.player1.moveRight(data)
	else:
		data.player1.stop(data)
	if keyboard.is_pressed("s"):
		if data.player1.height == data.player1.stadningHeight:
			data.player1.y += (data.player1.stadningHeight - data.player1.squatHeight)
		data.player1.height = data.player1.squatHeight
	else:
		if data.player1.height == data.player1.squatHeight:
			data.player1.y -= (data.player1.stadningHeight - data.player1.squatHeight)
			data.player1.height = data.player1.stadningHeight
			oldY = data.player1.y
			data.player1.fixFloorCollision(data)
			if oldY == data.player1.y:
				data.player1.height == data.player1.stadningHeight
			else:
				data.player1.height = data.player1.squatHeight
				data.player1.y = oldY + data.player1.stadningHeight - data.player1.squatHeight # 800 - data.player1.squatHeight
	if keyboard.is_pressed("a"):
		data.player1.grapple(data)
	else:
		data.player1.endGrapple(data)
def periodical(data):
	data.player1.move(data)
def runGame(data):
	userInteractions(data)
	periodical(data)
def moveScreen(data):
	data.screenX = data.player1.x - data.screenWidth/2
	data.screenY = data.player1.y - data.screenHeight/2
	if data.screenX < 0:
		data.screenX = 0
	elif data.screenX + data.screenWidth > data.map.mapWidth:
		data.screenX = data.map.mapWidth - data.screenWidth
	if data.screenY < 0:
		data.screenY = 0
	elif data.screenY + data.screenHeight > data.map.mapHeight:
		data.screenY = data.map.mapHeight - data.screenHeight
def drawFps(data):
	text = str(data.fpsActual)
	font = pygame.font.SysFont('Comic Sans MS', 20)
	d = min(abs(int(255*((data.fpsActual-10)/(50)))), 255)
	color = (255,d,d)
	text = font.render(text, True, color)
	data.screen.blit(text, (20,20))
def drawGame(data):
	moveScreen(data)
	data.map.drawMap(data)
	data.player1.drawPlayer(data)
	drawFps(data)
	pygame.display.flip()
	pygame.display.update()
def playGame(data):
	while True:
		oldTime = time.time()
		runGame(data)
		drawGame(data)
		data.fpsClock.tick(data.fps)
		data.fpsActual = int(1/(time.time() - oldTime))


def startGame():
	class Struct(object): pass
	data = Struct()
	init(data)
	playGame(data)

startGame()