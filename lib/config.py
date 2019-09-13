import json
import os

with open(os.environ['CONFIG']) as json_data:
    conf = json.load(json_data)