import os
import numpy as np

from PIL import Image
from matplotlib import colors as mplc

from imaging import ImageHelper

class DS_Scorer():
    def __init__(self, imhelp):
        self.image_help = imhelp

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


class Color_Picker():
    def __init__(self, orange_color, blue_color, color_detect_thresh, imhelp):
        self.image_help = imhelp

        self.o_hsv, self.b_hsv = mplc.rgb_to_hsv(orange_color), mplc.rgb_to_hsv(blue_color)
        self.COLOR_DETECT_THRESH = color_detect_thresh

    def pick_color(self, c_frame):
        # returns a tuple with the color: either None, 'o'(range) or 'b'(lue)
        # as well as its relative percent among all colors
        colors, counts = np.unique(np.reshape(c_frame, [-1, 3]), axis=0, return_counts=True)
        non_gray_mask = np.ravel(np.diff(np.diff(colors)) != 0)

        if sum(non_gray_mask) == 0:
            return (None, 0.00)

        ttc_i = np.argsort(counts[non_gray_mask])[-3:]
        top_three_colors = colors[non_gray_mask][ttc_i]
        ttc_hsv = mplc.rgb_to_hsv(top_three_colors)

        o_dist = np.min(np.linalg.norm(ttc_hsv - self.o_hsv, axis=1))
        b_dist = np.min(np.linalg.norm(ttc_hsv - self.b_hsv, axis=1))

        prcnt = np.sum(counts[non_gray_mask][ttc_i]) / np.sum(counts)

        if min(o_dist, b_dist) < self.COLOR_DETECT_THRESH:
            if o_dist < b_dist:
                return ('o', prcnt)
            return ('b', prcnt)
        return (None, prcnt)


class DS_Color_Picker(Color_Picker):
    def __init__(self, imhelp):
        super(DS_Color_Picker, self).__init__([255, 74, 41], [49, 173, 198], 50, imhelp)

    def pick_color(self, c_frame):
        return super(DS_Color_Picker, self).pick_color(c_frame[75:108, 13:46, :])


if __name__ == '__main__':
    imh = ImageHelper()
    s = DS_Scorer(imh)
    c = DS_Color_Picker(imh)

    x_path = os.path.expanduser('~/Documents/Code/tAIko/resources/taikotemp/recordings/extracted')

    def get_test_frame(f_no):
        f_path = x_path + '/out-{}.png'.format(f_no)
        return imh.clean_pic(f_path)

    # t1 = get_test_frame(4749)
    # print(c.pick_color(t1)) # 'o', ~67%

    # this is pretty quick, takes only 1 second : )
    import random
    for _ in range(100):
        fn = random.randint(1, 7035)
        print(c.pick_color(get_test_frame(fn)))
