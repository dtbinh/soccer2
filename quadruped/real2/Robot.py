#!/usr/bin/env python
##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################

from __future__ import print_function
from __future__ import division
from Leg import Leg
import time
import numpy
from tranforms import rotateAroundCenter, distance
import logging
logging.getLogger("Adafruit_I2C").setLevel(logging.ERROR)

##########################


class CrawlGait(object):
	"""
	Slow stable, 3 legs on the ground at all times

	This solution works but only allows 1 gait ... need to have multiple gaits
	"""
	z_profile = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 1, 0.5]  # 12 steps, normalized leg height
	scale_profile = [-0.5, -0.39, -0.28, -0.17, -0.06, 0.06, 0.17, 0.28, 0.39, 0.5, 0.17, -0.17]  # FIXME: wrong??

	def __init__(self, robot):
		self.current_step = 0
		self.legOffsets = [0, 6, 3, 9]
		self.i = 0
		self.robot = robot
		# self.reset()

	# def setFoot(self, foot0):
	# 	self.foot0 = foot0

	def height_at_progression(self, prog):
		"""
		Returns the normalized 1-D foot position for a 75% duty cycle
		|                   *
		|             *       *
		| *                      *
		+-------------------+----+-
		0                  .75  1.0
		Progress (step/gait_length)

		todo - just turn this into a lookup table ... why calculate it?
		"""
		# if prog < 0.0 or prog > 1.0:
		if 0.0 > prog > 1.0:
			raise Exception('prog out of bounds (0-1.0): {}'.format(prog))
			print('wtf??')
		speed = 0.0
		if prog <= 0.75: speed = 4.0 / 3.0 * prog - 0.5
		else: speed = -4.0 * (prog - 0.75) + 0.5  # don't think this is right???
		return speed

	def eachLeg(self, legNum, index, cmd):
		"""
		legNum - which leg to move
		index - the index of the gait: 0-n
		cmd - [x,y,z_rot]
		"""
		legnum = 0
		delta = list(cmd)  # need to make a copy
		zrot = float(delta[2])
		delta[2] = 0
		rest = self.robot.getFoot0(legNum)
		# print('2 zrot', zrot)
		# rest = self.legs[leg].resting_position
		# print('rest', rest)

		# hangle rotation
		# rotMove = rotateAroundCenter(rest, 'z', zrot) - rest

		# get correct index for this leg and get height
		indexmod = (index + self.legOffsets[legNum]) % len(self.z_profile)
		# z = self.z_profile[indexmod]*40.0

		# how far through the gait are we?
		# prog = indexmod/len(self.z_profile)

		# now scale (?) and handle translational/rotational movement
		# scale = 0.50*self.height_at_progression(prog)
		# move = scale * (numpy.array(delta) + rotMove)
		# move = rotateAroundCenter(scale * numpy.array(delta), 'z', deltaRot[2])

		# move[2] = z

		# newpos = self.legs[leg].resting_position + move
		# newpos = rest + move

		scale = self.scale_profile[indexmod]  # FIXME: this is fucked up!!!
		newpos = rest + scale * (numpy.array(delta) + rotateAroundCenter(rest, 'z', zrot) - rest)
		newpos[2] = -50.0+self.z_profile[indexmod]*25.0

		if legNum == legnum:
			# dr = rotateAroundCenter(rest, 'z', 0.5)
			# print('rest: {:3f}, {:3f}, {:3f}'.format(rest[0], rest[1], rest[2]))
			# print('rotate: {:3f}, {:3f}, {:3f}'.format(dr[0], dr[1], dr[2]))
			# print('scale:', scale)
			# print('[{}](x,y,z): {:.2f}\t{:.2f}\t{:.2f}'.format(indexmod, move[0], move[1], move[2]))
			print('[{}](x,y,z): {:.2f}\t{:.2f}\t{:.2f}'.format(indexmod, newpos[0], newpos[1], newpos[2]))

		# now move leg/servos
		# self.legs[legNum].move(*(newpos))
		self.robot.moveFoot(legNum, newpos)

	# def reset(self):
	# 	for leg in self.legs:
	# 		leg.reset()
		# pass
	def command(self, cmd):
		for i in range(0, len(self.z_profile)):
			self.step(i, cmd)
			time.sleep(0.05)  # maybe find biggest angular change to calculate this???
			# time.sleep(1)

	def step(self, i, cmd):
		"""
		"""
		# put this stuff back!!!!!!!!!! FIXME!!!!
		# for legNum in [0, 2, 1, 3]:  # order them diagonally
		# 	self.eachLeg(legNum, i, cmd)  # move each leg appropriately
		# 	time.sleep(0.01)  # need some time to wait for servos to move
		self.eachLeg(0, i, cmd)

	def pose(self, angles):
		pts = self.robot.legs[0].fk(*angles)
		self.robot.moveFoot(0, pts)

##########################


class Quadruped(object):
	"""
	"""
	def __init__(self, data):
		self.legs = []
		for i in range(0, 4):
			channel = i*4
			self.legs.append(
				Leg(
					data['legLengths'],
					[channel, channel+1, channel+2]
				)
			)

			for s in range(0, 3):
				if 'servoRangeAngles' in data:
					self.legs[i].servos[s].setServoRangeAngle(*data['servoRangeAngles'][s])
				if 'servoLimits' in data:
					self.legs[i].servos[s].setServoLimits(*data['servoLimits'][s])

	def __del__(self):
		"""
		Leg kills all servos on exit
		"""
		pass

	def getFoot0(self, i):
		return self.legs[i].foot0

	def moveFoot(self, i, pos):
		# if i == 0: print('Leg 0 ------------------------------')
		self.legs[i].move(*pos)


def quantize():
	"""
	turn this into table ... double check eqns
	"""
	def eqn(prog):
		speed = 0.0
		if prog <= 0.75: speed = 4.0 / 3.0 * prog - 0.5
		else: speed = -4.0 * (prog - 0.75) + 0.5
		return speed
	for i in range(0, 13):
		print('qantize {} -> {:.2f}'.format(i, eqn(i/12)))


if __name__ == "__main__":
	# quantize()
	# exit()

	# angles are always [min, max]
	test = {
		'legLengths': {
			'coxaLength': 17,
			'femurLength': 45,
			'tibiaLength': 63
		},
		'servoLimits': [[10, 170], [-80, 80], [-170, -10]],
		'servoRangeAngles': [[0, 180], [-90, 90], [-180, 0]]
	}
	robot = Quadruped(test)
	crawl = CrawlGait(robot)
	i = 5
	while i:
		print('step:', i)
		crawl.command([10.0, 0.0, 0.0])
		# time.sleep(1)
		i -= 1
	# crawl.pose([-45, -20, -110])
	# time.sleep(1)
