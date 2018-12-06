import pygame
import sys
import time
import random 
from pygame.locals import *
import keyboard
import math



"""
Players sprites were taken from here:
https://jesse-m.itch.io/jungle-pack
https://rvros.itch.io/animated-pixel-hero
Power Up Image:
https://banner2.kisspng.com/20180329/xeq/kisspng-dota-2-defense-of-the-ancients-invoker-video-game-orb-5abd7e8a203a64.364252811522368138132.jpg
"""

class Crates():
	def __init__(self):
		self.crates = [[546,2330], [576, 2330], [606, 2330]]
		self.size = 30
		self.image = pygame.image.load("crate.png")
		self.image = pygame.transform.scale(self.image, (self.size, self.size))
	def collidesWithPlayer(self,data):
		for player in data.players:
			for crate in self.crates:
				x,y,w,h = player.x, player.y, player.width, player.height
				if crate[0] < x + w and crate[0]  + self.size > x:
					if crate[1] < y+h and crate[1] + self.size > y:
						player.stunned = 15
						self.crates.remove(crate) 
						if player.grappleState == 1 or player.grappleState == 2:
							player.grappleState = 3
			if player.stunned > 0:
				player.stunned -= 1
	def drawCrates(self,data):
		for crate in self.crates:
			data.screen.blit(self.image, (crate[0]-data.screenX, crate[1] - data.screenY))
	def createCrate(self, x, y):
		self.crates.append([x,y])
class PowerUps():
	def __init__(self):
		self.puSize = 50
		self.speedBoost = [[2000, 2325], [1200, 2200]]
		self.boxDrops = [[1000, 550]]
		self.powers = []
		self.boostImage = pygame.transform.scale(pygame.image.load("boostImage.png"), (self.puSize, self.puSize))
		self.powerUpImage = pygame.transform.scale(pygame.image.load("powerUpImage.png"), (self.puSize, self.puSize))
		self.p1Console = [pygame.image.load("p1-n-pu.png"), pygame.image.load("p1-w-pu.png")]
		self.p2Console = [pygame.image.load("p2-n-pu.png"), pygame.image.load("p2-w-pu.png")]
	def drawBoostBar(self, data):
		for i in range(len(data.players)):
			if i == 0:
				images = self.p1Console
				if data.player1.powers == []:
					img = images[0]
				else:
					img = images[1]
				data.screen.blit(img, (200*i, 0))
				pygame.draw.rect(data.screen, (0,255,0), [55,35, min(100, data.player1.boost), 25])
			else:
				images = self.p2Console
				if data.player2.powers == []:
					img = images[0]
				else:
					img = images[1]
				data.screen.blit(img, (200*i, 0))
				pygame.draw.rect(data.screen, (0,255,0), [255,35, min(100, data.player2.boost), 25])
	def boostPlayer(self,data, player):
		p1 = player
		if p1.boost> 0:
			p1.boost -= 1
			p1.runningSpeed = 1.3*p1.unBoostedRunningSpeed
		else:
			p1.runningSpeed = p1.unBoostedRunningSpeed
	def unBoost(self,data, player):
		player.runningSpeed = player.unBoostedRunningSpeed
	def draw(self,data):
		for boost in self.speedBoost:
			x,y,s = boost[0] - data.screenX, boost[1] - data.screenY, self.puSize
			data.screen.blit(self.boostImage, (x,y))
		for item in self.boxDrops:
			x,y,s = item[0] - data.screenX, item[1] - data.screenY, self.puSize
			data.screen.blit(self.powerUpImage, (x,y))
		self.drawBoostBar(data)

	def collidesWithPlayer(self,data):
		for player in data.players:
			for boost in self.speedBoost:
				if player.x <= boost[0] + self.puSize and player.x + player.width >= boost[0]:
					if player.y <= boost[1] + self.puSize and player.y + player.height >= boost[1]:
						#self.speedBoost.remove(boost)
						player.boost += 10
			for item in self.boxDrops:
				if player.x <= item[0] + self.puSize and player.x + player.width >= item[0]:
					if player.y <= item[1] + self.puSize and player.y + player.height >= item[1]:
						if player.powers == []:
							player.powers = ["boxes", 3]
							self.boxDrops.remove(item)
	def removePowerUps(self, data):
		for player in data.players:
			if len(player.powers) == 2 and player.powers[1] <= 0:
				player.powers = []

	def update(self, player1, data):
		self.collidesWithPlayer(data)
		self.removePowerUps(data) 
