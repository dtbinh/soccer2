#!/usr/bin/env python
##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################

from __future__ import print_function
from __future__ import division
from Interfaces import PCA9685
import logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)

global_pwm = PCA9685()  # don't like global variables!!
global_pwm.set_pwm_freq(50)  # fix to 50 Hz, should be more than enough


class PWM(object):
	"""
	This handles low level pwm controller and timing
	"""
	# changed this to match arduino: 0-180 deg range
	maxAngle = 180.0  # servo max angle
	minAngle = 0.0
	pwm_max = 500  # Max pulse length out of 4096
	pwm_min = 130  # Min pulse length out of 4096
	# pwm = PCA9685()

	def __init__(self, channel):
		"""
		"""
		self.pwm = global_pwm
		if 0 > channel > 15:
			raise Exception('Servo channel out of range[0-15]: {}'.format(channel))
		self.channel = channel
		self.logger = logging.getLogger(__name__)

	def __del__(self):
		"""
		Shuts off servo on exit.
		"""
		self.stop()

	@staticmethod
	def all_stop():
		"""
		This stops all servos
		"""
		global_pwm.set_all_pwm(0, 0x1000)

	@staticmethod
	def set_pwm_freq(f):
		global_pwm.set_pwm_freq(f)

	def stop(self):
		"""
		This stops an individual servo
		"""
		self.pwm.set_pwm(self.channel, 0, 0x1000)

	def setServoRangePulse(self, minp, maxp):
		"""
		Sets the range of the on/off pulse. This must be between 0 and 4095.
		"""
		maxp = int(max(min(4095, maxp), 0))
		minp = int(max(min(4095, minp), 0))
		self.pwm_max = maxp
		self.pwm_min = minp

	def setServoRangeAngle(self, mina, maxa):
		"""
		There is no limit check on this. Some servos have >180 deg range while
		some have <180 range. Suggest maxa - mina ~= 180, but they can be
		any range, ex: mina 145 to maxa 325 deg which is 180 deg range.
		"""
		self.maxAngle = maxa
		self.minAngle = mina
		if mina >= maxa: raise Exception('setServoRangeAngle(): max > min')

	def angleToPWM(self, angle):
		"""
		in:
			- angle: angle to convert to pwm pulse
			- mina: min servo angle
			- maxa: max servo angle

		out: pwm pulse size (0-4096)
		"""
		# these are just to shorten up the equation below
		mina = self.minAngle
		maxa = self.maxAngle
		maxp = self.pwm_max
		minp = self.pwm_min
		# angle = max(min(maxa, angle), mina)  # aready done?
		# servo_min = 150  # Min pulse length out of 4096
		# servo_max = 600  # Max pulse length out of 4096
		# m = (self.pwm_max - self.pwm_min) / (maxa - mina)
		# b = self.pwm_max - m * maxa
		# pulse = m * angle + b
		# y=m*x+b
		pulse = (maxp - minp)/(maxa - mina)*(angle-maxa) + maxp
		return int(pulse)


