# -*- coding: utf-8 -*-

# ******************************************************************************
#
# Metatools
# ---------------------------------------------------------
# Metadata browser/editor
#
# Copyright (C) 2011-2016 NextGIS (info@nextgis.com)
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
# ******************************************************************************

import os

from lxml import etree
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QDialog, QMenu
from qgis.PyQt.QtXml import *

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/viewer.ui")
)

from .error_handler import ErrorHandler


class MetatoolsViewer(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MetatoolsViewer, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint)

        # set browser context menu
        self.webView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.webView.customContextMenuRequested.connect(self.openMenu)
        self.contextMenu = QMenu()
        self.actionCopy.triggered.connect(self.slotCopy)
        self.actionPrint.triggered.connect(self.slotPrint)
        self.actionCopyAll.triggered.connect(self.slotCopyAll)

    def openMenu(self, position):
        self.contextMenu.clear()
        if self.webView.selectedText():
            self.contextMenu.addAction(self.actionCopy)
        self.contextMenu.addAction(self.actionCopyAll)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.actionPrint)

        self.contextMenu.exec(self.webView.mapToGlobal(position))

    def slotPrint(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        if dialog.exec() == QDialog.Accepted:
            self.webView.print_(printer)

    def slotCopyAll(self):
        mimeData = QMimeData()
        mimeData.setHtml(self.webView.page().mainFrame().toHtml())
        mimeData.setText(self.webView.page().mainFrame().toPlainText())
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mimeData)

    def slotCopy(self):
        if self.webView.selectedText():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.webView.selectedText())

    def setContent(self, metaProvider, xsltFilePath):
        # load data
        with open(xsltFilePath) as xslt_file:
            xslt_content = xslt_file.read()

        # Parse XSLT
        xslt_tree = etree.XML(xslt_content.encode("utf-8"))
        transform = etree.XSLT(xslt_tree)

        # Load source XML from metaProvider
        src_xml = metaProvider.getMetadata()
        src_tree = etree.XML(src_xml.encode("utf-8"))

        # Apply transformation
        result_tree = transform(src_tree)

        # Convert result to string
        result = str(result_tree)

        if result:
            # QXmlPattern not support CDATA section
            result = result.replace("&amp;", "&")
            result = result.replace("&gt;", ">")
            result = result.replace("&lt;", "<")

            self.webView.setHtml(result)  # QString.fromUtf8(result))
            return True
        else:
            return False

    def setHtml(self, html):
        self.webView.setHtml(html)
