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
from pobject import *

class ApplicationBase (PRoot):
	"""
	Vstupní bod aplikace. Tato třída by měla být přetížena ve 
	front-endech a doplnit konkrétní funkce. 
	"""
	def __init__(self):
		
		PRoot.__init__ (self)
		
		# Aktuálně zobrazený formulář
		self.displayed_form = None
		
		# Zásobník zobrazených formulářů
		self.forms_stack = []
		
		self.event_pre_serialize = Event (self)
		self.event_deserialized = Event (self)
		
		# Cesta k souborům odkazujících relativně. Front-end by ji měl nastavit na místo, 
		# kde se pravděpodobně nachází data aplikace.
		self.pre_path = "./"
		
		self._dirty = True
		
	def getDeserializedEvent (self):
		"""
		Událost zavolaná ihned po úspěšné deserializaci všech objektů
		"""
		return self.event_deserialized
	
	def getSerializingEvent (self):
		"""
		Událost těsně před serializací objektů
		"""
		return self.event_pre_serialize
		
	def setTitle (self, title):
		"""
		Nastaví název aplikace. Obvykle se zobrazí v hlavičce okna aplikace, 
		pokud to má pro daný front-end smysl.
		
		@type title: string
		"""
		self._title = title
	
	def getTitle (self):
		"""
		Vrátí název aplikace nastavený přes setTitle
		
		@rtype: string
		"""
		return self._title
	
	title = property(fget=lambda self: self.getTitle(), fset=lambda self, v: self.setTitle(v))
	
	def getPrePath (self):
		return self.pre_path
	
	def setPrePath (self, pre_path):
		self.pre_path = pre_path
		
	def absolutePath (self, filename):
		"""
		Zkonvertuje relativní cestu na absolutní. Typické použití je při vyhledání datových souborů
		aplikace, kdy absolutní cesta datových souborů je závislá na front-endu.
		"""
		return self.pre_path + filename
		
	def getDisplayedForm (self):
		"""
		Vrátí aktuálně zobrazovaný formulář
		"""
		return self.displayed_form

	def display (self, form):
		"""
		Zobrazí formulář, aniž by ho dala do fronty. (Tohle by asi mělo být protected)
		"""
		self.displayed_form = form
		
	def pushForm (self, form):
		self.forms_stack.append (form)
		self.display (form)
		
	def popForm (self, form):
		oldform = self.forms_stack.pop ()
		
		assert oldform == form
		
		if len (self.forms_stack) > 0:
			self.display (self.forms_stack[-1])
		else:
			self.display (None)
			
	def writeFile (self, file):
		"""
		Vyžádá si uložení daného souboru. Typicky se tím způsobí uživatelská akce, kde si
		uživatel vybere soubor, kam chce soubor uložit a následně se zavolá metoda file.writeTo
		
		@type file: file.FileInput
		"""
		pass
	
	def readFile (self, file):
		"""
		Načte soubor.  Typicky se tím způsobí uživatelská akce, kde si
		uživatel vybere soubor, ze kterého se má číst a následně se zavolá metoda file.readFrom
		
		@type file: file.FileOutput
		"""
		pass
