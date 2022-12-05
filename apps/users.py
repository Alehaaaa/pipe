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

from pipeline.libs import config as cfg
from pipeline.libs.Qt import QtWidgets, QtCore
from pipeline.widgets import gui as gui


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setStyleSheet(cfg.stylesheet)
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)
        self.setMaximumHeight(50)

        self.label = QtWidgets.QLabel()
        self.label.setPixmap(cfg.users_icon)

        self.label_user = QtWidgets.QLabel("Username:")
        self.label_password = QtWidgets.QLabel("Password:")

        self.textName = QtWidgets.QLineEdit(self)
        self.textName.setMinimumSize(QtCore.QSize(0, 30))
        self.textPass = QtWidgets.QLineEdit(self)
        self.textPass.setMinimumSize(QtCore.QSize(0, 30))

        self.textPass.setInputMethodHints(
            QtCore.Qt.ImhHiddenText | QtCore.Qt.ImhNoAutoUppercase | QtCore.Qt.ImhNoPredictiveText)
        self.textPass.setEchoMode(QtWidgets.QLineEdit.Password)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.label)
        layout.addWidget(gui.HLine())
        layout.addWidget(self.label_user)
        layout.addWidget(self.textName)
        layout.addWidget(self.label_password)
        layout.addWidget(self.textPass)

        log = QtWidgets.QPushButton("Login")
        log.setDefault(True)

        canc = QtWidgets.QPushButton("Cancel")

        buttons = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal)
        buttons.addButton(log, QtWidgets.QDialogButtonBox.AcceptRole)
        buttons.addButton(canc, QtWidgets.QDialogButtonBox.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def result(self):
        return self.textName.text(), self.textPass.text()