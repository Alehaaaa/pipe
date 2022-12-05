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


""" GLOBAL VARIABLES """
import os
import logging
from pipeline.libs.Qt import QtGui, QtWidgets


logger = logging.getLogger(__name__)

"""
@DEBUG: should be True when in development
"""

from uuid import getnode

try:
    node = getnode()
except:
    node = None

# logger.info(node)
# logger.info(type(node))

DEBUG = False
# if node == 105566145655362 or node == 154880080880118:
#     DEBUG = True


_master_ = "master"
_admin_ = "admin"
_catagory_ = "catagory"
_component_ = "component"
_branch_ = "branch"
_new_ = "new"
_node_ = "node"
_root_ = "root"
_stage_ = "stage" #**************
_asset_ = "asset" #**************
_folder_ = "folder"
_heirarchy_folder_ = "heirarchy_folder"
_heirarchy_component_ = "heirarchy_component"
_dummy_ = "dummy"
_version_ = "version"
_standard_ = "standard"
_playblast_ = "playblast"
_thumb_ = "thumb"
_thumbnails_ = "thumbnails"
_version_pfx_ = "v"
_public_version_pfx_ = "p"
_playblast_pfx_ = "playblast"
alembic = 'alembic'

def script_dir():
    import os
    return os.path.dirname(os.path.dirname(__file__))


class Hierarcy_options(object):

    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))


    SINGLE = "Single folder"
    MULTIPLE = "Multipe folders"
    ASK_USER = "[ user input ]"


class icons(object):

    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))


    icons_path = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'brand'))

    publish = QtGui.QPixmap(os.path.join(icons_path, "{}.svg".format("Cloud Filled")))
    HDD = QtGui.QPixmap(os.path.join(icons_path, "{}.svg".format("HDD")))


localIconPath = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons'))
localIconPathHD = os.path.normpath(os.path.join(localIconPath, 'hd'))

# save_icon = QtGui.QPixmap(os.path.join(localIconPathHD, "%s.svg" % "save"))
simple_add_icon = QtGui.QPixmap(os.path.join(localIconPathHD, "%s.svg" % "add"))
simple_rm_icon = QtGui.QPixmap(os.path.join(localIconPathHD, "%s.svg" % "rm"))
simple_up_icon = QtGui.QPixmap(os.path.join(localIconPathHD, "%s.svg" % "up"))
simple_dn_icon = QtGui.QPixmap(os.path.join(localIconPathHD, "%s.svg" % "dn"))

import pipeline.CSS
light_down_arrow = os.path.join(os.path.dirname(pipeline.CSS.__file__),'Images','down_arrow.png')


commit_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "Commit Git_48px"))
pr_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "Pull Request_48px"))
down_arrow = os.path.join(localIconPath, "%s.svg" % "down_arrow")
folder_icon = os.path.join(localIconPath, "%s.svg" % "folder")
folder_open_icon = os.path.join(localIconPath, "%s.svg" % "folder-open")
cube_icon = os.path.join(localIconPath, "%s.svg" % "cube")
cube_icon_full = os.path.join(localIconPath, "%s.svg" % "cube-fill")
trash_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "trash"))
# script_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "script"))
delete_folder_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "delete_folder"))
add_comment_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "add-comment"))
add_comment_icon_big = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "add-comment-big"))
comment_full_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "comment_full"))
add_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "add"))
master_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "save_master"))
creation_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "creation"))
new_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "new"))
client_icon = os.path.join(localIconPath, "%s.svg" % "client")
add_cube_icon = os.path.join(localIconPath, "%s.svg" % "add_cube")
dummy_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "braces"))

up_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "Up Filled"))
down_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "Down Filled"))

