from __future__ import division
import json

import numpy as np
import pandas as pd

from psychopy import core, visual, event, data
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
        # Also note that hardcoding of 3 segments is baked into the trial
        # control code below; adapting the whole experiment to > 3 segments
        # will not be trivial

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
                posy = self.segment_offsets[::-1][i]
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

    def update(self, dirs, cohs):

        for dir, stim, coh in zip(dirs, self.stims, cohs):
            stim.update(dir, coh)

    def draw(self):

        for stim in self.stims:
            stim.draw()


def create_stimuli(exp):
    """Define stimulus objects."""
    # Fixation point
    fix = Point(exp.win,
                exp.p.fix_pos,
                exp.p.fix_radius,
                exp.p.fix_color)

    # Ensemble of random dot stimuli
    dots = DotBar(exp)

    return locals()


def define_cmdline_params(self, parser):
    """Choose the traversal schedule at runtime on command line."""
    parser.add_argument("--schedule", default="a")
    parser.add_argument("--init-coherence", default=.2, type=float)


def generate_trials(exp):

    # Load a file to determine the order of bar traversals
    # This lets us externally optimize/balance and repeat runs
    with open("schedules.json") as fid:
        schedules = json.load(fid)
        schedule = schedules[exp.p.schedule]

    # Define valid motion angles for each bar orientation
    ori_to_dir_map = dict(h=[0, 180], v=[90, 270])

    # Determine the length of each trial
    # (currently fixed across the run but useful to have here)
    trial_dur = exp.p.traversal_duration / exp.p.traversal_steps
    stim_dur = trial_dur - exp.p.wait_iti

    # Define a staircase to control coherence
    exp.staircase = data.StairHandler(np.log10(exp.p.init_coherence),
                                      nUp=exp.p.stair_n_up,
                                      nDown=exp.p.stair_n_down,
                                      nTrials=np.inf,
                                      maxVal=0,
                                      stepType="lin",
                                      stepSizes=exp.p.stair_step)

    # Outer iteration loop is over bar traversals
    # As specified by an orientation of the bar and a direction of its steps
    for ori, dir in schedule:

        # Define the step positions
        if dir == "p":
            positions = np.linspace(-1, 1, exp.p.traversal_steps)
        elif dir == "n":
            positions = np.linspace(1, -1, exp.p.traversal_steps)

        # Inner iteration loop is over steps within the traversal
        for step, pos in enumerate(positions, 1):

            # Increment the experiment trial counter
            exp.trial += 1

            # Define the coherence for this trial
            coherence=10 ** exp.staircase.next()

            # Determine the stimulus parameters for this trial
            odd_segment = flexible_values([0, 1, 2])
            trial_dirs = np.random.permutation(ori_to_dir_map[ori])
            dot_dirs = [trial_dirs[1] if i == odd_segment else trial_dirs[0]
                        for i in range(3)]

            info = exp.trial_info(

                bar_ori=ori,
                bar_dir=dir,
                bar_step=step,
                bar_pos=pos,

                dot_dirs=dot_dirs,
                odd_segment=odd_segment,
                odd_dir=dot_dirs[odd_segment],

                trial_dur=trial_dur,
                stim_dur=stim_dur,

                coherence=coherence,

                fix_broken=np.nan,

            )

            yield info


def run_trial(exp, info):

    # Set the position of the stimulus for this "trial"
    exp.s.dots.set_position(info.bar_ori, info.bar_pos)
    exp.s.dots.reset()

    # Pause for the inter-trial interval
    exp.wait_until(exp.iti_end, draw="fix", iti_duration=exp.p.wait_iti)

    # Initialize a clock to track RT
    trial_clock = core.Clock()

    # Keep track of whether the trial has had a fixation break
    fix_broken = False

    for i in exp.frame_range(seconds=info.stim_dur):

        # Pull relevant keypresses off the input buffer
        keys = event.getKeys(exp.p.key_names, timeStamped=trial_clock)

        # Only check responses after certain time has elapsed
        # and if there hasn't been a response in this trial
        check_keys = (trial_clock.getTime() > exp.p.wait_accept_resp
                      and not info["responded"])

        # Process keypresses
        if keys and check_keys:

            used_key, timestamp = keys[0]
            info["responded"] = True
            info["response"] = used_key
            info["rt"] = timestamp

            # Determine accuracy of the response
            if exp.p.key_names.index(used_key) == info.odd_segment:
                info[["correct", "result"]] = True, "correct"
            else:
                info[["correct", "result"]] = False, "wrong"

            # Change fixation point color to give feedback
            if exp.p.show_response_feedback:
                exp.show_feedback("fix", info.result)

        # TODO we should give feedback on fixation somehow
        # We don't want to end the trial as we normally would, but we
        # should provide some signal when the eye wanders too far outside
        # the fixation window. (While allowing blinks).
        # Currently doing a fixbreak click, but that's not helpful in scanner
        if not exp.check_fixation(allow_blinks=True) and not fix_broken:
            fix_broken = True
            exp.sounds.fixbreak.play()

        # Draw the next frame of the stimulus
        coherence = [0, 0, 0]
        coherence[info.odd_segment] = info.coherence
        exp.s.dots.update(info.dot_dirs, coherence)
        exp.draw(["dots", "fix"])

    # Reset the fixation color for the next trial
    exp.s.fix.color = exp.p.fix_color

    # Log fixation performance
    info["fix_broken"] = fix_broken

    # Update the staircase based on performance
    # TODO decide how we want to handle non-responses
    if info["responded"] and info["bar_step"] > 1:
        exp.staircase.addResponse(info["correct"])

    return info


def compute_performance(exp):
    """Determine average coherence on the final bar sweep."""
    df = pd.DataFrame(exp.trial_data)
    final_coh = df.iloc[-exp.p.traversal_steps:]["coherence"].mean()
    return final_coh,


def show_performance(exp, final_coh):
    """Report the coherence achieved at the end of the run."""
    lines = ["End of the run!", ""]

    null_values = None, np.nan
    if final_coh in null_values:
        visual.TextStim(exp.win, lines[0],
                        pos=(0, 0), height=.5).draw()
        exp.win.flip()
        return

    target_coh = exp.p.perform_coh_target

    if final_coh <= exp.p.init_coherence:
        verb = "got down"
    else:
        verb = "went up"

    lines.append(
        "You {} to {:.0%} signal".format(verb, final_coh)
        )
    if final_coh <= target_coh:
        lines.extend(["", "Great job!"])
    else:
        lines.extend(["", "Please try to be more accurate!"])

    n = len(lines)
    height = .5
    heights = (np.arange(n)[::-1] - (n / 2 - .5)) * height
    for line, y in zip(lines, heights):
        visual.TextStim(exp.win, line,
                        pos=(0, y), height=height).draw()
    exp.win.flip()
