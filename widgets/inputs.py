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


import pipeline.widgets.gui as gui
from pipeline.libs import config as cfg
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.CSS
from pipeline.CSS import loadCSS

logger = logging.getLogger(__name__)


class Toolbar():
    def __init__(self, parent, height, buttons = dict()):
        super(Toolbar, self).__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(2)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        _buttons = dict()
        for k in buttons:

            button = QtWidgets.QPushButton(buttons[k]['label'])
            button.setIconSize(QtCore.QSize(height-2, height-2))
            button.setIcon(QtGui.QIcon(buttons[k]['icon']))
            self.layout.addWidget(button)
            _buttons[k] = button





class GroupInput(QtWidgets.QWidget):
    def __init__(self, parent, label=None, inputWidget=None, ic=None):
        super(GroupInput, self).__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(2,2,2,2)
        self.layout.setSpacing(2)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)


        if isinstance(inputWidget, QtWidgets.QCheckBox):
            self.input = inputWidget
            self.input.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.input.setMinimumSize(QtCore.QSize(20, 0))
            self.layout.addWidget(self.input)
            ic = None
            if label:
                self.label = QtWidgets.QLabel(label)
                self.label.setMinimumSize(QtCore.QSize(100, 24))
                self.layout.addWidget(self.label)

            return
        else:
            if ic:
                self.icon = QtWidgets.QLabel()
                self.icon.setPixmap(ic)
                self.icon.setMaximumSize(QtCore.QSize(24, 24))
                self.icon.setMinimumSize(QtCore.QSize(24, 24))
                self.layout.addWidget(self.icon)

            if label:
                self.label = QtWidgets.QLabel(label)
                self.label.setMinimumSize(QtCore.QSize(100, 24))
                self.layout.addWidget(self.label)

            if inputWidget:
                self.input = inputWidget
                self.input.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                self.input.setMinimumSize(QtCore.QSize(0, 24))
                self.layout.addWidget(self.input)


class GroupRadioInput(QtWidgets.QWidget):
    def __init__(self, parent, label=None, options=None, ic=None):
        super(GroupRadioInput, self).__init__(parent)


        self.options = [option for option in options]
        self.option = self.options[0]

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        if ic:
            self.icon = QtWidgets.QLabel()
            self.icon.setPixmap(ic)
            self.icon.setMinimumSize(QtCore.QSize(24, 24))
            self.layout.addWidget(self.icon)
            self.icon.setAlignment(QtCore.Qt.AlignTop)


        if label:
            self.label = QtWidgets.QLabel(label)
            self.label.setMinimumSize(QtCore.QSize(100, 30))
            self.layout.addWidget(self.label)
            self.label.setAlignment(QtCore.Qt.AlignTop)


        self.options_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.options_widget)
        self.options_widget_layout = QtWidgets.QVBoxLayout(self.options_widget)


        self.options_radio_widgets = []

        for option in self.options:

            option_widget = QtWidgets.QRadioButton(option)

            self.options_radio_widgets.append( option_widget )
            self.options_widget_layout.addWidget(option_widget)
            option_widget.clicked.connect(self.selection)


        self.options_radio_widgets[0].setChecked(True)


    def selection(self):
        index = self.options_radio_widgets.index(self.sender())
        self.option = self.options[index]



