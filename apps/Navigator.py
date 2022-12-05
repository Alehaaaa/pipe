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
import sys
import logging
import os
import re
import functools
import threading
import traceback

import pipeline.libs.config as cfg
import pipeline.libs.files as files
import pipeline.libs.folder_view as folder_view
import pipeline.libs.misc as misc
import pipeline.libs.models as models
import pipeline.libs.nodes.elements as elemtents
import pipeline.widgets.comboBox as comboBox
from pipeline.libs.Qt import QtWidgets, QtCore
import pipeline.widgets.inputs  as inputs
import pipeline.apps.preset_editor as preset_editor




logger = logging.getLogger(__name__)




class BranchComboWidget(comboBox.ComboWidget):

    changed = QtCore.Signal(str)

    def __init__(self,
                 items=None,
                 path = None,
                 parent_layout=None,
                 parent=None):

        super(BranchComboWidget, self).__init__(parent_layout, parent)

        self.parent = parent
        self.discard_scan_update = False
        # self.setMaximumHeight(30)
        self.setMinimumHeight(30)

        # if self.parent.parent.pipeline_mode == cfg.Pipeline_mode.SUPER:
        #     self.setMaximumWidth(150)
        #     self.setMinimumWidth(150)

        self.label.setParent(None)
        self.label.deleteLater()


        self.setHidden(False)
        self.branches_model = None

        self.comboBox.currentIndexChanged.connect(self.update)
        # logger.info("connecting to {}".format(self.parent))
        self.changed.connect(self.parent.set_view_root)

        # self.comboBox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # customContextMenuRequested.connect(self.showMenu)

        # self.comboBox.customContextMenuRequested.connect(self.branches_options)


    # def showMenu(self, event):
    #     menu = QtWidgets.QMenu()
    #     clear_action = menu.addAction("Clear Selection", self)
    #     action = menu.exec_(self.mapToGlobal(event.pos()))
    #     if action == clear_action:
    #         self.clearSelection()

    # def branches_manager(self):
    #     # (self, parent = None, main_window = None, title = None, list = None, list_view = None)
    #
    #
    #
    #
    #     branches_editor = list_editor.List_editor_dialog(parent=self,
    #                                                      main_window=self.parent.parent,
    #                                                      title = "Branch editor",
    #                                                      list_model = self.branches_model,
    #                                                      list_view =  folder_view.Branch_list_view  )
    #     branches_editor.exec_()
    #
    # def branches_options(self, point):
    #     # logger.info("right click")
    #     # menu.addActions(actions)
    #     self.branch_options_menu = QtWidgets.QMenu(self)
    #     self.new_version_from_selection = QtWidgets.QAction("Branches manager...", self)
    #     self.new_version_from_selection.triggered.connect(self.branches_manager)
    #     self.branch_options_menu.addAction(self.new_version_from_selection)
    #
    #     # self.save_version_menu.addSeparator()
    #     # self.new_version_from_file = QtWidgets.QAction("Save from File...", self)
    #     # self.branch_options_menu.addAction(self.new_version_from_file)
    #     # self.new_version_from_file.triggered.connect(
    #     #     functools.partial(self.version_save, outliner.create_options.B_FILE))
    #
    #     # logger.info(self.ui.save_version_pushButton.mapToGlobal(point))
    #     self.branch_options_menu.exec_(self.comboBox.mapToGlobal(point))


    def update(self):
        if self.discard_scan_update:
            self.discard_scan_update = False
        else:
            # logger.info("updating with {}".format(self.comboBox.currentText()))
            path = os.path.join(self._path,self.comboBox.currentText()) if self._path else self.comboBox.currentText()
            self.changed.emit(path)
        # self.parent.address_label.setText(self.comboBox.currentText())


    def set_branch(self, string):

        if comboBox.setComboValue(self.comboBox, string):
            # logger.info("branch set to {}".format(string))
            self.update()

    def set_root(self, path):
        if path:
            self._path = path
            self.listDirectory()
            self.createModel()
            # self.update()
        else:
            self.comboBox.clear()

    def listDirectory(self):
        dir = self._path
        dirs = files.list_dir_folders(dir)

        if dirs:
            self._subdirectories = dirs

        return

    def createModel(self):

        self.comboBox.clear()
        # dt.CatagoryNode(name, path=path, project = self.parent.parent.project)

        li = []
        # p = self._parent_box.folderView.selectionModel()
        if self._subdirectories:

            # p = self._parent_box.selected_node if self._parent_box else None

            for dir in sorted(self._subdirectories):
                n = os.path.split(dir)[1]

                path = os.path.join(self._path, dir)

                if misc.branch_dir(path):
                    li.append(elemtents.BranchNode(n, path=path, project = self.parent.parent.project))

            if li:
                self.branches_model = models.List_Model(li)
                self.comboBox.setModel(self.branches_model)
                return True

        return False

        # li = []
        # [li.append(dt.DummyNode(i)) for i in sorted(self._items)]
        # li.insert(0, dt.CatagoryNode("stage"))
        #
        # self.setLabel("stage")

        # self.comboBox.setModel(models.List_Model(li))
        # self.comboBox.currentIndexChanged.connect(self.update)

    # def update(self):
    #     self._settings.stage = self.comboBox.currentText()
    #
    #     try:
    #         self.parent.dynamicCombo._box_list[-1].scan_directory()
    #     except:
    #         pass

