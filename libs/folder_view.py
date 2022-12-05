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


import functools
import logging
import os

import pipeline.apps.massage as massage
import pipeline.apps.project_outliner as outliner
import pipeline.libs.config as cfg
# import pipeline.libs.data as dt
import pipeline.libs.files as files
import pipeline.libs.models as models
import pipeline.libs.nodes.elements as elements
from pipeline.libs.Qt import QtWidgets, QtCore
import pipeline.maya_libs.maya_warpper as maya
import pipeline.apps.preset_editor as preset_editor
from pipeline.libs import permissions
import pipeline.widgets.inputs as inputs
import pipeline.CSS
from pipeline.CSS import loadCSS

reload(inputs)
logger = logging.getLogger(__name__)


class FolderView(QtWidgets.QListView):

    def __init__(self, parent, settings = None, search_mode = False):
        super(FolderView, self).__init__(parent)

        self.search_mode = search_mode
        self.role = settings.current_role
        self.permissions = permissions.Permissions
        self.css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(self.css)

        # self.menu = None

    def keyPressEvent (self, event):
        # logger.info(event.key())
        #
        # logger.info(QtCore.Qt.Key_Left)
        # logger.info(QtCore.Qt.Key_Right)
        # logger.info(QtCore.Qt.Key_Up)
        # logger.info(QtCore.Qt.Key_Down)
        super(FolderView, self).keyPressEvent(event)

        try:
            self.parent().update(self.selectionModel().selection().indexes()[0])
        except:
            pass

        if event.key() == QtCore.Qt.Key_Right:
            # logger.info("RIGHT")
            if self.parent()._child:
                self.parent()._child.folder_view.setFocus()
                index = self.parent()._child.folder_view.model().index(0,0,QtCore.QModelIndex())
                self.parent()._child.folder_view.setCurrentIndex(index)
                self.parent()._child.update(index)
                event.accept()

        if event.key() == QtCore.Qt.Key_Left:
            # logger.info("LEFT")
            if self.parent()._parent_box:
                self.parent()._parent_box.folder_view.setFocus()
                # self.parent()._parent_box.update(self.parent()._parent_box.folder_view.selectionModel().selection().indexes()[0])
                event.accept()



        # QtGui.QWidget.keyPressEvent(self, eventQKeyEvent)

    def setModel_(self, model):
        if model:

            self._proxyModel = models.Simple_ProxyModel()
            self._proxyModel.setSourceModel(model)
            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            self.setModel(self._proxyModel)

        else:
            pass
            # self.setModel(None)


    def asModelNode(self, index):

        index = self.model().mapToSource(index)
        return self.model().sourceModel().getNode(index)





    def contextMenuEvent(self, event):

        handled = True
        index = self.indexAt(event.pos())
        self.menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            node = self.asModelNode(index)

        top_actions = list()
        def_actions = list()

        if hasattr(self.parent(), '_parent_box'):
            if not self.parent()._parent_box:

                if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.create_preset):

                    presets_menu = self.menu.addMenu("Create preset... ")
                    presets_menu.addAction(QtWidgets.QAction('From file...', presets_menu, triggered=functools.partial(self.parent().apply_preset, None)))

                    presets_menu.addSeparator()

                    for p in preset_editor.Preset_dialog.list_saved_presets():
                        presets_menu.addAction(QtWidgets.QAction(p[1], presets_menu, triggered=functools.partial(self.parent().apply_preset, p[0])))


                    self.menu.addSeparator()


        if node:

            if node.typeInfo() != cfg._component_:

                if self.permissions.has_permissions(role_string=self.role(),action=self.permissions.create_category):

                    top_actions.append(QtWidgets.QAction("Create Category...", self.menu, triggered=functools.partial(self.create_catagory, node, index)))

                if self.permissions.has_permissions(role_string=self.role(),action=self.permissions.create_component):

                    top_actions.append(QtWidgets.QAction("Create Component...", self.menu, triggered=functools.partial(self.create_component, node, index)))

                if self.permissions.has_permissions(role_string=self.role(),action=self.permissions.rename):

                    top_actions.append(QtWidgets.QAction("Rename category...", self.menu, triggered=functools.partial(self.rename_catagory, node, index)))

            if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.delete):

                top_actions.append(QtWidgets.QAction("Delete...", self.menu, triggered=functools.partial(self.delete, node, index)))

            def_actions.append(QtWidgets.QAction("Explore...", self.menu,triggered=functools.partial(self.explore, node)))

            if node.typeInfo() == cfg._component_:
                if self.permissions.has_permissions(role_string=self.role(),action=self.permissions.rename):

                    top_actions.append(QtWidgets.QAction("Rename component...", self.menu, triggered=functools.partial(self.rename_component, node, index)))

        else:

            if not self.search_mode:

                if self.permissions.has_permissions(role_string=self.role(),action=self.permissions.create_category):
                    top_actions.append(QtWidgets.QAction("Create Category...", self.menu,triggered=functools.partial(self.create_catagory, node)))

                if self.permissions.has_permissions(role_string=self.role(),action=self.permissions.create_component):
                    top_actions.append(QtWidgets.QAction("Create Component...", self.menu,triggered=functools.partial(self.create_component, node)))

                def_actions.append(QtWidgets.QAction("Explore...", self.menu,triggered=functools.partial(self.explore, node)))
            else:
                event.accept()
                return

        self.menu.addActions(top_actions)
        self.menu.addSeparator()
        self.menu.addActions(def_actions)
        self.menu.setStyleSheet(self.css)

        self.menu.exec_(event.globalPos())
        event.accept()

        return

    def delete(self, node, index):
        if node:

            alert = massage.Prompt_alert(None, alert_string="This will send {} and all it's children to the trash. Procced?".format(node.name))
            result = alert.exec_()
            if result == QtWidgets.QDialog.Accepted:

            # if massage.Prompt_alert(None, alert_string="This will send {} and all it's children to the trash. Procced?".format(node.name)):#"warning", "Delete {}".format(node.name), "This will send {} and all it's children to the trash. Procced?".format(node.name)):
                node.delete_me()
                self.model().sourceModel().removeRows(0, 0, node=node)
                self._proxyModel.invalidate()
                self.parent().update(self.model().index(0, 0, QtCore.QModelIndex()))

    def explore(self, node):

        if node:
            node.explore()
        else:
            files.explore(self.parent()._path)

    def rename_component(self, node, index):
        # logger.info(elements.ComponentNode)
        if node:
            alert = "Caution: any dependencies of files from this component" \
                    "\nwill be broken and will have to be restored manually.\n\nThis is not undoable."
            rename_dialog = outliner.Rename_dialog(name_label_sting="New name", current_name = node.name, alert=alert, title="Rename component")
            result = rename_dialog.exec_()
            res = rename_dialog.result()
            if result == QtWidgets.QDialog.Accepted:


                maya.new_scene()
                self.parent().parent.parent.clear_current_component()

                node.rename(res["name"])
                node.version_model(force=True)
                node.masters_model(force=True)
                node.playblasts_model(force=True)
                # self.model().sourceModel().reset()
                self.parent().update(index)


    def rename_catagory(self, node, index):

        # logger.info(node.project)


        # logger.info(elements.ComponentNode)
        if node:
            alert = "Caution: any dependencies of files from this category" \
                    "\nwill be broken and will have to be restored manually.\n\nThis is not undoable."
            rename_dialog = outliner.Rename_dialog(name_label_sting="New name", current_name=node.name, alert=alert,
                                                   title="Rename category")

            result = rename_dialog.exec_()
            res = rename_dialog.result()
            if result == QtWidgets.QDialog.Accepted:

                maya.new_scene()
                self.parent().parent.parent.clear_current_component()

                node.rename(res["name"])
                self.parent().update(index)

    def create_catagory(self, node, index = None):

        folderDlg = outliner.newFolderDialog(string="")
        result = folderDlg.exec_()
        res = folderDlg.result()
        if result == QtWidgets.QDialog.Accepted:
            logger.info(res)

            base_folder_name = res["name"]
            step = res["step"]

            for i in range(0, res["quantity"]):

                number = files.set_padding((res["from"] + i)*step, res["padding"])

                if base_folder_name != "":

                    folder_name = "{0}{1}".format(base_folder_name, number) if res["quantity"] > 1 else "{0}".format(base_folder_name)

                else:
                    folder_name = "{0}".format(number) if res["quantity"] > 1 else "unnamed_folder"

                if node:
                    target_directory = node.path
                else:
                    target_directory = self.parent()._path

                skip = False
                if folder_name in files.list_dir_folders(target_directory):
                    skip = True
                if skip:
                    logger.info("Folder named {0} exsits at {1}. skipping...".format(folder_name, target_directory))
                    continue

                path = os.path.join(target_directory, folder_name)
                new_node = elements.CatagoryNode(folder_name, path=path, project=self.parent().parent.parent.project).create(path=path)

                if not node:

                    if self.model():
                        self.model().sourceModel().insertRows(0, 1, node=new_node)
                        self._proxyModel.invalidate()

                    else:
                        model = models.List_Model([new_node])
                        logger.info(model)
                        self.setModel_(model)

            if node and index:
                self.parent().update(index)

    def create_component(self, node, index=None):

        if node:
            ansestors = node.ansestors
        else:
            relative_path = files.reletive_path(self.parent().parent.parent.project.path, self.parent()._path)
            ansestors = files.splitall(relative_path)

        ansestors.pop(0)

        folderDlg = outliner.newComponentDialog(string="", ansestors = ansestors)
        result = folderDlg.exec_()
        res = folderDlg.result()
        if result == QtWidgets.QDialog.Accepted:
            logger.info(res)


            folder_name = res["name"]

            if node:
                target_directory = node.path
            else:
                target_directory = self.parent()._path
            #
            skip = False
            if folder_name in files.list_dir_folders(target_directory):
                skip = True
            if skip:
                logger.info("Folder named {0} exsits at {1}. skipping...".format(folder_name, target_directory))
                return
            #
            path = os.path.join(target_directory, folder_name)
            new_node = elements.ComponentNode(folder_name,
                                              path=path,
                                              format = res["format"],
                                              project=self.parent().parent.parent.project,
                                              version_file_type = res["version_file_type"],
                                              master_file_type = res["master_file_type"]).create(path=path)

            # create the actual component


            if not node:

                if self.model():
                    self.model().sourceModel().insertRows(0, 1, node=new_node)
                    self._proxyModel.invalidate()

                else:
                    model = models.List_Model([new_node])
                    logger.info(model)
                    self.setModel_(model)

                new_index = self.parent().set_selection(folder_name)
                self.parent().update(new_index)



            if node and index:

                self.parent().update(index)
                new_index = self.parent()._child.set_selection(folder_name)
                self.parent()._child.update(new_index)

            if res["option"] is not outliner.create_options.F_NONE:
                new_node.save_version(method=res["option"])

            return


# TODO: Add recursive creator