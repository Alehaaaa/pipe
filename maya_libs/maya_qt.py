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
import maya.mel as mel

import maya.OpenMayaUI as omui
import pipeline
import pipeline.maya_libs.maya_warpper as maya

from pipeline.libs.Qt import QtGui, QtWidgets, QtCore

try:
    from shiboken import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance


PIPELINE_WORKSPACE_CONTROL = 'pipeline_workspcae_control'
PIPELINE_ACTIONS_MENU = 'pipeline_actions_menu'
COMPONENT_EXPLORER_CONTROL = 'components_explorer_control'


def gShelfTopLevel():
    return mel.eval("$tempVar = $gShelfTopLevel")

def gMainWindow():
    return mel.eval("$tempVar = $gMainWindow")

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def show(dialog, *args, **kwargs):
    try:
        for c in maya_main_window().children():
            if isinstance(c, dialog):
                c.setParent(None)
                c.deleteLater()
    except:
        pass


    # logger.info(kwargs)

    window = dialog( maya_main_window(), **kwargs)
    window.show()

def dock_pipline_window(dialog, menu, *args):


    try:
        cmds.deleteUI(PIPELINE_WORKSPACE_CONTROL)
        logger.info('removed workspace {}'.format(PIPELINE_WORKSPACE_CONTROL))

    except:
        pass


    if maya.maya_api_version() >= 201700:

        main_control = cmds.workspaceControl(PIPELINE_WORKSPACE_CONTROL, ttc=["AttributeEditor", -1],
                                             iw=425, mw=True, wp='preferred',
                                                label = 'Pipeline - {}'.format(pipeline.__version__))
        # cmds.workspaceControl(main_control, e=True, rs=True)


        control_widget = omui.MQtUtil.findControl(PIPELINE_WORKSPACE_CONTROL)
        control_wrap = wrapInstance(long(control_widget), QtWidgets.QWidget)
        control_wrap.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        win = dialog(control_wrap, control_wrap.layout(), PIPELINE_WORKSPACE_CONTROL, menu)

        cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

    else:

        pipeline_window = cmds.window(width=425, sizeable=True)

        # self.ui_window = pm.window(GUIDE_UI_WINDOW_NAME, width=panelWeight, title="Guide Tools", sizeable=True)
        # self.ui_topLevelColumn = pm.columnLayout()

        # pipeline_form = cmds.columnLayout(parent=pipeline_window, adjustableColumn=True, columnAlign="center")
        pipeline_form = cmds.paneLayout( configuration = 'single')
        # pipeline_form = cmds.paneLayout( configuration='single', parent=pipeline_window)
        # cmds.formLayout(pipeline_form,e=True, adj=True)
        # cmds.columnLayout(pipeline_form, e=True, adj=True)

        dockControl = cmds.dockControl(PIPELINE_WORKSPACE_CONTROL, allowedArea=['right', 'left'], area='right', label = 'Pipeline - {}'.format(pipeline.__version__),
                                       content=pipeline_window, width=425, s=True)#, retain=False)
        # cmds.dockControl(dockControl, e=True, r=True)



        control_widget = omui.MQtUtil.findControl(PIPELINE_WORKSPACE_CONTROL)
        control_wrap = wrapInstance(long(control_widget), QtGui.QWidget)
        control_wrap.setAttribute(QtCore.Qt.WA_DeleteOnClose)


        # window_widget = omui.MQtUtil.findWindow(pipeline_window)
        window_wrap = wrapInstance(long(control_widget), QtGui.QDialog)
        # This is the main widget
        widget = window_wrap.children()[5]
        layout = window_wrap.children()[5].children()[0]

        win = dialog(widget, layout, PIPELINE_WORKSPACE_CONTROL, menu)

        cmds.evalDeferred(lambda *args: cmds.dockControl(dockControl, e=True, r=True))
        # control_wrap.raise_()

    return win.run()


