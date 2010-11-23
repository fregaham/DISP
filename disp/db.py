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

from session import SessionWrapper
import sqlobject

#from mod_python import apache

class SOConnection (SessionWrapper):
	"""
	sessionwrapper nad připojením k SQLObject databázi
	"""
	def __init__ (self, parent, url, **dargs):
		self._url = url
		self._dargs = dargs
		#apache.log_error ("SOConnection ctor...")
		SessionWrapper.__init__ (self, parent, self._connect)
		
	def _connect (self):
		#apache.log_error ("SOConnection connecting...")
		ret = sqlobject.connectionForURI(self._url, **self._dargs)
		return ret
	
	def _destruct (self):
		#apache.log_error ("SOConnection closing...")
		self._obj.close ()
		SessionWrapper._destruct (self)
	
class SOSQLiteConnection (SOConnection):
	"""
	Připojení k SQLite databázi v souboru. 
	"""
	def __init__ (self, parent, filename, **dargs):
		self._url = "sqlite://" + parent._root.absolutePath(filename)
		self._dargs = dargs
		SessionWrapper.__init__ (self, parent, self._connect)
		
	def _connect (self):
		ret = sqlobject.connectionForURI(self._url, **self._dargs)
		return ret
	
class SOClass (SessionWrapper):
	"""
	sessionwrapper nad třídou (tabulkou) v SQLObject databázi. 
	"""
	def __init__ (self, parent, klass):
		"""
		@param parent: SOConnection reprezentující spojení s databází
		@param klass: Třída odovozená SQLObject reprezentující tabulku v SQLObject databázi
		"""
		
		assert isinstance(parent, SOConnection)
		
		self._klass = klass
		SessionWrapper.__init__ (self, parent, self._connect)
		
	def _connect (self):
		ret = sqlobject.dbconnection.ConnWrapper(self._klass, self._parent._obj)
		return ret

