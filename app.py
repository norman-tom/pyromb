from cProfile import label

import numpy as np
from qgis2rorb.core.attributes.reach import Reach
from qgis2rorb.core.attributes.basin import Basin
from qgis2rorb.core.attributes.confluence import Confluence
from qgis2rorb.core.graph.catchment import Catchment
from qgis2rorb.core.gis.builder import Builder
import matplotlib.pyplot as plt
from qgis2rorb.core.model.controlvector import Traveller

from qgis2rorb.math import geometry

def main():
    path = 'C:\\Users\\toman\\Documents\\Code\\Hydrology\\RORB\\QGIS2RORB\\data'
    builder = Builder(path + '\\test_reach.shp', path + '\\test_basin.shp', path + '\\test_centroid.shp', path + '\\test_confluence.shp')
    tr = builder.reach()
    tc = builder.confluence()
    tb = builder.basin()
    
    catchment = Catchment(tc, tb, tr)
    connected = catchment.connect()


        #Plot the data to make sure it is correct.
    cx = []
    cy = []
    for c in tc:
        cx.append(c.coordinates()[0])
        cy.append(c.coordinates()[1])
    
    bx = []
    by = []
    for b in tb:
        bx.append(b.coordinates()[0])
        by.append(b.coordinates()[1])


    for r in tr:
        x = []
        y = []
        for p in r:
            x.append(p.coordinates()[0])
            y.append(p.coordinates()[1])
        plt.plot(x, y, label=r.getName())

    plt.scatter(cx, cy)
    plt.scatter(bx, by)
    plt.legend(loc="upper left")

    reachNames = [r.getName() for r in tr]
    nodeNames = []
    for i, n in enumerate(tc):
        nodeNames.append("{}[{}]".format(n.getName(), i))
            
    for i, b in enumerate(tb):
        nodeNames.append("{}[{}]".format(b.getName(), i+12))

    fig, ax = plt.subplots()
    im = ax.imshow(connected[0])
    ax.set_xticks(np.arange(0, len(reachNames)))
    ax.set_xticklabels(labels=reachNames)
    ax.set_yticks(np.arange(0, len(nodeNames)))
    ax.set_yticklabels(nodeNames)

    for i in range(len(nodeNames)):
        for j in range(len(reachNames)):
            text = ax.text(j, i, connected[0][i, j], ha='center', va='center', color='w')

    ax.set_title('Catchment Incidence Matrix (DS)')
    fig.tight_layout()

    fig, ax = plt.subplots()
    im = ax.imshow(connected[1])
    ax.set_xticks(np.arange(0, len(reachNames)))
    ax.set_xticklabels(labels=reachNames)
    ax.set_yticks(np.arange(0, len(nodeNames)))
    ax.set_yticklabels(nodeNames)

    for i in range(len(nodeNames)):
        for j in range(len(reachNames)):
            text = ax.text(j, i, connected[1][i, j], ha='center', va='center', color='w')

    ax.set_title('Catchment Incidence Matrix (US)')
    fig.tight_layout()

    #plt.show()

    traveller = Traveller(catchment)

    print(traveller.getVector())


if (__name__ == "__main__"):
    main()