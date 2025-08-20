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

    def record(self, i: int) -> dict:
        """
        Get the attributes of the ith feature in the QGIS feature source.

        Parameters
        ----------
        i : int
            The index of the feature to return the attributes of.

        Returns
        -------
        dict
            key:value pair of the attributes.
        """
        # Use QgsFeatureRequest to get the feature with a specific ID
        features = list(self._source.getFeatures(QgsFeatureRequest().setFilterFid(i)))
        if not features:
            return {}
        feature = features[0]
        
        record = {}
        for field in self._source.fields():
            record[field.name()] = feature[field.name()]
        return record

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

    def geometry(self, i: int) -> list:
        """
        Get the geometry of the ith feature in the QGIS feature source.

        Parameters
        ----------
        i : int
            The index of the feature to return the geometry for.

        Returns
        -------
        list
            List of x,y co-ordinates tuples
        """
        # Use QgsFeatureRequest to get the feature with a specific ID
        features = list(self._source.getFeatures(QgsFeatureRequest().setFilterFid(i)))
        if not features:
            return []
        feature = features[0]
        
        geom = feature.geometry()
        
        # Convert QGIS geometry to list of (x,y) tuples
        if geom.type() == QgsWkbTypes.PointGeometry:
            point = geom.asPoint()
            return [(point.x(), point.y())]
        elif geom.type() == QgsWkbTypes.LineGeometry:
            # Check if it's a multi-line geometry
            if geom.isMultipart():
                # For multi-line geometries, get the first part
                lines = geom.asMultiPolyline()
                if lines:
                    line = lines[0]  # Get the first line part
                    return [(point.x(), point.y()) for point in line]
                else:
                    return []
            else:
                # For single line geometries
                line = geom.asPolyline()
                return [(point.x(), point.y()) for point in line]
        elif geom.type() == QgsWkbTypes.PolygonGeometry:
            polygon = geom.asPolygon()
            # Return exterior ring coordinates
            return [(point.x(), point.y()) for point in polygon[0]]
        else:
            return []

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

    def __len__(self):
        """
        Get the number of features in the QGIS feature source.

        Returns
        -------
        int
            The number of features in the source.
        """
        return self._source.featureCount()
