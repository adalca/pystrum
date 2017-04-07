"""
patchlib (python version)

A powerful library for working with N-D patches. 
Modelled after the MATLAB patchlib (https://github.com/adalca/patchlib)
"""

import types
import numpy as np

import pynd.ndutils as nd
from imp import reload
reload(nd)


def patch_gen(vol, patch_size, stride=1, nargout=1):
    """
    NOT VERY WELL TESTED
    generator of patches from volume

    TODO: use .grid() to get sub

    """

    cropped_vol_size = np.array(vol.shape) - np.array(patch_size) + 1
    assert np.all(cropped_vol_size >= 0), \
        "patch size needs to be smaller than volume size"

    # get range subs
    sub = ()
    for cvs in cropped_vol_size:
        sub += (list(range(0, cvs, stride)), )

    # get ndgrid of subs
    ndg = nd.ndgrid(*sub)
    ndg = [f.flat for f in ndg]

    # generator
    slicer = lambda f, g: slice(f[idx], f[idx] + g)
    for idx in range(len(ndg[0])):
        patch_sub = [slicer(f, g) for f, g in zip(ndg, patch_size)]
        if nargout == 1:
            yield vol[patch_sub]
        else:
            yield (vol[patch_sub], patch_sub)


def quilt(patches, patch_size, grid_size, patch_stride=1, nan_func=lambda x:np.nanmean(x, 0)):
    """ patches should be a nPatches-by-nVoxels array, or a patch generator """

    patch_stack = stack(patches, patch_size, grid_size, patch_stride)
    return nan_func(patch_stack)


def stack(patches, patch_size, grid_size, patch_stride=1, nargout=1):
    """ UNFINISHED """

    assert np.all(np.mod(patch_size, 2) == 1), "patch size is not odd"
    K = patches.shape[2] if len(patches.shape) > 2 else 1

    # compute the input target_size and target
    if np.prod(grid_size) == patches.shape[0]: # given the number of patches in the grid
        target_size = grid2volsize(grid_size, patch_size, patch_stride=patch_stride)
    else:
        target_size = grid_size

    # compute the grid indexes (and check that the target size matches)
    [grid_idx, target_size_chk] = grid(target_size, patch_size, patch_stride, nargout=2)
    assert np.all(target_size == target_size_chk), 'Target does not match the provided target size'

    # prepare subscript and index vectors
    grid_sub = nd.ind2sub_entries(grid_idx, target_size)
    all_idx = list(range(grid_idx.size))

    # get index of layer location so that patches don't overlap
    # we do this by computing the modulo of the patch start location
    # with respect to the patch size. This won't be optimal yet, but we'll
    # eliminate any layers with no patches after
    mod_sub = np.array([_mod_base(g, patch_size) for g in grid_sub]).transpose()
    patch_payer_idx = nd.sub2ind(mod_sub, patch_size)

    # initiate the votes layer structure
    layer_ids = np.unique(patch_payer_idx)
    nb_layers = len(layer_ids)
    layers = np.empty([nb_layers, *target_size, K])
    layers[:] = np.NAN

    # prepare input matching matrix
    if nargout >= 2:
        idxmat = np.empty([2, nb_layers, *target_size, K])
        idxmat[:] = np.NAN

    #  go over each layer index
    for layer_idx in range(nb_layers):
        # get patches attributed to this layer
        patch_id_in_layer = np.where(patch_payer_idx == layer_ids[layer_idx])

        # prepare the layers
        layer_stack = np.empty([*target_size, K])
        layer_stack[:] = np.NAN
        if nargout >= 2:
            layer_idxmat = np.nan([2, *target_size, K])

        # go thorugh each patch location for patches in this layer
        for pidx in patch_id_in_layer[0]:

            # extract the patches
            localpatches = np.squeeze(patches[pidx, :])
            patch = np.reshape(localpatches, [*patch_size, K])

            # put the patches in the layers
            sub = [*grid_sub[pidx, :], 0]
            endsub = np.array(sub) + np.array([*patch_size, K])
            rge = nd.range(sub, endsub)
            layer_stack[rge] = patch

            # update input matching matrix
            if nargout >= 2:
                # the linear index of the patch in the grid
                locidx = np.ones([2, *patch_size, K]) * all_idx[pidx]
                locidx[1, :] = np.matlib.repmat(list(range(np.prod(patch_size))), 1, K)
                layer_idxmat[rge] = locidx

        # update layer
        layers[layer_idx, :] = np.reshape(layer_stack.flatten(), [*target_size, K])

        # update the complete idxmat
        if nargout >= 2:
            idxmat[0, layer_idx, :] = layer_idxmat[0, :]
            idxmat[1, layer_idx, :] = layer_idxmat[1, :]

    # setup outputs
    if nargout == 1:
        return layers
    elif nargout == 2:
        print("UNCHECKED")
        return (layers, idxmat)
    elif nargout == 3:
        print("UNCHECKED")
        p = np.zeros(1, np.max(patch_payer_idx.flatten()))
        p[layer_ids] = list(range(len(layer_ids)))
        return (layers, idxmat, p[patch_payer_idx])




