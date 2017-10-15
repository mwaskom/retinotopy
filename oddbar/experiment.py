import numpy as np
import pandas as pd
from psychopy import visual, event
from visigoth.stimuli import Point
from stimuli import RetBar


class OddBall(object):

    def __init__(self, p, r):

        self.p = p
        self.r = r
        self._rs = np.random.RandomState()
        self._calls_since_true = 0

    def __call__(self):

        self._calls_since_true += 1
        if self._calls_since_true < self.r:
            return False
        elif self._rs.rand() > self.p:
            return False
        else:
            self._calls_since_true = 0
            return True


def create_stimuli(exp):

    exp.win.allowStencil = True

    aperture = visual.Aperture(
        exp.win,
        exp.p.field_size
    )

    fix = Point(
        exp.win,
        exp.p.fix_pos,
        exp.p.fix_radius,
        exp.p.fix_color
    )

    # TODO incorporate fixation drift warning for training?
    ring = Point(
        exp.win,
        exp.p.fix_pos,
        exp.p.fix_radius * 1.5,
        exp.win.color,
    )

    bar = RetBar(
        exp.win,
        exp.p.field_size,
        exp.p.bar_width,
        exp.p.element_size,
        exp.p.element_tex,
        exp.p.element_sf,
        exp.p.drift_rate,
    )

    return locals()


def generate_trials(exp):

    def steps(bar, n, start=None, end=None, a=None):
        if bar:
            b = np.ones(n)
            x = np.linspace(start[0], end[0], n)
            y = np.linspace(start[1], end[1], n)
            a = np.full(n, a, np.float)
        else:
            b = np.zeros(n)
            x = y = a = np.full(n, np.nan)
        return np.stack([b, x, y, a], 1)

    field_radius = exp.p.field_size / 2
    diag = np.cos(np.pi / 4) * field_radius

    L = -field_radius, 0
    R = +field_radius, 0
    T = 0, +field_radius
    B = 0, -field_radius
    TL = -diag, +diag
    TR = +diag, +diag
    BL = -diag, -diag
    BR = +diag, -diag
    C = 0, 0

    steps = [
        steps(True, 16, L, R, 90), steps(True, 8, BR, C, 45), steps(False, 8),
        steps(True, 16, T, B, 0), steps(True, 8, BL, C, -45), steps(False, 8),
        steps(True, 16, R, L, 90), steps(True, 8, TL, C, 45), steps(False, 8),
        steps(True, 16, B, T, 0), steps(True, 8, TR, C, -45), steps(False, 8),
    ]

    dur = exp.p.step_duration
    steps = np.concatenate(steps, 0)
    steps = pd.DataFrame(steps, columns=["bar", "x", "y", "a"])
    steps["offset"] = np.arange(len(steps)) * dur + dur

    yield steps


def run_trial(exp, info):

    # Everything is done in one "trial" for simplicity, though note that
    # this means no data are saved if the experiment crashes/is aborted.

    framerate = exp.win.framerate

    frames_per_step = exp.p.step_duration * framerate
    frames_per_update = framerate / exp.p.update_rate
    update_frames = set(np.arange(0, frames_per_step, frames_per_update))

    steps = info
    stim_data = []

    oddballer = OddBall(exp.p.oddball_prob, exp.p.oddball_refract)

    task_data = []

    for _, step in steps.iterrows():

        if step.bar:
            exp.s.bar.update_pos(step.x, step.y, step.a)

        for frame, dropped in exp.frame_range(exp.p.step_duration,
                                              expected_offset=step.offset,
                                              yield_skipped=True):

            if frame in update_frames or any(update_frames & set(dropped)):

                oddball = oddballer()

                if step.bar:
                    sf = exp.p.oddball_sf if oddball else exp.p.element_sf
                    exp.s.bar.update_elements(sf)

            if step.bar:
                t = exp.draw(["bar", "ring", "fix"])
            else:
                t = exp.draw(["ring", "fix"])

            if not frame:
                stim_data.append((t, step.bar, step.x, step.y, step.a))

                if oddball:
                    task_data.append((t, "bar"))

            exp.check_abort()

    info = stim_data, task_data
    return info


def serialize_trial_info(exp, info):

    pass


def compute_performance(exp):

    return []


def save_data(exp):

    if exp.trial_data:

        stim, task = exp.trial_data[0]

        stim = pd.DataFrame(stim, columns=["onset", "bar", "x", "y", "a"])
        out_stim_fname = exp.output_stem + "_stim.csv"
        stim.to_csv(out_stim_fname, index=False)

        task = pd.DataFrame(task, columns=["time", "event"])
        out_task_fname = exp.output_stem + "_task.csv"
        task.to_csv(out_task_fname, index=False)


def show_performance(exp):

    exp.win.flip()
