#!/usr/bin/env python

import Module as Mod
import glob
# import wave
import random
import os


class Plugin(Mod.Module):
	"""
	Handles commands related to star wars.
	"""
	def __init__(self):
		Mod.Module.__init__(self, 'tv_movie_sounds')
		self.intent = 'tv_movie_sounds'

		self.star_wars_sounds = self.loadSounds('star_wars')
		self.venture_bros_sounds = self.loadSounds('venture_brothers')
		self.blues_bros_sounds = self.loadSounds('blues_bros')

	def loadSounds(self, kind):
		filename = '/Users/kevin/github/jarvis/sounds/' + kind  # FIXME 20160627 path wrong
		snds = glob.glob(filename + '/*.wav')
		self.logger.info('   [>] {0!s} loaded {1:d} sound files'.format(type, len(snds)))
		return snds

	def process(self, entity):
		print entity
		sound = ''

		name = entity['contact'][0]['value'].lower()
		# venture bros not working??? also, might be a bad wave file
		if name == 'star wars':
			sound = random.choice(self.star_wars_sounds)
		elif name == 'blues brothers':
			sound = random.choice(self.blues_bros_sounds)
		elif name == 'venture brothers':
			sound = random.choice(self.venture_bros_sounds)

		if sound == '':
			print 'Error: sound for {} does not exist'.format(name)
		else:
			self.playWave(sound)
		return ''

	def playWave(self, fname):
		"""
		Plays a Wave file
		in: path to sound to play
		out: none
		"""
		os.system('afplay {0!s}'.format((fname)))


if __name__ == '__main__':
	s = Plugin()
	en = {'contact': {'body': 'Star Wars'}}
	snd = s.process(en)
	print snd
