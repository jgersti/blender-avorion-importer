import numpy as np
from . categories import SHAPES
from . entities import Block

def _rotateReference(points, orientation):
    # np.any((a < 1) | (a > 5))
    if np.any((orientation < 0) | (orientation > 5)):
        print(f'Invalid orientation: {orientation}')
        return points

    o = np.asarray([0.5, 0.5,0.5])
    R = np.zeros((3,3))

    sign = lambda b: 2*b-1

    i, j = orientation // 2
    k = 3 - i - j
    u, v = sign(orientation % 2)
    w = u*v*sign(i < j)*sign(k != 1)
    R[i,0] = u
    R[j,1] = v
    R[k,2] = w

    # print(R)

    return np.einsum('ij,...j->...i', R, points-o) + o

def _getHexahedron(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 0, 0],
                      [0, 1, 0],
                      [0, 1, 1],
                      [1, 1, 1],
                      [1, 1, 0]])
    # faces = [np.asarray([0, 3, 2, 1]),
    #          np.asarray([4, 5, 6, 7]),
    #          np.asarray([0, 1, 5, 4]),
    #          np.asarray([2, 3, 7, 6]),
    #          np.asarray([1, 2, 6, 5]),
    #          np.asarray([0, 4, 7, 3])]
    faces = np.asarray([0, 1, 2, 3, 4, 5, 6, 7])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 12, faces, points

def _getWedge(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [1, 0, 0],
                      [1, 0, 1],
                      [0, 0, 1],
                      [1, 1, 0],
                      [1, 1, 1]])
    faces = np.asarray([3, 2, 5, 0, 1, 4])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 13, faces, points

def _getPyramid1(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 0, 0],
                      [1, 1, 0]])
    faces = np.asarray([0, 1, 2, 3, 4])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 14, faces, points


def _getPyramid2(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [0, 1, 0],
                      [1, 1, 1],
                      [1, 0, 1],
                      [1, 0, 0]])
    faces = np.asarray([0, 1, 2, 3, 4])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 14, faces, points

def _getTetrahedron1(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [1, 0, 0],
                      [1, 0, 1],
                      [1, 1, 0]])
    faces = np.asarray([0, 1, 3, 2])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 10, faces, points

def _getTetrahedron2(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [0, 1, 0]])
    faces = np.asarray([0, 1, 2, 3])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 10, faces, points

def _getTetrahedron3(lower, upper, orientation):
    ref = np.asarray([[1, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 1, 0]])
    faces = np.asarray([0, 1, 2, 3])

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 10, faces, points

def _getPolyhedron(lower, upper, orientation):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 0, 0],
                      [0, 1, 0],
                      [1, 1, 1],
                      [1, 1, 0]])
    faces = [np.asarray([0, 3, 2, 1]),
             np.asarray([0, 4, 6, 3]),
             np.asarray([2, 3, 6, 5]),
             np.asarray([0, 1, 4]),
             np.asarray([1, 2, 5]),
             np.asarray([4, 5, 6]),
             np.asarray([1, 5, 4])]

    points = _rotateReference(ref, orientation)
    points = np.einsum('...i,i->...i', points, upper-lower) + lower
    return 42, faces, points


def getCell(block: Block):
    shape2geometry = {
        'Edge':             _getWedge,
        'Corner 1':         _getTetrahedron1,
        'Corner 2':         _getPolyhedron,
        'Corner 3':         _getPyramid1,
        'Flat Corner':      _getPyramid2,
        'Twisted Corner 1': _getTetrahedron2,
        'Twisted Corner 2': _getTetrahedron3,
        'Default':          _getHexahedron
    }

    index2key = (key for key, indices in SHAPES.items() if block.type in indices)
    return shape2geometry[next(index2key, 'Default')](block.lower, block.upper, block.orientation)

def getBounds(block: Block):
    return block.lower, block.upper