class MultilineInput(QtWidgets.QDialog):
    def __init__(self, parent=None, caption = "", plainText=None):
        super(MultilineInput, self).__init__(parent)
        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)
        # self.setMaximumWidth(800)
        # self.setMinimumWidth(800)
        # self.setMaximumHeight(200)
        #
        # self.label = QtWidgets.QLabel()
        # self.label.setPixmap(cfg.edit_icon)
        #
        # self.label_Note = QtWidgets.QLabel(caption)
        # self.textNote = QtWidgets.QTextEdit(self)

        self.setMaximumWidth(800)
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.setMaximumHeight(200)

        self.label = QtWidgets.QLabel()
        self.label.setPixmap(cfg.edit_icon)

        self.label_Note = QtWidgets.QLabel(caption)

        self.textNote = QtWidgets.QTextEdit(self)
        self.textNote.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(gui.HLine())
        layout.addWidget(self.label_Note)
        layout.addWidget(self.textNote)


        ok = QtWidgets.QPushButton("Save")
        ok.setDefault(True)

        canc = QtWidgets.QPushButton("Cancel")


        buttons = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal)
        buttons.addButton(ok, QtWidgets.QDialogButtonBox.AcceptRole)
        buttons.addButton(canc, QtWidgets.QDialogButtonBox.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.textNote.setPlainText(plainText)

    def result(self):
        if self.textNote.toPlainText() == "":
            return ""
        return self.textNote.toPlainText()


class RangeInput(QtWidgets.QWidget):
    def __init__(self, parent, label=None,  ic=None):
        super(RangeInput, self).__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        if ic:
            self.icon = QtWidgets.QLabel()
            self.icon.setPixmap(ic)
            self.icon.setMinimumSize(QtCore.QSize(24, 24))
            self.layout.addWidget(self.icon)

        if label:
            self.label = QtWidgets.QLabel(label)
            self.label.setMinimumSize(QtCore.QSize(100, 30))
            self.layout.addWidget(self.label)

        self.from_label = QtWidgets.QLabel("From")
        # self.from_label.setMinimumSize(QtCore.QSize(100, 30))
        self.layout.addWidget(self.from_label)

        self.start_input = QtWidgets.QSpinBox(self)
        self.start_input.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.start_input.setMinimumSize(QtCore.QSize(0, 30))
        self.layout.addWidget(self.start_input)

        self.to_label = QtWidgets.QLabel("To")
        # self.to_label.setMinimumSize(QtCore.QSize(100, 30))
        self.layout.addWidget(self.to_label)

        self.end_input = QtWidgets.QSpinBox(self)
        self.end_input.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.end_input.setMinimumSize(QtCore.QSize(0, 30))
        self.layout.addWidget(self.end_input)


        self.step_label = QtWidgets.QLabel("Step")
        # self.to_label.setMinimumSize(QtCore.QSize(100, 30))
        self.layout.addWidget(self.to_label)

        self.step_input = QtWidgets.QSpinBox(self)
        self.step_input.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.step_input.setMinimumSize(QtCore.QSize(0, 30))
        self.layout.addWidget(self.step_input)


class QLabelButton(QtWidgets.QLabel):
    clicked = QtCore.Signal()
    '''
        custom QLbael the can send clicked signal
    '''

    def __init__(self, parent):
        QtWidgets.QLabel.__init__(self, parent)

        # color = cfg.colors.LIGHT_GRAY  # "#ccc"
        #
        # # self.setStyleSheet('''QLabel{
        # #     color: #ccc;
        # #     background-color: ''' + color + ''';
        # #     border-radius: 12px;
        # #     padding: 4px;
        # #     }
        # #     ''')

    def mouseReleaseEvent(self, ev):

        click = ev.pos()
        if self.mask().contains(click):
            self.clicked.emit()
            # self.emit(QtCore.SIGNAL('clicked()'))


class AlphaButton(QtWidgets.QWidget):
    alphaClick = QtCore.Signal()
    '''
        custom QLbael the can send clicked signal, only from the pixmap are that has 100% alpha
        used for the thumbnail transperent icon button
    '''

    def __init__(self, parent, alpha):
        QtWidgets.QWidget.__init__(self, parent)
        self.pixmap = alpha

        self.button = QLabelButton(self)
        # self.solid = QtGui.QPixmap(96,96)
        # self.solid.fill(QtGui.QColor(cfg.colors.LIGHT_PURPLE))

        self.button.setPixmap(self.pixmap)
        # self.button.setStyleSheet('''QLabel {
        # color: ''' + cfg.colors.LIGHT_PURPLE + ''';
        # }''')
        self.button.setScaledContents(True)
        self.button.setMask(self.pixmap.mask())
        self.button.clicked.connect(self.onClick)
        # self.connect(self.button, QtCore.SIGNAL('clicked()'), self.onClick)

    def onClick(self):
        self.alphaClick.emit()
        # self.emit(QtCore.SIGNAL('clicked()'))

    def set_pixmap(self, pixmap):

        self.button.setPixmap(pixmap)
        self.button.setScaledContents(True)
        self.button.setMask(pixmap.mask())



class NiceQPushButton(QtWidgets.QPushButton):

    def __init__(self, label = "", parent = None):
        QtWidgets.QPushButton.__init__(self, parent)

        self.setText(label)
        # dark = cfg.colors.DARK_GRAY
        # self.setStyleSheet(cfg.stylesheet)
        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)




