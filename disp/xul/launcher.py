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

import base64
from mod_python import apache
import mod_python.Session
from mod_python.util import FieldStorage
import simplejson
import types


def launch (app_ctor, req, abs_path):
	
	init = False
	mode = "normal"
	
	file_upload = None
	
	if req.method == "GET":
		field_storage = FieldStorage(req, keep_blank_values=1)
		for field in field_storage.list:
			if field.name == "init":
				init = True
			elif field.name == "download":
				mode = "download"
			elif field.name == "upload":
				mode = "upload"
				file_upload = field.value
	
	try:
		messages = simplejson.loads (req.read ())
	except ValueError:
		messages = None
	
	#if messages == "init":
		#init = True
		
	if type(messages) != types.ListType:
		messages = []
	
	sess = mod_python.Session.Session(req)
	
	session = sess.get ("xul_session", None)
	
	if session == None or init:
		app = app_ctor ()
		app.setPrePath (abs_path)
		app._init = True
		app._create = True
		app.initialize ()
		app._init = False
		
		app.event_deserialized.call ()
		
	else:
		app = app_ctor ()
		app.setPrePath (abs_path)
		
		app._create = False
		app._init = True
		app.initialize ()
		app._init = False
		
		app.deserialize (session)
		
		app._create = True
		
		app.event_deserialized.call ()
		
	if mode == "normal":
		app.xul_in (messages)
		ret = app.xul_out ()
	elif mode == "download":
		assert session != None
		
		f = app.xul_file_to_write
		
		req.content_type = f.content_type
		req.headers_out["Content-Disposition"] = "inline; filename=\"%s\"" % f.filename
		f.writeTo (req)
			
		app.web_file_to_write = None
		app.dirty ()
	elif mode == "upload":
		assert session != None
		
		f = app.xul_file_to_read
		if f != None:
			f.readFrom (va.file)
			
		app.web_file_to_read = None
		app.dirty ()
	
	app.event_pre_serialize.call ()
	sess["xul_session"] = app.serialize ()
	sess.save ()
	
	if mode == "normal":
		req.headers_out["Pragma"] = "no-cache"
		req.content_type = "text/plain; encoding=UTF-8"
		req.write (ret.encode ("utf-8"))
		
	elif mode == "download":
		pass
	elif mode == "upload":
		pass
	
	return apache.OK
