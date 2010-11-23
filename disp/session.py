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

from event import Event
import types

from pobject import PObject
from callback import Callback

#from mod_python import apache

class SessionWrapper (PObject):
	def __init__ (self, parent, handler, *largs, **dargs):
		PObject.__init__ (self, parent)
		self._ctor = Callback (self, handler, *largs, **dargs)
		
		self._root.getDeserializedEvent ().addHandler (self._construct)
		self._root.getSerializingEvent ().addHandler (self._destruct)
		
		#apache.log_error ("SessionWrapper ctor")
		
		self._obj = self._ctor ()
		
	def _construct (self):
		#apache.log_error ("SessionWrapper _construct")
		if "_obj" not in self.__dict__:
			self._obj = self._ctor ()
	
	def _destruct (self):
		del self._obj
		
	#def _setstate (self, state):
		#self.__dict__ = state
		#self._construct ()
		
	#def _getstate (self):
		#self._destruct ()
		#return self.__dict__
		
	def __call__(self, *args, **kw):
		return self._obj(*args, **kw)
	
	def __getattr__(self, attr):
		if "_obj" not in self.__dict__:
			raise AttributeError(attr)
		
		return getattr (self._obj, attr)
