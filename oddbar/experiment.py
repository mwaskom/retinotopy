import numpy as np
from psychopy import visual
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

    yield {}


def run_trial(exp, info):

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

    def steps(start, end, n):
        x = np.linspace(start[0], end[0], n)
        y = np.linspace(start[1], end[1], n)
        return np.stack([x, y], 1)

    step_pos = [
        steps(L, R, 16), steps(BR, C, 8), None,
        steps(T, B, 16), steps(BL, C, 8), None,
        steps(R, L, 16), steps(TL, C, 8), None,
        steps(B, T, 16), steps(TR, C, 8), None,
    ]

    step_angles = [
        90, 45, None,
        0, -45, None,
        90, 45, None,
        0, -45, None,
    ]

    blank_duration = 12  # TODO

    framerate = exp.win.framerate
    update_frames = set(np.arange(0,
                                  exp.p.step_duration * framerate,
                                  framerate / exp.p.update_rate))

    for pos_list, angle in zip(step_pos, step_angles):

        if pos_list is None:
            exp.wait_until(exp.check_abort, blank_duration, draw="fix")
            continue

        for pos in pos_list:

            exp.s.bar.update_pos(pos, angle)

            for frame, dropped in exp.frame_range(exp.p.step_duration,
                                                  yield_skipped=True):

                if frame in update_frames or any(update_frames & set(dropped)):
                
                    if np.random.rand() < exp.p.oddball_prob and frame:
                        sf = exp.p.oddball_sf
                    else:
                        sf = exp.p.element_sf
                    exp.s.bar.update_elements(sf)

                exp.draw(["bar", "ring", "fix"])

            exp.check_abort()
