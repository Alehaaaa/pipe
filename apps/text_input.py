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

import pipeline.libs.config as cfg
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.widgets.inputs as inputs

logger = logging.getLogger(__name__)



class TextBox(QtWidgets.QPlainTextEdit): #(QtWidgets.QTextEdit):
    text_saved = QtCore.Signal(str)

    def __init__(self, parent, text = ""):
        super(TextBox, self).__init__(parent)

        self.setStyleSheet(cfg.stylesheet)


        # self.layout = QtWidgets.QHBoxLayout(self)
        # self.layout.setContentsMargins(0,0,0,0)
        #
        # self.text_box = QtWidgets.QPlainTextEdit()
        # self.layout.addWidget(self.text_box)

        self.setStyleSheet(cfg.stylesheet)

        self._original_text = text
        # self.setPadding(5)
        self._changed = False
        # self.setText(self._original_text)

        font = QtGui.QFont()
        font.setItalic(True)
        font.setBold(True)
        self.setFont(font)



        self.commit_button = inputs.NiceQPushButton(parent=self)#QtWidgets.QPushButton(self, "Save")
        # self.commit_button.setPixmap(cfg.yes_icon)
        self.commit_button.setIconSize(QtCore.QSize(12, 12))
        self.commit_button.setIcon(QtGui.QIcon(cfg.yes_icon))
        # self.commit_button.setText("Save")
        # self.commit_button.setMinimumHeight(20)

        self.discard_button = inputs.NiceQPushButton(parent=self) #QtWidgets.QPushButton(self, "Save")
        # self.discard_button.setText("Discard")
        # self.discard_button.setMinimumHeight(20)
        self.discard_button.setIconSize(QtCore.QSize(12, 12))
        self.discard_button.setIcon(QtGui.QIcon(cfg.no_icon))

        self.viewport_VLayout = QtWidgets.QVBoxLayout(self)
        self.viewport().setLayout(self.viewport_VLayout)
        self.viewport_VLayout.setContentsMargins(0,0,0,0)
        self.viewport_VLayout.setAlignment(QtCore.Qt.AlignBottom)

        self.input_panel = QtWidgets.QWidget(self)
        self.input_panel_layout = QtWidgets.QHBoxLayout(self.input_panel)
        self.input_panel_layout.setContentsMargins(2,2,2,2 )
        self.input_panel_layout.setSpacing(5)
        self.input_panel_layout.setAlignment(QtCore.Qt.AlignRight)

        self.input_panel_layout.addWidget(self.commit_button)
        self.input_panel_layout.addWidget(self.discard_button)


        self.commit_button.clicked.connect(self.save_text)
        self.discard_button.clicked.connect(self.restore_text)



        self.icon_widget = QtWidgets.QWidget()
        self.icon_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.icon_widget_layout = QtWidgets.QVBoxLayout(self.icon_widget)
        self.icon_widget_layout.setContentsMargins(0,0,0,0)
        self.icon_widget_layout.setAlignment(QtCore.Qt.AlignTop)
        self.icon_label_widget = QtWidgets.QLabel()
        self.icon_label_widget.setPixmap(cfg.add_comment_icon)
        self.icon_widget_layout.addWidget(self.icon_label_widget)
        self.viewport_VLayout.addWidget(self.icon_widget)

        self.viewport_VLayout.addWidget(self.input_panel)
        self.textChanged.connect(self.text_edit)


        self.setText(self._original_text)
        self.panel_hide(True)

        # color = cfg.colors.DARK_GRAY
        # self.setStyleSheet('''QTextEdit{
        #     color: #ccc;
        #     border: 0px none;
        #     background-color: ''' + color + ''';
        #     }
        #     ''')



    def setText(self, text):
        super(TextBox, self).setPlainText(text)
        # logger.info("set text")
        self.icon_visiblity()

    def icon_visiblity(self):

        text = self.toPlainText()
        # logger.info("icon")
        # logger.info(text)
        if text == "":
            # logger.info("unhide")
            self.icon_widget.setHidden(False)

        else:
            # logger.info("hide")
            self.icon_widget.setHidden(True)


    def focusInEvent(self, e):
        self.icon_widget.setHidden(True)
        QtWidgets.QPlainTextEdit.focusOutEvent(self, e)
        # super(TextBox, self).focusInEvent(e)

    def focusOutEvent(self, e):
        self.icon_visiblity()
        QtWidgets.QPlainTextEdit.focusOutEvent(self, e)
        # super(TextBox, self).focusOutEvent(e)


    def set_orig_text(self, str):
        self._original_text = str
        self.restore_text()


    def text_edit(self):
        self._changed = True
        self.panel_hide(False)

    def save_text(self):
        self.panel_hide(True)
        text = self.toPlainText()
        self._original_text = text
        self.text_saved.emit(text)
        self.clearFocus()

    def restore_text(self):
        self.setPlainText(self._original_text)
        self.panel_hide(True)
        self.clearFocus()
        self.icon_visiblity()

    def panel_hide(self, bool):
        self.input_panel.setHidden(bool)

