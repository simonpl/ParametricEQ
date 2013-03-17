# MyEqualizer.py
# Copyright (C) 2013 - Tobias Wenig
#			tobiaswenig@yahoo.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os, sys, inspect

from gi.repository import GObject, Gst, Peas
from gi.repository import RB
from Equalizer import EQControl
from Equalizer import EQBandParams
from config import Config

class MyEqualizerPlugin(GObject.Object, Peas.Activatable):
	object = GObject.property(type = GObject.Object)
	def __init__(self):
		super(MyEqualizerPlugin, self).__init__()

	def do_activate(self):
		self.shell = self.object
		self.shell_player = self.shell.props.shell_player
		self.player = self.shell_player.props.player
		self.eq = Gst.ElementFactory.make('equalizer-nbands', 'MyEQ')	
		conf = Config()		
		params = conf.load()#[EQBandParams(40.0,10.0,6.0)]		
		self.eqDlg = EQControl(self, params)        	
		self.eqDlg.add_ui( self, self.shell )
		#print inspect.getdoc( self.sp )
		self.filterSet = False
		self.apply_settings(params)
		self.psc_id = self.shell_player.connect('playing-song-changed', self.playing_song_changed)
	
	def set_filter(self):
		try:
			if self.filterSet:
				return			
			print 'adding filter'
			self.player.add_filter(self.eq)
			self.filterSet = True
			print 'done setting filter'
		except Exception as inst:
			print 'unexpected exception',  sys.exc_info()[0], type(inst), inst  
			pass

	def do_deactivate(self):
		print 'entering do_deactivate'
		self.shell_player.disconnect(self.psc_id)
		
		try:		
			self.player.remove_filter(self.eq)
			print 'filter disabled'	
		except:
			pass
					
		del self.shell_player
		del self.shell
		del self.eq

	def playing_song_changed(self, sp, entry):
		if entry == None:
			return
		genre = entry.get_string(RB.RhythmDBPropType.GENRE)

	def find_file(self, filename):
		info = self.plugin_info
		data_dir = info.get_data_dir()
		path = os.path.join(data_dir, filename)
		
		if os.path.exists(path):
			return path

		return RB.file(filename)
	
	def apply_settings(self,params):
		numEQBands = len( params )
		result = False
		print "num-bands : ", numEQBands
		if numEQBands > 0:
			print "got eq bands"
			self.eq.set_property('num-bands', numEQBands)
			for i in range(0,numEQBands):
				band = self.eq.get_child_by_index(i)
				#print inspect.getdoc( band.props.freq )
				band.props.freq = params[i].frequency
				print 'band.props.freq', band.props.freq
				band.props.bandwidth = params[i].bandwidth
				print 'band.props.bandwidth', band.props.bandwidth
				band.props.gain = params[i].gain
				print 'band.props.gain', band.props.gain
				band.props.type = 0
			result = True
		if True == result:
			self.set_filter()

