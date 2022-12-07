'''

PIPELINE 2

Project manager for Maya

Ahutor: Lior Ben Horin
All rights reserved (c) 2017

pipeline.nnl.tv
liorbenhorin@gmail.com

---------------------------------------------------------------------------------------------

install:

Place the pipeline folder in your maya scripts folder and run this code (in python):

import pipeline
pipeline.start()

---------------------------------------------------------------------------------------------

You are using pipeline on you own risk.
Things can always go wrong, and under no circumstances the author
would be responsible for any damages caused from the use of this software.
When using this beta program you hereby agree to allow this program to collect
and send usage data to the author.

---------------------------------------------------------------------------------------------

The coded instructions, statements, computer programs, and/or related
material (collectively the "Data") in these files are subject to the terms
and conditions defined by
Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License:
   http://creativecommons.org/licenses/by-nc-nd/4.0/
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt

---------------------------------------------------------------------------------------------

'''


import logging
logger = logging.getLogger(__name__)

import maya.cmds as cmds

import pipeline.libs.settings as settings
import pipeline.libs.updates as updates
import pipeline.maya_libs.maya_gui as maya_gui


__version__ = (2,8,6)
__author__ = 'Lior Ben Horin'


def start():

    maya_gui.pipeline_main_menu()

    cmds.evalDeferred(lambda *args: maya_gui.action_show_pipeline())

    if settings.settings_node().check_for_updates:
        update = updates.Update_check_thread(silent=True)
        update.start()

