# -*- coding: utf-8 -*-

#******************************************************************************
#
# Metatools
# ---------------------------------------------------------
# Metadata browser/editor
#
# Copyright (C) 2011 NextGIS (info@nextgis.ru)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os

from ui_settings import Ui_MetatoolsSettingsDialog

currentPath = os.path.abspath( os.path.dirname( __file__ ) )

class MetatoolsSettings( QDialog, Ui_MetatoolsSettingsDialog ):
  def __init__( self ):
    QDialog.__init__( self )
    self.setupUi( self )

    self.manageGui()

    self.readSettings()

    QObject.connect( self.btnSelectFilter, SIGNAL( "clicked()" ), self.updateFilter )

  def manageGui( self ):
    # populate profiles combobox
    profilesDir = QDir( QDir.toNativeSeparators( os.path.join( currentPath, "xml_profiles" ) ) )
    profilesDir.setFilter( QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot )
    fileFilter = QStringList() << "*.xml" << "*.XML"
    profilesDir.setNameFilters( fileFilter )
    profiles = profilesDir.entryList()
    self.defaultProfileComboBox.addItems( profiles )

  def readSettings( self ):
    settings = QSettings( "NextGIS", "metatools" )
    self.leFilterFileName.setText( settings.value( "general/filterFile", QVariant() ).toString() )

    # restore default profile
    profile = settings.value( "iso19115/defaultProfile", QVariant() ).toString()
    self.defaultProfileComboBox.setCurrentIndex( self.defaultProfileComboBox.findText( profile ) )

  def updateFilter( self ):
    fileName = QFileDialog.getOpenFileName( self, self.tr( 'Select filter' ), '.', self.tr( 'Text files (*.txt *.TXT)' ) )

    if fileName.isEmpty():
      return

    self.leFilterFileName.setText( fileName )

  def accept( self ):
    # save settings
    settings = QSettings( "NextGIS", "metatools" )
    settings.setValue( "general/filterFile", self.leFilterFileName.text() )

    settings.setValue( "iso19115/defaultProfile",  self.defaultProfileComboBox.currentText()  )

    # close dialog
    QDialog.accept( self )
