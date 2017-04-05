from __future__ import division
import json
import itertools

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

        # Note that this code is written flexibly w.r.t number of segments but
        # it is being hardcoded at 3 here and not exposed in the params

        self.n_segments = n = 3
        segment_length = exp.p.field_size / n
        self.segment_length = segment_length - exp.p.bar_segment_gap
        self.segment_width = exp.p.bar_width
        offsets = np.linspace(-1, 1, n + 1) * (exp.p.field_size / 2)
        offsets = offsets[:-1] + (segment_length / 2)
        self.segment_offsets = offsets

    def set_position(self, ori, rel_pos):

        self.stims = []

        for i in range(self.n_segments):

            if ori == "v":
                posx = rel_pos * self.exp.p.field_size / 2
                posy = self.segment_offsets[i]
                pos = posx, posy
                aperture = self.segment_width, self.segment_length
            elif ori == "h":
                posx = self.segment_offsets[i]
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


def define_cmdline_params(self, parser):

    parser.add_argument("--schedule", required=True)


def generate_trials(exp):

    with open("schedules.json") as fid:
        schedules = json.load(fid)
        schedule = schedules[exp.p.schedule]

    mot_choices = list(itertools.combinations_with_replacement((0, 1), 3))

    for ori, dir in schedule:

        if dir == "p":
            positions = np.linspace(-1, 1, exp.p.traversal_steps)
        elif dir == "n":
            positions = np.linspace(1, -1, exp.p.traversal_steps)

        for step, pos in enumerate(positions, 1):

            mot_dirs = np.random.permutation(flexible_values(mot_choices))

            if ori == "h":
                dot_dirs = np.array([0, 180])[mot_dirs]
            elif ori == "v":
                dot_dirs = np.array([90, 270])[mot_dirs]

            odd_segment = np.unique(dot_dirs).size > 1

            info = exp.trial_info(

                bar_ori=ori,
                bar_dir=dir,
                bar_step=step,
                bar_pos=pos,

                dot_dirs=dot_dirs,
                odd_segment=odd_segment,

            )

            yield info


def run_trial(exp, info):

    exp.s.dots.set_position(info.bar_ori, info.bar_pos)
    exp.s.dots.reset()

    for _ in range(90):

        exp.s.dots.update(info.dot_dirs, .5)
        exp.draw(["dots", "fix"])

    return info