def grid2volsize(grid_size, patch_size, patch_stride=1):
    """
    compute the volume size from the grid size and patch information

    Parameters:
        grid_size (vector): the size of the grid in each dimension
        patch_size (vector): the size of the patch_gen
        patch_stride (vector/scalar, optional): the size of the stride

    Returns:
        Volume size filled up by the patches

    See Also:
        gridsize(), grid()

    Contact:
        {adalca,klbouman}@csail.mit.edu
    """

    # parameter checking
    if not isinstance(grid_size, np.ndarray):
        grid_size = np.array(grid_size, 'int')
    if not isinstance(patch_size, np.ndarray):
        patch_size = np.array(patch_size, 'int')
    nb_dims = len(patch_size)   # number of dimensions
    if isinstance(patch_stride, int):
        patch_stride = np.repeat(patch_stride, nb_dims).astype('int')

    patch_overlap = patch_size - patch_stride
    vol_size = grid_size * patch_stride + patch_overlap
    return vol_size


def gridsize(vol_size, patch_size, patch_stride=1, start_sub=0, nargout=1):
    """
    Number of patches that fit into volSize given a particular patch_size. patch_strideb
    cropped to the maximum size that fits the patch grid. For example, a [6x6] volume with
    patch_size opatch_stridee

    Parameters:
        vol_size (numpy vector): the size of the input volume
        patch_size (numpy vector): the size of the patches
        patch_stride (int or numpy vector, optional): stride (separation) in each dimension.
            default: 1
        start_sub (int or numpy vector, optional): the volume location where patches start
            This essentially means that the volume will be cropped starting at that location.
            e.g. if startSub is [2, 2], then only vol(2:end, 2:end) will be included.
            default: 0
        nargout (int, 1 or 2): optionally output new (cropped) volume size.
            return the grid_size only if nargout is 1, or (grid_size, new_vol_size)
            if narout is 2.
    Returns:
        grid_size only, if nargout is 1, or
        (grid_size, new_vol_size) if narout is 2

    See Also:
        grid()

    Contact:
        {adalca,klbouman}@csail.mit.edu
    """

    # parameter checking
    if not isinstance(vol_size, np.ndarray):
        vol_size = np.array(vol_size, 'int')
    if not isinstance(patch_size, np.ndarray):
        patch_size = np.array(patch_size, 'int')
    nb_dims = len(patch_size)   # number of dimensions
    if isinstance(patch_stride, int):
        patch_stride = np.repeat(patch_stride, nb_dims).astype('int')
    if isinstance(start_sub, int):
        start_sub = np.repeat(start_sub, nb_dims).astype('int')

    # adjacent patch overlap
    patch_overlap = patch_size - patch_stride

    # modified volume size if starting late
    mod_vol_size = vol_size - start_sub

    # compute the number of patches
    # the final volume size will be
    # >> grid_size * patch_stride + patch_overlap
    # thus the part that is a multiplier of patch_stride is vol_size - patch_overlap
    patch_stride_multiples = mod_vol_size - patch_overlap # not sure?
    grid_size = np.floor(patch_stride_multiples / patch_stride).astype('int')

    if nargout == 1:
        return grid_size
    else:
        # new volume size based on how far the patches can reach
        new_vol_size = grid2volsize(grid_size, patch_size, patch_stride=patch_stride)
        return (grid_size, new_vol_size)