class Map():
	def __init__(self):
		self.n = 1
		if self.n == 0:
			self.mapWidth = 3000
			self.mapHeight = 2000
			self.floors = [[(0,3000),2000],[(0,3000),1950],[(300,1000),1600],[(300,1000),1680],[(1300,3000),1150],[(1400,3000),1250],[(500,2700),600],[(500,2600),700],[(0,500),1150],[(0,500),1250], [(2600, 2700), 1000], [(1750, 2100), 950], [(1750, 2100), 1010], [(0,3000), 0]]#[[(0,self.mapWidth), self.mapHeight], [(200,self.mapWidth - 200),500] , [(200,self.mapWidth - 200), 740], [(0,self.mapWidth), 0]]
			self.walls = [[0, (0,2000)], [3000, (0,2000)], [800, (700, 1600)], [900, (700, 1600)], [1300, (1150, 1950)], [1400, (1250, 1950)], [2600, (600,1000)], [2700, (600,1000)], [300, (1600, 1680)], [1000, (1600, 1680)], [500, (600,700)], [500, (1150, 1250)], [1750, (950, 1010)], [2100, (950, 1010)]]
			self.grapplePlaces = [[(600, 2600), 10], [(400,1000), 1685]]
			self.picture = pygame.image.load("level-1.png")
			self.picture = pygame.transform.scale(self.picture, (self.mapWidth, self.mapHeight))
			self.xGreatorSection = [[0, 1680,1300,2000], [1300, 700, 3000,1150]] #x,y,x,y
			self.xLesserSection = [[0, 0, 2700, 600]]
			self.yLesserSection = [[900, 700, 1300, 1680], [2700, 0,3000, 1150]]
			self.yGreatorSection = [[0,600, 800,1680]]
			self.AICheckpoints = []
		else:
			self.mapWidth, self.mapHeight = 4750, 2500
			self.picture = pygame.image.load("level2.jpg")
			self.picture = pygame.transform.scale(self.picture, (self.mapWidth, self.mapHeight))
			self.floors = [[(3700, 4675), 1300],[(0, 850), 2400],[(850, 1450), 2475], [(1450, 4675), 2375], [(950, 950+300), 2250], [(950, 950+300), 2300], [(540, 540+90),1990+340], [(350, 1450),1990], [(1450,4100),1690+75], [(1150, 4200), 1690], [(2000,2400),1975], [(2000,2400), 1975 + 75], [(2480, 2880), 1825], [(2480, 2880), 1900], [(4100,4200),1690 + 450], [(4400,4475),1540], [(4400,4475),1540+760],[(3600, 3700), 1590], [(3600, 4675),1200], [(4375, 4475),1100], [(1900,4475),690], [(3450,3950),515], [(3450,3950),590], [(1450, 3050), 1190], [(1900, 4375),790], [(1900, 3300), 790], [(1450, 3050), 1290], [(1350, 1450), 1540], [(350, 1150), 625]]
			self.walls = [[540, (1990, 2330)], [630, (1990, 2330)], [850, (2400, 2475)], [1450, (2375, 2475)], [950, (2250, 2300)], [1250, (2250, 2300)], [2000, (1990, 2065)], [2480, (1815, 1890)], [4100, (1765, 2140)], [4200, (1690, 2140)], [4400, (1540, 760 + 1540)], [4475, (1540, 760 + 1540)], [4675, (0, 2375)], [3600, (1200, 1590)], [3400, (790, 1690)], [3300, (790, 1690)], [4475, (690, 1100)], [3450, (515, 590)], [3950, (515, 590)], [1900, (690, 790)], [3050, (1190, 1290)], [3700, (1300, 1590)], [4375, (790, 1100)], [1450, (0, 1540)], [1350, (0,1540)], [1150, (625, 1690)], [350, (625, 1990)], [0, (0, 2500)]]
			self.grapplePlaces = []
			self.xGreatorSection = [[350,1990, 4200, 2500],[4200, 2140, 4750, 2500], [3300, 790,4475, 1200], [11450, 690,3300,1190]]
			self.xLesserSection = [[3600, 1300, 4750, 1690], [1450, 0, 4750, 690 ], [1350, 1190, 3300, 1690], [0, 0, 1350, 625]]
			self.yGreatorSection = [[0, 625, 350, 2400]]
			self.yLesserSection = [[4200,1690,4750,2140],[3300, 1200,3600, 1690], [4475,690, 4675, 1200], [1150, 625, 1350, 1690]]
			self.AICheckpoints = [(1100, 2425), (1250,2425), (2000, 2325), (4250,2325), (4350, 2200), (4200, 2070), (4350, 2000)]
		self.sections = [self.xLesserSection, self.xGreatorSection, self.yLesserSection, self.yGreatorSection]
	
	def getLeaderSection(self,data, player):
		p = player
		for section in self.sections:
			for box in section:
				if p.x >= box[0] and p.x <= box[2] and p.y >= box[1] and p.y <= box[3]:
					return section
		#print("section error fuck you spencer, this is a terrible idea")
		#return 1/0
	def findNewLeader(self, data):
		if self.getLeaderSection(data, data.player2) != self.getLeaderSection(data, data.player1):
			return
		else:
			section = self.getLeaderSection(data, data.currentLeader)
			if section == self.xGreatorSection:
				if data.player1.x > data.player2.x:
					data.currentLeader = data.player1
				else:
					data.currentLeader = data.player2
			elif section == self.xLesserSection:
				if data.player1.x < data.player2.x:
					data.currentLeader = data.player1
				else:
					data.currentLeader = data.player2
			elif section == self.yLesserSection:
				if data.player1.y < data.player2.y:
					data.currentLeader = data.player1
				else:
					data.currentLeader = data.player2
			elif section == self.yGreatorSection:
				if data.player1.y > data.player2.y:
					data.currentLeader = data.player1
				else:
					data.currentLeader = data.player2
			else:
				pass
				#print("you fucked up")
				#return 1/0

	def drawBackground(self, data):
		data.screen.blit(self.picture,(-data.screenX,-data.screenY))
	def drawGrapplePlaces(self, data):
		pass
		"""
		for grap in self.grapplePlaces:
			y,x1,x2 = grap[1] - data.screenY, grap[0][0]-data.screenX, grap[0][1] - data.screenX
			pygame.draw.line(data.screen, (0,0,255) , (x1,y), (x2,y), 5)
		"""
	def drawWalls(self,data):
		
		pass
		"""
		for wall in self.walls:
			x,y1,y2 = wall[0] - data.screenX, wall[1][0] - data.screenY, wall[1][1] - data.screenY
			pygame.draw.line(data.screen, (255,255,255), (x,y1), (x,y2), 2)
		"""	
	def drawFloors(self,data):
		pass
		"""
		for floor in self.floors:
			x1,y,x2 = floor[0][0] - data.screenX, floor[1] - data.screenY, floor[0][1] - data.screenX
			pygame.draw.line(data.screen, (255,255,255), (x1,y), (x2,y), 2)
			"""
	def drawMap(self, data):
		self.drawBackground(data)
		self.drawWalls(data)
		self.drawFloors(data)
		self.drawGrapplePlaces(data) 
