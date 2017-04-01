"""
patch library
"""

import numpy as np
import pynd.ndutils as nd

def patch_gen(vol, patch_size, stride=1, nargout=1):
    """
    UNTESTED
    generator of patches from volume
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

def gridsize(vol, patch_size, stride=1):
    cropped_vol_size = np.array(vol.shape) - np.array(patch_size) + 1

    # get range subs
    sub = ()
    for cvs in cropped_vol_size:
        sub += (len(list(range(0, cvs, stride))), )

    return sub