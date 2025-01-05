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
import sys
import tempfile

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

from . import resources_rc  # noqa: F401
from .error_handler import ErrorHandler
from .metadata_provider import MetadataProvider
from .metatoolssettings import MetatoolsSettings
from .standard import MetaInfoStandard

minQtVersion = "4.6.0"
currentPath = os.path.abspath(os.path.dirname(__file__))


class MetatoolsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.loadingCanceled = False

        try:
            self.QgisVersion = str(Qgis.QGIS_VERSION_INT)
        except:
            self.QgisVersion = str(Qgis.qgisVersion)[0]

        # get plugin folder (more simple version of original plugin)
        self.pluginPath = currentPath

        # i18n support
        overrideLocale = QSettings().value("locale/overrideFlag", False)
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", "")

        self.localePath = (
            self.pluginPath + "/i18n/metatools_" + localeFullName[0:2] + ".qm"
        )

        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        if int(self.QgisVersion) < 10900:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Metatools",
                QCoreApplication.translate(
                    "Metatools", "Quantum GIS version detected: %d.%d\n"
                )
                % (self.QgisVersion[0], self.QgisVersion[2])
                + QCoreApplication.translate(
                    "Metatools",
                    "This version of Metatools requires at least QGIS version 2.0\nPlugin will not be enabled.",
                ),
            )
            self.loadingCanceled = True
            return None

        if qVersion() < minQtVersion:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Metatools",
                QCoreApplication.translate(
                    "Metatools", "Qt version detected: %s\n"
                )
                % (qVersion())
                + QCoreApplication.translate(
                    "Metatools",
                    "This version of Metatools requires at least Qt version %s\nPlugin will not be enabled.",
                )
                % (minQtVersion),
            )
            self.loadingCanceled = True
            return None

        # create editAction that will start metadata editor
        self.editAction = QAction(
            QIcon(":/plugins/metatools/icons/edit.png"),
            QCoreApplication.translate("Metatools", "Edit metadata"),
            self.iface.mainWindow(),
        )
        self.editAction.setStatusTip(
            QCoreApplication.translate("Metatools", "Edit metadata")
        )
        self.editAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Edit metadata")
        )

        # create applyTemplateAction that will start templates manager
        self.applyTemplatesAction = QAction(
            QIcon(":/plugins/metatools/icons/templates.png"),
            QCoreApplication.translate("Metatools", "Apply templates"),
            self.iface.mainWindow(),
        )
        self.applyTemplatesAction.setStatusTip(
            QCoreApplication.translate("Metatools", "Edit and apply templates")
        )
        self.applyTemplatesAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Edit and apply templates")
        )

        # create viewAction that will start metadata viewer
        self.viewAction = QAction(
            QIcon(":/plugins/metatools/icons/view.png"),
            QCoreApplication.translate("Metatools", "View metadata"),
            self.iface.mainWindow(),
        )
        self.viewAction.setStatusTip(
            QCoreApplication.translate("Metatools", "View metadata")
        )
        self.viewAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "View metadata")
        )

        # create configAction that will start plugin configuration
        self.configAction = QAction(
            QIcon(":/plugins/metatools/icons/settings.png"),
            QCoreApplication.translate(
                "Metatools", "Configure Metatools plugin"
            ),
            self.iface.mainWindow(),
        )
        self.configAction.setStatusTip(
            QCoreApplication.translate("Metatools", "Configure plugin")
        )
        self.configAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Configure plugin")
        )

        # create configAction that will start plugin configuration
        self.validateAction = QAction(
            QIcon(":/plugins/metatools/icons/check.png"),
            QCoreApplication.translate("Metatools", "Validate metadata"),
            self.iface.mainWindow(),
        )
        self.validateAction.setStatusTip(
            QCoreApplication.translate("Metatools", "Validate metadata")
        )
        self.validateAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Validate metadata")
        )

        self.importAction = QAction(
            QIcon(":/plugins/metatools/icons/import.png"),
            QCoreApplication.translate("Metatools", "Import metadata"),
            self.iface.mainWindow(),
        )
        self.importAction.setStatusTip(
            QCoreApplication.translate(
                "Metatools", "Import metadata from file"
            )
        )
        self.importAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Import metadata")
        )

        self.exportAction = QAction(
            QIcon(":/plugins/metatools/icons/export.png"),
            QCoreApplication.translate("Metatools", "Export metadata"),
            self.iface.mainWindow(),
        )
        self.exportAction.setStatusTip(
            QCoreApplication.translate("Metatools", "Export metadata")
        )
        self.exportAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Export metadata to file")
        )

        self.metaBrowserAction = QAction(
            QIcon(":/plugins/metatools/icons/view.png"),
            QCoreApplication.translate("Metatools", "Metadata browser"),
            self.iface.mainWindow(),
        )
        self.metaBrowserAction.setStatusTip(
            QCoreApplication.translate("Metatools", "Metadata browser")
        )
        self.metaBrowserAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "Metadata browser")
        )

        # ------------ FGDC actions
        # Tkme action
        self.usgsAction = QAction(
            QIcon(":/plugins/metatools/icons/usgs.png"),
            QCoreApplication.translate("Metatools", "USGS Tool"),
            self.iface.mainWindow(),
        )
        self.usgsAction.setStatusTip(
            QCoreApplication.translate("Metatools", "USGS Tool")
        )
        self.usgsAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "USGS Tool")
        )

        # mp action
        self.mpAction = QAction(
            QIcon(":/plugins/metatools/icons/usgs_check.png"),
            QCoreApplication.translate("Metatools", "MP Tool"),
            self.iface.mainWindow(),
        )
        self.mpAction.setStatusTip(
            QCoreApplication.translate("Metatools", "MP Tool")
        )
        self.mpAction.setWhatsThis(
            QCoreApplication.translate("Metatools", "MP Tool")
        )

        settings = QgsSettings()
        hasTools = settings.value(
            "QgsCollapsibleGroupBox/gbFGDCTools/checked", False
        )
        if not hasTools:
            self.usgsAction.setEnabled(False)
            self.mpAction.setEnabled(False)

        self.editAction.triggered.connect(self.doEdit)
        self.applyTemplatesAction.triggered.connect(self.doApplyTemplates)
        self.viewAction.triggered.connect(self.doView)
        self.configAction.triggered.connect(self.doConfigure)
        self.validateAction.triggered.connect(self.validateMetadataFile)
        self.usgsAction.triggered.connect(self.execUsgs)
        self.mpAction.triggered.connect(self.execMp)
        self.importAction.triggered.connect(self.doImport)
        self.exportAction.triggered.connect(self.doExport)

        # add menu items
        self.iface.addPluginToMenu("Metatools", self.usgsAction)
        self.iface.addPluginToMenu("Metatools", self.mpAction)
        self.iface.addPluginToMenu("Metatools", self.importAction)
        self.iface.addPluginToMenu("Metatools", self.exportAction)
        self.iface.addPluginToMenu("Metatools", self.viewAction)
        self.iface.addPluginToMenu("Metatools", self.editAction)
        self.iface.addPluginToMenu("Metatools", self.validateAction)
        self.iface.addPluginToMenu("Metatools", self.applyTemplatesAction)
        self.iface.addPluginToMenu("Metatools", self.configAction)

        # add toolbar and buttons
        self.toolBar = self.iface.addToolBar(
            QCoreApplication.translate("Metatools", "Metatools")
        )
        self.toolBar.setObjectName(
            QCoreApplication.translate("Metatools", "Metatools")
        )

        self.toolBar.addAction(self.importAction)
        self.toolBar.addAction(self.exportAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.viewAction)
        self.toolBar.addAction(self.editAction)
        self.toolBar.addAction(self.validateAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.applyTemplatesAction)
        self.toolBar.addAction(self.configAction)

        # add fgdc toolbar
        self.fgdcToolBar = self.iface.addToolBar(
            QCoreApplication.translate("Metatools", "Metatools: FGDC tools")
        )
        self.fgdcToolBar.setObjectName(
            QCoreApplication.translate("Metatools", "Metatools: FGDC tools")
        )

        self.fgdcToolBar.addAction(self.usgsAction)
        self.fgdcToolBar.addAction(self.mpAction)

        # track layer changing
        self.iface.currentLayerChanged.connect(self.layerChanged)

        # disable some actions when there is no active layer
        self.layer = None
        self.disableLayerActions()

        # check already selected layers
        self.layerChanged()

    def unload(self):
        if self.loadingCanceled:
            return

        # disconnect signals
        self.iface.currentLayerChanged.disconnect(self.layerChanged)

        # remove the plugin menu items and toolbar
        self.iface.removePluginMenu("Metatools", self.editAction)
        self.iface.removePluginMenu("Metatools", self.applyTemplatesAction)
        self.iface.removePluginMenu("Metatools", self.viewAction)
        self.iface.removePluginMenu("Metatools", self.configAction)
        self.iface.removePluginMenu("Metatools", self.validateAction)
        self.iface.removePluginMenu("Metatools", self.usgsAction)
        self.iface.removePluginMenu("Metatools", self.mpAction)
        self.iface.removePluginMenu("Metatools", self.importAction)
        self.iface.removePluginMenu("Metatools", self.exportAction)

        del self.toolBar
        del self.fgdcToolBar

    def layerChanged(self):
        self.layer = self.iface.activeLayer()

        # check layer type - return (True/False, Desc)
        res = MetadataProvider.IsLayerSupport(self.layer)

        if not res[0]:
            self.disableLayerActions()
            self.layer = None
            self.metaProvider = None
        else:
            self.enableLayerActions()
            self.metaProvider = MetadataProvider.getProvider(self.layer)

    def disableLayerActions(self):
        self.viewAction.setEnabled(False)
        self.editAction.setEnabled(False)
        self.usgsAction.setEnabled(False)
        self.mpAction.setEnabled(False)
        self.validateAction.setEnabled(False)
        self.importAction.setEnabled(False)
        self.exportAction.setEnabled(False)

    def enableLayerActions(self):
        settings = QgsSettings()
        hasTools = settings.value("tools/hasFGDC", False)

        self.viewAction.setEnabled(True)
        self.editAction.setEnabled(True)
        self.usgsAction.setEnabled(
            hasTools and settings.value("tools/tkme", "") != ""
        )
        self.mpAction.setEnabled(
            hasTools and settings.value("tools/mp", "") != ""
        )
        self.validateAction.setEnabled(True)
        self.importAction.setEnabled(True)
        self.exportAction.setEnabled(True)

    def doEdit(self):
        try:
            from .metatoolseditor import MetatoolsEditor
        except:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "Editor can't be loaded: %s %s!"
                )
                % (str(sys.exc_info()[0]), str(sys.exc_info()[1])),
            )
            return

        # check if metadata file exists
        if not self.checkMetadata():
            return

        # check matadata standard
        standard = MetaInfoStandard.tryDetermineStandard(self.metaProvider)
        if (
            standard != MetaInfoStandard.ISO19115
            and standard != MetaInfoStandard.FGDC
        ):
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools",
                    "Unsupported metadata standard! Only ISO19115 and FGDC supported now!",
                ),
            )
            return

        dlg = MetatoolsEditor()
        dlg.setContent(self.metaProvider)
        dlg.exec()

    def doConfigure(self):
        dlg = MetatoolsSettings()
        dlg.exec()

        settings = QgsSettings()
        hasTools = settings.value("tools/hasFGDC", False)
        if hasTools:
            self.usgsAction.setEnabled(settings.value("tools/tkme", "") != "")
            self.mpAction.setEnabled(settings.value("tools/mp", "") != "")

    def doApplyTemplates(self):
        try:
            from .apply_templates_dialog import ApplyTemplatesDialog
        except ImportError:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "Applyer can't be loaded: %s %s!"
                )
                % (str(sys.exc_info()[0]), str(sys.exc_info()[1])),
            )
            return
        dlg = ApplyTemplatesDialog(self.iface)
        dlg.exec()

    def doView(self):
        try:
            from .metatoolsviewer import MetatoolsViewer
        except:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "Viewer can't be loaded: %s %s!"
                )
                % (str(sys.exc_info()[0]), str(sys.exc_info()[1])),
            )
            return

        # check metadata exists
        if not self.checkMetadata():
            return

        # check matadata standard
        standard = MetaInfoStandard.tryDetermineStandard(self.metaProvider)
        if (
            standard != MetaInfoStandard.ISO19115
            and standard != MetaInfoStandard.FGDC
        ):
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools",
                    "Unsupported metadata standard! Only ISO19115 and FGDC supported now!",
                ),
            )
            return

        # TODO: validate metadata file

        # get xsl file path
        settings = QgsSettings()
        if standard == MetaInfoStandard.ISO19115:
            xsltFilePath = os.path.join(
                self.pluginPath, "xsl/"
            ) + settings.value("iso19115/stylesheet", "iso19115.xsl")
        if standard == MetaInfoStandard.FGDC:
            xsltFilePath = os.path.join(
                self.pluginPath, "xsl/"
            ) + settings.value("fgdc/stylesheet", "fgdc.xsl")

        dlg = MetatoolsViewer()
        if dlg.setContent(self.metaProvider, xsltFilePath):
            dlg.exec()

    def checkMetadata(self):
        if not self.metaProvider.checkExists():
            result = QMessageBox.question(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools",
                    "The layer does not have metadata! Create metadata?",
                ),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if result == QMessageBox.Yes:
                try:
                    settings = QgsSettings()
                    profile = settings.value("general/defaultProfile", "")
                    if profile == "":
                        QMessageBox.warning(
                            self.iface.mainWindow(),
                            QCoreApplication.translate(
                                "Metatools", "Metatools"
                            ),
                            QCoreApplication.translate(
                                "Metatools",
                                "No profile selected. Please set default profile in plugin settings",
                            ),
                        )
                        return False

                    profilePath = str(
                        QDir.toNativeSeparators(
                            os.path.join(
                                currentPath, "xml_profiles", str(profile)
                            )
                        )
                    )
                    self.metaProvider.ImportFromFile(profilePath)
                except:
                    QMessageBox.warning(
                        self.iface.mainWindow(),
                        QCoreApplication.translate("Metatools", "Metatools"),
                        QCoreApplication.translate(
                            "Metatools", "Metadata file can't be created: "
                        )
                        + str(sys.exc_info()[1]),
                    )
                    return False
                return True
            else:
                return False
        else:
            return True

    # ----------------- external tools -----------------

    def execUsgs(self):
        settings = QgsSettings()
        if not settings.value("tools/hasFGDC", False):
            return

        # check if metadata file exists
        if not self.checkMetadata():
            return

        # check matadata standard
        standard = MetaInfoStandard.tryDetermineStandard(self.metaProvider)

        if standard != MetaInfoStandard.FGDC:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "USGS tool support only FGDC standard!"
                ),
            )
            return

        # start tool
        execFilePath = settings.value("tools/tkme", "")

        try:
            import subprocess

            prov = self.metaProvider
            temporaryMetafile = prov.SaveToTempFile()
            subprocess.Popen(
                [str(execFilePath), str(temporaryMetafile)],
                cwd=toolPath,
            ).wait()
            prov.LoadFromTempFile(temporaryMetafile)
        except:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "USGS tool can't be runing: "
                )
                + str(sys.exc_info()[1]),
            )

    def execMp(self):
        settings = QgsSettings()
        if not settings.value("tools/hasFGDC", False):
            return

        # check if metadata exists
        if not self.checkMetadata():
            return

        # check matadata standard
        standard = MetaInfoStandard.tryDetermineStandard(self.metaProvider)

        if standard != MetaInfoStandard.FGDC:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "MP tool support only FGDC standard!"
                ),
            )
            return

        # start tool
        mpFilePath = settings.value("tools/mp", "")
        errFilePath = settings.value("tools/err2html", "")

        with tempfile.NamedTemporaryFile() as temp_file:
            tempPath = temp_file.name
        temporaryMetafile = self.metaProvider.SaveToTempFile()
        result = ""

        try:
            import subprocess

            subprocess.check_call(
                [mpFilePath, "-e", tempPath, temporaryMetafile],
                shell=throwShell,
                cwd=toolPath,
            )

            if sys.hexversion >= 34013184:
                result = subprocess.check_output(
                    [errFilePath, tempPath], shell=throwShell, cwd=toolPath
                )
            else:
                # workaround for python < 2.7
                # ... stderr=subprocess.STDOUT, stdin=subprocess.PIPE ... ! FUCKED Python 2.5 bug on windows!
                err2htmlProc = subprocess.Popen(
                    [errFilePath, tempPath],
                    shell=throwShell,
                    cwd=toolPath,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                )
                err2htmlProc.stdin.close()
                result = err2htmlProc.communicate()[0]

        except:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "MP tool can't be runing: "
                )
                + str(sys.exc_info()[1]),
            )
            return
        finally:
            if os.path.exists(tempPath):
                os.remove(tempPath)
            # explicit kill temporary metafile
            if os.path.exists(temporaryMetafile):
                os.remove(temporaryMetafile)

        # show result
        from .metatoolsviewer import MetatoolsViewer

        dlg = MetatoolsViewer()
        dlg.setHtml(result)
        dlg.setWindowTitle(
            QCoreApplication.translate("Metatools", "MP result")
        )
        dlg.exec()

    # ----------------- validator -----------------

    def validateMetadataFile(self):
        # check if metadata exists
        if not self.checkMetadata():
            return

        # check matadata standard
        standard = MetaInfoStandard.tryDetermineStandard(self.metaProvider)
        if standard != MetaInfoStandard.FGDC:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools",
                    "Unsupported metadata standard! Only FGDC supported now!",
                ),
            )
            return

        # from qgis.PyQt.QtXmlPatterns import QXmlSchema, QXmlSchemaValidator
        # TODO: validate metadata file

        # setup xml schema
        schema = QXmlSchema()

        # setup handler
        self.handler = ErrorHandler(
            QCoreApplication.translate("Metatools", "Metadata is invalid")
        )
        schema.setMessageHandler(self.handler)

        # load schema from file
        xsdFilePath = self.pluginPath + "/xsd/fgdc/fgdc-std-001-1998.xsd"
        # if standard != MetaInfoStandard.FGDC:
        #    xsdFilePath = 'c:/xsd/gml/basicTypes.xsd' #   gmd/gmd.xsd'
        schemaUrl = QUrl(xsdFilePath)
        loadResult = schema.load(schemaUrl)
        if not loadResult or self.handler.errorOccured:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "Schema for validate not loaded!"
                ),
            )
            return

        # setup validator
        validator = QXmlSchemaValidator(schema)
        validator.setMessageHandler(self.handler)

        # validate
        metadata = self.metaProvider.getMetadata().encode("utf-8")
        if validator.validate(metadata):
            QMessageBox.information(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate("Metatools", "Metadata is valid!"),
            )

    # ----------------- import\ export -----------------

    def doImport(self):
        # check if metadata exists
        if not self.checkMetadata():
            return

        fileName, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            QCoreApplication.translate("Metatools", "Select metadata file"),
            "",
            QCoreApplication.translate(
                "Metatools",
                "XML files (*.xml);;Text files (*.txt *.TXT);;All files (*.*)",
            ),
        )

        if fileName == "":
            return

        try:
            self.metaProvider.ImportFromFile(fileName)
        except:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "Metadata can't be imported: "
                )
                + str(sys.exc_info()[1]),
            )
            return

        QMessageBox.information(
            self.iface.mainWindow(),
            QCoreApplication.translate("Metatools", "Metatools"),
            QCoreApplication.translate(
                "Metatools", "Metadata was imported successful!"
            ),
        )

    def doExport(self):
        # check if metadata exists
        if not self.checkMetadata():
            return

        fileName, _ = QFileDialog.getSaveFileName(
            self.iface.mainWindow(),
            QCoreApplication.translate("Metatools", "Save metadata to file"),
            "",
            QCoreApplication.translate(
                "Metatools",
                "XML files (*.xml);;Text files (*.txt *.TXT);;All files (*.*)",
            ),
        )

        if fileName == "":
            return

        try:
            self.metaProvider.ExportToFile(fileName)
        except:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QCoreApplication.translate("Metatools", "Metatools"),
                QCoreApplication.translate(
                    "Metatools", "Metadata can't be exported: "
                )
                + str(sys.exc_info()[1]),
            )
            return

        QMessageBox.information(
            self.iface.mainWindow(),
            QCoreApplication.translate("Metatools", "Metatools"),
            QCoreApplication.translate(
                "Metatools", "Metadata was exported successful!"
            ),
        )
