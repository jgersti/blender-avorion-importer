from collections.abc import Sequence, Iterable
from dataclasses import dataclass, field, replace
from typing import Self, Literal

import numpy as np
import numpy.typing as npt

from .categories import get_shape
from .parser import Block

__all__ = ["Geometry"]


def _rotation(o: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
    def sign(b: npt.NDArray[np.int64]) -> npt.NDArray[np.int64]:
        return 2 * b - 1

    i, j = o // 2
    k = 3 - i - j
    u, v = sign(o % 2)
    w = u * v * sign(i < j) * sign(k != 1)

    R = np.zeros((3, 3))
    R[i, 0] = u
    R[j, 1] = v
    R[k, 2] = w

    return R


def _rotate(vertices: npt.NDArray[np.float64], R: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # assume reference vertices
    centroid = np.array([0.5, 0.5, 0.5])
    return np.einsum("ij,...j->...i", R, vertices - centroid) + centroid

def _transform(vertices: npt.NDArray[np.float64], scale: npt.NDArray[np.float64], translation: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    return np.einsum("...i,i->...i", vertices, scale) + translation

@dataclass(frozen=True, slots=True)
class Geometry:
    vertices: npt.NDArray[np.float64]
    faces: npt.NDArray[np.int64]
    offsets: npt.NDArray[np.int64]

    @classmethod
    def concatenate(cls, geometries: Iterable[Self]) -> tuple[Self, Sequence[int]]:
        vertices = []
        faces = []
        offsets = []

        num_faces = []

        vertex_offset = 0
        for geo in geometries:
            vertices.append(geo.vertices)
            faces.append(geo.faces)
            faces[-1] += vertex_offset
            offsets.append(geo.offsets)

            num_faces.append(len(geo.offsets))
            vertex_offset += len(geo.vertices)

        new = cls(
            vertices=np.vstack(vertices) if vertices else np.array([], np.float64),
            faces=np.hstack(faces) if faces else np.array([], np.int64),
            offsets=np.hstack(offsets)if offsets else np.array([], np.int64),
        )

        return new, num_faces


    @classmethod
    def from_block(cls, block: Block) -> Self:
        factories = {
            "Cube": cls.hexahedron,
            "Edge": cls.wedge,
            "Corner 1": cls.tetrahedron_1,
            "Corner 2": cls.polyhedron,
            "Corner 3": cls.pyramid_1,
            "Flat Corner": cls.pyramid_2,
            "Twisted Corner 1": cls.tetrahedron_2,
            "Twisted Corner 2": cls.tetrahedron_3,
        }

        ref = factories[get_shape(block.type)]()
        v = _rotate(ref.vertices, _rotation(block.orientation))
        v = _transform(v, block.upper - block.lower, block.lower)
        return replace(ref, vertices=v)

    @classmethod
    def hexahedron(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]]),
            faces = np.asarray([0, 3, 2, 1, 4, 5, 6, 7, 0, 1, 5, 4, 2, 3, 7, 6, 1, 2, 6, 5, 0, 4, 7, 3], dtype=np.int64),
            offsets = np.asarray([4, 4, 4, 4, 4, 4], dtype=np.int64),
        )

    @classmethod
    def wedge(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [1, 1, 0], [1, 1, 1]]),
            faces = np.asarray([0, 1, 2, 3, 0, 3, 5, 4, 1, 4, 5, 2, 2, 5, 3, 0, 4, 1], dtype=np.int64),
            offsets = np.asarray([4, 4, 4, 3, 3], dtype=np.int64),
        )


    @classmethod
    def pyramid_1(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0], [1, 1, 0]]),
            faces = np.asarray([0, 3, 2, 1, 0, 1, 4, 0, 4, 3, 1, 2, 4, 2, 3, 4], dtype=np.int64),
            offsets = np.asarray([4, 3, 3, 3, 3], dtype=np.int64),
        )


    @classmethod
    def pyramid_2(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [0, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]]),
            faces = np.asarray([0, 3, 2, 1, 0, 1, 4, 0, 4, 3, 1, 2, 4, 2, 3, 4], dtype=np.int64),
            offsets = np.asarray([4, 3, 3, 3, 3], dtype=np.int64),
        )


    @classmethod
    def tetrahedron_1(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0]]),
            faces = np.asarray([0, 2, 1, 0, 2, 3, 0, 3, 1, 1, 3, 2], dtype=np.int64),
            offsets = np.asarray([3, 3, 3, 3], dtype=np.int64),
        )


    @classmethod
    def tetrahedron_2(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [0, 0, 1], [1, 0, 1], [0, 1, 0]]),
            faces = np.asarray([0, 1, 3, 0, 2, 1, 0, 3, 2, 1, 2, 3], dtype=np.int64),
            offsets = np.asarray([3, 3, 3, 3], dtype=np.int64),
        )


    @classmethod
    def tetrahedron_3(cls) -> Self:
        return cls(
            vertices = np.asarray([[1, 0, 0], [0, 0, 1], [1, 0, 1], [1, 1, 0]]),
            faces = np.asarray([0, 1, 3, 0, 2, 1, 0, 3, 2, 1, 2, 3], dtype=np.int64),
            offsets = np.asarray([3, 3, 3, 3], dtype=np.int64),
        )


    @classmethod
    def polyhedron(cls) -> Self:
        return cls(
            vertices = np.asarray([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 1, 0], [1, 1, 1], [1, 1, 0]]),
            faces = np.asarray([0, 3, 2, 1, 0, 4, 6, 3, 2, 3, 6, 5, 0, 1, 4, 1, 2, 5, 4, 5, 6, 1, 5, 4], dtype=np.int64),
            offsets = np.asarray([4, 4, 4, 3, 3, 3, 3], dtype=np.int64),
        )

