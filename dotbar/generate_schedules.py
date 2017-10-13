import json
import numpy as np


if __name__ == "__main__":

    schedules = {}

    letters = "abcde"

    orientations = ["v", "h"]
    directions = ["p" ,"n"]

    for name in letters:

        # TODO need to improve to actually optimize (or at least balance)
        # This is just a prototype to get the file existing
        ori = list(np.random.choice(orientations, 8))
        dir = list(np.random.choice(directions, 8))
        schedules[name] = list(zip(ori, dir))

    with open("schedules.json", "w") as fid:
        json.dump(schedules, fid)
        
