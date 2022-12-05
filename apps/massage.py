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

import os
import logging
import pipeline
from pipeline.libs import config as cfg
import pipeline.libs.misc as misc
import pipeline.libs.lic as lic
from pipeline.libs.Qt import QtCore, QtGui, QtWidgets
import pipeline.CSS
from pipeline.CSS import loadCSS
logger = logging.getLogger(__name__)


class PromptUser(QtWidgets.QMessageBox):
    def __init__(self, parent, title='oops!', prompt=None, override_yes_text=None, override_no_label=None,
                 override_cancel_label="Cancel", cancel_button=False, color=None, override_yes_icon=None,
                 override_no_icon=None, cancel_icon=None):
        super(PromptUser, self).__init__(parent)

        if not color:
            color = '#fff'

        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)

        self.setObjectName('prompt_massage')
        self.setStyleSheet(self.styleSheet() + ''' QLabel { color: ''' + color + ''' ;} ''')

        self.setWindowTitle(title)
        self.setText(prompt)
        self.setIconPixmap(cfg.simple_warning_icon)

        if override_yes_icon:
            self.yes_btn = QtWidgets.QPushButton(self)
            self.yes_btn.setText(override_yes_text)

            self.yes_btn.setMinimumHeight(30)
            self.yes_btn.setIconSize(QtCore.QSize(24, 24))

            self.yes_btn.setIcon(QtGui.QIcon(override_yes_icon))
            self.addButton(self.yes_btn, QtWidgets.QMessageBox.YesRole)
        else:
            self.addButton(override_yes_text, QtWidgets.QMessageBox.YesRole)

        if override_yes_icon:
            self.no_btn = QtWidgets.QPushButton(self)
            self.no_btn.setText(override_no_label)
            self.no_btn.setIcon(QtGui.QIcon(override_no_icon))
            self.addButton(self.no_btn, QtWidgets.QMessageBox.NoRole)

            self.no_btn.setMinimumHeight(30)
            self.no_btn.setIconSize(QtCore.QSize(24, 24))
        else:
            self.addButton(override_no_label, QtWidgets.QMessageBox.NoRole)

        # self.addButton(override_no_label, QtWidgets.QMessageBox.NoRole)

        if cancel_button:
            if cancel_icon:
                self.canc_btn = QtWidgets.QPushButton(self)
                self.canc_btn.setText(override_cancel_label)
                self.canc_btn.setIcon(QtGui.QIcon(cancel_icon))
                self.addButton(self.canc_btn, QtWidgets.QMessageBox.RejectRole)

                self.canc_btn.setMinimumHeight(30)
                self.canc_btn.setIconSize(QtCore.QSize(24, 24))
            else:
                self.addButton(override_cancel_label, QtWidgets.QMessageBox.RejectRole)

            # self.addButton(override_cancel_label, QtWidgets.QMessageBox.RejectRole)


# class PromptUser(QtWidgets.QMessageBox):
#     def __init__(self, parent, prompt=None,
#                  override_yes_text=None,
#                  override_no_label=None,
#                  override_cancel_label="Cancel",
#                  cancel_button=False):
#         super(PromptUser, self).__init__(parent)
#
#         self.setText(prompt)
#         self.setIconPixmap(cfg.simple_warning_icon)
#         # self.addButton(override_ok_text, QtWidgets.QMessageBox.AcceptRole)
#         # self.addButton(override_cance_label, QtWidgets.QMessageBox.RejectRole)
#         self.addButton(override_yes_text, QtWidgets.QMessageBox.YesRole)
#         self.addButton(override_no_label, QtWidgets.QMessageBox.NoRole)
#         if cancel_button:
#             self.addButton(override_cancel_label, QtWidgets.QMessageBox.RejectRole)
#


def warning(icon, title, message):
    if icon == "critical":
        dlg_icon = cfg.warning_icon
    elif icon == "warning":
        dlg_icon = cfg.simple_warning_icon
    else:
        dlg_icon = cfg.warning_icon

    reply = QtWidgets.QMessageBox()
    reply.setIconPixmap(dlg_icon)

    reply.setText(message)

    reply.setWindowTitle(title)
    css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
    reply.setStyleSheet(css)
    reply.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

    result = reply.exec_()
    if result == QtWidgets.QMessageBox.Yes:
        return True
    else:
        return False



