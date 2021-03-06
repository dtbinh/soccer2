#!/usr/bin/env python
##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################

from __future__ import print_function
from __future__ import division

from Servo import Servo
from nose.tools import raises


def test_servo():
	Servo.all_stop()
	s = Servo(10)
	s.angle = 90
	s.setServoRangePulse(0, 4095)  # use the entire range
	assert(s.angleToPWM(0) == 0)
	assert(s.angleToPWM(180) == 4095)
	assert(s.angle == 90)
	assert(s.channel == 10)

	s.angle = 270  # limited to 0-180
	assert(s.angle == 180)
	s.angle = -10
	assert(s.angle == 0)


def test_limits():
	"""
	switching order messing things up
	"""
	s = Servo(15)
	s.setServoRangeAngle(0, 180)
	s.setServoLimits(0, 180)
	s.angle = 0; assert(s.angle == 0)
	s.angle = 45; assert(s.angle == 45)
	s.angle = 90; assert(s.angle == 90)
	s.angle = 180; assert(s.angle == 180)
	s.angle = 270; assert(s.angle == 180)
	s.angle = -45; assert(s.angle == 0)
	s.angle = -90; assert(s.angle == 0)
	s.angle = -270; assert(s.angle == 0)

	s.setServoRangeAngle(-90, 90)
	s.setServoLimits(-90, 90)
	s.angle = 0; assert(s.angle == 0)
	s.angle = 45; assert(s.angle == 45)
	s.angle = 90; assert(s.angle == 90)
	s.angle = 180; assert(s.angle == 90)
	s.angle = 270; assert(s.angle == 90)
	s.angle = -45; assert(s.angle == -45)
	s.angle = -90; assert(s.angle == -90)
	s.angle = -270; assert(s.angle == -90)


@raises(Exception)
def test_fail():
	s = Servo(15)
	s.setServoRangeAngle(0, 180)
	s.setServoLimits(-180, 90)  # this is outside of range, should fail


@raises(Exception)
def test_fail2():
	s = Servo(15)
	s.setServoRangeAngle(0, 180)
	s.setServoLimits(180, 0)

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
	print('run this with "nosetests -v test_servo.py"')
# 	# cmd_servo()
# 	# swing_servo()
# 	# test_limits()
# 	checks()
