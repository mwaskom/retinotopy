from __future__ import division
import itertools
import json

import numpy as np
import pandas as pd

from visigoth import flexible_values
from visigoth.stimuli import Point, RandomDotMotion


class DotBar(object):

    def __init__(self, exp):

        self.exp = exp

        self.dot_params = dict(elliptical=False,
                               size=exp.p.dot_size,
                               color=exp.p.dot_color,
                               density=exp.p.dot_density,
                               speed=exp.p.dot_speed,
                               interval=exp.p.dot_interval)

        # Hardcoding 3 segments for now
        self.n_segments = 3
        segment_length = (exp.p.field_size / self.n_segments
                          - exp.p.bar_segment_gap * (self.n_segments - 1))
        self.segment_length = segment_length
        self.segment_width = exp.p.bar_width

    def set_position(self, ori, rel_pos):

        self.stims = []

        segment_offsets = (np.linspace(-1, 1, self.n_segments)
                           * (self.exp.p.field_size / self.n_segments))

        for i in range(self.n_segments):

            if ori == "v":
                posx = rel_pos * self.exp.p.field_size / 2
                posy = segment_offsets[i]
                pos = posx, posy
                aperture = self.segment_width, self.segment_length
            elif ori == "h":
                posy = segment_offsets[i]
                posy = rel_pos * self.exp.p.field_size / 2
                pos = posx, posy
                aperture = self.segment_length, self.segment_width

            stim = RandomDotMotion(self.exp.win,
                                   pos=pos,
                                   aperture=aperture,
                                   **self.dot_params)

            self.stims.append(stim)

    def reset(self):

        for stim in self.stims:
            stim.reset()

    def update(self, dirs, coh):

        for dir, stim in zip(dirs, self.stims):
            stim.update(dir, coh)

    def draw(self):

        for stim in self.stims:
            stim.draw()


def create_stimuli(exp):

    # Fixation point
    fix = Point(exp.win,
                exp.p.fix_pos,
                exp.p.fix_radius,
                exp.p.fix_trial_color)

    # Ensemble of random dot stimuli
    dots = DotBar(exp)

    return locals()


def generate_trials(exp):

    positions = itertools.cycle(np.linspace(-1, 1, 10))

    while True:

        yield pd.Series(dict(ori="v", pos=next(positions)))


def run_trial(exp, info):

    exp.s.dots.set_position(info.ori, info.pos)
    exp.s.dots.reset()

    for _ in range(120):

        exp.s.dots.update([0, 0, 180], .2)
        exp.draw(["dots", "fix"])

    return info
