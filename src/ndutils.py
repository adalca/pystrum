''' Utilities for nd (n-dimensional) arrays '''
import numpy as np

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
