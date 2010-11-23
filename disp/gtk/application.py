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
import disp.session

import gtk

class ApplicationGtk (disp.application.ApplicationBase):
	def __init__(self):
		disp.application.ApplicationBase.__init__ (self)
		
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		vbox = gtk.VBox()

		window.add (vbox)
		
		self.gtk_window = window
		self.gtk_vbox = vbox
		
		window.connect("delete-event", self.on_window_delete)
		
		#window.set_default_size (800, 600)
		
		self.event_deserialized ()
		
	def setTitle (self, title):
		self._title = title
		
		self.gtk_window.set_title (title)
		
	def on_window_delete (self, widget, event):
		gtk.main_quit()
		
	def run (self):
		
		self._init = False
		self.initialize ()
		
		form = self.getDisplayedForm ()
		if form != None:
			form.gtk_show ()
		#self.getDisplayedForm ().gtk_show ()
		self.gtk_vbox.show ()
		self.gtk_window.show ()
		
		gtk.main()
		
	def append (self, form):
		#disp.application.ApplicationBase.append (self, form)
		self.gtk_vbox.add (form.gtk_object)
		
	def display (self, form):
		oldform = self.getDisplayedForm ()
		
		if oldform != None:
			oldform.gtk_hide ()
			
		self.displayed_form = form
	
		if self.displayed_form != None:
			self.displayed_form.gtk_show ()
			
		self.dirty ()
		
	def writeFile (self, f):
		dialog = gtk.FileChooserDialog("Save..", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		
		response = dialog.run ()
		
		if response == gtk.RESPONSE_OK:
			filename = dialog.get_filename()
			
			fp = file(filename, "w")
			f.writeTo(fp)
			fp.close ()
		
		dialog.destroy()
			
	def readFile (self, f):
		dialog = gtk.FileChooserDialog("Open..", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		
		response = dialog.run ()
		
		if response == gtk.RESPONSE_OK:
			filename = dialog.get_filename()
			
			fp = file(filename, "r")
			f.readFrom(fp)
			fp.close ()
		
		dialog.destroy()

disp.application.Application = ApplicationGtk
