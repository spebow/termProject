import pygame
import sys
import time
import random 
from pygame.locals import *
import keyboard
import math

"""
Players sprites were taken from here:
https://jesse-m.itch.io/jungle-pack/download/eyJleHBpcmVzIjoxNTQyODU5Mzc2LCJpZCI6MTMwMDQ5fQ%3d%3d.wag%2bBxv0sMSYsZWrkavm82ppU5M%3d
"""
class Crates():
	def __init__(self):
		self.crates = [[800,380]]
		self.size = 60
		self.image = pygame.image.load("crate.png")
		self.image = pygame.transform.scale(self.image, (self.size, self.size))
		self.stunned = 0
	def collidesWithPlayer(self,data):
		for crate in self.crates:
			x,y,w,h = data.player1.x, data.player1.y, data.player1.width, data.player1.height
			print(crate[1] , y)
			if crate[0] < x + w and crate[0]  + self.size > x:
				if crate[1] < y+h and crate[1] + self.size > y:
					self.stunned = 15
					self.crates.remove(crate) 
		if self.stunned > 0:
			self.stunned -= 1
	def drawCrates(self,data):
		for crate in self.crates:
			data.screen.blit(self.image, (crate[0]-data.screenX, crate[1] - data.screenY))
class PowerUps():
	def __init__(self):
		self.puSize = 50
		self.speedBoost = [[2000, 500 - self.puSize]]
		self.powers = []
		self.boost = 0
	def drawBoostBar(self, data):
		text = "Boost"
		font = pygame.font.SysFont('Comic Sans MS', 20)
		color = (0,255,0)
		text = font.render(text, True, color)
		data.screen.blit(text, (60,20))
		pygame.draw.rect(data.screen, (0,255,0), [125,28, self.boost, 15])

	def boostPlayer(self,data):
		p1 = data.player1
		if self.boost> 0:
			self.boost -= 1
			p1.runningSpeed = 2*p1.unBoostedRunningSpeed
		else:
			p1.runningSpeed = p1.unBoostedRunningSpeed
	def unBoost(self,data):
		data.player1.runningSpeed = data.player1.unBoostedRunningSpeed
	def draw(self,data):
		for boost in self.speedBoost:
			x,y,s = boost[0] - data.screenX, boost[1] - data.screenY, self.puSize
			pygame.draw.rect(data.screen, (0,255,0), [x, y, s, s])
		self.drawBoostBar(data)

	def collidesWithPlayer(self, player1,data):
		for boost in self.speedBoost:
			if player1.x <= boost[0] + self.puSize and player1.x + player1.width >= boost[0]:
				if player1.y <= boost[1] + self.puSize and player1.y + player1.height >= boost[1]:
					self.speedBoost.remove(boost)
					self.boost += 100
	def updatePowers(self,data):
		for power in self.powers:
			power[1] -= 1
			if power[1] <= 0:
				pass
	def update(self, player1, data):
		self.collidesWithPlayer(player1,data)
		self.updatePowers(data)
