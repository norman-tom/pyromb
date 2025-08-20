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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingOutputNumber,
                       QgsProcessingParameterDefinition,
                       QgsVectorLayer)
from qgis.PyQt.QtGui import QIcon
import processing
import os

from .custom_types.qvector_layer import QVectorLayer
import pyromb


class BuildUrbsAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm builds a URBS control vector file from input GIS layers.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when calling
    # from the QGIS console.

    IN_REACH = 'IN_REACH'
    IN_BASIN = 'IN_BASIN'
    IN_CENTROID = 'IN_CENTROID'
    IN_CONFLUENCE = 'IN_CONFLUENCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.IN_REACH,
                self.tr('Reach layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.IN_BASIN,
                self.tr('Basin layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.IN_CENTROID,
                self.tr('Centroid layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.IN_CONFLUENCE,
                self.tr('Confluence layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('URBS control vector file'),
                self.tr('Control vector (*.catg)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        reaches = self.parameterAsSource(parameters, self.IN_REACH, context)
        basins = self.parameterAsSource(parameters, self.IN_BASIN, context)
        centroids = self.parameterAsSource(parameters, self.IN_CENTROID, context)
        confluences = self.parameterAsSource(parameters, self.IN_CONFLUENCE, context)
        sink = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        reach_vector = QVectorLayer(reaches)
        basin_vector = QVectorLayer(basins)
        centroid_vector = QVectorLayer(centroids)
        confluence_vector = QVectorLayer(confluences)

        builder = pyromb.Builder()
        tr = builder.reach(reach_vector)
        tc = builder.confluence(confluence_vector)
        tb = builder.basin(centroid_vector, basin_vector)

        catchment = pyromb.Catchment(tc, tb, tr)
        catchment.connect()
        traveller = pyromb.Traveller(catchment)

        with open(sink, 'w') as f:
            f.write(traveller.getVector(pyromb.URBS()))

        return {self.OUTPUT: sink}

    def name(self):
        return 'buildurbs'

    def displayName(self):
        return self.tr('Build URBS Control Vector')

    def group(self):
        return self.tr('ROM Builder')

    def groupId(self):
        return 'rombuilder'

    def shortHelpString(self):
        return self.tr("Build a URBS control vector file from GIS layers representing catchment reaches, basins, centroids, and confluences.\n\n"
                       "Input layers:\n"
                       "- Reach layer: Line features representing stream reaches\n"
                       "- Basin layer: Polygon features representing catchment basins\n"
                       "- Centroid layer: Point features representing basin centroids\n"
                       "- Confluence layer: Point features representing stream confluences\n\n"
                       "The algorithm will generate a .catg file compatible with URBS hydrological modeling software.")

    def icon(self):
        return QIcon()

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return BuildUrbsAlgorithm()
