import numpy as np

def accurate_depth_image(depth_data: np.ndarray, from_mm: int):
    """ from a given milimeter, creates an image
        consisting of datapoints with 255 mm range
    """
    depth_data_translated = depth_data - from_mm

    # use the original depth data as a mask
    depth_data_translated[depth_data < from_mm] = 0
    depth_data_translated[depth_data > from_mm+255] = 255

    return depth_data_translated.astype(np.uint8)
