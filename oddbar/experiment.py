from __future__ import division
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

    event.clearEvents()

    framerate = exp.win.framerate

    frames_per_step = exp.p.step_duration * framerate
    frames_per_update = framerate / exp.p.update_rate
    update_frames = set(np.arange(0, frames_per_step, frames_per_update))

    oddballer = OddBall(exp.p.oddball_prob, exp.p.oddball_refract)

    stim_data = []
    task_data = []

    for _, step in info.iterrows():

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
                    exp.s.fix.color = exp.p.fix_bar_color
                else:
                    if oddball:
                        exp.s.fix.color = exp.p.fix_odd_color
                    else:
                        exp.s.fix.color = exp.p.fix_fix_color

            if step.bar:
                stims = ["bar", "ring", "fix"]
            else:
                stims = ["ring", "fix"]
            t = exp.draw(stims)

            if not frame:
                stim_data.append((t, step.bar, step.x, step.y, step.a))

                if oddball:
                    kind = "bar" if step.bar else "fix"
                    task_data.append((t, kind))

            exp.check_abort()

    keys = event.getKeys([exp.p.key], timeStamped=exp.clock)
    task_data.extend([(t, "key") for (_, t) in keys])

    stim_cols = ["onset", "bar", "x", "y", "a"]
    stim_data = pd.DataFrame(stim_data, columns=stim_cols)

    task_cols = ["time", "event"]
    task_data = pd.DataFrame(task_data, columns=task_cols)

    return stim_data, task_data


def serialize_trial_info(exp, info):

    return pd.Series(dict(correct=np.nan, responded=True, rt=0)).to_json()


def compute_performance(exp):

    if exp.trial_data:

        _, task = exp.trial_data[0]

        oddballs = task.query("event in ['bar', 'fix']")
        responses = task.query("event == 'key'")

        hits = 0
        misses = 0
        false_alarms = 0

        for t in oddballs["time"]:

            closest = (responses.time - t).min()
            if 0 < closest < exp.p.response_window:
                hits += 1
            else:
                misses += 1

        for t in responses["time"]:

            closest = (t - oddballs.time).min()
            if not 0 < closest < exp.p.response_window:
                false_alarms += 1

    else:

        hits = misses = false_alarms = None

    return hits, misses, false_alarms


def save_data(exp):

    if exp.trial_data:

        stim, task = exp.trial_data[0]

        out_stim_fname = exp.output_stem + "_stim.csv"
        stim.to_csv(out_stim_fname, index=False)

        out_task_fname = exp.output_stem + "_task.csv"
        task.to_csv(out_task_fname, index=False)


def show_performance(exp, hits, misses, false_alarms):

    exp.win.flip()

    lines = ["End of the run!"]

    null_values = None, np.nan
    if hits in null_values:
        visual.TextStim(exp.win, lines[0],
                        pos=(0, 0), height=.5).draw()
        exp.win.flip()
        return

    hit_s = "" if hits == 1 else "s"
    false_alarm_s = "" if false_alarms == 1 else "s"
    lines.extend([
        "",
        "You detected {} oddball{}, missed {}".format(hits, hit_s, misses),
        "and had {} false alarm{}!".format(false_alarms, false_alarm_s),
        ])

    if lines:
        n = len(lines)
        height = .5
        heights = (np.arange(n)[::-1] - (n / 2 - .5)) * height
        for line, y in zip(lines, heights):
            visual.TextStim(exp.win, line,
                            pos=(0, y), height=height).draw()
        exp.win.flip()
