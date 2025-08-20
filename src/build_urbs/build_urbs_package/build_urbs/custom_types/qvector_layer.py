# -*- coding: utf-8 -*-

"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Tom Norman'
__date__ = '2025-08-20'
__copyright__ = '(C) 2025 by Tom Norman'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsFeatureRequest, QgsWkbTypes
from PyQt5.QtCore import QVariant


class QVectorLayer:
    """
    A wrapper for a QGIS feature source that implements the VectorLayer interface
    required by pyromb.
    """

    def __init__(self, source) -> None:
        self._source = source

    def getRecords(self):
        """
        Get all records from the QGIS feature source.

        Returns
        -------
        list
            A list of dictionaries representing the attributes of each feature.
        """
        records = []
        for feature in self._source.getFeatures():
            record = {}
            for field in self._source.fields():
                record[field.name()] = feature[field.name()]
            records.append(record)
        return records

    def getGeometry(self):
        """
        Get all geometries from the QGIS feature source.

        Returns
        -------
        list
            A list of geometries for each feature in the source.
        """
        geometries = []
        for feature in self._source.getFeatures():
            geometries.append(feature.geometry())
        return geometries

    @property
    def fieldNames(self):
        """
        Get the field names from the QGIS feature source.

        Returns
        -------
        list
            A list of field names in the source.
        """
        return [field.name() for field in self._source.fields()]
