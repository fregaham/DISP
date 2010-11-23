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

import types
import callback

from pobject import PObject

class Event(PObject):
	"""
	Událost. K události se může objekt přihlásit pomocí addHandler. Vyvolání události
	se provede zavolnáním metody call. Po zavolání se zavolají callbacky všech zaregistrovaných 
	"handlerů".
	"""
	def __init__ (self, parent):
		PObject.__init__ (self, parent)
		self.notdirty ()
		self.handlers = []
		
	def addHandler (self, handler, *largs, **dargs):
		self.dirty ()
		
		self.handlers.append (callback.Callback (self, handler, *largs, **dargs))
			
	def __iadd__ (self, callback):
		self.handlers.append (callback)

	def removeHandler (self, handler, *largs, **dargs):
		self.dirty ()
		# callbacks have defined equivalence, we can do this: 
		self.handlers.remove (callback.Callback (None, None, handler, *largs, **dargs))
		
	def isEmpty (self):
		return len (self.handlers) == 0
	
	def __call__ (self, *largs, **dargs):
		self.call (*largs, **dargs)

	def call (self, *largs, **dargs):
		for callback in self.handlers:
			
			callback (*largs, **dargs)