class FolderStaticWidget(QtWidgets.QWidget):

    component_changed = QtCore.Signal()

    def __init__(self,
                 items = [],
                 label = "",
                 parent_layout=None,
                 parent=None
                 ):

        QtWidgets.QWidget.__init__(self, parent)

        self.setHidden(True)
        self._parent_layout = parent_layout

        # UI
        # self.setMaximumHeight(60)
        # self.setMinimumHeight(200)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        # self.layout.setAlignment(QtCore.Qt.AlignLeft)

        self.label = QtWidgets.QLabel()
        # self.label.setMargin(5)

        text = "Results for '{}':".format(label) if items else "No results for '{}'...".format(label)
        self.label.setText(text)
        # bold_font = QtGui.QFont()
        # bold_font.setBold(True)
        # self.label.setFont(bold_font)
        self.layout.addWidget(self.label)
        self.parent = parent
        self._parent_layout.addWidget(self)
        self.folder_view = folder_view.FolderView(self, settings = self.parent.parent.settings, search_mode = True)
        self.layout.addWidget(self.folder_view)

        # Local and init calls

        # self._parent_box = parent_box
        self._parent_layout = parent_layout
        # self._box_list = box_list
        # self._box_list.append(self)
        # self._subdirectories = None
        # self._path = None
        # self._child = None
        # self._model = None

        self._selected = None


        # if path:
        #     self._path = path
        #     self.listDirectory()

        self.createModel(items)

            # self.update(self.folderView.selectionModel().selectedIndexes()[0])
        # logger.info(self.folderView.selectionModel().selectedIndexes())
        self.folder_view.clicked.connect(self.update)

        self.setHidden(False)
        self.component_changed.connect(self.parent.set_current_component)


    # def navigate(self, items):
    #     try:
    #         current = self
    #         for i in range(0, len(items)):
    #             if comboBox.setComboValue(current.comboBox, items[i]):
    #                 current.update()
    #                 current = current._child
    #     except:
    #         logger.info("can not complete navigation to {}".format(items))

    @property
    def selected_node(self):
        return self._selected

    @selected_node.setter
    def selected_node(self, value):
        self._selected = value
    #
    # def listDirectory(self):
    #     dir = self._path
    #     dirs = files.list_dir_folders(dir)
    #
    #     if dirs:
    #         self._subdirectories = dirs
    #
    #     return



    def createModel(self, items):
        li = []
        # self.label.setText(os.path.split(self._path)[1])
        # p = self._parent_box.folderView.selectionModel()
        # if self._subdirectories:

            # p = self._parent_box.selected_node if self._parent_box else None

        for dir in sorted(items):
            n = files.reletive_path(self.parent.parent.project.path, dir)
            # n = os.path.split(dir)[1]


            node = self.node_generator(n, dir)
            if node:
                li.append(node)

        if li:
            self.folder_view.setModel_(models.List_Model(li))
            return True

        return False

    def node_generator(self, name, dir):
        # logger.info(dir)
        path = dir #os.path.join(self._path, dir)

        if misc.catagory_dir(path):
            return elemtents.CatagoryNode(name, path=path, project = self.parent.parent.project)
        if misc.component_dir(path):
            return elemtents.ComponentNode(name, path=path, project = self.parent.parent.project)

        return None


    # def addChild(self, path):
    #
    #     if files.list_dir_folders(path):
    #         widget = FolderDynamicWidget(
    #             path=path,
    #             box_list=self._box_list,
    #             parent_box=self,
    #             parent_layout=self._parent_layout,
    #             parent=self.parent)
    #         self._child = widget


    def update(self, index):

        index = self.folder_view.model().mapToSource(index)
        self.selected_node = self.folder_view.model().sourceModel().getNode(index)

        if self.selected_node.typeInfo() == cfg._component_:
            # self.parent.selected_component = self.selected_node

            self.component_changed.emit()
        return

    def remove(self):
        # self.removeChild()
        self.setParent(None)
        self.deleteLater()
        self._child = None
        del self