class NiceQLabel(QtWidgets.QLabel):
    def __init__(self, label, parent = None, color = None, icon = None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setText(label)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        if icon:
            self.setPixmap(icon.scaled(16, 16))

        color = color if color else  cfg.colors.LIGHT_GRAY #"#ccc"

        self.setObjectName('nice_label')
        #
        # self.setStyleSheet('''QLabel{
        #     color: #ccc;
        #     background-color: ''' + color + ''';
        #     border-radius: 10px;
        #     padding: 4px;
        #     }
        #     ''')


# from PySide2 import QtWidgets, QtCore


class SearchLine(QtWidgets.QLineEdit):
    def __init__(self, parent, label = ""):
        super(SearchLine, self).__init__(parent)

        self.label = label
        self.setText(self.label)
        # self.setStyleSheet(cfg.stylesheet)
        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # color = cfg.colors.DARK_GRAY
        # self.setStyleSheet('''QLineEdit{
        #     color: #ccc;
        #     background-color: ''' + color + ''';
        #     border-radius: 15px;
        #     padding: 4px;
        #     }
        #     ''')

        # self.textChanged.connect(self.search_changed)
    def reset_label(self):
        self.setText(self.label)

    def focusOutEvent(self, e):
        if self.text() != "" and self.text() != self.label:
            super(SearchLine, self).focusOutEvent(e)
            e.accept()
            return

        self.reset_label()
        super(SearchLine, self).focusOutEvent(e)
        e.accept()
        return

    def focusInEvent(self, e):
        if self.text() == self.label:
            self.setText("")
            super(SearchLine, self).focusInEvent(e)
            e.accept()
            return

        super(SearchLine, self).focusInEvent(e)
        e.accept()
        return

    # def textChanged(self, *args, **kwargs):
    #     super(SearchLine, self).textChanged(args, kwargs)



class Completer_list_view(QtWidgets.QListView):
    def __init__(self, parent):
        super(Completer_list_view, self).__init__(parent)
        self.parent = parent


    def hideEvent(self, e):


        QtWidgets.QListView.hideEvent(self, e)
        e.accept()


        if len(self.parent.text()) > 0:
            self.parent.clearFocus()
            # self.parent.reset_label()

        # if len(self.parent.text()) == 0:
        #
        #     self.parent.reset_label()
        #     self.hide()
        return




class SuggestionSearchBar(SearchLine):
    def __init__(self, parent, label = "", suggestions_model = None):
        super(SuggestionSearchBar, self).__init__(parent, label)

        self.completer = QtWidgets.QCompleter(suggestions_model, self)
        self.completer.setPopup(Completer_list_view(self))
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        # self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setCompleter(self.completer)
        if suggestions_model:
            self.completer.setModel(suggestions_model)


    def focusInEvent(self, e):
        super(SuggestionSearchBar, self).focusInEvent(e)
        e.accept()
        self.completer.complete()
        return

    def set_suggestions_model(self, model = None):
        if model:
            self.completer.setModel(model)


class FileDialog(object):

    @staticmethod
    def get_file(caption = 'Open', filter = '*.*', dir = ''):
        import pymel.core as pm
        path = pm.fileDialog2(spe=False, caption = caption, dir = dir, fileFilter=filter, fm=1, dialogStyle=2)
        if path:
            return path[0]

        return None
