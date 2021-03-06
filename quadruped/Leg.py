#!/usr/bin/env python
##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################

from __future__ import print_function
from __future__ import division
import numpy as np
from math import sin, cos, acos, atan2, sqrt, pi
from math import radians as d2r
from math import degrees as r2d
from lib.kinematics import T
# from Interfaces import PCA9685
import logging
from lib.Servo import Servo
# import time

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)


class Leg(object):
	"""
	"""

	def __init__(self, lengths, channels, limits=None):
		"""
		"""
		if not len(channels) == 3: raise Exception('len(channels) != 3')

		self.servos = []
		# self.footPosition = [0.0, 0.0, 0.0]
		# self.angles = [0.0, 0.0, 0.0]

		self.coxaLength = lengths['coxaLength']
		self.tibiaLength = lengths['tibiaLength']
		self.femurLength = lengths['femurLength']

		# Create each servo and move it to the initial position
		# servo arrange: coxa femur tibia
		for i in range(0, 3):
			# print('leg channels', channels)
			if limits: lim = limits[i]
			else: lim = None
			
			self.servos.append(Servo(channels[i], lim))
			# self.servos[i].angle = initAngles[i]
			# print('servo {} angle {}'.format(channels[i], initAngles[i]))
			# time.sleep(1)

		# initAngles = [-45, -20, -110]
		# initAngles = [0, -20, -90]
		# initAngles = [0, 45, -135]  # [x,y,z] = [55.7, 0, -33.3] mm
		initAngles = [0, 45, -150]  # [x,y,z] = [55.7, 0, -33.3] mm
		self.foot0 = self.fk(*initAngles)
		# print('init foot0', self.foot0)
		# exit()
		# self.servos[0].all_stop()

	def __del__(self):
		"""
		Turn off servos associated with this leg
		"""
		self.servos[0].stop()
		self.servos[1].stop()
		self.servos[2].stop()

	def fk(self, a, b, g):
		"""
		angle are all degrees
		"""
		Lc = self.coxaLength
		Lf = self.femurLength
		Lt = self.tibiaLength

		if 0:
			phi = a
			theta2 = b
			theta3 = g

			params = [
				# a_ij alpha_ij  S_j  theta_j
				[Lc,   d2r(90.0),   0.0,   d2r(theta2)],  # frame 12
				[Lf,    d2r(0.0),   0.0,   d2r(theta3)]   # frame 23
			]

			r = T(params, d2r(phi))
			foot = r.dot(np.array([Lt, 0.0, 0.0, 1.0]))

			return foot[0:-1]  # DH return vector size 4, only grab (x,y,z) which are the 1st 3 elements
		else:
			a = d2r(a)
			b = d2r(b)
			g = d2r(g)
			foot = [
				Lc*cos(a) + Lf*cos(a)*cos(b) + Lt*(-sin(b)*sin(g)*cos(a) + cos(a)*cos(b)*cos(g)),
				Lc*sin(a) + Lf*sin(a)*cos(b) + Lt*(-sin(a)*sin(b)*sin(g) + sin(a)*cos(b)*cos(g)),
				Lf*sin(b) + Lt*(sin(b)*cos(g) + sin(g)*cos(b))
			]

			return np.array(foot)

	def ik(self, x, y, z):
		"""
		Calculates the inverse kinematics from a given foot coordinate (x,y,z)[mm]
		and returns the joint angles[degrees]

		Reference (there are typos)
		https://tote.readthedocs.io/en/latest/ik.html
		"""
		try:
			Lc = self.coxaLength
			Lf = self.femurLength
			Lt = self.tibiaLength
			a = atan2(y, x)  # <---
			# a = atan2(x, y)
			f = sqrt(x**2 + y**2) - Lc
			b1 = atan2(z, f)  # <---
			# b1 = atan2(f, z)
			d = sqrt(f**2 + z**2)  # <---
			b2 = acos((Lf**2 + d**2 - Lt**2) / (2.0 * Lf * d))
			b = b1 + b2
			g = acos((Lf**2 + Lt**2 - d**2) / (2.0 * Lf * Lt))

			#### FIXES ###################################
			g -= pi  # fix to align fk and ik frames
			##############################################

			# print('ik angles: {:.2f} {:.2f} {:.2f}'.format(r2d(a), r2d(b), r2d(g)))

			# return a, b, g  # coxaAngle, femurAngle, tibiaAngle
			return r2d(a), r2d(b), r2d(g)  # coxaAngle, femurAngle, tibiaAngle
		except Exception as e:
			print('ik error:', e)
			raise e

	def move(self, x, y, z):
		"""
		Attempts to move it's foot to coordinates [x,y,z]
		"""
		try:
			a, b, c = self.ik(x, y, z)  # inverse kinematics
			angles = [a, b, c]
			# print('angles: {:.2f} {:.2f} {:.2f}'.format(*angles))
			for i, servo in enumerate(self.servos):
				# print('i, servo:', i, servo)
				angle = angles[i]
				if i == 2: angle = -1*angle - 180   # correct for tibia servo backwards
				# print('servo {} angle {}'.format(i, angle))
				servo.angle = angle

		except Exception as e:
			print (e)
			raise

	def reset(self):
		# self.angles = self.resting_position
		self.move(*self.foot0)




if __name__ == "__main__":
	# test_fk_ik()
	# test_full_fk_ik([0,1,2])
	# test_full_fk_ik([4,5,6])
	# test_full_fk_ik([8,9,10])
	# test_full_fk_ik([12,13,14])
	# check_range()
	print('Hello cowboy!')