class Folder_comboBox(QtWidgets.QComboBox):
    def __init__(self, parent):
        super(Folder_comboBox, self).__init__(parent)

    def setModel_(self, model):
        self.setModel(model)

    # def setModel_(self, model):
    #     if model:
    #
    #         self._proxyModel = models.Simple_ProxyModel()
    #         self._proxyModel.setSourceModel(model)
    #         self._proxyModel.setDynamicSortFilter(True)
    #         self._proxyModel.setSortRole(models.Versions_Model.sortRole)
    #         self.setModel(self._proxyModel)
    #
    #     else:
    #         pass
    #         # self.setModel(None)
    #
    #
    # def asModelNode(self, index):
    #
    #     index = self.model().mapToSource(index)
    #     return self.model().sourceModel().getNode(index)


class FolderDynamicWidget(QtWidgets.QWidget):

    component_changed = QtCore.Signal()

    def __init__(self,
                 path=None,
                 box_list=[],
                 parent_box=None,
                 parent_layout=None,
                 parent=None,
                 silent=False
                 ):

        QtWidgets.QWidget.__init__(self, parent)

        self.setHidden(True)
        self._parent_layout = parent_layout
        # Local and init calls
        self.parent = parent
        self._parent_box = parent_box
        # self._parent_layout = parent_layout
        self._box_list = box_list
        self._box_list.append(self)
        self._subdirectories = None
        self._path = None
        self._child = None
        self._model = None
        self._selected = None
        self._ready = False
        # UI
        # self.setMaximumHeight(60)
        # self.setMinimumHeight(200)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self._parent_layout.addWidget(self)

        # if self.parent.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.SUPER:

        self.label = QtWidgets.QPushButton()
        self.label.setMinimumHeight(30)
        self.layout.addWidget(self.label)
        self.label.setIconSize(QtCore.QSize(20, 20))
        # self.label.setStyleSheet('''
        #                                     QPushButton::menu-indicator{
        #                                         subcontrol-position: right center;
        #                                         subcontrol-origin: padding;
        #                                         left: -5px;
        #                                     }
        #                                     ''')
        self.folder_view = folder_view.FolderView(self, settings = self.parent.parent.settings)
        self.folder_view.clicked.connect(self.update)
        # self.layout.addWidget(self.folder_view)
        # else:
        #     self.folder_view = Folder_comboBox(self)
        #     # self.v = QtWidgets.QPushButton('asf')
        #     self.folder_view.setIconSize(QtCore.QSize(24, 24))
        #     self.folder_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        #     # self.folder_view.setStyleSheet(cfg.stylesheet)
        #

        self.layout.addWidget(self.folder_view)

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.progressBar.setMaximumHeight(5)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet('''
        QProgressBar
        {
            border: 1px solid ''' + cfg.colors.DARK_GRAY_MINUS + ''';
        }
        QProgressBar::chunk
        {
            background-color:  ''' + cfg.colors.DARK_PURPLE + ''';
        }''')

        self.layout.addWidget(self.progressBar)

        if path:
            self._path = path
            self.scan = Scandir_list_thread(path_to_dir=self._path)#, project=self.parent.parent.project)
            self.scan.update.connect(self.createModel_from_scan)
            self.scan.percent.connect(self.progressBar.setValue)

            # self.listDirectory()

        # self.createModel()
        self.component_changed.connect(self.parent.set_current_component)
        self.setHidden(False)

        # if self.parent.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.SUPER:
        self.set_menu()

        # if self.parent.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.STANDARD:
        #
        #     self.folder_view.setMinimumHeight(30)
        #     self.folder_view.setMaximumHeight(30)
        #
        #     self.bottom_gap = QtWidgets.QLabel()
        #     self.bottom_gap.setMinimumHeight(20)
        #     self.bottom_gap.setMaximumHeight(20)
        #     self.layout.addWidget(self.bottom_gap)
        #
        #     self.folder_view.currentIndexChanged.connect(self.update)
        #     if self.folder_view.model():
        #         if hasattr(self.folder_view.model(),'items'):
        #             if len(self.folder_view.model().items) == 1:
        #                 self.update(0)

        self.scan.start()
        self.folder_view.setModel_(models.List_Model(list()))


        # self.folder_view.setHidden(True)
        # self.label.setHidden(True)

    def node_generator(self, name, dir):

        path = os.path.join(self._path, dir)
        # logger.info(path)
        if misc.catagory_dir(path):
            return elemtents.CatagoryNode(name, path=path, project = self.parent.parent.project)
        if misc.component_dir(path):
            return elemtents.ComponentNode(name, path=path, project = self.parent.parent.project)

        return None

    def append_item(self, name):

        item = self.node_generator(name, name)

        self.folder_view.model().sourceModel().insertRows(0,1,QtCore.QModelIndex(), item)


    def hide_loader(self):
        # self.folder_view.setHidden(False)
        self.progressBar.setHidden(True)

    def set_menu(self):
        menu = QtWidgets.QMenu(self.label)
        if not self._parent_box:

            presets_menu = menu.addMenu("Create preset... ")
            presets_menu.addAction(QtWidgets.QAction('From file...', presets_menu, triggered=functools.partial(self.apply_preset, None)))

            presets_menu.addSeparator()

            for p in preset_editor.Preset_dialog.list_saved_presets():
                presets_menu.addAction(QtWidgets.QAction(p[1], presets_menu, triggered=functools.partial(self.apply_preset, p[0])))


            menu.addSeparator()

        menu.addAction(QtWidgets.QAction("Create Category...", menu,
                                             triggered=functools.partial(self.folder_view.create_catagory, None)))
        menu.addAction(QtWidgets.QAction("Create Component...", menu,
                                             triggered=functools.partial(self.folder_view.create_component, None)))
        menu.addSeparator()

        menu.addAction(QtWidgets.QAction("Explore...", menu,
                                             triggered=functools.partial(self.folder_view.explore, None)))

        self.label.setMenu(menu)



    def apply_preset(self, preset_file):

        if hasattr(self.parent.parent, "preset_generation_dialog"):
            if isinstance(self.parent.parent.preset_generation_dialog, preset_editor.Preset_generation_dialog):
                self.parent.parent.preset_generation_dialog.close()





        # if preset_file:
            # logger.info('applying {}'.format(preset_file))
        self.parent.parent.preset_generation_dialog = preset_editor.Preset_generation_dialog(
                parent=self.parent.parent, pipeline_window = self.parent.parent, preset_file=preset_file)
        # else:
        #     logger.info('select file...')

        # self.parent.parent.preset_generation_dialog.show()

    def set_selection(self,  string):
        # logger.info(self.set_selection.__name__)
        # logger.info(self._path)
        if self.folder_view.model().sourceModel():
            model = self.folder_view.model().sourceModel()
            items = model.items
            # logger.info(items)
            # logger.info(model.rowCount(None))
            index = None
            # logger.info("item to match {}".format(string))
            for i in items:
                # logger.info(i.name)
                if i.name == string:
                    # logger.info("item index is")
                    # logger.info(items.index(i))
                    index = model.index(items.index(i), 0, QtCore.QModelIndex())



            if index:
                # logger.info(index)
                proxy_index = self.folder_view.model().mapFromSource(index)
                self.folder_view.setCurrentIndex(proxy_index)
                return proxy_index

        else:
            logger.info("no matching index to {}".format(string))

        return False

    def navigate(self, navigation_items):
        try:
            current = self
            for index, item in enumerate(navigation_items):
                # logger.info(item)
                selection = None
                current.append_item(item)
                selection = current.set_selection(item)
                if selection:
                    # logger.info("updating for {}".format(item))
                    current.force_update(item)
                    self.parent.parent.set_focus_widget = current.folder_view
                    # print ">>>", item
                    if item == navigation_items[-1]:

                        current.selected_node = current.folder_view.model().sourceModel().getNode(selection)

                        current.component_changed.emit()

                    current = current._child

        except Exception, err:
            logger.info(err)
            logger.info(traceback.print_exc())
            logger.info("can not complete navigation to {}".format(navigation_items))

    # def navigate(self, items):
    #     logger.info('NAVIGATING')
    #     try:
    #         current = self
    #         for item in items:
    #             logger.info(current._path)
    #             selection = None
    #             # current.force_update()
    #             selection = current.set_selection(item)
    #             if selection:
    #
    #                 logger.info("updating for {}".format(item))
    #                 current.update(selection)
    #                 self.parent.parent.set_focus_widget = current.folder_view
    #                 current = current._child
    #                 # print current
    #
    #     except:
    #         import traceback
    #         print traceback.format_exc()
    #         logger.info("can not complete navigation to {}".format(items))

    @property
    def selected_node(self):
        return self._selected

    @selected_node.setter
    def selected_node(self, value):
        self._selected = value

    # def listDirectory(self):
    #     dir = self._path
    #     dirs = files.list_dir_folders(dir)
    #
    #     if dirs:
    #         self._subdirectories = dirs
    #
    #     return

    def createModel_from_scan(self, scan=None):
        li = list()

        if scan:

            for item in scan:
                if item["type"] == 'catagory':
                    li.append(elemtents.CatagoryNode(item["name"], path=item["path"], project=self.parent.parent.project))
                if item["type"] == 'component':
                    li.append(elemtents.ComponentNode(item["name"], path=item["path"], project=self.parent.parent.project))
                if item["type"] == 'branch':
                    li.append(elemtents.BranchNode(item["name"], path=item["path"], project=self.parent.parent.project))

        self.createModel(li)
        self._ready = True

    def createModel(self, li = None):
        self.label.setText("/{}".format(os.path.split(self._path)[1]))
        self.folder_view.setModel_(models.List_Model(li))
        self.hide_loader()


    # def node_generator(self, name, dir):
    #
    #     path = os.path.join(self._path, dir)
    #     # logger.info(path)
    #     if misc.catagory_dir(path):
    #         return elemtents.CatagoryNode(name, path=path, project = self.parent.parent.project)
    #     if misc.component_dir(path):
    #         return elemtents.ComponentNode(name, path=path, project = self.parent.parent.project)
    #
    #     return None


    def addChild(self, path, silent=False):

        # if files.list_dir_folders(path):
        widget = FolderDynamicWidget(
            path=path,
            box_list=self._box_list,
            parent_box=self,
            parent_layout=self._parent_layout,
            parent=self.parent,
            silent=silent)
        self._child = widget

    def force_update(self, name):
        # directory_name = self.selected_node.path

        path = os.path.join(self._path, name)
        # logger.info("FORCE update on {}".format(path))
        # self.parent.address_label.setText(self.selected_node.relative_path)

        self.removeChild()
        scan = self.scan_directory(path)

        if scan is not True:
            '''
            if the folder is a stage folder don't list it and return True
            '''
            self.addChild(scan, silent=True)
            return

        return

    def update(self, index):
        # if self.parent.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.SUPER:
        index = self.folder_view.model().mapToSource(index)
        self.selected_node = self.folder_view.model().sourceModel().getNode(index)
        # else:
        #     self.selected_node = self.folder_view.model().items[index]

        if self.selected_node.typeInfo() == cfg._component_:
            # self.parent.selected_component = self.selected_node
            # pass
            self.component_changed.emit()


        # logger.info("node is {}".format(self.selected_node.name))
        # logger.info("childrens")
        # for c in self.selected_node.children:
        #     logger.info(c.name)


        directory_name = self.selected_node.path

        path = os.path.join(self._path, directory_name)

        # self.parent.address_label.setText(self.selected_node.relative_path)

        self.removeChild()
        scan = self.scan_directory(path)

        if scan is not True:
            '''
            if the folder is a stage folder don't list it and return True
            '''
            self.addChild(scan)
            return

        return

    def scan_directory(self, path):

        if misc.component_dir(path):
            return True
        # if files.list_all_directory(path):
        #     return True

        return path

    def removeChild(self):

        if self._child:
            c = self._child

            try:
                # print "{} killing thread".format(c._path)
                c.scan.kill()
            except:
                print traceback.print_exc()

            c.removeChild()
            c.setParent(None)
            c.deleteLater()
            self._child = None
            del c

    def remove(self):
        try:
            # print "{} killing thread".format(self._path)
            self.scan.kill()
        except:
            print traceback.print_exc()

        self.removeChild()
        self.setParent(None)
        self.deleteLater()
        self._child = None
        del self


    def hideChild(self, bool):
        if self._child:
            c = self._child
            c.hide(bool)
            c.setHidden(bool)


    def hide(self, bool):
        self.hideChild(bool)
        self.setHidden(bool)


