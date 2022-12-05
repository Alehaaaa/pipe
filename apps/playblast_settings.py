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


import pipeline.libs.settings as settings
import pipeline.libs.config as cfg
import pipeline.widgets.gui as gui
import pipeline.widgets.inputs as inputs
import pipeline.maya_libs.maya_warpper as maya
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore



class Playblast_options(QtWidgets.QDialog):
    def __init__(self, parent = None):#, title = None, hud = True, offscreen = True, formats = None, format = "movie", compressions = None, compression = "H.264", scale = 50):
        super(Playblast_options, self).__init__(parent)

        self.setStyleSheet(cfg.stylesheet)

        title = "Playblast options"

        settings_node = settings.settings_node()

        hud = settings_node.playblast_hud
        offscreen = settings_node.playblast_offscreen
        format = settings_node.playblast_format
        compression = settings_node.playblast_compression
        scale = settings_node.playblast_scale
        # camera = settings_node.playblast_camera


        self.setMaximumWidth(400)
        self.setMinimumWidth(400)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # self.setMaximumHeight(50)


        layout = QtWidgets.QVBoxLayout(self)
        self.item_name = QtWidgets.QLabel(title)

        self.include_hud = QtWidgets.QCheckBox("Record HUD")
        self.include_hud.setChecked(hud)

        self.render_offscreen = QtWidgets.QCheckBox("Record Offscreen")
        self.render_offscreen.setChecked(offscreen)


        self.scaleLayout = QtWidgets.QHBoxLayout(self)

        self.scale_label = QtWidgets.QLabel("Scale:")

        self.scaleSlider = QtWidgets.QSlider()
        self.scaleSlider.setOrientation(QtCore.Qt.Horizontal)
        self.scaleSlider.setMinimum(10)
        self.scaleSlider.setMaximum(100)
        self.scaleSlider.setValue(scale)

        self.scaleSpinbox = QtWidgets.QSpinBox()
        self.scaleSpinbox.setMinimum(10)
        self.scaleSpinbox.setMaximum(100)
        self.scaleSpinbox.setValue(scale)

        self.scaleSlider.valueChanged.connect(self.sacle_spinbox_value)
        self.scaleSpinbox.valueChanged.connect(self.sacle_slider_value)


        self.scaleLayout.addWidget(self.scaleSpinbox)
        self.scaleLayout.addWidget(self.scaleSlider)

        self.input_ftm_widget = inputs.GroupInput(self, label="Format", inputWidget=QtWidgets.QComboBox(self),
                                                  ic=cfg.time_icon)

        self.ftm_input = self.input_ftm_widget.input
        self.ftm_input.setEditable(False)
        fmts = maya.getPlayblastFormat()#maya.getPlayblastOptions()["format"]
        self.ftm_input.addItems(fmts)
        # layout.addWidget(self.input_ftm_widget)
        i = self.ftm_input.findText(format, QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.ftm_input.setCurrentIndex(i)

        self.input_c_widget = inputs.GroupInput(self, label="Compression", inputWidget=QtWidgets.QComboBox(self),
                                                      ic=cfg.time_icon)

        self.c_input = self.input_c_widget.input
        self.c_input.setEditable(False)

        self.ftm_input.activated.connect(self.on_format_changed)
        self.on_format_changed()
        # cs = maya.getPlayblastOptions()["compression"]
        # self.c_input.addItems(cs)
        #
        i = self.c_input.findText(compression, QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.c_input.setCurrentIndex(i)


        #
        # self.input_cam_widget = inputs.GroupInput(self, label="Camera", inputWidget=QtWidgets.QComboBox(self),
        #                                           ic=cfg.camrea_icon)
        #
        # self.cam_input = self.input_cam_widget.input
        # self.cam_input.setEditable(False)
        # # fmts = maya.getPlayblastFormat()#maya.getPlayblastOptions()["format"]
        # self.cam_input.addItems(['Active camera', 'Render camera'])
        # # layout.addWidget(self.input_ftm_widget)
        # i = self.cam_input.findText(camera, QtCore.Qt.MatchFixedString)
        # if i >= 0:
        #     self.cam_input.setCurrentIndex(i)


        layout.addWidget(self.item_name)

        layout.addWidget(gui.HLine())
        layout.addWidget(self.include_hud)
        layout.addWidget(self.render_offscreen)
        layout.addWidget(self.scale_label)
        layout.addLayout(self.scaleLayout)
        layout.addWidget(self.input_ftm_widget)
        layout.addWidget(self.input_c_widget)
        # layout.addWidget(self.input_cam_widget)


        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)




    def sacle_spinbox_value(self,value):
        self.scaleSpinbox.setValue(value)

    def sacle_slider_value(self,value):
        self.scaleSlider.setValue(value)


    def result(self):
        res = {}
        hud = False
        offscreen = False

        if self.include_hud.isChecked():
            hud = True
        if self.render_offscreen.isChecked():
            offscreen = True

        res["hud"] = hud
        res["offscreen"] = offscreen
        res["format"] = self.ftm_input.currentText()
        res["compression"] = self.c_input.currentText()
        # res["camera"] = self.cam_input.currentText()
        res["scale"] = self.scaleSpinbox.value()

        return res


    def on_format_changed(self):
        '''

        This part is cloned from maya-capture-gui by Marcus Ottosson

        '''

        """Refresh the available compressions."""

        format = self.ftm_input.currentText()
        compressions = maya.getPlayblastCompression(format)
        self.c_input.clear()
        self.c_input.addItems(compressions)
