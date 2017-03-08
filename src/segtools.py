''' 
nd segmentation (label map) utilities

Contact: adalca@csail.mit.edu
'''

import numpy as np
import ndutils as nd

def seg2contour(seg, exclude_zero=True, contour_type='inner'):
	''' 
	transform nd segmentation (label maps) to contour maps

	Parameters
	----------
	seg : nd array 
		volume of labels/segmentations
	exclude_zero : optional logical
		whether to exclude the zero label.
		default True
	contour_type : string
		where to draw contour voxels relative to label 'inner','outer', or 'both'

	Output
	------
	con : nd array
		nd array (volume) of contour maps

	See Also
	--------
	seg_overlap
	'''

	# extract unique labels
	labels = np.unique(seg)
	if exclude_zero:
		labels = np.delete(labels, np.where(labels == 0))
	
	# get the contour of each label
	contour_map = seg * 0
	for li, lab in enumerate(labels):

		# extract binary label map for this label
		label_map = seg == lab
		
		# extract contour map for this label
		label_contour_map = nd.bw2contour(label_map, type=contour_type)
		
		# assign contour to this label
		contour_map[label_contour_map] = lab

	return contour_map
