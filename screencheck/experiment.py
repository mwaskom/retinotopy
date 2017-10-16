from __future__ import division
import numpy as np
import pandas as pd
from psychopy import visual, event


def create_stimuli(exp):

    return locals()


def generate_trials(exp):

    yield {}


def run_trial(exp, info):

    colors = [u'#35193e', u'#701f57', u'#ad1759',
              u'#e13342', u'#f37651', u'#f6b48f']
    radii = [12, 10, 8, 6, 4, 2]

    for color, radius in zip(colors, radii):

        visual.Circle(
            exp.win,
            radius,
            128,
            fillColor=color,
            lineColor="white"
        ).draw()

        visual.Circle(
            exp.win,
            .5,
            128,
            pos=(radius - 1, 0),
            fillColor=exp.win.color,
            lineColor=exp.win.color,
        ).draw()

        visual.TextStim(
            exp.win,
            radius,
            pos=(radius - 1, 0),
            color="white",
            height=.75,
        ).draw()



    exp.win.flip()
    event.waitKeys(["return"])
