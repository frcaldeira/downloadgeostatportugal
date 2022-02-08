# -*- coding: utf-8 -*-
"""
/***************************************************************************
 downloadGeoStatPortugal
                                 A QGIS plugin
 This plugin enables the open data download of geographical and statistical Information from Statistics Portugal
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-17
        copyright            : (C) 2021 by Francisco Caldeira / Instituto Nacional de Estatística
        email                : francisco.caldeira@ine.pt
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load downloadGeoStatPortugal class from file downloadGeoStatPortugal.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .downloadGeoStatPortugal import downloadGeoStatPortugal
    return downloadGeoStatPortugal(iface)