collapse_icon = os.path.join(localIconPath, "%s.svg" % "unfold-less")
expend_icon = os.path.join(localIconPath, "%s.svg" % "unfold-more")
offline_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "offline"))
catagory_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "catagory"))
asset_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "asset"))
component_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "component"))
delete_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "delete"))
load_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "load"))
unload_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "unload"))
project_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "project"))
key_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "Key"))
lock_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "Lock"))
users_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "users"))
settings_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "settings"))
set_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "set"))
yes_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "yes"))
no_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "no"))
search_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "search"))
edit_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "edit"))
new_folder_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "new_folder"))
open_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "open"))
save_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "save"))
save_master_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "save_master"))
down_arrow_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "down_arrow"))
import_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "import"))
export_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "export"))
help_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "help"))
anim_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "anim"))
asset_mode_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "asset_mode"))
reload_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "reload"))
shutter_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "shutter"))
camrea_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "camera"))
play_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "play"))
large_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "large"))
small_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "small"))
tab_icon = os.path.join(localIconPath, "%s.svg" % "tab")
link_on_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "link"))
link_off_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "link-off"))
branch_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "branch"))
square_file_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "square_file"))
binoculars_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "binoculars"))
cursor_outline_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "cursor-default-outline"))
square_file_outline_icon  = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "square_file_outline"))
square_file_multiple_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "square_file_multiple"))
information_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "information"))
logo_text_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "logo_plus_name"))
# large_image_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "large_image"))
large_image_icon_dark = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "large_image_dark"))
# large_image_icon_click = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "large_image_click"))
large_image_icon_click_dark = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "large_image_click_dark"))
wide_image_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "wide_image"))
wide_image_icon_click = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "wide_image_click"))
wide_image_icon_dark = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "wide_image_dark"))
wide_image_icon_click_dark = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "wide_image_click_dark"))
warning_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "critical"))
simple_warning_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "warning"))
massage_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "massage"))
archive_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "archive"))
logo = QtGui.QPixmap(os.path.join(localIconPath, "%s.png" % "pipeline_logo"))
time_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "time"))
buffer_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "buffer"))
counter_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "counter"))
text_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg" % "cursor-text"))



class colors(object):

    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    DARK_PURPLE = "#0269c9"#532C9C"
    DARK_GRAY_MINUS = "#202020"
    DARK_GRAY_MINUS_A = '#262626'
    DARK_GRAY = "#363636"
    LIGHT_GRAY_plus = "#656565"
    LIGHT_GRAY = "#555555"
    LIGHT_GRAY_minus = "#484848"
    LIGHT_BLUE = "#077fff"
    LIGHT_PURPLE = "#0183fc"#"#961bff"
    LIGHT_PURPLE_plus = '#4fa7f9' #"#A338FF"
    LIGHT_PURPLE_plus = '#4fa7f9'
    WARNING_RED = "#CD5C5C"

class Pipeline_navigation_mode(object):

    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    SUPER = 'supervisor'
    STANDARD = 'standard'

class playblast_save_options(object):

    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    PROJECT_ROOT = "project/"
    PROJECT_SISTER = "../project"
    COMPONENT = "component/"

