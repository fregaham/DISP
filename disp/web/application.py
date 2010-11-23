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
import disp.event
import disp.application

import disp.web.form

from disp.pobject import *
#import mod_python
from mod_python import apache
from mod_python.util import FieldStorage

class WebInContext:
	def __init__ (self):
		self.events = []
	
	def addEvent (self, event, *list, **dict):
		self.events.append ( (event,list,dict) )
		
class WebOutContext:
	def __init__ (self):
		self.url = None

class ApplicationWeb (disp.application.ApplicationBase):
	def __init__(self):
		disp.application.ApplicationBase.__init__ (self)
		
		self.web_event_post = disp.event.Event (self)
		
		self.web_file_to_write = None
		self.web_file_to_read = None
		self.web_upload = disp.web.form.FileUploadWeb (self, None)
		
		self._title = "Hello, world!"
		
	def setTitle (self, title):
		self._title = title
		
	def getTitle (self):
		return self._title
		
	def writeFile (self, file):
		self.web_file_to_write = file
		
	def readFile (self, file):
		
		#apache.log_error ("ApplicationWeb.readFile file=%s" % (str(file)))
		
		self.web_file_to_read = file
		self.web_upload.setFile(file)
		
	#def web_fileUpload (self, file):
		#self.web_files_to_read = None
		
	def web_in (self, req):
		
		field_storage = FieldStorage(req, keep_blank_values=1)
		
		context = WebInContext ()

		for field in field_storage.list:

			try:
				
				path = field.name[len(self._id):].split (".")
	
				#apache.log_error ("path = " + str(path))

				if (len (path) > 1):
					if path[1] == "__post":
						self.web_event_post.call ()
					else:
						self._children[path[1]].web_in (path[2:], field, context)

			except AttributeError, x:
				pass

		#Spustime udalosti
		for event, listargs, dictargs in context.events:
			#apache.log_error ("event " + str(event))
			event.call (*listargs, **dictargs)
	
	def web_out (self, url, req):
		
		if self.web_file_to_read != None:
			
			context = WebOutContext ()
			context.url = url
		
			ret = """<html>
	<head>
		<title>%s</title>
		<link rel="stylesheet" type="text/css" title="Style" href="./style.css" />
	</head>
	<body>
		<form enctype=\"multipart/form-data\" action=\"%s\" method="POST">
	""" % (disp.web.form.escape_xml (self._title), context.url)
			ret = ret + self.web_upload.web_out (context)
			ret = ret + "</body></html>"
		
			req.headers_out["Pragma"] = "no-cache"
			req.content_type = "text/html; encoding=UTF-8"
	
			req.write(ret.encode("utf8"))
			
		
		elif self.web_file_to_write != None:
			# We have file to "download":
			f = self.web_file_to_write
			
			req.content_type = f.content_type
			req.headers_out["Content-Disposition"] = "attachment; filename=\"%s\"" % f.filename
			f.writeTo (req)
			
			self.web_file_to_write = None
			
		else:
		
			context = WebOutContext ()
			context.url = url
		
			ret = """<html>
	<head>
		<title>%s</title>
		<link rel="stylesheet" type="text/css" title="Style" href="./style.css" />
	</head>
	<body>
		<form action=\"%s\" method="POST">
	""" % (disp.web.form.escape_xml (self._title), context.url)
	
			ret = ret + "<div><input type=\"hidden\" id=\"%s\" name=\"%s\" value=\"1\"/></div>" % (self._id + ".__post", self._id+".__post")
			
			#apache.log_error ("web_out, form=" + `self.displayed_form`)
			
			#if self.displayed_form != None:
			ret = ret + self.displayed_form.web_out (context)
			ret = ret + "</body></html>"
		
			req.headers_out["Pragma"] = "no-cache"
			req.content_type = "text/html; encoding=UTF-8"
	
			req.write(ret.encode("utf8"))
		
disp.application.Application = ApplicationWeb
