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

def launch (req, app_ctor, url, abs_path):
	
	sess = mod_python.Session.Session(req)
	
	session = sess.get ("web_session", None)
	
	if session == None:
		app = app_ctor ()
		app.setPrePath (abs_path)
		
		app._init = True
		app.initialize ()
		app._init = False
		
		app.event_deserialized.call ()
		
	else:
		
		app = app_ctor ()
		app.setPrePath (abs_path)
		
		app._init = True
		app.initialize ()
		app._init = False
		
		try:
			app.deserialize (session)
		except:
			#nevysla deserializace, zaciname odznovu...
			app = app_ctor ()
			app.setPrePath (abs_path)
		
			app._init = True
			app.initialize ()
			app._init = False
		
		app.event_deserialized.call ()
		
		
	app.web_in (req)
	
	form = app.displayed_form
	
	app.web_out (url, req)
	
	app.event_pre_serialize.call ()
	
	sess["web_session"] = app.serialize ()
	sess.save ()
	
	return apache.OK
