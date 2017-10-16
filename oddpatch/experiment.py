from __future__ import division
import numpy as np
import pandas as pd
from psychopy import core, event, visual
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

    # Set up the grid of positions
    a, r = np.r_[0:360:30], [4, 7, 10]
    aa, rr = np.meshgrid(a, r)
    aa, rr = np.deg2rad(aa.ravel()), rr.ravel()
    xys = np.c_[np.cos(aa) * rr, np.sin(aa) * rr]

    # Set up the iti timing
    counts = [12, 9, 6, 4, 3, 2]
    durations = np.arange(0, 6 * exp.p.iti_unit, exp.p.iti_unit)
    iti = np.concatenate([
        np.full(c, d) for c, d in zip(counts, durations)
    ])

    # Set up oddballs
    oddball = np.zeros(36)
    oddball[:exp.p.oddballs] = 1

    # Randomize trials
    xx, yy = np.random.permutation(xys).T
    iti[1:] = np.random.permutation(iti[1:])
    oddball = np.random.permutation(oddball)

    # Compute expected stimulus offset
    trial_duration = iti + exp.p.stim_duration + exp.p.resp_duration
    should_offset = trial_duration.cumsum() - exp.p.resp_duration

    # Combine into one data structure
    trials = pd.DataFrame(dict(
        x=xx,
        y=yy,
        a=aa,
        r=rr,
        iti=iti,
        oddball=oddball.astype(bool),
        should_offset=should_offset,
    ))

    for _, t in trials.iterrows():

        info = exp.trial_info(
            stim_onset=np.nan,
            **t.to_dict()
        )

        yield pd.Series(info)


def run_trial(exp, info):

    # Update stimulus
    exp.s.patch.update_pos(info.x, info.y)

    # Inter-trial interval
    exp.wait_until(exp.iti_end, draw="fix", iti_duration=info.iti)

    # Stimulus period
    framerate = exp.win.framerate
    frames_per_stim = exp.p.stim_duration * framerate
    frames_per_update = framerate / exp.p.update_rate
    update_frames = set(np.arange(0, frames_per_stim, frames_per_update))

    trial_clock = core.Clock()
    event.clearEvents()

    stim_offset = info.should_offset
    for frame, dropped in exp.frame_range(exp.p.stim_duration,
                                          expected_offset=stim_offset,
                                          yield_skipped=True):

        if frame in update_frames or any(update_frames & set(dropped)):
            sf = exp.p.oddball_sf if info.oddball else exp.p.element_sf
            exp.s.patch.update_elements(sf)

        t = exp.draw(["patch", "fix"])
        if not frame:
            trial_clock.reset()
            info["stim_onset"] = t

    # Post-stimulus period
    resp_offset = info.should_offset + exp.p.resp_duration
    for frame in exp.frame_range(exp.p.resp_duration,
                                 expected_offset=resp_offset):
        exp.draw("fix")

    # Check responses
    keys = event.getKeys([exp.p.key], timeStamped=trial_clock)
    if keys:
        _, rt = keys[0]
        info["responded"] = True
        info["rt"] = rt
        info["correct"] = bool(info.oddball)
    else:
        info["responded"] = False
        info["correct"] = not info.oddball

    return info


def compute_performance(exp):

    if exp.trial_data:

        trials = pd.DataFrame(exp.trial_data)

        oddball = trials.oddball.fillna(0).astype(bool)
        responded = trials.responded.fillna(0).astype(bool)

        print(oddball)
        print(responded)

        hits = (oddball & responded).sum()
        misses = (oddball & ~responded).sum()
        false_alarms = (~oddball & responded).sum()

    else:

        hits = misses = false_alarms = None

    return hits, misses, false_alarms


def show_performance(exp, hits, misses, false_alarms):

    # TODO copied from oddbar
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
        "You detected {} oddball{}, missed {},".format(hits, hit_s, misses),
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
