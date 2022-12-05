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

from pipeline.libs.Qt import QtGui, QtWidgets, QtCore, QtCompat



def HLine():
    toto = QtWidgets.QFrame()
    toto.setFrameShape(QtWidgets.QFrame.HLine)
    toto.setFrameShadow(QtWidgets.QFrame.Sunken)
    return toto


class Title(QtWidgets.QWidget):
    def __init__(self, parent, label="Input", seperator = True, size = [60,20]):
        super(Title, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.setSpacing(5)
        self.label = QtWidgets.QLabel(label)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.label.setMinimumSize(QtCore.QSize(size[0], size[1]))

        self.layout.addWidget(self.label)

        if seperator:
            self.layout.addWidget(HLine())
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


class WidgetLayout(QtWidgets.QWidget):
    def __init__(self, parent=None, layout=None):
        super(WidgetLayout, self).__init__(parent)

        self.layout = layout
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        # self.layout.setAlignment(QtCore.Qt.AlignLeft)


class Tabs(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Tabs, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.layout.addWidget(self.tab_widget)
        self.layout.setContentsMargins(5, 5, 5, 10)

    def setCurrentIndex(self, index):
        self.tab_widget.setCurrentIndex(index)
        # self.tab_widget.setIconSize(QtCore.QSize(16,16))


# class Progress_window(QtWidgets.QDialog):
#     def __init__(self, parent=None, title='', caption='', min=0, max=100):
#         super(Progress_window, self).__init__(parent)
#         # self.setStyleSheet(cfg.stylesheet)
#         self.setMaximumWidth(300)
#         self.setMinimumWidth(300)
#         self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
#
#         self.setMinimumHeight(80)
#         self.setMaximumHeight(80)
#
#         self.layout = QtWidgets.QVBoxLayout(self)
#         self.layout.setContentsMargins(10, 10, 10, 10)
#
#         self.title = Title(self, label=caption, seperator=False)
#         self.title.setMaximumHeight(30)
#         self.layout.addWidget(self.title)
#
#         self.progress_bar = QtWidgets.QProgressBar()
#         self.progress_bar.setMinimum(min)
#         self.progress_bar.setMaximum(max)
#         self.progress_bar.setValue(0)
#         self.layout.addWidget(self.progress_bar)
#
#     def setValue(self, value):
#         self.progress_bar.setValue(value)