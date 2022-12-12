# -*- coding: utf-8 -*-
"""
/***************************************************************************
 downloadGeoStatPortugal
                                 A QGIS plugin
 This plugin enables the open data download of geographical and statistical Information from Statistics Portugal
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-09-17
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Francisco Caldeira / Instituto Nacional de Estatística
        email                : francisco.caldeira@ine.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import * #QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.core import *
from qgis.gui import QgsMessageBar

from urllib.request import urlopen

from osgeo import ogr

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .downloadGeoStatPortugal_dialog import downloadGeoStatPortugalDialog
import os.path
import zipfile
import requests
import io


class downloadGeoStatPortugal:
    """QGIS Plugin Implementation."""

    global SelectedGeography
    SelectedGeography = "xxx"
    global SelectedYear
    SelectedYear = "2021"
    global getChildNodeLevel
    getChildNodeLevel = "xxx"

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'downloadGeoStatPortugal_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Download Statistics Portugal Open Data')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None





    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('downloadGeoStatPortugal', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/downloadGeoStatPortugal/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Download Statistics Portugal Open Data'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def downloadData(self,GeographicalUnit, year, NodeLevel):
        #setting the path to download
        #The name of the files and path depends on geographical unit
        #That can be
        #1. Country
            #Web server path/portugal2011.zip

        #2. NUTS-I
            #Web server path/continente2011.zip
        #3. NUTS-II
            #Web server path/norte2011.zip
        #4. NUTS-III
            #Web server path/bgri11_111.zip
        #5. Municipalities
            #Web server path/BGRI2011_1601.zip

        self.iface.messageBar().pushMessage("Info","Downloading data!")

        #Identify prefix BGRI ou BGRE
        if year == "1991":
            pre = "BGRE"
        else:
            pre = "BGRI"


        # var with path
        url = "Web server path" + year + "/"




        #Construct the download path
        if NodeLevel == "Nacional":
            url = url + "portugal" + year + ".zip"

        if NodeLevel == "NUTS-I":
            url = url + pre + year[2:] + "_" + GeographicalUnit  + ".zip"


        if NodeLevel == "NUTS-II":
            url = url + "nuts2/" + pre + year[2:] + "_" + GeographicalUnit  + ".zip"

        if NodeLevel == "NUTS-III":
            url = url  + "nuts3/" + pre + year[2:] + "_" + GeographicalUnit  + ".zip"

        if NodeLevel == "Municipios":
            url = url  + "municipios/" + pre + year + "_" + GeographicalUnit  + ".zip"

        #Dealing with the excepctions that are Portugal and R.A. dos Açores
        #They are exceptions because there are more than one layer inside the geopackage

        # In the case of Portugal there are 4 layers needed to be added: Portugal Continental, R.A. Madeira,
        #R.A. Açores grupo Ocidental e R.A. Açores Grupo central e Oriental



        #In the case of R.A. Açores there are 2 layers needed to be added
        #R.A. Açores grupo Ocidental e R.A. Açores Grupo central e Oriental

        # Change the cursor
        #self.dlg.lbl1.setText( "Downloading data, please wait!")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.dlg.lbl1.setText( url)



        #the filename
        filename = os.path.basename(url)

        # Download the file from the URL defined in binary format
        zipresp = requests.get(url, stream = True)

        self.dlg.lbl1.setText( url)




        #DownloadPath
        pasta = self.plugin_dir + '/dados_INE/'
        // thanks gvlx  
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            
        # open method to open a file on your system and write the contents
        with open( pasta + filename, "wb") as code:
            code.write(zipresp.content)

        code.close()

        #pushMessage
        #self.iface.messageBar().pushMessage("Info","Unziping data!")

        #Unzip the zip and delete the zip file
        with zipfile.ZipFile(pasta + filename, 'r') as zip_ref:
            zip_ref.extractall(pasta)
            zip_ref.close()
            os.remove(pasta + filename)

        #Restore the default cursor
        QApplication.restoreOverrideCursor()


        #Change the filename
        GeoPackName = filename.replace("zip", "gpkg", 1)
        BGRILayerName = filename.replace(".zip", "", 1)

        #get the path to a geopackage
        path_to_gpkg = os.path.join(pasta, GeoPackName)

        conn = ogr.Open(path_to_gpkg)

        # append the layername part
        gpkg_BGRI_layer1 = path_to_gpkg + "|layername=" + BGRILayerName

        #self.dlg.lbl1.setText(gpkg_BGRI_layer1 )
        #self.dlg.lbl1.setText("The layer " + BGRILayerName + " was added to the map" )

        if (NodeLevel == "Nacional") | (GeographicalUnit == "raa"):

            if year == "1991":
                express = "BGRE91"
            else:
                express = "BGRI" + year[2:4]

            gpkg_BGRI_layer1 = path_to_gpkg + "|layername=" + express + "_AC25"
            gpkg_BGRI_layer2 = path_to_gpkg + "|layername=" + express + "_AC26"
            gpkg_BGRI_layer3 = path_to_gpkg + "|layername=" + express + "_CONT"
            gpkg_BGRI_layer4 = path_to_gpkg + "|layername=" + express + "_MAD"
            vlayer1 = QgsVectorLayer(gpkg_BGRI_layer1, express + "_AC25", "ogr")
            vlayer2 = QgsVectorLayer(gpkg_BGRI_layer2, express + "_AC26", "ogr")
            vlayer3 = QgsVectorLayer(gpkg_BGRI_layer3, express + "_CONT", "ogr")
            vlayer4 = QgsVectorLayer(gpkg_BGRI_layer4, express + "_MAD", "ogr")
            vlayer1.setName(express + "_AC25")
            vlayer2.setName(express + "_AC26")
            vlayer3.setName(express + "_CONT")
            vlayer4.setName(express + "_MAD")


            vlayer1.loadNamedStyle(self.plugin_dir+'/BGRI' + year + '.qml')
            vlayer2.loadNamedStyle(self.plugin_dir+'/BGRI' + year + '.qml')
            vlayer3.loadNamedStyle(self.plugin_dir+'/BGRI' + year + '.qml')
            vlayer4.loadNamedStyle(self.plugin_dir+'/BGRI' + year + '.qml')

            QgsProject.instance().addMapLayer(vlayer1)
            QgsProject.instance().addMapLayer(vlayer2)

            if NodeLevel == "Nacional":
                QgsProject.instance().addMapLayer(vlayer3)
                QgsProject.instance().addMapLayer(vlayer4)



        else:
            vlayer1 = QgsVectorLayer(gpkg_BGRI_layer1, BGRILayerName, "ogr")

            # Set the layer name
            vlayer1.setName(BGRILayerName)

            #Symbology used (drak green outline and label the BGRI code only visible
            #when scale < 3 000 dark green text either
            vlayer1.loadNamedStyle(self.plugin_dir+'/BGRI' + year + '.qml')

            #Add the layer to the map bro
            QgsProject.instance().addMapLayer(vlayer1)


        #Warns the user that
        #self.dlg.lbl1.setText("The layer " + url + " was added to the map" )

        self.dlg.lbl1.setText("The layer " + BGRILayerName + " was added to the map" )





    def SelectedYearChanged(self):
        global SelectedYear
        if self.dlg.rb1991.isChecked()==True:
            SelectedYear = "1991"


        if self.dlg.rb2001.isChecked()==True:
            SelectedYear = "2001"


        if self.dlg.rb2011.isChecked()==True:
            SelectedYear = "2011"


        if self.dlg.rb2021.isChecked()==True:
            SelectedYear = "2021"

        #Enable the download button
        getSelected = self.dlg.GU_treeWidget.selectedItems()
        if getSelected:
            self.dlg.pB_Download.setEnabled(True)


    def TreeViewSelectionChanged(self):
         getSelected = self.dlg.GU_treeWidget.selectedItems()
         global SelectedGeography
         global getChildNodeLevel
         if getSelected:
             baseNode = getSelected[0]
             getChildNode = baseNode.text(1)
             getChildNodeLevel = baseNode.text(2)
             SelectedGeography = getChildNode
             #self.dlg.lbl1.setText(SelectedGeography)

            #Enable the download button
             self.dlg.pB_Download.setEnabled(True)


    def TreeViewitemDoubleClicked(self):
         getSelected = self.dlg.GU_treeWidget.selectedItems()
         global SelectedGeography
         global getChildNodeLevel
         if getSelected:
             baseNode = getSelected[0]
             getChildNode = baseNode.text(1)
             getChildNodeLevel = baseNode.text(2)
             SelectedGeography = getChildNode

            #Enable the download button
             self.dlg.pB_Download.setEnabled(True)

    def button_DownloadData(self):
        self.dlg.pB_Download.setEnabled(False)
        self.dlg.lbl1.setText(SelectedGeography + SelectedYear + getChildNodeLevel )
        self.downloadData (SelectedGeography, SelectedYear, getChildNodeLevel)
        #self.dlg.pB_Download.setEnabled(True)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Download Statistics Portugal Open Data'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = downloadGeoStatPortugalDialog()


        # This column is used to retrieve tuhe filename to download
        self.dlg.GU_treeWidget.hideColumn(1)
        self.dlg.GU_treeWidget.hideColumn(2)

        self.dlg.GU_treeWidget.itemSelectionChanged.connect(lambda:self.TreeViewSelectionChanged())

        self.dlg.GU_treeWidget.itemDoubleClicked.connect(lambda:self.TreeViewitemDoubleClicked())

        self.dlg.rb1991.toggled.connect(lambda:self.SelectedYearChanged())
        self.dlg.rb2001.toggled.connect(lambda:self.SelectedYearChanged())
        self.dlg.rb2011.toggled.connect(lambda:self.SelectedYearChanged())
        self.dlg.rb2021.toggled.connect(lambda:self.SelectedYearChanged())
        self.dlg.pB_Download.clicked.connect(lambda:self.button_DownloadData())

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass




        #



