'''
Utilities for nd (n-dimensional) arrays
Tested on Python 3.5

Contact: adalca@csail.mit.edu
'''

import numpy as np
import scipy as sp
import scipy.ndimage


def boundingbox(bwvol):
    '''
    bounding box coordinates of a nd volume

    Parameters
    ----------
    vol : nd array
        the binary (black/white) array for which to compute the boundingbox

    Output
    ------
    boundingbox : 1-by-(nd*2) array
        [xstart ystart ... xend yend ...]
    '''

    # find indices where bwvol is True
    idx = np.where(bwvol)

    # get the starts
    starts = [np.min(x) for x in idx]

    # get the ends
    ends = [np.max(x) for x in idx]

    # concatinate [starts, ends]
    return np.concatenate((starts, ends), 0)



def bwdist(bwvol):
    '''
    positive distance transform from positive entries in logical image

    Parameters
    ----------
    bwvol : nd array
        The logical volume

    Output
    ------
    possdtrf : nd array
        the positive distance transform

    See Also
    --------
    bw2sdtrf
    '''

    # reverse volume to run scipy function
    revbwvol = np.logical_not(bwvol)

    # get distance
    return scipy.ndimage.morphology.distance_transform_edt(revbwvol)



def bw2sdtrf(bwvol):
    '''
    computes the signed distance transform from the surface between the
    binary True/False elements of logical bwvol

    Note: the distance transform on either side of the surface will be +1/-1
    - i.e. there are no voxels for which the dst should be 0.

    Runtime: currently the function uses bwdist twice. If there is a quick way to
    compute the surface, bwdist could be used only once.

    Parameters
    ----------
    bwvol : nd array
        The logical volume

    Output
    ------
    sdtrf : nd array
        the signed distance transform

    See Also
    --------
    bwdist
    '''

    # get the positive transform (outside the positive island)
    posdst = bwdist(bwvol)

    # get the negative transform (distance inside the island)
    notbwvol = np.logical_not(bwvol)
    negdst = bwdist(notbwvol)

    # combine the positive and negative map
    return posdst * notbwvol - negdst * bwvol


def bw2contour(bwvol, type='both'):
    '''
    computes the contour of island(s) on a nd logical volume

    Parameters
    ----------
    bwvol : nd array
        The logical volume
    type : optional string
        since the contour is drawn on voxels, it can be drawn on the inside
        of the island ('inner'), outside of the island ('outer'), or both
        ('both' - default)

    Output
    ------
    contour : nd array
        the contour map of the same size of the input

    See Also
    --------
    bwdist, bw2dstrf
    '''

    # obtain a signed distance transform for the bw volume
    sdtrf = bw2sdtrf(bwvol)

    if type == 'inner':
        return np.logical_and(sdtrf <= 0, sdtrf > -1.0001)
    elif type == 'outer':
        return np.logical_and(sdtrf >= 0, sdtrf < 1.0001)
    else:
        assert type == 'both', 'type should only be inner, outer or both'
        return np.abs(sdtrf) < 1.01


def ndgrid(*args, **kwargs):
    '''
    Disclaimer: This code is taken directly from the scitools package [1]
    Since at the time of writing scitools predominantly requires python 2.7 while we work with 3.5+
    To avoid issues, we copy the quick code here.

    Same as calling ``meshgrid`` with *indexing* = ``'ij'`` (see
    ``meshgrid`` for documentation).
    '''
    kwargs['indexing'] = 'ij'
    return np.meshgrid(*args, **kwargs)



def volsize2ndgrid(volsize):
    '''
    return the dense nd-grid for the volume with size volsize
    essentially return the ndgrid fpr
    '''
    ranges = [np.arange(e) for e in volsize]
    return ndgrid(*ranges)



def bw_sphere(volshape, rad, loc=None):
    '''
    compute a logical (black/white) image of a sphere
    '''

    # if the location is not given, use the center of the volume.
    if loc is None:
        loc = 1.0 * (np.array(volshape)-1) / 2
    assert len(loc) == len(volshape), \
        'Location (%d) and volume dimensions (%d) do not match' % (len(loc), len(volshape))


    # compute distances between each location in the volume and ``loc``
    volgrid = volsize2ndgrid(volshape)
    dst = [np.square(loc[d] - volgrid[d]) for d in range(len(volshape))]
    dst = np.sqrt(np.sum(dst, 0))

    # draw the sphere
    return dst <= rad


def volcrop(vol, new_vol_size=None, start=None, end=None, crop=None):
    '''
    crop a nd volume.

    Parameters
    ----------
    vol : nd array
        the nd-dimentional volume to crop. If only specified parameters, is returned intact
    new_vol_size : nd vector, optional
        the new size of the cropped volume
    crop : nd tuple, optional
        either tuple of integers or tuple of tuples.
        If tuple of integers, will crop that amount from both sides.
        if tuple of tuples, expect each inner tuple to specify (start, end)
    start : int, optional
        start of cropped volume
    end : int, optional
        end of cropped volume

    Output
    ------
    cropped_vol : nd array
    '''

    vol_size = np.asarray(vol.shape)

    # check which parameters are passed
    passed_new_vol_size = new_vol_size is not None
    passed_crop_size = (crop is not None) and (not isinstance(crop[0], tuple))
    passed_start = start is not None
    passed_end = end is not None
    passed_crop = crop is not None and (isinstance(crop[0], tuple))

    # from whatever is passed, we want to obtain start and end.
    if passed_start and passed_end:
        assert not (passed_new_vol_size or passed_crop_size or passed_crop), \
            "If passing start and end, don't pass anything else"

    elif passed_new_vol_size or passed_crop_size:
        # compute new volume size and crop_size
        if passed_new_vol_size:
            assert not (passed_crop_size or passed_crop), \
                "Cannot use both new volume size and crop info"

        elif passed_crop_size:
            assert not passed_crop, "Cannot use both crop_size and crop"
            new_vol_size = vol_size - 2 * np.asarray(crop)

        # compute start and end
        if passed_start:
            assert not passed_end, "When giving passed_crop_size, cannot pass both start and end"
            end = start + new_vol_size

        elif passed_end:
            assert not passed_start, "When giving passed_crop_size, cannot pass both start and end"
            start = end - new_vol_size

        else: # none of crop_size, crop, start or end are passed
            mid = np.asarray(new_vol_size) // 2 # // does integer division
            start = mid - (new_vol_size // 2)
            end = start + new_vol_size

    elif passed_crop:
        assert not (passed_start or passed_end), "Cannot pass both passed_crop and start or end"
        start = [val[0] for val in crop]
        end = vol_size - [val[1] for val in crop]

    elif passed_start: # nothing else is passed
        end = vol_size

    else:
        assert passed_end
        start = vol_size * 0


    # get indices. Since we want this to be an nd-volume crop function, we
    idx = []
    for i in range(len(end)):
        idx.append(slice(start[i], end[i]))

    return vol[idx]



def axissplit(arr, axis):
    '''
    Split a nd volume along an exis into n volumes, where n is the size of the axis dim.

    Parameters
    ----------
    arr : nd array
        array to split
    axis : integer
        indicating axis to split

    Output
    ------
    outarr : 1-by-n array
        where n is the size of the axis dim in original volume.
        each entry is a sub-volume of the original volume

    See also numpy.split()
    '''
    nba = arr.shape[axis]
    return np.split(arr, nba, axis=axis)