class Player():
	def __init__(self, n):
		self.n = n
		self.powerUpKeyLifted = True
		self.powers = [] 
		self.boost = 0
		self.stunned = 0
		self.x = 100
		self.y = 2350
		self.width = 50
		self.height = 50
		self.xSpeed = 0
		self.ySpeed = 0
		self.color = (255,0,0)
		self.jumpStrength = 25
		self.runningSpeed = 25
		self.unBoostedRunningSpeed = self.runningSpeed
		self.djUsed = False
		self.djkeyLifted = False
		self.wjUsed = False
		self.squatHeight = 25
		self.stadningHeight = 50
		self.grappleState = 0 #0 is not grappling, 1 is extending, 2 is swining, 3 is retracting
		self.grappleAngle = 60
		self.grapplingHook = [[self.x + self.width/2, self.y],[self.x + self.width/2, self.y]]
		self.grappleExtendSpeed = 70
		self.direction = 1
		self.isGrappling = False
		self.runningImages = self.createRunningImages(n)
		self.idleImages = self.createIdleImages(n)
		self.jumpingImages = self.createJumpingImages(n)
		self.state = "running"
		self.runningProgress = 0 
		self.idleProgress = 0
		self.jumpingProgress = 0
		if n == 0:
			self.wallSlidingPicture = pygame.image.load("player1 sprite/wallSlide.png" )
			self.wallSlidingPicture = pygame.transform.scale(self.wallSlidingPicture, (self.width, self.height))
		else:
			self.wallSlidingPicture = pygame.image.load("player2 sprite/adventurer-crnr-grb-00.png" )
			self.wallSlidingPicture = pygame.transform.scale(self.wallSlidingPicture, (self.width, self.height))
	def __repr__(self):
		return "player " + str(self.n + 1)
	def createRunningImages(self,n):
		if n == 0:
			names = ["run-1", "run-2", "run-3", "run-4", "run-5", "run-6","run-7", "run-8"]
			images = []
			for name in names:
				img = pygame.image.load("player1 sprite/%s.png" %name)
				img = pygame.transform.scale(img, (self.width, self.height))
				images.append(img)
			return images
		else:
			names = ["adventurer-run-00","adventurer-run-01","adventurer-run-02","adventurer-run-03","adventurer-run-04","adventurer-run-05"]
			images = []
			for name in names:
				img = pygame.image.load("player2 sprite/%s.png" %name)
				img = pygame.transform.scale(img, (self.width, self.height))
				images.append(img)
			return images
	def createIdleImages(self,n):
		if n == 0:
			names = ["idle-1", "idle-2", "idle-3", "idle-4", "idle-5", "idle-6","idle-7", "idle-8", "idle-9", "idle-10", "idle-11", "idle-12"]
			images = []
			for name in names:
				img = pygame.image.load("player1 sprite/%s.png" %name)
				img = pygame.transform.scale(img, (self.width, self.height))
				images.append(img)
			return images
		else:
			names = ["adventurer-idle-00", "adventurer-idle-00", "adventurer-idle-00", "adventurer-idle-01", "adventurer-idle-01","adventurer-idle-01","adventurer-idle-02","adventurer-idle-02","adventurer-idle-02"]
			images = []
			for name in names:
				img = pygame.image.load("player2 sprite/%s.png" %name)
				img = pygame.transform.scale(img, (self.width, self.height))
				images.append(img)
			return images
	def createJumpingImages(self,n):
		if n == 0:
			names = ["jump-1", "jump-2"]
			images = []
			for name in names:
				img = pygame.image.load("player1 sprite/%s.png" %name)
				img = pygame.transform.scale(img, (self.width, self.height))
				images.append(img)
			return images
		else:
			names = ["adventurer-fall-00", "adventurer-fall-01"]
			images = []
			for name in names:
				img = pygame.image.load("player2 sprite/%s.png" %name)
				img = pygame.transform.scale(img, (self.width, self.height))
				images.append(img)
			return images
	def userPowerUp(self,data):
		if self.powerUpKeyLifted:
			if len(self.powers) == 2 and self.powers[0] == "boxes":
				data.crates.createCrate(self.x - self.width*self.direction, self.y + self.height - data.crates.size)
				self.powers[1] -= 1
			self.powerUpKeyLifted = False
	def grappleHit(self,data):
		for pad in data.map.grapplePlaces:
			px1, px2, py= pad[0][0], pad[0][1], pad[1]
			if self.grapplingHook[1][1] > py or self.grapplingHook[0][1] < py :
				continue
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
			self.xSpeed, self.ySpeed = 0,0
			return
		self.isGrappling = True
		g = self.grapplingHook
		length = ((g[0][0] - g[1][0])**2 + (g[0][1] - g[1][1])**2)**.5
		angle = math.atan((g[0][0] - g[1][0])/(g[0][1] - g[1][1]))
		newAngle = angle + (self.direction/(length))*30
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
		if self.isOnWall(data) and isinstance(self, AI):
			self.ySpeed = self.jumpStrength
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
				if self.y + min(self.ySpeed, 0) <= y and self.y + self.height >= y:
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
			if self.x  + self.width > min(floorHit[0]) and self.x < max(floorHit[0]):
				self.fixFloorCollision(data)
			else:
				self.fixWallCollision(data)
		else:
			if self.y < max(wallHit[1]) and self.y + self.height > min(wallHit[1]):
				self.fixWallCollision(data)
			else:
				self.fixFloorCollision(data)

		


	def move(self,data):
		self.updateGrappleLocation(data)
		if self.isOnWall(data): #and self.ySpeed < 0:
			#print (self.x)
			self.ySpeed -= data.wallGravity
		elif self.isOnFloor(data):
			pass
		elif not self.isGrappling and self.ySpeed > -30:
			self.ySpeed -= data.gravity
		if self.crouched():
			self.xSpeed/= 1.02
			if self.xSpeed < .5 and self.xSpeed > 0:
				self.xSpeed = 0.5
			elif self.xSpeed > -0.5 and self.xSpeed < 0:
				self.xSpeed = -.5
		self.y -= self.ySpeed
		if self.stunned <= 0:
			self.x += self.xSpeed
		else:
			self.x += self.xSpeed/5

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
		
		if self.height == self.squatHeight:
			picture = self.wallSlidingPicture
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
			picture = self.wallSlidingPicture
		elif self.isGrappling:
			picture = self.wallSlidingPicture
		else:
			#self.jumpingProgress += 1
			picture = self.jumpingImages[self.jumpingProgress%len(self.jumpingImages)]

		
		if self.direction < 0:
			picture = pygame.transform.flip(picture, True, False)
		data.screen.blit(picture,(x,y))
		#pygame.draw.rect(data.screen, self.color, [x, y, sx, sy])
		self.drawGrapplingHook(data)
