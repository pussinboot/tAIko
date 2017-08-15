import os

import numpy as np
from scipy.stats import gamma as gamma_fun

from brains import analysis, imaging
from control import ds


class QQ_Learner:
    def __init__(self, ds_trainer, savedata_folder=None):
        # params
        self.alpha = 0.95
        self.gamma_const = 0.66

        # for exploration
        self.explore_n = 500
        self.explore_rate = 0.004

        # reward factor constant (must be > 1)
        self.r_f = 1.25

        # things to keep in mind
        self.last_state_action_pairs = []
        self.last_reward = 0

        # savedata
        if savedata_folder is None:
            savedata_folder = '../resources/training_savedata/'
        self.savedata_fname = os.path.join(savedata_folder, 'training.npz')

        load_def = True
        if os.path.exists(self.savedata_fname):
            try:
                with np.load(self.savedata_fname) as saved_data:
                    self.Q_vals = saved_data['q_vals']
                    self.trained_n = saved_data['n']
                load_def = self.Q_vals.shape == (100, 3)
            except:
                pass

        if load_def:
            self.Q_vals = np.zeros([100, 3])  # 100 intensities 3 actions
            self.trained_n = 0  # keep track of how many times we've updated Q

        # for finding our weighted avg max q-val we precompute some things
        self.pre_comp_gamma = np.zeros([100, 100])
        self.pre_comp_gamma_sum = np.zeros(100)

        def precompute_gamma_weights():
            start_x = np.arange(0.1, 10.1, 0.1)
            for i in range(100):
                dist = gamma_fun((i + 1) / 10)
                self.pre_comp_gamma[i] = dist.pdf(start_x)
            self.pre_comp_gamma_sum = np.sum(self.pre_comp_gamma, axis=1)

        precompute_gamma_weights()

        # helper objects
        self.imh = imaging.ImageHelper()
        self.ds_s = analysis.DS_Scorer(self.imh)
        self.ds_a = analysis.DS_Color_Picker(self.imh)

        self.trainer = ds_trainer

        # finally start training
        self.trainer.choose_new_track()

    def save_data(self):
        np.savez(self.savedata_fname, q_vals=self.Q_vals, n=self.trained_n)

    def restart(self):
        # internal state
        self.last_state_action_pairs = []
        self.last_reward = 0

        # helpful modules
        self.ds_s.restart()
        self.trainer.choose_new_track()

    # action selection

    def select_action(self, state):
        return np.argmax(self.Q_vals[state, :])

    def explore(self, state):
        # with certain probability return random action
        random_test = np.random.random() < (1 / (1 + np.exp(self.explore_rate * (self.trained_n - self.explore_n))))
        if random_test:
            # want to do nothing most often..
            return int(np.floor(np.random.exponential(0.5) % 3))
        else:
            # otherwise just most util
            return self.select_action(state)

    # Q learning
    # accessing q Q_vals[(50,2)] (state, action)

    def find_weighted_max_q_val(self, last_state):
        # weighted mean
        wm_t = np.sum(np.multiply(self.Q_vals.transpose(), self.pre_comp_gamma[last_state]), axis=1)
        wm = wm_t / (self.pre_comp_gamma_sum[last_state] + 1e-8)
        return np.max(wm)

    def update_q(self, new_reward):
        # normalize reward
        n_reward = new_reward * (np.sign(new_reward - self.last_reward) + self.r_f) / (1 + self.r_f)
        # update last reward..
        self.last_reward = new_reward
        for t, sap in enumerate(self.last_state_action_pairs):
            max_a_q = self.find_weighted_max_q_val(sap[0])
            # i had (gamma ** (t + 1)) in here.. but i dont think extra discounting is necessary?
            # we should apply what we've learned to everything equally after getting feedback.
            self.Q_vals[sap] += self.alpha * (n_reward + (self.gamma_const * max_a_q) - self.Q_vals[sap])

    def training_step(self):
        # frame skip
        self.trainer.advance_frame()

        # get pic
        new_f_fname = self.trainer.find_last_frame()
        new_frame = self.imh.clean_pic(new_f_fname)

        # if lvl ended we start over
        if self.ds_a.check_lvl_over(new_frame):
            self.restart()
            return

        # check if score updated
        new_score, score_diff = self.ds_s.get_score(new_frame)

        if score_diff > 0:
            self.trained_n += 1
            print(self.trained_n, 'update q-valz score_diff =', score_diff)
            self.update_q(score_diff)
            self.last_state_action_pairs = []

        # find current state
        color_choice, s = self.ds_a.pick_color(new_frame)
        cur_state = int(np.floor(100 * s))

        # pick a new action?
        num_but = self.explore(cur_state)
        # print(color_choice, cur_state, 'pressing', num_but, 'buttons')
        self.trainer.advance_frame([color_choice, num_but])
        self.last_state_action_pairs += [(cur_state, num_but)]


if __name__ == '__main__':
    training_control = ds.Training()
    q_learner = QQ_Learner(training_control)

    while True:
        try:
            q_learner.training_step()
        except KeyboardInterrupt:
            q_learner.save_data()
            break

    print('bye bye')
