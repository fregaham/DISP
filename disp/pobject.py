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

import string
import cPickle
from cStringIO import StringIO

class PObject(object):
	def __init__ (self, parent = None):
		
		self._children = {}
		self._child_id = 0
		
		self._name = None
		self._id = ""
		self._parent = None
		self._root = None
		self._dirty = True
		
		if parent != None:
			parent.insertChild (self)
				
	def dirty (self):
		if not self._root._init:
			self._dirty = True
			
	def notdirty (self):
		if self._root._init:
			self._dirty = False
			
	def _getChildSplitted (self, rid_splitted):
		if len(rid_splitted) == 0:
			return self
		
		return self._children[rid_splitted[0]]._getChildSplitted (rid_splitted[1:])
			
	def getChild (self, rid):
		""" returns child with relative id 'rid' """ 
		
		ids = rid.split (".")
		return self._getChildSplitted (ids[1:])
	
	def getRoot (self):
		return self._root
			
	def insertChild (self, child):
		child._parent = self
		child._root = self._root
		
		if child._name == None:
			self._child_id += 1
			child._name = str (self._child_id)
		
		child._id = self._id + "." + child._name
		self._children[child._name] = child
		
		# Pokud nejsme v inicializacni fazi, pridanim objektu zaspinujeme tento objekt
		if not self._root._init:
			self.dirty ()
		
class PRef (PObject):
	def __init__ (self, parent = None, pobject = None):
		PObject.__init__ (self, parent)
		self._pid = None
		self.ref (pobject)
		
	def ref (self, pobject):
		if pobject != None:
			self._pid = pobject._id
		else:
			self._pid = None
		
	def deref (self):
		if self._pid == None:
			return None
		
		return self._root.getChild (self._pid)

def iteratePreOrder(root):
	yield root
	for child in root._children.values():
		for i in iteratePreOrder (child):
			yield i
		
class PRoot (PObject):
	def __init__ (self):
		PObject.__init__ (self)
		
		self._root = self
		self._id = ""
		
		self._init = True
		
		self._dirty = False
		
	def persistent_id (self, obj):
		if isinstance (obj, PObject):
			return obj._id
		else:
			return None

	def serialize(self):
	
		# Mapa objektu
		objs = {}
	
		# Mapa slovniku
		dicts = []
	
		# Nejprve rozdelime objekty a oddelime vnitrnosti
		lst = [i for i in iteratePreOrder (self)]
		for obj in lst:
			
			_id = obj._id
			
			if hasattr (obj, "_getstate"):
				dict = obj._getstate ()
			else:
				dict = obj.__dict__
		
			if dict["_dirty"]:
				
				objs[_id] = obj
				# Smazeme implicitne dane vlastnosti
				
				#apache.log_error ("serialize obj (%s) id: %s" % (str(obj), _id))
				
				del dict["_id"]
				del dict["_root"]
				del dict["_name"]
				del dict["_parent"]
				del dict["_children"]
			
				obj.__dict__ = {}
				
				# id tam musime nechat, kvuli persistent_id
				obj.__dict__["_id"] = _id
				dicts.append ( (obj._id, dict) )
			
			else:
				# Je cisty, dictionary vubec nepotrebujeme
				obj.__dict__ = {}
				obj.__dict__["_id"] = _id
				#dicts.append ( (obj._id, dict) )
		
		# Do prvniho baliku dame objekty bez vnitrnosti
		pickled_objs = cPickle.dumps (objs)
		
		# Do druheho baliku slovniky
		src = StringIO()
		pickler = cPickle.Pickler (src)
		
		pickler.persistent_id = self.persistent_id
		pickler.dump (dicts)
		
		return (pickled_objs, src.getvalue())
			
	def persistent_load (self, pid):
		
		try:
			return self.getChild (pid)
		except:
			# Zkusime tedy hledat mezi prave loadovanymi
			return self.loading_objs [pid]
		
	def deserialize (self, data):
		pickled_objs = data[0]
		pickled_dicts = data[1]
		
		objs = cPickle.loads (pickled_objs)
		
		self.loading_objs = objs
		
		src = StringIO(pickled_dicts)
		unpickler = cPickle.Unpickler (src)
		unpickler.persistent_load = self.persistent_load
		
		dicts = unpickler.load ()
		
		del self.loading_objs
			
		for key_string, dict in dicts:
			# Existuje jiz tento objekt?
				
			key = key_string.split (".")
				
			try:
				#apache.log_error ("deserialize key = %s" % (str(key)))
				
				obj = self._getChildSplitted (key[1:])
				
				#apache.log_error ("deserialize obj (%s) id: %s" % (str(obj), string.join(key,".")))
				
				new_dict = {}
				new_dict["_id"] = obj.__dict__["_id"]
				new_dict["_root"] = obj.__dict__["_root"]
				new_dict["_name"] = obj.__dict__["_name"]
				new_dict["_parent"] = obj.__dict__["_parent"]
				new_dict["_children"] = obj.__dict__["_children"]
					
				# Jiste je dirty, kdyz byl serializovan
				new_dict["_dirty"] = True
					
				# Vlozima nova data
				new_dict.update (dict)
					
				if hasattr (obj, "_setstate"):
					obj._setstate (new_dict)
				else:
					obj.__dict__ = new_dict
					
			except Exception, x:
				
				
				# Asi neexistuje... 
				# Pri serializace jsme prochazeli pre-order, 
				# Pokud existoval, musi ted parent existovat
					
				try:
					obj = objs [key_string]
				except:
					#apache.log_error ("deserialize cannot find object: %s" % key_string)
					continue
				
				try:
					parent = self._getChildSplitted (key[1:-1])
				except:
					# apache.log_error ("deserialize cannot find parent: %s" % string.join(key,"."))
					continue
				
				#apache.log_error ("deserialize failed")
						
				new_dict = {}
				new_dict["_id"] = key_string
				new_dict["_root"] = parent.__dict__["_root"]
				new_dict["_name"] = key[-1]
				new_dict["_parent"] = parent
				new_dict["_children"] = {}
					
				new_dict["_dirty"] = True
					
				new_dict.update (dict)
					
				if hasattr (obj, "_setstate"):
					obj._setstate (new_dict)
				else:
					obj.__dict__ = new_dict
					
				# Pridame objekt do slovniku rodice
				parent.__dict__["_children"] [key[-1]] = obj
					
