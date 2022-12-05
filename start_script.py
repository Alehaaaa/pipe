'''
TO RUN PIPELINE FROM MAYA SCRIPT DIRECTORY:

1. Copy Pipeline folder into maya scripts directory*
2. Start maya and from the script editor - in a PYTHON tab - run this:

import pipeline
pipeline.start()

* If you don't know where is your maya scripts directory,
From the script editor - in a PYTHON tab - run this:

import maya.cmds as cmds
print cmds.internalVar(q = True, usd = True)

***************************************************************************

TO RUN PIPELINE FROM A DIFFERENT LOCATION:

1. Start maya and from the script editor - in a PYTHON tab - run this:


import sys

path_to_pipeline = '/Path/to/Pipeline/Folder'
if not path_to_pipeline in sys.path:
    sys.path.append(path_to_pipeline)

import pipeline
pipeline.start()

'''




