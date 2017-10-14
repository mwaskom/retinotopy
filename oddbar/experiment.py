import numpy as np
import pandas as pd
from psychopy import visual, event
from visigoth.stimuli import Point
from stimuli import RetBar


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

    def steps(start, end, a, n):
        x = np.linspace(start[0], end[0], n)
        y = np.linspace(start[1], end[1], n)
        a = np.full(n, a, np.float)
        return np.stack([x, y, a], 1)

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
        steps(L, R, 90, 16), steps(BR, C, 45, 8), None,
        steps(T, B, 0, 16), steps(BL, C, -45, 8), None,
        steps(R, L, 90, 16), steps(TL, C, 45, 8), None,
        steps(B, T, 0, 16), steps(TR, C, -45, 8), None,
    ]

    yield steps


def run_trial(exp, info):

    framerate = exp.win.framerate

    frames_per_step = exp.p.step_duration * framerate
    frames_per_update = framerate / exp.p.update_rate
    update_frames = set(np.arange(0, frames_per_step, frames_per_update))

    steps = info
    stim_data = []

    for step in steps:

        if step is None:

            # TODO dimming fixation task during blank?
            exp.wait_until(exp.check_abort, exp.p.wait_blank, draw="fix")
            continue

        for x, y, a in step:

            exp.s.bar.update_pos(x, y, a)

            for frame, dropped in exp.frame_range(exp.p.step_duration,
                                                  yield_skipped=True):

                if frame in update_frames or any(update_frames & set(dropped)):
                
                    if np.random.rand() < exp.p.oddball_prob:
                        # TODO log times of these
                        # TODO or determine them above
                        sf = exp.p.oddball_sf
                    else:
                        sf = exp.p.element_sf
                    exp.s.bar.update_elements(sf)

                t = exp.draw(["bar", "ring", "fix"])
                if not frame:
                    stim_data.append((x, y, a, t))

            exp.check_abort()

    info = stim_data
    return info


def serialize_trial_info(exp, info):

    pass


def compute_performance(exp):

    return []


def save_data(exp):

    if exp.trial_data:
        stim = exp.trial_data[0]
        stim = pd.DataFrame(stim, columns=["x", "y", "a", "t"])
        out_stim_fname = exp.output_stem + "_stim.csv"
        stim.to_csv(out_stim_fname)


def show_performance(exp):

    exp.win.flip()
