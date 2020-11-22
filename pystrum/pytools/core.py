import collections

def flatten_collection(l):
    # https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten_collection(el)
        else:
            yield el

def unzip(zipped_list):
    """
    undo zip(l1, l2)
    https://www.geeksforgeeks.org/python-unzip-a-list-of-tuples/

    Args:
        zipped_list ([type]): [description]

    Returns:
        [type]: [description]
    """
    res = ([ i for i, j in zipped_list], 
           [ j for i, j in zipped_list])
    return res
