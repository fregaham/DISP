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

import disp
import disp.application
from mod_python import apache
import simplejson
import types

class ApplicationXul (disp.application.ApplicationBase):
	def __init__(self):
		disp.application.ApplicationBase.__init__ (self)
		
		# zpravy pro klienta
		self.messages_call = []
		self.messages_create = []
		
		self.xul_file_to_write = None
		self.xul_file_to_read = None
		
	def setTitle (self, title):
		self._title = title
		self.xul_client_call ("__root__", "set_title", title)
		
	def append (self, form):
		self.xul_client_call ("__root__", "add", form._id)
		
	def display (self, form):
		disp.application.ApplicationBase.display (self, form)
		self.xul_client_call ("__root__", "display", form._id)
		
	def xul_in (self, messages):
		
		for msg in messages:
			if msg[0] == "call":
				obj = self._root.getChild (msg[1])
				fname = msg[2]
				args = msg[3]
				
				obj.xul_call (fname, args)
				
			elif msg[0] == "state":
				obj = self._root.getChild (msg[1])
				state = msg[2]
				
				obj.xul_state (state)
				
	def xul_alert (self, txt):
		self.messages.append (["alert", txt])
		
	def xul_out (self):
		msg = self.messages_create
		msg.extend (self.messages_call)
		self.messages_call = []
		self.messages_create = []
		
		return simplejson.JSONEncoder(ensure_ascii=False).encode(msg)
	
	def xul_client_call (self, id, fname, args):
		if self._create:
			self.messages_call.append (["call", id, fname, args])
		
	def xul_client_create (self, xul_class, id):
		if self._create:
			self.messages_create.append (["create", xul_class, id])
			
	def writeFile (self, file):
		self.xul_file_to_write = file
		
		# TODO: vygenerovat neco jako klic, pak podle toho klice priradit konkretni soubor... 
		# nebo tak neco... 
		self.messages_call.append (["file_out", "42"])
		
	def readFile (self, file):
		self.xul_file_to_read = file
		
		# TODO: vygenerovat neco jako klic, pak podle toho klice priradit konkretni soubor... 
		# nebo tak neco... 
		self.messages_call.append (["file_in", "42"])
		
disp.application.Application = ApplicationXul