class AI(Player):
	def __init__(self, n):
		super().__init__(n)
		self.currentPoint = 0
		self.jumpFirst = False
		self.alreadyJumpedOnWall = False
	def computerInteractions(self, data):
		cp, i = data.map.AICheckpoints, self.currentPoint
	
		if self.ySpeed == 0:
			if (self.x - cp[i][0])*self.direction >= 0 and abs(self.x - cp[i][0]) <= abs(self.xSpeed) + 1:
				self.currentPoint += 1
		elif abs(self.y-cp[i][1]) < abs(self.ySpeed)  and self.x == cp[i][0]:
			self.currentPoint += 1
		
		if self.currentPoint >= len(cp):
			self.currentPoint = 0
		i = self.currentPoint
		if self.isOnWall(data) and not self.alreadyJumpedOnWall:
			self.jumpFirst = True
		if not self.isOnWall(data):
			self.alreadyJumpedOnWall = False
	
		if self.y > cp[i][1]:
			if i == 5:
				print("jumping")
			self.jump(data)
			self.jumpFirst = False
			if self.isOnWall(data):
				self.alreadyJumpedOnWall = True
		if self.x < cp[i][0]: #and not self.isOnWall(data):
			self.moveRight(data)
			self.direction = 1
		elif self.x > cp[i][0]: #and not self.isOnWall(data):
			self.direction = -1
			self.moveLeft(data)

	def drawAICheckPoints(self, data):
		for p in data.map.AICheckpoints:
			color = (255,0,0)
			if p == data.map.AICheckpoints[self.currentPoint]:
				color = (0,0,255)
			pygame.draw.ellipse(data.screen, color, [p[0]-data.screenX, p[1] - data.screenY, 10, 10])
