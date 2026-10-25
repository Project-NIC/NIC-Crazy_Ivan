"""Read MakeHuman's base mesh: the vertices and the faces of each group."""
import numpy as np
def load(path):
    V=[]; groups={}; cur=None
    for line in open(path):
        if line.startswith('v '):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('g '):
            cur=line.split()[1]
        elif line.startswith('f '):
            idx=[int(t.split('/')[0])-1 for t in line.split()[1:]]
            groups.setdefault(cur,[]).append(idx)
    return np.array(V),groups
