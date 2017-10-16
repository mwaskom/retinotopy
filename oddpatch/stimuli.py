from __future__ import division
import numpy as np
from psychopy import visual
from scipy.spatial.distance import cdist
from visigoth.stimuli import ElementArray


class Patch(object):

    def __init__(self, win, patch_size,
                 element_size, element_tex, element_sf,
                 drift_rate):

        xys = poisson_disc_sample(patch_size * 2, element_size / 4)
        self.xys = xys
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
        self.array.pedestal_contrs = 1
        self.update_elements()

        a = np.deg2rad(np.r_[0:363:3, 360:-3:-3, 0])
        r = np.r_[np.full(121, 1.), np.full(121, 2.), [1.]]
        vertices = np.c_[np.cos(a) * r, np.sin(a) * r]
        self.edge = visual.ShapeStim(
            win,
            vertices=vertices,
            size=patch_size,
            fillColor=win.color,
            lineColor=win.color,
        )

    def update_pos(self, x, y):

        self.array.fieldPos = x, y
        self.edge.pos = x, y

    def update_elements(self, sf=None):
        # TODO copied from bar: abstract and standardize!
        n = len(self.xys)
        self.array.xys = np.random.permutation(self.array.xys)
        self.array.oris = np.random.uniform(0, 360, n)
        self.array.phases = np.random.uniform(0, 1, n)
        self.array.sfs = sf or self.element_sf

    def draw(self):

        self.array.phases += self.drift_step
        self.array.draw()
        self.edge.draw()


def poisson_disc_sample(size, radius=.5, candidates=20, seed=None):
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
            in_array = np.sqrt(x ** 2 + y ** 2) < (size / 2)
            in_ring = np.all(cdist(samples, [(x, y)]) > radius)

            if in_array and in_ring:
                # Accept the candidate
                samples.append((x, y))
                queue.append((x, y))
                break

        if (i + 1) == candidates:
            # We've exhausted the particular sample
            queue.pop(s_idx)

    return samples