class Navigator(QtWidgets.QWidget):

    root_changed = QtCore.Signal(str)
    component_changed = QtCore.Signal()

    def __init__(self, parent = None):
        super(Navigator, self).__init__(parent)

        # self.setMinimumHeight(100)
        self.parent = parent
        self.layout =  QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.address_widget = QtWidgets.QWidget(self)
        self.address_widget_layout = QtWidgets.QHBoxLayout(self.address_widget)
        self.address_widget_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.address_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.address_widget)


        self.branch_widget = BranchComboWidget(items=None,parent_layout=self.address_widget_layout,parent=self)
        # self.branch_widget = BranchComboWidget(items=None, parent_layout=self.parent.ui.horizontalLayout, parent=self)


        # self.address_label = QtWidgets.QLabel()
        # self.address_label.setMargin(5)
        # bold_font = QtGui.QFont()
        # bold_font.setBold(True)
        # self.address_label.setFont(bold_font)
        # self.address_label.setStyleSheet("background-color: #353535")
        # self.address_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.address_widget_layout.addWidget(self.address_label)

        self.search_line = inputs.SearchLine(self, label="Search components...")
        self.address_widget_layout.addWidget(self.search_line)
        self.search_line.textChanged.connect(self.search_changed)
        self.search_line.setMaximumWidth(150)
        self.search_line.setMinimumWidth(150)

        if self.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.STANDARD:
            self.search_line.setHidden(True)

        #
        # self.search_icon_label = QtWidgets.QLabel()
        # self.search_icon_label.setPixmap(cfg.search_icon)
        # self.address_widget_layout.addWidget(self.search_icon_label)


        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff )
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()



        self.horizontalLayout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QtWidgets.QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.splitter.setChildrenCollapsible(False)


        self.horizontalLayout.addWidget(self.splitter)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.layout.addWidget(self.scrollArea)

        self.rootFolder = None
        self.results_folder = None




        # self.walk_root = None
        # self.walk_subFolders = None
        # self.walk_files = None
        # self.up_to_date = False

        self.current_component = None
        self.component_changed.connect(self.parent.set_current_component)

        self.root_changed.connect(self.parent.set_branch_root)




    # def walk(self):
    #     if self.rootFolder:
    #
    #         if self.up_to_date:
    #             return self.walk_root, self.walk_subFolders, self.walk_files
    #
    #         else:
    #
    #             path = self.rootFolder._path
    #             xxx = os.walk(path)
    #             self.up_to_date = True
    #             return self.walk_root, self.walk_subFolders, self.walk_files
    #
    #     return




    def rebuild(self):

        # self.label.setParent(None)
        # self.label.deleteLater()
        #
        if self.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.STANDARD:
            self.search_line.setHidden(True)
        else:
            self.search_line.setHidden(False)
        self.branch_widget.update()
        #
        # del self.rootFolder




    def search_changed(self, str):
        if self.rootFolder and (self.search_line.text() != "") and (self.search_line.text() != self.search_line.label):
            self.filter_folders(self.rootFolder._path, str)
            # logger.info("searching...")
            return

        # if self.rootFolder and (self.search_line.text() == ""):

        if isinstance(self.results_folder, FolderStaticWidget):
            self.results_folder.remove()
            self.results_folder = None

        if isinstance(self.rootFolder, FolderDynamicWidget):
            self.rootFolder.hide(False)

        # logger.info("Not searching")
        return

    def filter_folders(self, path, search_string):

        all_folders = []

        for root, subFolders, _files in os.walk(path):

            for s in subFolders:
                all_folders.append(os.path.join(root,s))


        string = search_string

        results = []
        for folder in all_folders:

            search_in = files.reletive_path(path, folder) #os.path.join(self.parent.project.path, "assets")
            # logger.info(search_in)
            f = None
            try:
                f = re.search(string, search_in, re.IGNORECASE) #os.path.split(folder)[1])
            except:
                logger.info("This search pattern {} is invalid".format(string))

            # logger.info(search_in)

            if f:
                # logger.info("HIT! {}".format(folder))
                if misc.component_dir(folder):

                    results.append(folder)
        #
        # logger.info(" {} -------".format(string))
        #
        # for r in results:
        #     logger.info(r)
        # logger.info("-------")
        # if results:
        self.set_view_with_search_results(results, search_string)

    def set_branch_root(self, path):



        if path:
            self.branch_widget.set_root(path)


        else:
            self.branch_widget.set_root(None)
            # self.address_label.setText("")


    def set_view_root(self, path):
        if self.parent.pipeline_navigation_mode == cfg.Pipeline_navigation_mode.SUPER:
            self.search_line.setText(self.search_line.label)
        # self.search_changed(self.search_line.label)


        if isinstance(self.rootFolder, FolderDynamicWidget):
            self.rootFolder.remove()
            self.rootFolder = None


        if path:

            self.rootFolder = FolderDynamicWidget(
                path=path,
                box_list=[],
                parent_box=None,
                parent_layout=self.splitter,
                parent=self)


            self.parent.set_focus_widget = self.rootFolder.folder_view


            self.current_component = None
            self.component_changed.emit()
            self.root_changed.emit(path)
            # logger.info(self.selected_component)



    def set_view_with_search_results(self, results, search_string):

        if isinstance(self.rootFolder, FolderDynamicWidget):
            self.rootFolder.hide(True)

        if isinstance(self.results_folder, FolderStaticWidget):
            self.results_folder.remove()
            self.results_folder = None

        self.results_folder = FolderStaticWidget(
            items=results,
            label = search_string,
            parent_layout=self.splitter,
            parent=self)



    def set_current_component(self):
        # logger.info(self.sender())
        # if self.sender():# is not self:
        self.current_component = self.sender().selected_node

        # logger.info(self.current_component.name)

        self.component_changed.emit()


