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

import os
import sys
import inspect

from qgis.core import QgsProcessingProvider
from .build_urbs_algorithm import BuildUrbsAlgorithm


cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
cmd_subfolder = os.path.join(cmd_folder, "custom_types")

if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)


class BuildUrbsProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def loadAlgorithms(self):
        self.addAlgorithm(BuildUrbsAlgorithm())

    def id(self):
        return "buildurbs"

    def name(self):
        return "ROM Builder: URBS"

    def icon(self):
        return QgsProcessingProvider.icon(self)

    def longName(self):
        return self.name()
