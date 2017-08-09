import os
import numpy as np
from PIL import Image

DEFAULT_MASK_PATH = os.path.expanduser('~/Documents/Code/tAIko/resources/taikotemp/what_i_want/')


class ImageHelper:
    def __init__(self, mask_path=None):
        if mask_path is None:
            mask_path = DEFAULT_MASK_PATH
        self.mask_path = mask_path

    def clean_pic(self, fname):
        starting_pic = Image.open(fname, 'r')
        as_array = np.asarray(starting_pic)
        as_array = as_array[:, :, :3]
        return as_array

    def clean_array_mask(self, idx):
        im_path = self.mask_path + '{}.png'.format(idx)

        start_pic = self.clean_pic(im_path)

        mask = (start_pic == [0, 255, 0])
        to_return = start_pic.copy()
        to_return[mask] = -1

        return to_return