def remap( x, oMin, oMax, nMin, nMax ):

    #range check
    if oMin == oMax:
        print "Warning: Zero input range"
        return None

    if nMin == nMax:
        print "Warning: Zero output range"
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result

# class Scanner_list(object):
#     def __init__(self, path, percent_signal):
#
#         self.root_path = path
#         self._subdirectories = None
#         self.percent_signal = percent_signal
#
#     def scan(self):
#         self.listDirectory()
#         return self.createModel()
#
#     def listDirectory(self):
#         dir = self.root_path
#         # TODO: USE Scandir
#         dirs = files.list_dir_folders(dir)
#
#         if dirs:
#             self._subdirectories = dirs
#             return True
#         return False
#
#     def createModel(self):
#         li = list()
#         if self._subdirectories:
#             max = len(self._subdirectories)
#             self.percent_signal.emit(0)
#
#             for index, dir in enumerate(misc.human_sort(self._subdirectories)):
#                 n = os.path.split(dir)[1]
#
#                 node = self.node_generator(n, dir)
#                 if node:
#                     li.append(node)
#
#                 val = remap(index, 0, max, 0, 100)
#                 self.percent_signal.emit(val)
#
#         return li
#
#     def node_generator(self, name, dir):
#
#         path = os.path.join(self.root_path, dir)
#
#         if misc.catagory_dir(path):
#             return {"type": "catagory", "name": name, "path": path}
#         if misc.component_dir(path):
#             return {"type": "component", "name": name, "path": path}
#         if misc.branch_dir(path):
#             return {"type": "branch", "name": name, "path": path}
#
#         return {"type": None, "name": None, "path": None}
#

