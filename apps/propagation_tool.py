""" This module holds the class for the propagtion tool ui """
#
# import logging
# import os
#
# import pipeline.apps.toolBox as toolBox
# import pipeline.libs.config as cfg
# import pipeline.libs.data as dt
# import pipeline.libs.files as files
# import pipeline.libs.nodes.assets as assets
# import pipeline.libs.views as views
# import pipeline.widgets.gui as gui
# import pipeline.widgets.inputs as inputs
# from pipeline.libs.Qt import QtWidgets, QtCore
#
# if cfg._dev:
#     reload(cfg)
#     reload(dt)
#     reload(views)
#     reload(files)
#     reload(toolBox)
#     reload(inputs)
#
# logger = logging.getLogger(__name__)
#
#
# class PropagateWindow(QtWidgets.QDialog):
#     def __init__(self, parent=None):
#         super(PropagateWindow, self).__init__(parent)
#
#         self.setMaximumWidth(1000)
#         self.setMinimumWidth(600)
#
#         self.buttons = QtWidgets.QDialogButtonBox(
#             QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
#             QtCore.Qt.Horizontal, self)
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)
#         self.ready(False)
#
#
#         self.dynamicCombo = None
#         self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint)
#         self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
#
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.setContentsMargins(5, 5, 5, 10)
#
#
#         self.main_widget = QtWidgets.QWidget(self)
#         self.main_layout = QtWidgets.QVBoxLayout(self.main_widget)
#         self.main_layout.setContentsMargins(0,0,0,0)
#         layout.addWidget(self.main_widget)
#
#         self.main_title = gui.Title(self, label="Propagte shot tool")
#         self.main_layout.addWidget(self.main_title)
#
#         self.name_widget = inputs.GroupInput(self.main_widget, label="Prefix", inputWidget=QtWidgets.QLineEdit(self),
#                                              ic=cfg.text_icon)
#
#         self.name_input = self.name_widget.input
#         self.name_input.setText("")
#
#         self.main_layout.addWidget(self.name_widget)
#
#         self.input_range_widget = inputs.RangeInput(self.main_widget, label="Range",
#                                                                     ic=cfg.buffer_icon)
#
#         self.range_start_slider = self.input_range_widget.start_input
#         self.range_end_slider = self.input_range_widget.end_input
#         self.range_start_slider.setMinimum(1)
#         self.range_start_slider.setMaximum(10000)
#         self.range_start_slider.setValue(1)
#         self.range_end_slider.setMinimum(1)
#         self.range_end_slider.setMaximum(10000)
#         self.range_end_slider.setValue(1)
#         self.main_layout.addWidget(self.input_range_widget)
#
#
#         self.create_stages_title = gui.Title(self, label="Add stages:")
#         self.main_layout.addWidget(self.create_stages_title)
#
#         stages = cfg.stages[cfg._animation_]
#
#         self.stages_options = {}
#         for stage in stages:
#             widget = QtWidgets.QWidget(self)
#             layout_ = QtWidgets.QVBoxLayout(widget)
#             layout_.setContentsMargins(5, 2, 5, 2)
#             layout_.setAlignment(QtCore.Qt.AlignLeft)
#             checkbox = QtWidgets.QCheckBox(stage)
#             checkbox.setChecked(True)
#             self.stages_options[stage] = checkbox
#             layout_.addWidget(checkbox)
#             self.main_layout.addWidget(widget)
#
#         self.path_caption = gui.Title(self, label="Sequence selection:")
#         self.main_layout.addWidget(self.path_caption)
#
#
#         self.navigation_widget = QtWidgets.QWidget(self.main_widget)
#         self.navigation_layout = QtWidgets.QHBoxLayout(self.navigation_widget)
#         self.navigation_layout.setContentsMargins(5, 0, 5, 0)
#         self.dynamic_path = None
#
#         self.main_layout.addWidget(self.navigation_widget)
#
#         self.navigation_layout.setAlignment(QtCore.Qt.AlignLeft)
#         if self.parent().project:
#
#             if isinstance(self.dynamicCombo, toolBox.SimpleComboDynamicWidget):
#                 self.dynamicCombo.remove()
#                 self.dynamicCombo = None
#
#             dir = os.path.join(self.parent().project.path)
#
#             self.dynamicCombo = toolBox.SimpleComboDynamicWidget(
#                 settings=self.parent().settings,
#                 project=self.parent().project,
#                 path=dir,
#                 box_list=[],
#                 parent_box=None,
#                 parent_layout=self.navigation_layout,
#                 parent=self.parent(),
#                 dialouge = self,
#                 whitelist=[cfg._animation_])
#
#             self.name_format = None
#             if self.parent()._stageNode:
#                 elements = files.relpath_wrapper(self.parent()._stageNode._path, self.parent().project.path).split(os.sep)
#                 logger.info(self.parent().project.path)
#                 logger.info(self.parent()._stageNode._path)
#                 logger.info(elements)
#                 self.dynamicCombo.navigate(elements)
#                 self.name_format = self.parent()._stageNode.name_format
#
#                 name = self.parent()._stageNode.parent().name
#                 padding = self.parent().project.project_padding
#                 if files.is_number(name[-padding:]):
#                     name = name[:-padding]
#                 self.name_input.setText(name)
#
#             layout.addWidget(self.buttons)
#
#
#     def ready(self, bool):
#         logger.info("ready {}".format(bool))
#         self.buttons.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool)
#
#     def result(self):
#         if not self.name_format:
#             elements = files.relpath_wrapper(self.dynamic_path, self.parent().project.path).split(os.sep)
#             self.name_format = len(elements)
#
#         res = {}
#         res["name"] = self.name_input.text()
#         quantity = (self.range_end_slider.value() + 1) - self.range_start_slider.value()
#         res["quantity"] = quantity
#         res["from"] = self.range_start_slider.value()
#         res["padding"] = self.parent().project.project_padding
#         stages = {}
#         for option in self.stages_options:
#             stages[option] = self.stages_options[option].isChecked()
#         res["stages"] = stages
#         res["name_format"] = self.name_format
#         try:
#             parent =  assets.AssetNode(os.path.split(self.dynamic_path)[1], parent=None, path = self.dynamic_path,
#                                        project=self.parent().project,
#                                        settings=self.parent().settings, pipelineUI=self.parent(), section=cfg._animation_)
#
#             return res, parent
#         except:
#             logger.info("could not init asset node in {}".format(self.dynamic_path))