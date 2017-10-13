from __future__ import division
import numpy as np
from psychopy import visual
from scipy.spatial.distance import cdist
from visigoth.stimuli import ElementArray


class RetBar(object):

    def __init__(self, win, field_size, bar_width,
                 element_size, element_tex, element_sf,
                 drift_rate):

        bar_length = field_size + 2 * element_size
        xys = poisson_disc_sample(bar_length, bar_width, element_size / 4)
        self.xys = xys
        self.edge_offset = bar_width / 2 + element_size / 2
        self.drift_step = drift_rate / win.framerate

        self.element_size = element_size
        self.element_tex = element_tex
        self.element_sf = element_sf

        self.array = ElementArray(

            win,
            xys=xys,
            nElements=len(xys),
            sizes=element_size,
            elementTex=element_tex,
            sfs=element_sf,

        )
        self.update_elements()

        self.edges = [
            visual.Rect(
                win,
                width=field_size,
                height=element_size,
                fillColor=win.color,
                lineWidth=0,
            )
            for _ in ["top", "bottom"]
        ]

    def update_pos(self, pos, angle):

        theta = np.deg2rad(angle)
        mat = np.array([[np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]])

        self.array.fieldPos = pos
        self.array.xys = mat.dot(self.xys.T).T
        self.edges[0].pos = np.add(pos, mat.dot([0, +self.edge_offset]))
        self.edges[1].pos = np.add(pos, mat.dot([0, -self.edge_offset]))
        self.edges[0].ori = -angle
        self.edges[1].ori = -angle

    def update_elements(self, sf=None):

        n = len(self.xys)
        self.array.xys = np.random.permutation(self.array.xys)
        self.array.oris = np.random.uniform(0, 360, n)
        self.array.phases = np.random.uniform(0, 1, n)

        if sf is None:
            sf = self.element_sf
        self.array.sfs = sf

    def draw(self):

        self.array.phases += self.drift_step
        self.array.draw()
        for edge in self.edges:
            edge.draw()


def poisson_disc_sample(length, width, radius=.5, candidates=20, seed=None):
    """Find positions using poisson-disc sampling."""
    # See http://bost.ocks.org/mike/algorithms/
    rs = np.random.RandomState(seed)
    uniform = rs.uniform
    randint = rs.randint

    # Start at a fixed point we know will work
    start = 0, 0
    samples = [start]
    queue = [start]

    while queue:

        # Pick a sample to expand from
        s_idx = randint(len(queue))
        s_x, s_y = queue[s_idx]

        for i in xrange(candidates):

            # Generate a candidate from this sample
            a = uniform(0, 2 * np.pi)
            r = uniform(radius, 2 * radius)
            x, y = s_x + r * np.cos(a), s_y + r * np.sin(a)

            # Check the three conditions to accept the candidate
            in_array = (0 < x < length) & (0 < y < width)
            in_ring = np.all(cdist(samples, [(x, y)]) > radius)

            if in_array and in_ring:
                # Accept the candidate
                samples.append((x, y))
                queue.append((x, y))
                break

        if (i + 1) == candidates:
            # We've exhausted the particular sample
            queue.pop(s_idx)

    # Remove first sample to give space around the fix point
    samples = np.array(samples)[1:]

    return samples - [(length / 2, width / 2)]

