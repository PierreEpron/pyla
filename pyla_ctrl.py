import os, sys, datetime, logging
from pathlib import *
from pyla import compute

bbox = (10, 10, 1910, 1070)
hsl_state = True

from_path = Path('images')
to_path = Path('results/results')

compute([x for x in from_path.glob('*.jpg')], bbox, hsl_state, to_path)

