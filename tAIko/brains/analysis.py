import os
import numpy as np
from PIL import Image

from imaging import ImageHelper


class DS_Scorer():
    def __init__(self, mask_path=None):
        self.image_help = ImageHelper()

        self.masks = [self.image_help.clean_array_mask(i) for i in range(10)]

        self.last_score = 0
        self.NUM_DETECT_THRESH = 80

    def restart(self):
        self.last_score = 0

    def get_score(self, c_frame):
        score_crop = c_frame[52:68, -94:-10, :]
        read_num = []

        for i in reversed(range(7)):
            looking_at = score_crop[:, 12 * i:12 * (i + 1), :]

            abs_diff = [np.mean(np.fabs(looking_at - self.masks[j])) for j in range(10)]
            most_likely = np.argmin(abs_diff)

            if abs_diff[most_likely] > self.NUM_DETECT_THRESH:
                break

            read_num += [most_likely]

        new_score = sum([n * 10 ** i for i, n in enumerate(read_num)])

        # score can't go down, and differs by at least 100 and at most 25k?
        # (stupid things where you have to mash and u get bonus for complete)
        score_diff = new_score - self.last_score

        if score_diff < 100 or score_diff > 25000:
            new_score = self.last_score

        self.last_score = new_score

        return (new_score, score_diff)


if __name__ == '__main__':
    s = DS_Scorer()
