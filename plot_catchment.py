import matplotlib.pyplot as plt
import numpy as np

def plot_catchment(connected, tr, tc, tb):
    cx = []
    cy = []
    cname = []
    for c in tc:
        cx.append(c.coordinates()[0])
        cy.append(c.coordinates()[1])
        cname.append(c.name)
    bx = []
    by = []
    bname = []
    for b in tb:
        bx.append(b.coordinates()[0])
        by.append(b.coordinates()[1])
        bname.append(b.name)
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
    for n, x, y in zip(cname, cx, cy):
        plt.annotate(n, (x, y), (x + 10, y + 10))
    for n, x, y in zip(bname, bx, by):
        plt.annotate(n, (x, y), (x + 10, y + 10))
    reachNames = [r.getName() for r in tr]
    nodeNames = []
    for i, n in enumerate(tc):
        nodeNames.append("{}[{}]".format(n.name, i))
    for i, b in enumerate(tb):
        nodeNames.append("{}[{}]".format(b.name, i+12))
        
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
    plt.show()