def grid(vol_size, patch_size, patch_stride=1, start_sub=0, nargout=1, grid_type='idx'):
    """
    grid of patch starting points for nd volume that fit into given volume size

    The index is in the given volume. If the volume gets cropped as part of the function and you
    want a linear indexing into the new volume size, use
    >> newidx = ind2ind(new_vol_size, vol_size, idx)
    new_vol_size can be passed by the current function, see below.

    Parameters:
        vol_size (numpy vector): the size of the input volume
        patch_size (numpy vector): the size of the patches
        patch_stride (int or numpy vector, optional): stride (separation) in each dimension.
            default: 1
        start_sub (int or numpy vector, optional): the volume location where patches start
            This essentially means that the volume will be cropped starting at that location.
            e.g. if startSub is [2, 2], then only vol(2:end, 2:end) will be included.
            default: 0
        nargout (int, 1,2 or 3): optionally output new (cropped) volume size and the grid size
            return the idx array only if nargout is 1, or (idx, new_vol_size) if nargout is 2,
            or (idx, new_vol_size, grid_size) if nargout is 3
        grid_type ('idx' or 'sub', optional): how to describe the grid, in linear index (idx)
            or nd subscripts ('sub'). sub will be a nb_patches x nb_dims ndarray. This is
            equivalent to sub = ind2sub(vol_size, idx), but is done faster inside this function.
            [TODO: or it was in MATLAB, this might not be true in python anymore]

    Returns:
        idx nd array only if nargout is 1, or (idx, new_vol_size) if nargout is 2,
            or (idx, new_vol_size, grid_size) if nargout is 3

    See also:
        gridsize()

    Contact:
        {adalca,klbouman}@csail.mit.edu
    """

    # parameter checking
    assert grid_type in ('idx', 'sub')
    if not isinstance(vol_size, np.ndarray):
        vol_size = np.array(vol_size, 'int')
    if not isinstance(patch_size, np.ndarray):
        patch_size = np.array(patch_size, 'int')
    nb_dims = len(patch_size)   # number of dimensions
    if isinstance(patch_stride, int):
        patch_stride = np.repeat(patch_stride, nb_dims).astype('int')
    if isinstance(start_sub, int):
        start_sub = np.repeat(start_sub, nb_dims).astype('int')

    # get the grid data
    [grid_size, new_vol_size] = gridsize(vol_size, patch_size,
                                         patch_stride=patch_stride,
                                         start_sub=start_sub,
                                         nargout=2)

    # compute grid linear index
    # prepare the sample grid in each dimension
    xvec = ()
    for idx in range(nb_dims):
        volend = new_vol_size[idx] + start_sub[idx] - patch_size[idx] + 1
        locs = list(range(start_sub[idx], volend, patch_stride[idx]))
        xvec += (locs, )
        assert any((locs[-1] + patch_size - 1) == (new_vol_size + start_sub - 1))

    # get the nd grid
    # if want subs, this is the faster way to compute in MATLAB (rather than ind -> ind2sub)
    # TODO: need to investigate for python
    idx = nd.ndgrid(*xvec)
    if grid_type == 'idx':
        # if want index, this is the faster way to compute (rather than sub -> sub2ind
        all_idx = np.array(list(range(0, np.prod(vol_size))))
        all_idx = np.reshape(all_idx, vol_size)
        idx = all_idx[idx]

    if nargout == 1:
        return idx
    elif nargout == 2:
        return (idx, new_vol_size)
    else:
        return (idx, new_vol_size, grid_size)


def _row_gen(nparray):
    for rowi in nparray.shape[0]:
        yield nparray[rowi, :]

def _mod_base(X, Y, base=0):
    """
    modulo with respect to a specific base numbering system
    i.e. returns base + ((X - base) % Y)
    x = modBase(X, Y) behaves like X % Y

    Parameters:
        X (array_like): divident
        Y (array_like): divisor
        base (optional, default 0): the base

    Returns:
        the modulo
    """

    return base + np.mod(X - base, Y)