class About(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setStyleSheet(cfg.stylesheet)
        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)
        self.setMaximumWidth(460)
        self.setMinimumWidth(460)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setMinimumHeight(260)
        self.setMaximumHeight(260)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20,20, 20)


        self.massage_widget = QtWidgets.QWidget(self)
        self.massage_layout = QtWidgets.QVBoxLayout(self.massage_widget)
        self.massage_layout.setContentsMargins(5, 5, 5, 5)

        self.logo_label = QtWidgets.QLabel(self)
        self.logo_label.setPixmap(cfg.logo_text_icon)
        self.massage_layout.addWidget(self.logo_label)

        self.spacer_label = QtWidgets.QLabel()
        self.spacer_label.setMinimumHeight(20)

        self.version_label = QtWidgets.QLabel()
        version = "Version {}".format(misc.version_string(pipeline.__version__))
        self.version_label.setText(version)

        self.owner_label = QtWidgets.QLabel()
        # import pipeline2_sb.libs.lic as lic
        license = lic.License_node.check_lic(pipeline.__version__)
        if license:
            owner = "Licensed to {}".format(lic.License_node(version=pipeline.__version__, encrypted=True).license_file["email"])
        else:
            owner = "Trial version"
        self.owner_label.setText(owner)

        self.link_label = Click_label()
        link = '''<a href='http://pipeline.nnl.tv'><font color=''' + cfg.colors.LIGHT_BLUE + '''>pipeline.nnl.tv</font></a>'''
        self.link_label.setText(link)

        font = QtGui.QFont()
        font.setBold(True)
        # font.setPointSize(13)
        self.link_label.setStyleSheet(''' QLabel { color: ''' + cfg.colors.LIGHT_BLUE + ''' ;} ''')
        self.link_label.setFont(font)

        self.massage_layout.addWidget(self.spacer_label)
        self.massage_layout.addWidget(self.version_label)
        self.massage_layout.addWidget(self.owner_label)
        self.massage_layout.addWidget(self.link_label)

        self.layout.addWidget(self.massage_widget)


        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        # buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        self.link_label.clicked.connect(self.launch_link)

    def launch_link(self):
        import webbrowser
        webbrowser.open('http://pipeline.nnl.tv/')

class Click_label(QtWidgets.QLabel):
    clicked = QtCore.Signal()

    def __init__(self):
        super(Click_label, self).__init__()

    def mouseReleaseEvent(self, e):
        logger.info(e)
        self.clicked.emit()
        e.accept()


class Prompt_alert(QtWidgets.QDialog):
    def __init__(self, parent=None, alert_string=""):
        super(Prompt_alert, self).__init__(parent)
        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)
        # self.setMaximumWidth(450)
        # self.setMinimumWidth(450)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # self.setMinimumHeight(150)
        # self.setMaximumHeight(150)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 5,20, 10)


        self.massage_widget = QtWidgets.QWidget(self)
        self.massage_layout = QtWidgets.QHBoxLayout(self.massage_widget)
        self.massage_layout.setContentsMargins(5, 5, 5, 5)

        self.prompt_icon = QtWidgets.QLabel(self)
        self.prompt_icon.setPixmap(cfg.warning_icon)
        self.massage_layout.addWidget(self.prompt_icon)


        self.alert_label = QtWidgets.QLabel()
        self.alert_label.setMargin(10)
        self.alert_label.setText(alert_string)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(13)
        self.alert_label.setStyleSheet(''' QLabel { color: ''' + cfg.colors.WARNING_RED + ''' ;} ''')
        self.alert_label.setFont(font)

        self.massage_layout.addWidget(self.alert_label)
        self.layout.addWidget(self.massage_widget)


        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)





def massage(icon, title, message, parent=None):
    reply = QtWidgets.QMessageBox(parent) if parent else QtWidgets.QMessageBox()

    if icon == "critical":
        reply.setIconPixmap(cfg.warning_icon)

    elif icon == "warning":
        reply.setIconPixmap(cfg.simple_warning_icon)

    elif icon == "massage":
        reply.setIconPixmap(cfg.massage_icon)

    else:
        reply.setIconPixmap(icon)

    css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
    reply.setStyleSheet(css)

    reply.setText(message)
    reply.setWindowTitle(title)
    reply.setStandardButtons(QtWidgets.QMessageBox.Close)

    result = reply.exec_()