class maya_menu_items(object):

    @classmethod
    def __iter__(cls):
        return(getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    MAIN_MENU = 'Pipeline'
    SAVE_VERSION = 'pipeline_save_version'
    SAVE_VERSION_FROM_FILE = 'pipeline_save_version_from_file'
    SAVE_VERSION_FROM_SELECTION = 'pipeline_save_version_from_selection'
    PUBLISH = 'pipeline_save_master'
    PLAYBLAST = 'pipeline_save_playblast'
    PLAYBLAST_OPTIONS = 'pipeline_playblast_options'
    PRESET_MANAGER = 'pipeline_preset_manager'
    UPDATE_CHECK = 'pipeline_update_check'
    TOGGLE_MODE = 'pipeline_toggle_mode'
    ABOUT = 'pipeline_about'


purple_button_stylesheet = '''QPushButton{
                                            background-color: ''' + colors.LIGHT_PURPLE + ''';
                                            border: 0px none;
                                            border-radius: 12px;
                                            padding: 0px;
                                            }
                                            QPushButton::hover{
                                            background-color: ''' + colors.DARK_PURPLE + ''';
                                            }
                                            QPushButton::pressed{
                                            background-color: ''' + colors.DARK_PURPLE + ''';
                                            }'''

table_button_stylesheet = '''
            QPushButton{
            border: 0px none;
            border-radius: 0px;
            border-bottom: 1px solid ''' + colors.LIGHT_GRAY + ''';
            background-color: ''' + colors.DARK_GRAY_MINUS_A + ''';
            }
            QPushButton::hover {
            background-color: ''' + colors.LIGHT_GRAY_plus + ''';
            }
            QPushButton::pressed {
            background-color: ''' + colors.LIGHT_GRAY_minus + ''';
            }
            '''

rounded_button_stylesheet = '''
    QPushButton {
    border: 0px none;
    border-radius: 12px;
    padding: 0px;
    text-align: center;
    background-color: ''' + colors.LIGHT_GRAY + ''';
    }
    QPushButton::hover {
    background-color: ''' + colors.LIGHT_GRAY_plus + ''';
    }
    QPushButton::pressed {
    background-color: ''' + colors.LIGHT_GRAY_minus + ''';
    }
'''

stylesheet = '''
    QListView{
    border: 0px;
    background-color: ''' + colors.DARK_GRAY_MINUS_A + ''';
    }
    QListView::item{
    border: 0px;
    padding-top: 2px;
    padding-left: 5px;
    }
    QListView::item::selected{
    border: 0px;
    background-color: ''' + QtWidgets.QApplication.topLevelWidgets()[0].palette().highlight().color().name() + ''';
    }
    QTableView{
    border: none;
    background-color: ''' + colors.DARK_GRAY_MINUS_A + ''';
    }
    QTableView::item{
    border: none;
    padding: 5px;
    border-bottom: 1px solid ''' + colors.LIGHT_GRAY + ''';
    }
    QTableView::item::focus{
    border: none;
    }
    QPushButton {
    border: 0px none;
    /*border-radius: 15px;*/
    padding: 5px;
    background-color: ''' + colors.LIGHT_GRAY + ''';
    }
    QPushButton::hover {
    background-color: ''' + colors.LIGHT_GRAY_plus + ''';
    }
    QPushButton::pressed {
    background-color: ''' + colors.LIGHT_GRAY_minus + ''';
    }
    QPushButton::menu-indicator{
    subcontrol-position: right center;
    subcontrol-origin: padding;
    left: -5px;
    }
    QDialogButtonBox > QPushButton {
    padding-top: 5%;
    padding-bottom: 5%;
    padding-left: 25%;
    padding-right: 25%
    }
    QLineEdit{
        color: #ccc;
        background-color: ''' + colors.DARK_GRAY_MINUS_A + ''';
        /*border-radius: 15px;*/
        padding-left: 10px;
        padding-right: 10px;
    }
    QTabWidget::pane{
        border: 0px none;
    }
    QTabBar::tab{
        left: -10px;
        border-top: 0px none;
        border-right: 0px none;
        border-left: 0px none;
        border-bottom: 2px solid ''' + colors.DARK_GRAY_MINUS_A + ''';
        padding: 6px;
        margin-left: 10px;
    }
    QTabBar::tab::selected, QTabBar::tab:hover{
        border-bottom: 2px solid ''' + colors.LIGHT_PURPLE + ''';
    }
    QComboBox {
    border: 0px solid gray;
    padding-left: 10px;
    background-color: ''' + colors.LIGHT_GRAY + ''';
    }
    QComboBox::drop-down {
    border: 0px solid gray;
    border-left: 2px solid ''' + colors.LIGHT_GRAY_minus + ''';
    left: -10px;
    }
    QComboBox::hover {
    background-color: ''' + colors.LIGHT_GRAY_plus + ''';
    }
    QComboBox::pressed {
    background-color: ''' + colors.LIGHT_GRAY + ''';
    }
    QComboBox::down-arrow {
    image: url(''' + down_arrow + ''');
    left: 5px;
    }
    QPlainTextEdit{
    color: #ccc;
    border: 0px none;
    background-color: ''' + colors.DARK_GRAY_MINUS_A + ''';
    padding-left: 5px;
    padding-right: 5px;
    padding-top: 5px;
    padding-bottom: 5px;
    }
    '''
# .replace("\\", "\\\\")
