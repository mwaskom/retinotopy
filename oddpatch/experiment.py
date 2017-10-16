from __future__ import division
import numpy as np
import pandas as pd
from psychopy import event
from visigoth.stimuli import Point
from stimuli import Patch


def create_stimuli(exp):

    fix = Point(
        exp.win,
        exp.p.fix_pos,
        exp.p.fix_radius,
        exp.p.fix_color,
    )

    patch = Patch(
        exp.win,
        exp.p.patch_size,
        exp.p.element_size,
        exp.p.element_tex,
        exp.p.element_sf,
        exp.p.drift_rate,
    )

    return locals()


def generate_trials(exp):

    a, r = np.r_[0:360:30], [4, 7, 10]
    aa, rr = np.meshgrid(a, r)
    aa, rr = np.deg2rad(aa.ravel()), rr.ravel()
    xx, yy = np.cos(aa) * rr, np.sin(aa) * rr

    for x, y in zip(xx, yy):

        info = exp.trial_info(

            x=x,
            y=y,

        )

        yield pd.Series(info)


def run_trial(exp, info):

    exp.s.patch.update_pos(info.x, info.y)
    exp.wait_until(timeout=.5, draw=["patch", "fix"])
    exp.wait_until(timeout=.2, draw=["fix"])

    return info