class Scandir_list_thread(QtCore.QObject, threading.Thread):
    update = QtCore.Signal(object)
    percent = QtCore.Signal(int)

    def __init__(self, path_to_dir='.'):

        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        self._path = path_to_dir
        self.daemon = True
        self.killed = False
        #
        # self.results_list = Scanner_list(path_to_dir, self.percent)

    def run(self):
        li = []
        try:
            li = self.createModel()
        except SystemExit:
            pass
            # print 'system exit at in {}.thread.run():'.format(self.__class__.__name__)
        except:
            print 'exceptions in {}.thread.run():'.format(self.__class__.__name__)
            print traceback.print_exc()
        finally:
            self.update.emit(li)
            return
        # try:
        #     list = self.createModel()
        #     self.update.emit(list)
        # except:
        #     print traceback.print_exc()
        #     self.update.emit([])
        # finally:
        #     return

    def createModel(self):
        li = list()
        # if self._path:
        subdirectories = files.list_dir_folders(self._path)

        if subdirectories:
            max = len(subdirectories)

            for index, dir in enumerate(misc.human_sort(subdirectories)):
                n = os.path.split(dir)[1]

                node = self.node_generator(n, dir)
                if node:
                    li.append(node)

                val = remap(index, 0, max, 0, 100)
                self.percent.emit(val)

        return li

    def node_generator(self, name, dir):

        path = os.path.join(self._path, dir)

        if misc.catagory_dir(path):
            return {"type": "catagory", "name": name, "path": path}
        if misc.component_dir(path):
            return {"type": "component", "name": name, "path": path}
        if misc.branch_dir(path):
            return {"type": "branch", "name": name, "path": path}

        return {"type": None, "name": None, "path": None}

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to

        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
    trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        try:
            self.update.disconnect()
            self.percent.disconnect()
        except:
            pass
        self.killed = True
