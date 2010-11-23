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

class Cursor:
	"""
	Rozhrani kurzoru. 
	"""
	def __init__ (self):
		pass
	
	def begin (self):
		pass
	
	def getIterator (self):
		return self.__iter__()
	
	def getItem (self, i):
		return self[i]
	
	def getItems (self, i, j):
		return self[i:j]
	
	def getLength (self):
		return self.__len__ ()
	
	def __iter__ (self):
		return None
	
	def __getitem__ (self, i):
		return None
	
	def count (self):
		return self.__len__ ()
	
	def __len__ (self):
		return None

	def end (self):
		pass

class SOCursor (Cursor):
	"""
	Implementace rozhrani kurzoru pro prochazeni tabulek pomoci SQLObject
	"""
	def __init__ (self, table, **dargs):
		"""
		@param table: Tabulka, ktera se pouzije pro dotaz
		@param dargs: Další argumenty, které se předaji metodě select. viz dokumentace k SQLObject
		"""
		Cursor.__init__ (self)
		self.table = table
		
		self.dargs = dargs
	
	def begin (self):
		self.cursor = self.table.select (**self.dargs)
		
	def __iter__ (self):
		return self.cursor.lazyIter ()
	
	def __getitem__ (self, i):
		return self.cursor[i]
	
	def __len__ (self):
		return self.count ()
	
	def count (self):
		return self.cursor.count ()

	def end (self):
		del self.cursor
