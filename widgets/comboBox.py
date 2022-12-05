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
import pipeline.libs.config as cfg




def setComboValue(QComboBox, String):
    index = QComboBox.findText(String, QtCore.Qt.MatchFixedString)
    if index >= 0:
        QComboBox.setCurrentIndex(index)
        return True
    return False


class ComboWidget(QtWidgets.QWidget):
    def __init__(self,parent_layout=None,parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # super(ComboWidget, self).__init__(parent)

        self.setHidden(True)
        self._parent_layout = parent_layout

        # UI
        self.setMaximumHeight(60)
        self.setMinimumHeight(60)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        self.label = QtWidgets.QLabel()
        self.comboBox = QtWidgets.QComboBox(parent)
        self.comboBox.setIconSize(QtCore.QSize(24, 24))
        self.comboBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.comboBox.setStyleSheet(cfg.stylesheet)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.comboBox)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self._parent_layout.addWidget(self)
        self.setStyleSheet('''
            QComboBox::down-arrow {
            image:url(''' + cfg.light_down_arrow + ''');
            margin-right: 10px;
            }
            ''')
        # print cfg.down_arrow, '<<'
        # print cfg.light_down_arrow, '<<'
        # self.setStyleSheet('''
        #     QComboBox {
        #     border: 0px solid gray;
        #     border-radius: 15px;
        #     padding-left: 10px;
        #     background-color: ''' + cfg.colors.LIGHT_GRAY + ''';
        #     }
        #     QComboBox::drop-down {
        #     border: 0px solid gray;
        #     border-left: 2px solid ''' + cfg.colors.LIGHT_GRAY_minus + ''';
        #     border-radius: 15px;
        #     left: -10px;
        #     }
        #     QComboBox::hover {
        #     background-color: ''' + cfg.colors.LIGHT_GRAY_plus + ''';
        #     }
        #     QComboBox::down-arrow {
        #     image:url(''' + cfg.down_arrow + ''');
        #     left: 5px;
        #     }
        #     ''')

    def setLabel(self, text):
        self.label.setText(text)

    def remove(self):
        self.setParent(None)
        self.deleteLater()
        self._child = None
        del self