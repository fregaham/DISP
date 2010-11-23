# -*- coding: utf-8 -*-
# copyright (C) 2006 Marek Schmidt

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import callback
import application

from pobject import PObject

class FileOutput(PObject):
	"""
	Zápis do souboru
	"""
	def __init__(self, parent=None, func = None, content_type="text/plain", filename="unnamed"):
		"""
		@param func: funkce která zapisuje, jejím jediným argumentem je stream tzn. neco co má metodu write. 
		"""
		PObject.__init__ (self, parent)
		self.notdirty()
		
		if func != None:
			self._callback = callback.Callback (self, func)
		else:
			self._callback = None
		self.content_type = content_type
		self.filename = filename

	def writeTo (self, stream):
		if self._callback != None:
			self._callback (stream)

	def open (self):
		self._root.writeFile (self)
		
class FileInput(PObject):
	"""
	Čtení ze souboru. 
	"""
	def __init__(self, parent=None, func = None):
		"""
		@param func: funkce která čte ze souboru. Jejím jediným argumentem bude stream, tzn něco co má metodu read.
		"""
		PObject.__init__ (self, parent)
		self.notdirty()
		
		if func != None:
			self._callback = callback.Callback (self, func)
		else:
			self._callback = None
			
	def readFrom (self, stream):
		if self._callback != None:
			self._callback (stream)
			
	def open (self):
		self._root.readFile (self)