class Map():
	def __init__(self):
		self.mapWidth = 3000
		self.mapHeight = 1000
		self.floors = [[(0,self.mapWidth), self.mapHeight], [(200,self.mapWidth - 200),500] , [(200,self.mapWidth - 200), 740], [(0,self.mapWidth), 0]]
		self.walls = [[0, (self.mapHeight, 0)] , [self.mapWidth,(self.mapHeight,0)], [200, (500, 740)] , [self.mapWidth-200, (500,740)]]
		self.grapplePlaces = [[(400,self.mapWidth - 400), 0]]
		self.picture = pygame.image.load("download.jpg")
		self.picture = pygame.transform.scale(self.picture, (self.mapWidth, self.mapHeight))
	def drawBackground(self, data):
		data.screen.blit(self.picture,(-data.screenX,-data.screenY))
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
		self.unBoostedRunningSpeed = self.runningSpeed
		self.djUsed = False
		self.djkeyLifted = False
		self.wjUsed = False
		self.squatHeight = 50
		self.stadningHeight = 100
		self.grappleState = 0 #0 is not grappling, 1 is extending, 2 is swining, 3 is retracting
		self.grappleAngle = 60
		self.grapplingHook = [[self.x + self.width/2, self.y],[self.x + self.width/2, self.y]]
		self.grappleExtendSpeed = 70
		self.direction = 1
		self.isGrappling = False
		self.runningImages = self.createRunningImages()
		self.idleImages = self.createIdleImages()
		self.jumpingImages = self.createJumpingImages()
		self.state = "running"
		self.runningProgress = 0 
		self.idleProgress = 0
		self.jumpingProgress = 0
	def createRunningImages(self):
		names = ["run-1", "run-2", "run-3", "run-4", "run-5", "run-6","run-7", "run-8"]
		images = []
		for name in names:
			img = pygame.image.load("player1 sprite/%s.png" %name)
			img = pygame.transform.scale(img, (self.width, self.height))
			images.append(img)
		return images
	def createIdleImages(self):
		names = ["idle-1", "idle-2", "idle-3", "idle-4", "idle-5", "idle-6","idle-7", "idle-8", "idle-9", "idle-10", "idle-11", "idle-12"]
		images = []
		for name in names:
			img = pygame.image.load("player1 sprite/%s.png" %name)
			img = pygame.transform.scale(img, (self.width, self.height))
			images.append(img)
		return images
	def createJumpingImages(self):
		names = ["jump-1", "jump-2"]
		images = []
		for name in names:
			img = pygame.image.load("player1 sprite/%s.png" %name)
			img = pygame.transform.scale(img, (self.width, self.height))
			images.append(img)
		return images
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
				return (True, tx, py)
		return (False,0,0)
	def extendGrapple(self,data):
		g = self.grapplingHook
		newLen = ((g[0][0] - g[1][0])**2 + (g[0][1] - g[1][1])**2)**0.5 + self.grappleExtendSpeed
		x2,y2 = g[0][0] + newLen*math.cos(math.radians(self.grappleAngle))*(self.direction), g[0][1] - newLen*math.sin(math.radians(self.grappleAngle))
		self.grapplingHook[1] = [x2,y2]
		self.grapplingHook[0] = [self.x + self.width/2 + self.direction*60, self.y]
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
		newAngle = angle + (self.direction/(length))*20
		self.xSpeed = (g[1][0] - g[0][0]) + math.sin(newAngle)*length
		self.ySpeed = -(math.cos(newAngle)*length - (g[0][1] - g[1][1]))

		
	def retractGrapple(self,data):
		self.isGrappling = False
		self.grapplingHook[1] = [self.x + self.width/2, self.y]
		self.grappleState = 0
	def updateGrappleLocation(self,data):
		if self.grappleState == 0:
			self.grapplingHook[1] = [self.x + self.width/2, self.y]
		self.grapplingHook[0] = [self.x + self.width/2 + self.direction*60, self.y]
		if self.grappleState == 1:
			self.extendGrapple(data)
		elif self.grappleState == 2:
			self.swingFromGrapple(data)
		elif self.grappleState == 3:
			self.retractGrapple(data)
		if self.grappleState == 0:
			self.grapplingHook[1] = [self.x + self.width/2, self.y]
		self.grapplingHook[0] = [self.x + self.width/2 + self.direction*60, self.y]
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
	def crouched(self):
		return self.height == self.squatHeight
	def moveRight(self,data):
		if self.isOnFloor(data) and not self.crouched():
			self.xSpeed = self.runningSpeed
		if self.isOnWall(data):
			self.xSpeed = self.runningSpeed
	def moveLeft(self, data):
		if self.isOnFloor(data) and not self.crouched():
			self.xSpeed = -self.runningSpeed
		if self.isOnWall(data):
			self.xSpeed = -self.runningSpeed
	def stop(self,data):
		if self.isOnFloor(data) and not self.crouched():
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
		if self.xSpeed != 0:
			tx = abs((self.x - wall[0])/self.xSpeed)
		else:
			tx = 1
		if self.ySpeed != 0:
			ty = abs((self.y - floor[1])/self.ySpeed)
		else:
			ty = 1
		if tx < ty:
			self.fixFloorCollision(data)
		else:
			self.fixWallCollision(data)

		


	def move(self,data):
		self.updateGrappleLocation(data)
		if self.isOnWall(data) and self.ySpeed < 0:
			self.ySpeed -= data.wallGravity
		elif not self.isGrappling:
			self.ySpeed -= data.gravity
		if self.crouched():
			self.xSpeed/= 1.02
			if self.xSpeed < .5 and self.xSpeed > 0:
				self.xSpeed = 0.5
			elif self.xSpeed > -0.5 and self.xSpeed < 0:
				self.xSpeed = -.5
		self.y -= self.ySpeed
		if data.crates.stunned <= 0:
			self.x += self.xSpeed

		if self.isOnFloor(data) and self.isOnWall(data):
			self.fixDoubleCollision(data)
		if self.isOnFloor(data):
			self.fixFloorCollision(data)
			if self.ySpeed <= 0:
				self.djUsed = False
		if self.isOnWall(data):
			self.fixWallCollision(data)
			self.wjUsed = False
	def drawGrapplingHook(self,data):
		if self.grapplingHook[0][1] != self.grapplingHook[1][1]:
			x1,y1 = self.grapplingHook[0][0] - data.screenX, self.grapplingHook[0][1] - data.screenY
			x2,y2 = self.grapplingHook[1][0] - data.screenX, self.grapplingHook[1][1] - data.screenY	
			pygame.draw.line(data.screen, (255,0,0), (x1,y1), (x2,y2), 5)
	def drawPlayer(self, data):
		x,y,sx, sy = self.x, self.y, self.width, self.height
		x -= data.screenX
		y -= data.screenY
		if data.crates.stunned > 0:
			picture = self.idleImages[1]
		elif self.height == self.squatHeight:
			picture = pygame.image.load("player1 sprite/wallSlide.png" )
			if self.direction > 0:
				picture = pygame.transform.rotate(picture, 270)
			else:
				picture = pygame.transform.rotate(picture, -90)
			picture = pygame.transform.scale(picture, (self.width, self.height))
		elif self.isOnFloor(data) and self.xSpeed != 0:
			self.runningProgress += 1
			picture = self.runningImages[self.runningProgress%len(self.runningImages)]
		elif self.isOnFloor(data) and self.xSpeed == 0:
			self.idleProgress += 1
			picture = self.idleImages[self.idleProgress%len(self.idleImages)]
		elif self.isOnWall(data):
			picture = pygame.image.load("player1 sprite/wallSlide.png" )
			picture = pygame.transform.scale(picture, (self.width, self.height))
		elif self.isGrappling:
			picture = pygame.image.load("player1 sprite/wallSlide.png" )
			picture = pygame.transform.scale(picture, (self.width, self.height))
		else:
			#self.jumpingProgress += 1
			picture = self.jumpingImages[self.jumpingProgress%len(self.jumpingImages)]

		
		if self.direction < 0:
			picture = pygame.transform.flip(picture, True, False)
		data.screen.blit(picture,(x,y))
		#pygame.draw.rect(data.screen, self.color, [x, y, sx, sy])
		self.drawGrapplingHook(data)
