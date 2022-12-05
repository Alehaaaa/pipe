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
import os
import functools
logger = logging.getLogger(__name__)

import maya.cmds as cmds

import pipeline.libs.config as cfg
import pipeline.apps.pipeline_main as pipeline_main
import pipeline.apps.preset_editor as preset_editor
import pipeline.libs.updates as updates
import pipeline.libs.settings as settings
import pipeline.apps.playblast_settings as playblast_settings
import pipeline.apps.massage as massage
import pipeline.maya_libs.maya_qt as maya_qt

from pipeline.libs.Qt import QtWidgets


# global PIPELINE_WINDOW_OBJECT
# PIPELINE_WINDOW_OBJECT = None



def action_show_pipeline(*args):
    # global PIPELINE_WINDOW_OBJECT
    # PIPELINE_WINDOW_OBJECT = \
    maya_qt.dock_pipline_window(pipeline_main.pipeLineUI, maya_menu_items.PIPELINE_ACTIONS_MENU)

def action_toggle_pipeline_mode(*args):
    # global PIPELINE_WINDOW_OBJECT
    # if isinstance(PIPELINE_WINDOW_OBJECT, pipeline_main.pipeLineUI):
    #     PIPELINE_WINDOW_OBJECT.toggle_pipeline_mode()
    # else:
    #     massage.massage(cfg.information_icon, 'Pipeline', 'Pipline window needs to be open when toggling modes', parent=None)

    try:
        pipeline_win = pipeline_main.pipeLineUI.instances
        print pipeline_win
        if len(pipeline_win) == 1:
            pipeline_win[0].toggle_pipeline_mode()
        else:
            massage.massage(cfg.information_icon, 'Pipeline', 'Pipline window needs to be open when toggling modes',parent=None)
    except:
        massage.massage(cfg.information_icon, 'Pipeline', 'Pipline window needs to be open when toggling modes', parent=None)


def action_show_preset_manager(*args):
    # global PIPELINE_WINDOW_OBJECT

    # if isinstance(PIPELINE_WINDOW_OBJECT, pipeline_main.pipeLineUI):
    #     maya_qt.show(preset_editor.Preset_dialog, pipeline_window=PIPELINE_WINDOW_OBJECT)
    # else:
    maya_qt.show(preset_editor.Preset_dialog)

    # try:
    #     pipeline_win = pipeline_main.pipeLineUI.instances
    #     print pipeline_win
    #     if len(pipeline_win) == 1:
    #         pipeline_win[0].toggle_pipeline_mode()
    #     else:
    #         massage.massage(cfg.information_icon, 'Pipeline', 'Pipline window needs to be open when toggling modes',parent=None)
    # except:
    #     massage.massage(cfg.information_icon, 'Pipeline', 'Pipline window needs to be open when toggling modes', parent=None)
    #
    #

def action_show_playblast_options(*args):

    options = playblast_settings.Playblast_options(maya_qt.maya_main_window())
    result = options.exec_()
    res = options.result()

    if result == QtWidgets.QDialog.Accepted:

        settings_node = settings.settings_node()
        settings_node.playblast_compression = res["compression"]
        settings_node.playblast_format = res["format"]
        settings_node.playblast_hud = res["hud"]
        settings_node.playblast_scale = res["scale"]
        settings_node.playblast_offscreen = res["offscreen"]
        # settings_node.playblast_camera = res['camera']

        logger.info("Playblast settings changed:")
        for k, v in res.iteritems():
            logger.info("{} : {}".format(k, v))


def action_check_for_updates(*args):
    update = updates.Update_check_thread(silent=False)
    update.start()


def action_about_window(*args):
    about = massage.About(maya_qt.maya_main_window())
    about.exec_()


def reloadModule(name="pipeline", *args):

    module = __import__("pipeline", globals(), locals(), ["*"], -1)

    path = module.__path__[0]

    __reloadRecursive(path, "pipeline")

def __reloadRecursive(path, parentName):

    for root, dirs, files in os.walk(path, True, None):

        # parse all the files of given path and reload python modules
        for sfile in files:
            if sfile.endswith(".py"):

                if (not sfile.startswith('start_script')) and (not sfile.startswith('Qt')):



                    if sfile == "__init__.py":
                        name = parentName
                    else:
                        name = parentName+"."+sfile[:-3]

                    logger.info("reload : %s"%name)
                    try:
                        module = __import__(name, globals(), locals(), ["*"], -1)
                        reload(module)
                    except ImportError, e:
                        logger.error(e)
                        # for arg in e.args:
                        #     logger(arg, sev_error)
                    except Exception, e:
                        logger.error(e)
                        # for arg in e.args:
                        #     logger(arg, sev_error)

        # Now reload sub modules
        for dirName in dirs:
            if (not dirName == 'ehp') and (not dirName == 'requests') and (not dirName == 'send2trash') \
                        and (not dirName == 'scripts') and (not dirName == 'CSS'):
                __reloadRecursive(path+"/"+dirName, parentName+"."+dirName)
        break





class pipeline_main_menu(object):

    def __init__(self):

        self.create_menu()

    def create_menu(self):

        m = maya_menu_items

        for menu in cmds.lsUI(m=True):

            if menu.startswith(m.MAIN_MENU):

                cmds.deleteUI(menu)


        pipeline_menu =cmds.menu(m.MAIN_MENU, parent = maya_qt.gMainWindow(), label = 'Pipeline', tearOff = True)

        cmds.menuItem(parent=pipeline_menu, divider=True, label='Apps')
        cmds.menuItem(m.PIPELINE_WINDOW, parent=pipeline_menu,label='Pipeline window', c=action_show_pipeline)
        cmds.menuItem(m.PIPELINE_ACTIONS_MENU,subMenu = True, tearOff = True, parent=pipeline_menu, label='Pipeline actions')
        # cmds.menuItem(m.TOGGLE_MODE, parent = pipeline_menu, label ='Toggle pipeline mode',c = functools.partial(action_toggle_pipeline_mode, ))

        cmds.menuItem(parent=pipeline_menu, divider=True, label='Options')
        cmds.menuItem(m.PRESET_MANAGER, parent = pipeline_menu, label ='Presets manager', c = action_show_preset_manager)
        cmds.menuItem(m.PLAYBLAST_OPTIONS, parent = pipeline_menu,label ='Playblast options',c = action_show_playblast_options)

        cmds.menuItem(m.UPDATE_CHECK, parent = pipeline_menu,label ='Check for updates...', c = action_check_for_updates)
        cmds.menuItem(m.ABOUT, parent = pipeline_menu, label ='About Pipeline', c = action_about_window)

        cmds.menuItem(parent=pipeline_menu, divider=True, label ='Debug')
        cmds.menuItem(m.RELOAD, parent = pipeline_menu, label ='Reload pipeline', c = reloadModule)


class maya_menu_items(object):
    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    MAIN_MENU = 'pipeline_menu'
    PIPELINE_ACTIONS_MENU = 'pipeline_actions_menu'
    PIPELINE_WINDOW = 'pipline_show_window'
    PLAYBLAST_OPTIONS = 'pipeline_playblast_options'
    PRESET_MANAGER = 'pipeline_preset_manager'
    UPDATE_CHECK = 'pipeline_update_check'
    TOGGLE_MODE = 'pipeline_toggle_mode'
    ABOUT = 'pipeline_about'
    RELOAD = 'pipeline_reload'