class Servo(PWM):
	"""
	Keeps info for servo and commands their movement.
	angles are in degrees
	servo commands are between -90 and 90 degrees, with 0 deg being center
	"""
	_angle = 0.0  # current angle
	# _angle0 = 0.0  # initial reset angle

	def __init__(self, channel, limits=None):
		"""
		remove channel from here? also, move limits to attach?

		pos0 [angle] - initial or neutral position
		limits [angle, angle] - [optional] set the angular limits of the servo to avoid collision
		"""
		PWM.__init__(self, channel)

		if limits: self.setServoLimits(*limits)
		else: self.setServoLimits(0.0, 180.0)

	def attach(self, channel, limits=None):
		"""
		Not sure if this is useful, but sort of mirrors Arduino.
		"""
		self.channel = channel
		if limits: self.setServoLimits(*limits)

	@property
	def angle(self):
		"""
		Returns the current servo angle
		"""
		# print('@property angle')
		return self._angle

	@angle.setter
	def angle(self, angle):
		"""
		Sets the servo angle and clamps it between [limitMinAngle, limitMaxAngle].
		It also commands the servo to move.
		"""
		# check range of input
		self._angle = max(min(self.limitMaxAngle, angle), self.limitMinAngle)
		# self.move(self._angle)
		# print('@angle.setter: {} {}'.format(angle, self._angle))
		# self.logger.debug('@angle.setter: {} {}'.format(angle, self._angle))
		pulse = self.angleToPWM(self._angle)
		self.pwm.set_pwm(self.channel, 0, pulse)
		# time.sleep(0.1/60*self._angle)  # 0.1 sec per 60 deg movement

	def setServoLimits(self, minAngle, maxAngle):
		"""
		sets maximum and minimum achievable angles. Remeber, the limits have to
		be within the servo range of [0, 180] ... anything more of less won't
		work unless your change setServoRangleAngle() to something other than
		0 - 180.

		in:
			minAngle - degrees
			maxAngle - degrees
		"""
		self.limitMaxAngle = maxAngle
		self.limitMinAngle = minAngle
		if maxAngle > self.maxAngle or minAngle < self.minAngle or minAngle > maxAngle:
			raise Exception('setServoLimits(): your limits are outside of servo range (see setServoRangleAngle())')


# def cmd_servo():
# 	Servo.all_stop()
# 	s = Servo(15, [-85, 85])
# 	time.sleep(.1)
# 	print('neg')
# 	s.angle = -90
# 	time.sleep(1)
# 	print('center')
# 	s.angle = 0
# 	time.sleep(1)
# 	print('pos')
# 	s.angle = 90
# 	time.sleep(1)
# 	print('center')
# 	s.angle = 0
# 	time.sleep(1)
# 	# s.all_stop()
# 	Servo.all_stop()
# 	# assert(s.angle == 90 and s.channel == 10)
#
#
# def swing_servo():
# 	Servo.all_stop()
# 	s = Servo(15)
# 	time.sleep(.01)
# 	i = 3
# 	while i:
# 		for a in range(0, 180, 5):
# 			s.angle = a
# 			time.sleep(0.1)
# 		time.sleep(1)
# 		i -= 1
# 	# Servo.all_stop()
# 	s.angle = 90
# 	Servo.all_stop()
#
#
# def checks():
# 	check = lambda x, a, b: max(min(b, x), a)
# 	print('0 in [0,180]:', check(0, 0, 180))
# 	print('90 in [0,180]:', check(90, 0, 180))
# 	print('180 in [0,180]:', check(180, 0, 180))
# 	print('-90 in [0,180]:', check(-90, 0, 180))
# 	print('-180 in [0,180]:', check(-180, 0, 180))
# 	print('--------------------')
# 	print('these are wrong! Cannot reverse order')
# 	print('0 in [180,0]:', check(0, 180, 0))
# 	print('45 in [180,0]:', check(45, 180, 0))
# 	print('90 in [180,0]:', check(90, 180, 0))
# 	print('180 in [180,0]:', check(180, 180, 0))
# 	print('-90 in [180,0]:', check(-90, 180, 0))
# 	print('-180 in [180,0]:', check(-180, 180, 0))
# 	print('--------------------')
# 	print('0 in [-180,0]:', check(0, -180, 0))
# 	print('90 in [-180,0]:', check(90, -180, 0))
# 	print('180 in [-180,0]:', check(180, -180, 0))
# 	print('-90 in [-180,0]:', check(-90, -180, 0))
# 	print('-45 in [-180,0]:', check(-45, -180, 0))
# 	print('-180 in [-180,0]:', check(-180, -180, 0))


if __name__ == "__main__":
	# cmd_servo()
	# swing_servo()
	# test_limits()
	# checks()
	print('Hello space cowboy!')
