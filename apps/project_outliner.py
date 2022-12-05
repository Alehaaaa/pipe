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
import re

import pipeline.libs.config as cfg
import pipeline.widgets.gui as gui
import pipeline.widgets.inputs as inputs
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.CSS
from pipeline.CSS import loadCSS


logger = logging.getLogger(__name__)



class newNodeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, string="", name_label_string="", title=""):
        super(newNodeDialog, self).__init__(parent)
        # self.setStyleSheet(cfg.stylesheet)
        self.setMaximumWidth(400)
        self.setMinimumWidth(400)
        self.setMaximumHeight(50)

        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.input_widget = QtWidgets.QWidget(self)
        self.input_layout = QtWidgets.QVBoxLayout(self.input_widget)

        self.name_widget = inputs.GroupInput(self, label=name_label_string, inputWidget=QtWidgets.QLineEdit(self),
                                             ic=cfg.text_icon)

        self.name_input = self.name_widget.input
        self.name_input.setText(string)

        self.create_title = gui.Title(self, label=title)
        self.input_layout.addWidget(self.create_title)

        self.input_layout.addWidget(self.name_widget)

        self.layout.addWidget(self.input_widget)

        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(5, 5, 5, 10)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)


class create_options(object):

    @classmethod
    def __iter__(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__"))

    A_EMPTY = "Empty scene"
    B_FILE = "From File"
    C_SCENE = "From scene"
    D_SELECTION_ONLY = "From selection"
    E_SELECTION_ALL = "From selection - Include connections"
    F_NONE = "Do not create"



class New_branch_dialog(newNodeDialog):


    def __init__(self, parent=None, string="", name_label_sting="Name", title="Create new branch"):
        super(New_branch_dialog, self).__init__(parent, string, name_label_sting, title)

        self.name_input.textChanged.connect(self.name_changed)


    def name_changed(self, str):
        self.name_input.setStyleSheet("")

    def accept(self):

        m = re.match("^[a-zA-Z0-9_-]*$" , self.name_input.text())
        if not m:
            self.name_input.setStyleSheet("color: #CD5C5C;")
            logger.info("No special characters or whitespaces allowed")
        else:
            super(New_branch_dialog, self).accept()

    def result(self):
        res = {}
        res["name"] = self.name_input.text()
        return res





class newComponentDialog(newNodeDialog):


    def __init__(self, parent=None, string="", name_label_sting="Name", title="Create new Component", ansestors = []):
        super(newComponentDialog, self).__init__(parent, string, name_label_sting, title)

        ansestors = ansestors


        self.options_input_widget = inputs.GroupRadioInput(self, label = "Initial version", options = create_options(), ic=cfg.creation_icon)
        self.input_layout.addWidget(self.options_input_widget)

        self.version_file_type_input_widget = inputs.GroupRadioInput(self, label = "Version file type", options = ['mayaAscii', 'mayaBinary'], ic=cfg.settings_icon)
        self.input_layout.addWidget(self.version_file_type_input_widget)

        self.master_file_type_input_widget = inputs.GroupRadioInput(self, label = "Master file type", options = ['mayaAscii', 'mayaBinary'], ic=cfg.settings_icon)
        self.input_layout.addWidget(self.master_file_type_input_widget)

        self.name_format_widget = FormatWidget(self, name_input=self.name_input, ancestors=ansestors)
        self.input_layout.addWidget(self.name_format_widget)

        self.name_input.textChanged.connect(self.name_format_widget.preview_format)
        self.name_input.textChanged.connect(self.name_changed)



    def name_changed(self, str):
        self.name_input.setStyleSheet("")

    def accept(self):

        m = re.match("^[a-zA-Z0-9_-]*$" , self.name_input.text())
        if not m:
            self.name_input.setStyleSheet("color: #CD5C5C;")
            logger.info("No special characters or whitespaces allowed")
        else:
            super(newComponentDialog, self).accept()


    def file_type_parse(self, file_type_string):
        if file_type_string == 'mayaAscii': return 'ma'
        else: return 'mb'

    def result(self):
        res = {}
        res["name"] = self.name_input.text()
        res["format"] = self.name_format_widget.depth_slider.value()
        res["option"] = self.options_input_widget.option
        res["version_file_type"] = self.file_type_parse(self.version_file_type_input_widget.option)
        res["master_file_type"] = self.file_type_parse(self.master_file_type_input_widget.option)
        return res



class Rename_dialog(newNodeDialog):


    def __init__(self, parent=None, string="", name_label_sting="", current_name = "", title="", alert=None):
        super(Rename_dialog, self).__init__(parent, string, name_label_sting, title)

        self.name_input.setText(current_name)
        self.name_input.textChanged.connect(self.name_changed)

        if alert:
            self.alert_label = QtWidgets.QLabel()
            self.alert_label.setMargin(10)
            self.alert_label.setText(alert)
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(13)
            self.alert_label.setStyleSheet(''' QLabel { color: ''' + cfg.colors.WARNING_RED + ''' ;} ''')
            self.alert_label.setFont(font)
            self.input_layout.addWidget(self.alert_label)


    def name_changed(self, str):
        self.name_input.setStyleSheet("")

    def accept(self):

        m = re.match("^[a-zA-Z0-9_-]*$" , self.name_input.text())
        if not m:
            self.name_input.setStyleSheet('''color: ''' + cfg.colors.WARNING_RED + ''';''')
            logger.info("No special characters or whitespaces allowed")
        else:

            import pipeline.apps.massage as massage
            if massage.warning("critical","Warning","Proceed with rename?"):

                super(Rename_dialog, self).accept()
            else:
                super(Rename_dialog, self).reject()

    def result(self):
        res = {}
        res["name"] = self.name_input.text()
        return res




class newFolderDialog(newNodeDialog):
    def __init__(self, parent=None, string="", name_label_sting="Name", title="Create new Category"):
        super(newFolderDialog, self).__init__(parent, string, name_label_sting, title)

        self.input_range_widget = inputs.RangeInput(self, label="Range",
                                             ic=cfg.buffer_icon)

        self.range_start_slider = self.input_range_widget.start_input
        self.range_end_slider = self.input_range_widget.end_input
        self.range_step_slider = self.input_range_widget.step_input
        self.range_start_slider.setMinimum(1)
        self.range_start_slider.setMaximum(10000)
        self.range_start_slider.setValue(1)
        self.range_end_slider.setMinimum(1)
        self.range_end_slider.setMaximum(10000)
        self.range_end_slider.setValue(1)
        self.range_step_slider.setMinimum(1)
        self.range_step_slider.setMaximum(10000)
        self.range_step_slider.setValue(1)
        self.input_layout.addWidget(self.input_range_widget)

        self.range_start_slider.valueChanged.connect(self.editEndSliderMin)

        # self.input_quantity_widget = inputs.groupInput(self, label="Quantity", inputWidget=QtWidgets.QSpinBox(self),
        #                                         ic=cfg.buffer_icon)
        #
        # self.quantity_slider = self.input_quantity_widget.input
        # self.quantity_slider.setMinimum(1)
        # self.quantity_slider.setMaximum(1000)
        # self.quantity_slider.setValue(1)
        #
        # self.input_from_widget = inputs.groupInput(self, label="From", inputWidget=QtWidgets.QSpinBox(self),
        #                                     ic=cfg.tab_icon)
        #
        # self.from_slider = self.input_from_widget.input
        # self.from_slider.setMinimum(1)
        # self.from_slider.setMaximum(1000)
        # self.from_slider.setValue(1)

        self.input_padding_widget = inputs.GroupInput(self, label="Padding", inputWidget=QtWidgets.QSpinBox(self),
                                                      ic=cfg.counter_icon)

        self.padding_slider = self.input_padding_widget.input
        self.padding_slider.setMinimum(0)
        self.padding_slider.setMaximum(6)
        self.padding_slider.setValue(3)

        # self.input_layout.addWidget(self.input_quantity_widget)
        # self.input_layout.addWidget(self.input_from_widget)

        self.input_layout.addWidget(self.input_padding_widget)
        self.name_input.textChanged.connect(self.name_changed)

    def name_changed(self, str):
        self.name_input.setStyleSheet("")

    def accept(self):

        m = re.match("^[a-zA-Z0-9_-]*$" , self.name_input.text())
        if not m:
            self.name_input.setStyleSheet('''color: ''' + cfg.colors.WARNING_RED + ''';''')
            logger.info("No special characters or whitespaces allowed")
        else:
            super(newFolderDialog, self).accept()

    def editEndSliderMin(self):

        self.range_end_slider.setMinimum(self.range_start_slider.value())


    def result(self):
        res = {}
        res["name"] = self.name_input.text()
        quantity = (self.range_end_slider.value()+1) - self.range_start_slider.value()
        res["quantity"] = quantity
        res["from"] = self.range_start_slider.value()
        res["step"] = self.range_step_slider.value()
        res["padding"] = self.padding_slider.value()
        return res


class newAssetDialog(newFolderDialog):
    def __init__(self, parent=None, string="", name_label_sting="Name", title="Create new asset", stages=[],
                 ancestors=None, project=None):
        super(newAssetDialog, self).__init__(parent, string, name_label_sting, title)

        self.create_stages_title = gui.Title(self, label="Add stages:")
        self.input_layout.addWidget(self.create_stages_title)
        self.project = project

        self.stages_options = {}
        for stage in stages:
            widget = QtWidgets.QWidget(self)
            layout = QtWidgets.QVBoxLayout(widget)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setAlignment(QtCore.Qt.AlignLeft)
            checkbox = QtWidgets.QCheckBox(stage)
            self.stages_options[stage] = checkbox
            layout.addWidget(checkbox)
            self.input_layout.addWidget(widget)

        ancestors_names = []
        [ancestors_names.append("<{}>".format(node.name)) for node in ancestors]

        self.name_format_widget = NameFormatWidget(self, name_input=self.name_input, ancestors=ancestors_names,
                                                   project=self.project)
        self.input_layout.addWidget(self.name_format_widget)
        self.name_input.textChanged.connect(self.name_format_widget.preview_format)

    def result(self):


        res = {}
        res["name"] = self.name_input.text()
        quantity = (self.range_end_slider.value() + 1) - self.range_start_slider.value()
        res["quantity"] = quantity #self.quantity_slider.value()
        res["from"] = self.range_start_slider.value() #self.from_slider.value()
        res["padding"] = self.padding_slider.value()
        stages = {}
        for option in self.stages_options:
            stages[option] = self.stages_options[option].isChecked()  # {stage: bool}
        res["stages"] = stages
        res["name_format"] = self.name_format_widget.depth_slider.value()
        return res


class newStageDialog(newNodeDialog):
    def __init__(self, parent=None, string="", parent_name=None, name_label_sting="Name", title="Create new stage",
                 stages=[], ancestors=None, project=None):
        super(newStageDialog, self).__init__(parent, string, name_label_sting, title)

        self.project = project
        self.name_widget.setParent(None)
        self.name_widget.deleteLater()

        # self.create_stages_title = gui.Title(self, label = "Add stages:")
        # self.input_layout.addWidget(self.create_stages_title)

        self.stages_options = {}
        for stage in stages:
            widget = QtWidgets.QWidget(self)
            layout = QtWidgets.QVBoxLayout(widget)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setAlignment(QtCore.Qt.AlignLeft)
            checkbox = QtWidgets.QCheckBox(stage)
            self.stages_options[stage] = checkbox
            layout.addWidget(checkbox)
            self.input_layout.addWidget(widget)

        ancestors_names = []
        [ancestors_names.append("<{}>".format(node.name)) for node in ancestors]

        self.name_format_widget = NameFormatWidget(self, parent_name=parent_name, ancestors=ancestors_names,
                                                   project=self.project)
        self.input_layout.addWidget(self.name_format_widget)
        # self.name_input.textChanged.connect(self.name_format_widget.preview_format)

    def result(self):
        res = {}
        stages = {}
        for option in self.stages_options:
            stages[option] = self.stages_options[option].isChecked()  # {stage: bool}
        res["stages"] = stages
        res["name_format"] = self.name_format_widget.depth_slider.value()
        return res


class newTreeDialog(newFolderDialog):
    def __init__(self, parent=None, string="", name_label_sting="Name", title="Create new tree", stages=[],
                 project=None, section=None):
        super(newTreeDialog, self).__init__(parent, string, name_label_sting, title)
        self.project = project
        self.levels_names = self.project.levels[section]
        self.levels = []
        self.name_widget.label.setText("{} name".format(self.levels_names[0]))
        self.name_input.setText(self.levels_names[0])
        self.levels.append(
            [self.levels_names[0], self.name_input, self.range_start_slider, self.range_end_slider,  self.padding_slider])
        names = []
        for i in range(1, len(self.levels_names) - 1):
            names.append(self.levels_names[i])

        for level in names:
            name_widget = inputs.GroupInput(self, label=level, inputWidget=QtWidgets.QLineEdit(self),
                                            ic=cfg.text_icon)
            name_widget.label.setText("{} name".format(level))
            create_title = gui.Title(self, label=level)
            name_input = name_widget.input
            name_input.setText(level)
            self.input_layout.addWidget(create_title)
            self.input_layout.addWidget(name_widget)

            input_quantity_widget = inputs.GroupInput(self, label="Quantity", inputWidget=QtWidgets.QSpinBox(self),
                                                      ic=cfg.buffer_icon)

            quantity_slider = input_quantity_widget.input
            quantity_slider.setMinimum(1)
            quantity_slider.setMaximum(1000)
            quantity_slider.setValue(1)
            self.input_layout.addWidget(input_quantity_widget)

            # input_from_widget = inputs.groupInput(self, label="From", inputWidget=QtWidgets.QSpinBox(self),
            #                                ic=cfg.tab_icon)
            #
            # from_slider = input_from_widget.input
            # from_slider.setMinimum(1)
            # from_slider.setMaximum(1000)
            # from_slider.setValue(1)
            # self.input_layout.addWidget(input_from_widget)

            input_padding_widget = inputs.GroupInput(self, label="Padding", inputWidget=QtWidgets.QSpinBox(self),
                                                     ic=cfg.counter_icon)

            padding_slider = input_padding_widget.input
            padding_slider.setMinimum(0)
            padding_slider.setMaximum(6)
            padding_slider.setValue(3)
            self.input_layout.addWidget(input_padding_widget)
            self.levels.append([level, name_input, quantity_slider, padding_slider])

        self.create_stages_title = gui.Title(self, label="Add stages:")
        self.input_layout.addWidget(self.create_stages_title)
        self.project = project
        stages = self.project.stages[section]

        self.stages_options = {}
        for stage in stages:
            widget = QtWidgets.QWidget(self)
            layout = QtWidgets.QVBoxLayout(widget)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setAlignment(QtCore.Qt.AlignLeft)
            checkbox = QtWidgets.QCheckBox(stage)
            self.stages_options[stage] = checkbox
            layout.addWidget(checkbox)
            self.input_layout.addWidget(widget)

        ancestors = list(self.project.levels[section])
        ancestors = ancestors[:-1]

        self.name_format_widget = NameFormatWidget(self, multi_inputs=self.levels, ancestors=ancestors,
                                                   project=self.project)
        self.input_layout.addWidget(self.name_format_widget)

        for l in self.levels:
            l[1].textChanged.connect(self.name_format_widget.preview_format)
            l[3].valueChanged.connect(self.name_format_widget.preview_format)

    def result(self):
        res = {}
        levels = []
        for i in range(len(self.levels)):
            level = self.levels[i]
            if i == 0:
                quantity = (level[3].value() + 1) - level[2].value()
                fr = level[2].value()
                levels.append([level[0], level[1].text(), quantity, fr, level[4].value()])
            else:
                levels.append([level[0], level[1].text(), level[2].value(), 1, level[3].value()])

        res["levels"] = levels
        '''
        res["levels"] is a list with instruction for tree creation:
        [ [level_name, folder_name, padding, quantitiy] , ... for each level ]
        '''

        stages = {}
        for option in self.stages_options:
            stages[option] = self.stages_options[option].isChecked()  # {stage: bool}
        res["stages"] = stages
        res["name_format"] = self.name_format_widget.depth_slider.value()
        return res


class NameFormatWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, parent_name=None, name_input=None, multi_inputs=None, ancestors=None, project=None):
        super(NameFormatWidget, self).__init__(parent)

        self.project = project

        self.name_input = name_input
        self.multi_inputs = multi_inputs
        self.ancestors = ancestors
        self.parent_name = parent_name

        self.ancestors_names = ancestors

        if not multi_inputs:
            self.ancestors_names.reverse()
            self.ancestors_names.pop(0)

        self.max_depth = len(self.ancestors_names)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        self.file_name_title = gui.Title(self, label="File name format:")
        self.layout.addWidget(self.file_name_title)

        self.input_format_widget = inputs.GroupInput(self, label="Format Depth", inputWidget=QtWidgets.QSpinBox(self),
                                                     ic=cfg.counter_icon)

        self.depth_slider = self.input_format_widget.input
        self.depth_slider.setMinimum(0)
        self.depth_slider.setMaximum(self.max_depth)
        self.depth_slider.setValue(self.max_depth)

        self.format_preview_widget = inputs.GroupInput(self, inputWidget=QtWidgets.QLineEdit(self))
        self.format_preview = self.format_preview_widget.input
        self.format_preview.setEnabled(False)
        self.preview_format()

        self.layout.addWidget(self.input_format_widget)
        self.layout.addWidget(self.format_preview_widget)

        self.depth_slider.valueChanged.connect(self.preview_format)

    def pad_proxy(self, val):
        pad = ""
        for i in range(val):
            pad += "#"
        return pad

    def preview_format(self):
        levels = self.ancestors_names[-self.depth_slider.value():] if self.depth_slider.value() > 0 else []
        if self.name_input:
            new_name = "<{}>".format(self.name_input.text()) if self.name_input.text() else "<{}>".format("asset_name")
            levels.append(new_name)

        if self.multi_inputs:
            levels = []
            if self.depth_slider.value() > 0:
                for input in self.multi_inputs[-self.depth_slider.value():]:
                    text = input[1]
                    pad = input[3]
                    new_name = "<{}>".format(text.text()) if text.text() else "<{}>".format(self.pad_proxy(pad.value()))
                    levels.append(new_name)
            else:
                input = self.multi_inputs[-1]
                text = input[1]
                pad = input[3]
                new_name = "<{}>".format(text.text()) if text.text() else "<{}>".format(self.pad_proxy(pad.value()))
                levels.append(new_name)

        levels.append("<stage>")

        string = "_".join(levels)

        pad = self.pad_proxy(self.project.project_padding)

        final = "{0}_{1}_{2}{3}.{4}".format(self.project.prefix, string, "v", pad,
                                            "ma") if self.project.prefix else "{0}_{1}{2}.{3}".format(string, "v", pad,
                                                                                                      "ma")
        self.format_preview.setText(final)



class FormatWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, name_input = None, ancestors=[]):
        super(FormatWidget, self).__init__(parent)

        # self.project = project

        self.name_input = name_input
        self.ancestors = ancestors
        # self.ancestors_names = []
        # [self.ancestors_names.append("<{}>".format(a)) for a in ancestors]

        self.max_depth = len(self.ancestors)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        self.file_name_title = gui.Title(self, label="File name format: (Advanced) ")
        self.layout.addWidget(self.file_name_title)

        self.input_format_widget = inputs.GroupInput(self, label="Include categories", inputWidget=QtWidgets.QSpinBox(self),
                                                     ic=cfg.counter_icon)

        self.depth_slider = self.input_format_widget.input
        self.depth_slider.setMinimum(0)
        self.depth_slider.setMaximum(self.max_depth)

        if self.max_depth >= 1:
            self.depth_slider.setValue(1)
        else:
            self.depth_slider.setValue(self.max_depth)


        self.format_preview_widget = inputs.GroupInput(self, inputWidget=QtWidgets.QLineEdit(self))
        self.format_preview = self.format_preview_widget.input
        self.format_preview.setEnabled(False)
        self.preview_format()

        self.layout.addWidget(self.input_format_widget)
        self.layout.addWidget(self.format_preview_widget)

        self.depth_slider.valueChanged.connect(self.preview_format)

    def pad_proxy(self, val):
        pad = ""
        for i in range(val):
            pad += "#"
        return pad

    def preview_format(self):


        elements = self.ancestors[-self.depth_slider.value():] if self.depth_slider.value() > 0 else []

        if self.name_input:
            new_name = "{}".format(self.name_input.text()) if self.name_input.text() else "{}".format("[input name]")
            elements.append(new_name)


        string = "_".join(elements)

        pad = self.pad_proxy(3)

        final = "{}".format(string)
        self.format_preview.setText(final)