def init(data):
	data.humans = [False, False]
	data.endGame = True
	data.playingGame = True
	data.screenWidth, data.screenHeight = 1000, 600
	data.fps = 30
	pygame.init()
	data.fpsClock = pygame.time.Clock()
	data.screen = pygame.display.set_mode((data.screenWidth, data.screenHeight),0,32)
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1)
	data.powerUps = PowerUps()
	data.gravity = 3
	data.map = Map()
	data.screenX, data.screenY = 0,0
	data.wallGravity = 1.3
	data.fpsActual = 0
	pygame.font.init()	 
	data.crates = Crates()
def userInteractions(data):
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	if isinstance(data.player1, AI):
		data.player1.computerInteractions(data)
	else:

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
		if keyboard.is_pressed("down"):
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
		if keyboard.is_pressed("k"):
			data.player1.grapple(data)
		else:
			data.player1.endGrapple(data)
		if keyboard.is_pressed("l"):
			data.powerUps.boostPlayer(data, data.player1)
		else:
			data.powerUps.unBoost(data, data.player1)
		if keyboard.is_pressed("j"):
			data.player1.userPowerUp(data)
		else:
			data.player1.powerUpKeyLifted = True

	if isinstance(data.player2, AI):
		data.player2.computerInteractions(data)
	else:
		if keyboard.is_pressed("w"):
			data.player2.jump(data)
			data.player2.djkeyLifted = False
		else:
			data.player2.djkeyLifted = True
		if keyboard.is_pressed("a"):
			data.player2.direction = -1
			data.player2.moveLeft(data)
		elif keyboard.is_pressed("d"):
			data.player2.direction = 1
			data.player2.moveRight(data)
		else:
			data.player2.stop(data)
		if keyboard.is_pressed("s"):
			if data.player2.height == data.player2.stadningHeight:
				data.player2.y += (data.player2.stadningHeight - data.player2.squatHeight)
			data.player2.height = data.player2.squatHeight
		else:
			if data.player2.height == data.player2.squatHeight:
				data.player2.y -= (data.player2.stadningHeight - data.player2.squatHeight)
				data.player2.height = data.player2.stadningHeight
				oldY = data.player2.y
				data.player2.fixFloorCollision(data)
				if oldY == data.player2.y:
					data.player2.height == data.player2.stadningHeight
				else:
					data.player2.height = data.player2.squatHeight
					data.player2.y = oldY + data.player2.stadningHeight - data.player2.squatHeight # 800 - data.player2.squatHeight
		if keyboard.is_pressed("g"):
			data.player2.grapple(data)
		else:
			data.player2.endGrapple(data)
		if keyboard.is_pressed("h"):
			data.powerUps.boostPlayer(data, data.player2)
		else:
			data.powerUps.unBoost(data, data.player2)
		if keyboard.is_pressed("f"):
			data.player2.userPowerUp(data)
		else:
			data.player2.powerUpKeyLifted = True
