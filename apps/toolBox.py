# import logging
# import os
#
# import pipeline.libs.config as cfg
# import pipeline.libs.data as dt
# import pipeline.libs.files as files
# import pipeline.libs.misc as misc
# import pipeline.libs.models as models
# import pipeline.libs.nodes.assets as assets
# import pipeline.libs.nodes.stages as stages
# import pipeline.widgets.comboBox as comboBox
# #
# if cfg._dev:
#     reload(cfg)
#     reload(dt)
#     reload(models)
#     reload(files)
#     # reload(serializer)
#     reload(comboBox)
#     reload(misc)
#     reload(stages)
#     reload(assets)
#
# logger = logging.getLogger(__name__)
#
#
# class ComboStaticWidget(comboBox.ComboWidget):
#     def __init__(self,
#                  settings=None,
#                  items=None,
#                  parent_layout=None,
#                  parent=None, **kwargs):
#
#         super(ComboStaticWidget, self).__init__(parent_layout, parent)
#
#         self.parent = parent
#         self._settings = settings
#         self._items = items
#         self._model = None
#         self.createModel()
#         self.setHidden(False)
#
#
#     def createModel(self):
#
#
#         li = []
#         [li.append(dt.DummyNode(i)) for i in sorted(self._items)]
#         li.insert(0, dt.CatagoryNode("stage"))
#
#         self.setLabel("stage")
#
#         self.comboBox.setModel(models.List_Model(li))
#         self.comboBox.currentIndexChanged.connect(self.update)
#
#     def update(self):
#         self._settings.stage = self.comboBox.currentText()
#
#         try:
#             self.parent.dynamicCombo._box_list[-1].scan_directory()
#         except:
#             pass
#
# class ComboDynamicWidget(comboBox.ComboWidget):
#     def __init__(self,
#                  settings=None,
#                  project=None,
#                  path=None,
#                  box_list=[],
#                  parent_box=None,
#                  parent_layout=None,
#                  parent=None
#                  ):
#
#         super(ComboDynamicWidget, self).__init__(parent_layout, parent)
#
#         # Local and init calls
#         self.parent = parent
#         self._settings = settings
#         self._project = project
#         self._parent_box = parent_box
#         self._parent_layout = parent_layout
#         self._box_list = box_list
#         self._box_list.append(self)
#         self._stage = None
#         self._subdirectories = None
#         self._path = None
#         self._child = None
#         self._model = None
#         self._level = "dir"
#
#         if path:
#             self._path = path
#             self.listDirectory()
#
#         self.createModel()
#         self.comboBox.currentIndexChanged.connect(self.update)
#         self.setHidden(False)
#
#     def navigate(self, items):
#         try:
#             current = self
#             for i in range(0, len(items)):
#                 if comboBox.setComboValue(current.comboBox, items[i]):
#                     current.update()
#                     current = current._child
#         except:
#             logger.info("can not complete navigation to {}".format(items))
#
#     def listDirectory(self):
#         dir = self._path
#         dirs = files.list_dir_folders(dir)
#
#         if dirs:
#             self._subdirectories = dirs
#
#         return
#
#     def createModel(self):
#
#         li = [dt.CatagoryNode("<{}>".format(self._level))]
#
#         self.setLabel(self._level)
#
#         if self._level != "n/a":
#             if self._subdirectories:
#                 for dir in sorted(self._subdirectories):
#                     n = os.path.split(dir)[1]
#                     li.append(dt.FolderNode(n, settings=self.parent.settings, path=os.path.join(self._path, dir)))
#
#         self.comboBox.setModel(models.List_Model(li))
#
#
#     def addChild(self, path):
#
#         if files.list_dir_folders(path):
#             widget = ComboDynamicWidget(
#                 settings=self._settings,
#                 project=self._project,
#                 path=path,
#                 box_list=self._box_list,
#                 parent_box=self,
#                 parent_layout=self._parent_layout,
#                 parent=self.parent)
#             self._child = widget
#
#     def update(self):
#
#         self.removeChild()
#         scan = self.stageScan()
#
#         if scan is not True:
#             '''
#             if the folder is a stage folder don't list it and return True
#             '''
#             self.addChild(scan)
#             logger.info("adding")
#             return
#
#         logger.info("not adding")
#         return
#
#     def stageScan(self):
#
#         path = os.path.join(self._path, self.comboBox.currentText())
#         if files.list_all_directory():
#             return True
#
#         return path
#
#     def removeChild(self):
#
#         if self._child:
#             c = self._child
#
#             c.removeChild()
#             c.setParent(None)
#             c.deleteLater()
#             self._child = None
#             del c
#
#     def remove(self):
#         self.removeChild()
#         self.setParent(None)
#         self.deleteLater()
#         self._child = None
#         del self
#
#
# class ToolBoxComboDynamicWidget(ComboDynamicWidget):
#     def __init__(self,
#                  settings=None,
#                  project=None,
#                  path=None,
#                  stage=None,
#                  box_list=None,
#                  parent_box=None,
#                  parent_layout=None,
#                  parent=None
#                  ):
#
#         super(ToolBoxComboDynamicWidget, self).__init__(settings=settings,
#                                                         project=project,
#                                                         path=path,
#                                                         box_list=box_list,
#                                                         parent_box=parent_box,
#                                                         parent_layout=parent_layout,
#                                                         parent=parent
#                                                         )
#
#         # Local and init calls
#
#         self._node = None
#         self._level = "n/a"
#         self.section = None
#
#         if path and stage:
#             self._path = path
#             self._stage = stage
#             self.listDirectory()
#
#         self.show_label = True
#         self.createModel()
#
#
#     def listDirectory(self):
#         dir = self._path
#         dirs = files.list_dir_folders(dir)
#
#         if dirs:
#
#             self._subdirectories = dirs
#
#             relative_path = files.relpath_wrapper(dir, self.parent.project.path)
#             depth = relative_path.count(os.sep)
#
#             if self._stage in self._project.stages[self._project.assets_root]:  # "asset"]:
#                 options = self._project.levels[self._project.assets_root]  # "asset"]
#                 self.section = self._project.assets_root
#                 if len(options) > depth:
#                     self._level = options[depth]
#
#                     return
#
#             if self._stage in self._project.stages[self._project.animation_root]:  # "animation"]:
#                 options = self._project.levels[self._project.animation_root]  # "animation"]
#                 if len(options) > depth:
#                     self._level = options[depth]
#                     self.section = self._project.animation_root
#
#                     return
#
#         self._level = "n/a"
#     #
#     # def createModel(self):
#     #
#     #     li = [dt.CatagoryNode("<{}>".format(self._level))]
#     #
#     #
#     #     self.setLabel(self._level)
#     #
#     #     if self._level != "n/a":
#     #         if self._subdirectories:
#     #             for dir in sorted(self._subdirectories):
#     #                 n = os.path.split(dir)[1]
#     #                 li.append(dt.FolderNode(n, settings = self.parent.settings, path = os.path.join(self._path,dir)))
#     #
#     #
#     #     self.comboBox.setModel(models.List_Model(li))
#
#
#     def addChild(self, path):
#
#         if files.list_dir_folders(path):
#             widget = ToolBoxComboDynamicWidget(
#                 settings=self._settings,
#                 project=self._project,
#                 path=path,
#                 stage=self._stage,
#                 box_list=self._box_list,
#                 parent_box=self,
#                 parent_layout=self._parent_layout,
#                 parent=self.parent)
#             self._child = widget
#
#
#     def stageScan(self):
#
#         path = os.path.join(self._path, self.comboBox.currentText())
#
#         self._node = None
#
#         if misc.assetDir(path):
#
#             '''
#             if the path is an assets folder
#             '''
#
#             p = self._parent_box._node if self._parent_box else self._node
#
#             self._node = assets.AssetNode(os.path.split(path)[1], parent=p, path=os.path.join(path),
#                                           project=self._project,
#                                           settings=self._settings, pipelineUI=self.parent, section=self.section)
#
#             for dir in files.list_dir_folders(path):
#
#                 '''
#                 scan each folder to see if it is a stage folder
#                 '''
#
#                 if misc.stageDir(os.path.join(path, dir)):
#                     if dir == self._settings.stage:
#                         '''
#                         if its a stage, see if it is a match to the current selected stage, if so, set it as the current stage folder
#                         '''
#
#                         stage = stages.StageNode(dir, parent=self._node, path=os.path.join(path, dir),
#                                                  project=self._project,
#                                                  settings=self._settings, pipelineUI=self.parent, section=self.section)
#
#                         self.parent.set_stage_node(stage)
#
#                         self.parent.update_versions_table()
#                         self.parent.update_masters_table()
#                         self.parent.update_playblasts_table()
#                         return True
#
#
#             self.parent.set_stage_node(None)
#
#             self.parent.update_versions_table()
#             self.parent.update_masters_table()
#             self.parent.update_playblasts_table()
#             return True
#
#         if self._parent_box:
#             self._node = dt.FolderNode(os.path.split(path)[1], parent=self._parent_box._node, path=path,
#                                        project=self._project,
#                                        settings=self._settings, pipelineUI=self.parent)
#         else:
#             self._node = dt.FolderNode(os.path.split(path)[1], parent=None, path=path, project=self._project,
#                                        settings=self._settings, pipelineUI=self.parent)
#
#         self.parent.set_stage_node(None)
#
#         self.parent.update_versions_table()
#         self.parent.update_masters_table()
#         self.parent.update_playblasts_table()
#         return path
#
#
#
# class DresserComboDynamicWidget(ComboDynamicWidget):
#     def __init__(self,
#                  settings=None,
#                  project=None,
#                  path=None,
#                  box_list=None,
#                  parent_box=None,
#                  parent_layout=None,
#                  parent=None,
#                  ):
#
#         super(DresserComboDynamicWidget, self).__init__(settings=settings,
#                                                         project = project,
#                                                         path = path,
#                                                         box_list = box_list,
#                                                         parent_box=parent_box,
#                                                         parent_layout=parent_layout,
#                                                         parent=parent,
#                                                         )
#
#         self.listDirectory()
#         self.show_label = True
#         self.createModel()
#         self.parent._dresserRootPath = self._path
#     #
#     def listDirectory(self):
#
#         dir = self._path
#         dirs = files.list_dir_folders(dir)
#
#         if dirs:
#
#             self._subdirectories = dirs
#
#             relative_path = files.relpath_wrapper(dir, os.path.join(self.parent.project.path, "asset_lib"))
#             depth = relative_path.count(os.sep)
#             options = self._project.levels[self._project.assets_root]
#             self.section = self._project.assets_root
#             if len(options) > depth:
#                 self._level = options[depth]
#
#                 return
#
#         self._level = "n/a"
#
#
#     def addChild(self, path):
#         if files.list_dir_folders(path):
#             widget = DresserComboDynamicWidget(
#                 settings=self._settings,
#                 project=self._project,
#                 path=path,
#                 box_list=self._box_list,
#                 parent_box=self,
#                 parent_layout=self._parent_layout,
#                 parent=self.parent)
#
#             self._child = widget
#
#     def stageScan(self):
#
#         path = os.path.join(self._path, self.comboBox.currentText())
#         if files.list_directory(path, "ma"):
#             return True
#
#         return path
#
#     def update(self):
#         super(DresserComboDynamicWidget, self).update()
#
#         folder = None if self.comboBox.currentText().startswith("<") and self.comboBox.currentText().endswith(">") else self.comboBox.currentText()
#
#         self.parent._dresserRootPath = self._path if not folder else os.path.join(self._path, folder)
#
#
# class SimpleComboDynamicWidget(ComboDynamicWidget):
#     def __init__(self,
#                  settings=None,
#                  project=None,
#                  path=None,
#                  box_list=None,
#                  parent_box=None,
#                  parent_layout=None,
#                  parent=None,
#                  whitelist = [],
#                  dialouge = None
#                  ):
#
#         self.whitelist = whitelist
#         self.dialouge = dialouge
#
#         super(SimpleComboDynamicWidget, self).__init__(settings=settings,
#                                                         project = project,
#                                                         path = path,
#                                                         box_list = box_list,
#                                                         parent_box=parent_box,
#                                                         parent_layout=parent_layout,
#                                                         parent=parent
#                                                         )
#
#         self.show_label = True
#         self.listDirectory()
#         self.createModel()
#         self.parent.dynamic_path = self._path
#         self.label.setHidden(True)
#
#     def listDirectory(self):
#         self._subdirectories = []
#         dir = self._path
#         dirs = files.list_dir_folders(dir)
#         if dirs:
#             if self.whitelist:
#                 for d in dirs:
#                     if d in self.whitelist:
#                         self._subdirectories.append(d)
#             else:
#                 self._subdirectories = dirs
#
#
#     def addChild(self, path):
#         if files.list_dir_folders(path):
#             widget = SimpleComboDynamicWidget(
#                 settings=self._settings,
#                 project=self._project,
#                 path=path,
#                 box_list=self._box_list,
#                 parent_box=self,
#                 parent_layout=self._parent_layout,
#                 parent=self.parent,
#                 whitelist=[],
#                 dialouge = self.dialouge)
#
#             self._child = widget
#
#     def stageScan(self):
#         path = os.path.join(self._path, self.comboBox.currentText())
#         if self.hasAssets(path):
#             return True
#
#         return path
#
#     def hasAssets(self, path):
#
#         dirs = files.list_dir_folders(path)
#         if dirs:
#             for d in dirs:
#                 if misc.assetDir(os.path.join(path, d)):
#                     return True
#         return False
#
#     def createModel(self):
#
#         li = [dt.CatagoryNode("<{}>".format("dir"))]
#
#         if self._subdirectories:
#             for dir in sorted(self._subdirectories):
#                 n = os.path.split(dir)[1]
#                 li.append(dt.FolderNode(n, settings=self.parent.settings, path=os.path.join(self._path, dir)))
#
#         self.comboBox.setModel(models.List_Model(li))
#
#     def update(self):
#
#         super(SimpleComboDynamicWidget, self).update()
#         self.dialouge.ready(False)
#         folder = None if self.comboBox.currentText().startswith("<") and self.comboBox.currentText().endswith(">") else self.comboBox.currentText()
#
#         self.dialouge.dynamic_path = self._path if not folder else os.path.join(self._path, folder)
#
#
#         if self.hasAssets(self.dialouge.dynamic_path):
#             self.dialouge.ready(True)
#
