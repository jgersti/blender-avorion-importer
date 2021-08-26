import numpy as np

from avorion_utils.shapes import getCell, getBounds


def _getColors(blocks):
    helper = vtk.vtkNamedColors()
    return np.asarray([helper.HTMLColorToRGBA(f"#{b.color[2:]}") for b in blocks], dtype=np.uint8)


def _getOrientations(blocks, comp):
    return np.array([b.orientation[comp] for b in blocks], dtype=np.uint64)


def _getMaterials(blocks):
    return np.array([b.material for b in blocks], dtype=np.uint64)


def _getTypes(blocks):
    return np.array([b.type for b in blocks], dtype=np.uint64)


def createModel(blocks, merge=True, tolerance=1e-6):
    # model = None
    # n = len(blocks)
    # printProgressBar(0, n, empty=' ', length=80, prefix='Build Model', decimals=0)

    # for k, b in enumerate(blocks[0:3]):
    #     t, i, p = getCell(b)
    #     if type(i) is list:
    #         cell = [[1+len(i), len(i)]]
    #         for sub in i:
    #             cell.extend([[len(sub)], sub])
    #             cell[0][0] += len(sub)
    #     else:
    #         cell = [[len(i)], i]

    #     ug = pv.UnstructuredGrid(np.asarray(np.concatenate(cell)), np.asarray([t]), np.asarray(p))
    #     data = ug.cell_arrays
    #     data['color'] = _getColors([b])
    #     data['material'] = _getMaterials([b])
    #     data['type'] = _getTypes([b])

    #     block = ug.extract_surface()
    #     # print(block)
    #     block.triangulate(inplace=True)
    #     # print(block)

    #     if model is None:
    #         model = block
    #     else:
    #         model.boolean_union(block, inplace=True)
    #         # model = model + block

    #     printProgressBar(k+1, n, empty=' ', length=80, prefix='Build Model', decimals=0)

    # print(model, model.array_names)
    # model.clean(tolerance=tolerance)
    # print(model, model.array_names)
    # return model, n

    if merge:
        def insert(pts, npts):
            i = vtk.reference(-1)
            ind = []
            for p in npts:
                pts.InsertUniquePoint(p, i)
                ind.append(i.get())
            return np.array(ind)

        _bounds = np.asarray([getBounds(b) for b in blocks])
        _bounds = np.ravel(np.column_stack([np.min(_bounds[:, 0, :], axis=0), np.max(_bounds[:, 1, :], axis=0)]))

        _internal = vtk.vtkPoints()
        points = vtk.vtkMergePoints()
        points.InitPointInsertion(_internal, _bounds)
    else:
        def insert(pts, npts):
            n = len(pts)
            pts.extend(npts)
            return np.arange(n, n + len(npts))

        points = []

    cells = []
    offsets = []
    types = []
    n = len(blocks)
    printProgressBar(0, n, empty=' ', length=80, prefix='Build Model', decimals=0)
    for i, _block in enumerate(blocks):
        _type, _indices, _points = getCell(_block)
        pIndices = insert(points, _points)

        if type(_indices) is list:
            cell = [[1+len(_indices), len(_indices)]]
            for sub in _indices:
                cell.extend([[len(sub)], pIndices[sub]])
                cell[0][0] += len(sub)
        else:
            cell = [[len(_indices)], pIndices[_indices]]

        cells.extend(np.concatenate(cell))
        offsets.append(1 + cell[0][0] + (offsets[-1] if offsets else 0))
        types.append(_type)
        printProgressBar(i+1, n, empty=' ', length=80, prefix='Build Model', decimals=0)

    if pv._vtk.VTK9:
        model = pv.UnstructuredGrid(np.asarray(cells),
                                    np.asarray(types),
                                    np.asarray(points) if not merge else nps.vtk_to_numpy(points.GetPoints().GetData()))
    else:
        model = pv.UnstructuredGrid(np.asarray(offsets),
                                    np.asarray(cells),
                                    np.asarray(types),
                                    np.asarray(points) if not merge else nps.vtk_to_numpy(points.GetPoints().GetData()))

    data = model.cell_arrays
    data['color'] = _getColors(blocks)
    data['material'] = _getMaterials(blocks)
    data['type'] = _getTypes(blocks)

    noc = model.number_of_cells
    print(model)
    model = model.extract_surface(pass_pointid=False)
    print(model)
    # model.clean(inplace=True)
    # print(model)
    # model.triangulate(inplace=True)
    # print(model)
    # model.clean(inplace=True)
    # print(model)
    return model, noc