def periodical(data):
	data.player1.move(data)
	data.powerUps.update(data.player1, data)
	data.player2.move(data)
	data.crates.collidesWithPlayer(data)
def runGame(data):
	userInteractions(data)
	periodical(data)
def moveScreen(data):
	data.map.findNewLeader(data)
	p = data.currentLeader
	if abs(data.player1.x - data.player2.x) < data.screenWidth/1.3:
		data.screenX = ((data.player1.x + data.player2.x)/2) - data.screenWidth/2
	else:
		if p.x > min(data.player1.x, data.player2.x):
			data.screenX = p.x - data.screenWidth*(1.15/1.3)
		else:
			data.screenX = p.x - data.screenWidth* (.15/1.3)

	if abs(data.player1.y - data.player2.y) < data.screenHeight/1.3:
		data.screenY = ((data.player1.y + data.player2.y)/2) - data.screenHeight/2
	else:
		if p.y > min(data.player1.y, data.player2.y):
			data.screenY = p.y - data.screenHeight*(1.15/1.3)
		else:
			data.screenY = p.y - data.screenHeight* (.15/1.3)
	if data.screenX < 0:
		data.screenX = 0
	elif data.screenX + data.screenWidth > data.map.mapWidth:
		data.screenX = data.map.mapWidth - data.screenWidth
	if data.screenY < 0:
		data.screenY = 0
	elif data.screenY + data.screenHeight > data.map.mapHeight:
		data.screenY = data.map.mapHeight - data.screenHeight
def drawFps(data):
	pass
	"""
	text = str(data.fpsActual)
	font = pygame.font.SysFont('Comic Sans MS', 20)
	d = max(min(int((((data.fpsActual-10)/20)*255)), 0),255)
	color = (255,d,d)
	text = font.render(text, True, color)
	data.screen.blit(text, (20,20))
	"""