def init(data):
	data.screenWidth, data.screenHeight = 600, 800
	data.fps = 30
	pygame.init()
	data.fpsClock = pygame.time.Clock()
	data.screen = pygame.display.set_mode((data.screenWidth, data.screenHeight),0,32)
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1)
	data.player1 = Player()
	data.powerUps = PowerUps()
	data.gravity = 2
	data.map = Map()
	data.screenX, data.screenY = 0,0
	data.wallGravity = 1
	data.fpsActual = 0
	pygame.font.init()	
	data.crates = Crates()
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
	if keyboard.is_pressed("d"):
		data.powerUps.boostPlayer(data)
	else:
		data.powerUps.unBoost(data)
def periodical(data):
	data.player1.move(data)
	data.powerUps.update(data.player1, data)
	data.crates.collidesWithPlayer(data)
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
	d = min(abs(int(255*((data.fpsActual-10)/(30)))), 255)
	color = (255,d,d)
	text = font.render(text, True, color)
	data.screen.blit(text, (20,20))
def drawGame(data):
	moveScreen(data)
	data.map.drawMap(data)
	data.powerUps.draw(data)
	data.crates.drawCrates(data)
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

def preGame(data):
	while True:
		oldTime = time.time()
		
		data.fpsClock.tick(data.fps)
		data.fpsActual = int(1/(time.time() - oldTime))
def startGame():
	class Struct(object): pass
	data = Struct()
	init(data)
	#preGame(data)
	playGame(data)

startGame()