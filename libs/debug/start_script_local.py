""" To start Pipeline, run this script from maya's script editor or a shelf button
 Remember to alter the path below! """

import sys

path_to_pipeline = '/Users/liorbenhorin/Documents/Projects/2016/GitHub/pipeline2'
if not path_to_pipeline in sys.path:
    sys.path.append(path_to_pipeline)

import pipeline
# reload(pipeline)
pipeline.start()