def drawGame(data):
	moveScreen(data)
	data.map.drawMap(data)
	data.powerUps.draw(data)
	data.crates.drawCrates(data)
	for p in data.players:
		if isinstance(p, AI):
			p.drawAICheckPoints(data)
	data.player1.drawPlayer(data)
	data.player2.drawPlayer(data)
	drawFps(data)
	pygame.display.flip()
	pygame.display.update()
def countdown(data):
	ogTime = time.time()
	while True:
		secondsLeft = math.ceil((3 - (time.time() - ogTime)))
		size = int((secondsLeft - (3 - (time.time() - ogTime)))*50 + 10)
		moveScreen(data)
		data.map.drawMap(data)
		data.powerUps.draw(data)
		data.crates.drawCrates(data)
		data.player1.drawPlayer(data)
		text = str(secondsLeft)
		font = pygame.font.SysFont('Comic Sans MS', size)
		color = (0,255,0)
		text = font.render(text, True, color)
		data.screen.blit(text, (data.screenWidth/2, data.screenHeight/2))		
		pygame.display.flip()
		pygame.display.update()
		if secondsLeft<=0:
			break
def endGame(data):
	 for player in data.players:
	 	if player.x > data.screenX + data.screenWidth or player.x + player.width < data.screenX:
	 			pass #data.playingGame = False
	 	if player.y + player.height < data.screenY or player.y > data.screenY + data.screenHeight:
	 			pass #data.playingGame = False
def endGameUserInteractions(data):
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	if keyboard.is_pressed("space"):
		data.endGame = False
def drawEndGame(data):
	data.map.drawMap(data)
	data.powerUps.draw(data)
	data.crates.drawCrates(data)
	data.player1.drawPlayer(data)
	data.player2.drawPlayer(data)
	text = str(data.currentLeader) + " wins!, press space to restart"
	font = pygame.font.SysFont('Comic Sans MS', 20)
	color = (255,0,0)
	text = font.render(text, True, color)
	data.screen.blit(text, (data.screenWidth/2,data.screenHeight/2))
	pygame.display.flip()
	pygame.display.update()
def runEndGame(data):
	while data.endGame:
		endGameUserInteractions(data)
		drawEndGame(data)
	startGame()
def playGame(data):
	countdown(data)
	while data.playingGame:
		oldTime = time.time()
		runGame(data)
		drawGame(data)
		endGame(data)
		data.fpsClock.tick(data.fps) 
		data.fpsActual = int(1/(time.time() - oldTime))
	runEndGame(data)

def endPreGame(data):
	data.preGame = False
def preGameInit(data):
	data.preGame = True
	data.background = pygame.image.load("startScreen.png")
def preGameExit(data):
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	if keyboard.is_pressed("space"):
		endPreGame(data)
def preGameUser(data):
	if keyboard.is_pressed("w"):
		data.humans[1] = True
	if keyboard.is_pressed("up"):
		data.humans[0] = True
def preGameDraw(data):
	data.screen.blit(data.background, (0,0))
	if not data.humans[0]:
		text = str("Press up to join")
	else:
		text = str("Player 1 joined")
	if not data.humans[1]:
		text2 = str("Press w to join")
	else:
		text2 = str("Player 2 joined")
	font = pygame.font.SysFont('Knewave', 40)
	color = (0,0,0)
	text = font.render(text, True, color)
	text2 = font.render(text2, True, color)
	data.screen.blit(text, (80,375))
	data.screen.blit(text2, (650,375))
	pygame.display.flip()
	pygame.display.update()
def preGame(data):
	preGameInit(data)
	while True:
		oldTime = time.time()
		preGameExit(data)
		preGameUser(data)
		preGameDraw(data)
		data.fpsClock.tick(data.fps)
		if not data.preGame:
			break
	if data.humans[0]:
		data.player1 = Player(0)
	else:
		data.player1 = AI(0)
	if data.humans[1]:
		data.player2 = Player(1)
	else:
		data.player2 = AI(1)
	data.players = [data.player1, data.player2]
	data.currentLeader = data.player1 
def startGame():
	class Struct(object): pass
	data = Struct()
	init(data)
	preGame(data)
	playGame(data)

startGame()  