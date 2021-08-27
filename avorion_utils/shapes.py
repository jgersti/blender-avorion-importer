import numpy as np
from . categories import get_shape
from . parser import Block

def _rotate_reference(points: np.ndarray, orientation: np.ndarray) -> np.ndarray:
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


def _shift_reference(points: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.einsum("...i,i->...i", points, upper-lower) + lower

def _create_hexahedron(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 0, 0],
                      [0, 1, 0],
                      [0, 1, 1],
                      [1, 1, 1],
                      [1, 1, 0]])
    faces = np.asarray([0, 3, 2, 1,
                        4, 5, 6, 7,
                        0, 1, 5, 4,
                        2, 3, 7, 6,
                        1, 2, 6, 5,
                        0, 4, 7, 3],
                       dtype = np.int64)
    offsets = np.asarray([4, 4, 4, 4, 4, 4], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets

def _create_wedge(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [1, 0, 0],
                      [1, 0, 1],
                      [0, 0, 1],
                      [1, 1, 0],
                      [1, 1, 1]])
    faces = np.asarray([0, 1, 2, 3,
                        0, 3, 5, 4,
                        1, 4, 5, 2,
                        2, 5, 3,
                        0, 4, 1], dtype=np.int64)
    offsets = np.asarray([4, 4, 4, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets

def _create_pyramid_1(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 0, 0],
                      [1, 1, 0]])
    faces = np.asarray([0, 3, 2, 1,
                        0, 1, 4,
                        0, 4, 3,
                        1, 2, 4,
                        2, 3, 4],
                       dtype=np.int64)
    offsets = np.asarray([4, 3, 3, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets


def _create_pyramid_2(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [0, 1, 0],
                      [1, 1, 1],
                      [1, 0, 1],
                      [1, 0, 0]])
    faces = np.asarray([0, 3, 2, 1,
                        0, 1, 4,
                        0, 4, 3,
                        1, 2, 4,
                        2, 3, 4],
                       dtype=np.int64)
    offsets = np.asarray([4, 3, 3, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets

def _create_tetrahedron_1(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [1, 0, 0],
                      [1, 0, 1],
                      [1, 1, 0]])
    faces = np.asarray([0, 2, 1,
                        0, 2, 3,
                        0, 3, 1,
                        1, 3, 2],
                       dtype=np.int64)
    offsets = np.asarray([3, 3, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets

def _create_tetrahedron_2(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [0, 1, 0]])
    faces = np.asarray([0, 1, 3,
                        0, 2, 1,
                        0, 3, 2,
                        1, 2, 3],
                       dtype=np.int64)
    offsets = np.asarray([3, 3, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets

def _create_tetrahedron_3(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[1, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 1, 0]])
    faces = np.asarray([0, 1, 3,
                        0, 2, 1,
                        0, 3, 2,
                        1, 2, 3],
                       dtype=np.int64)
    offsets = np.asarray([3, 3, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets

def _create_polyhedron(lower: np.ndarray, upper: np.ndarray, orientation: np.ndarray):
    ref = np.asarray([[0, 0, 0],
                      [0, 0, 1],
                      [1, 0, 1],
                      [1, 0, 0],
                      [0, 1, 0],
                      [1, 1, 1],
                      [1, 1, 0]])
    faces = np.asarray([0, 3, 2, 1,
                        0, 4, 6, 3,
                        2, 3, 6, 5,
                        0, 1, 4,
                        1, 2, 5,
                        4, 5, 6,
                        1, 5, 4],
                       dtype=np.int64)
    offsets = np.asarray([4, 4, 4, 3, 3, 3, 3], dtype=np.int64)

    points = _shift_reference(_rotate_reference(ref, orientation), lower, upper)
    return points, faces, offsets


def generate_geometry(block: Block):
    shape2geometry = {
        'Cube':             _create_hexahedron,
        'Edge':             _create_wedge,
        'Corner 1':         _create_tetrahedron_1,
        'Corner 2':         _create_polyhedron,
        'Corner 3':         _create_pyramid_1,
        'Flat Corner':      _create_pyramid_2,
        'Twisted Corner 1': _create_tetrahedron_2,
        'Twisted Corner 2': _create_tetrahedron_3,
    }

    return shape2geometry[get_shape(block.type)](block.lower, block.upper, block.orientation)
    # return shape2geometry['Cube'](block.lower, block.upper, block.orientation)

def getBounds(block: Block):
    return block.lower, block.upper
