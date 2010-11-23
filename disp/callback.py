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
from pobject import *

class Callback(PObject):
	""" Serializovatelná obálka nad funkcemi nebo metodami. """
	def __init__ (self, parent=None, func=None, *largs, **dargs):
		
		PObject.__init__ (self, parent)
		self.notdirty()
		
		if type(func) == types.FunctionType:
			self._callback = (None, func, largs, dargs)
		elif type(func) == types.MethodType:
			self._callback = (func.im_self, func.im_func.func_name, largs, dargs)
		else:
			#TODO: vlastni typ exceptiony
			raise Exception("Only functions or bound methods may be callbacks")
		
	def __call__ (self, *largs, **dargs):
		(instance, funcname, custom_largs, custom_dargs) = self._callback
		
		arglist = [x for x in largs]
		arglist.extend(custom_largs)

		kwmap = {}
		kwmap.update(dargs)
		kwmap.update(custom_dargs)
			
		if instance == None:
			func = funcname
		else:
			func = getattr (instance, funcname)
				
		return func (*arglist, **kwmap)
		
	def __eq__ (self, callback):
		return self._callback == callback._callback
