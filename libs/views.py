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
#
# import cPickle
import os
import functools
import logging

import pipeline.libs.config as cfg
import pipeline.libs.data as dt
import pipeline.libs.misc as misc
import pipeline.libs.models as models
import pipeline.libs.serializer as serializer
import pipeline.widgets.inputs as inputs
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore, QtCompat
import pipeline.apps.massage as massage
from  pipeline.libs import permissions
import pipeline.CSS
from pipeline.CSS import loadCSS

logger = logging.getLogger(__name__)

global counter

class Hierarchy_file_type_delegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.cb = None

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.LIGHT_GRAY_minus), 0.5))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.restore()
        super(Hierarchy_file_type_delegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):

        cb = QtWidgets.QComboBox(parent)
        cb.setStyleSheet("")
        cb.setEditable(False)

        roles = ["mayaAscii", "mayaBinary"]
        cb.addItems(roles)
        return cb

    def setEditorData(self, editor, index):
        cb = editor
        string = index.data(QtCore.Qt.EditRole)
        i = cb.findText(string)
        if i >= 0:
            cb.setCurrentIndex(i)
        else:
            cb.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        cb = editor
        model.setData(index, cb.currentText(), QtCore.Qt.EditRole)


class Hierarchy_branches_delegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.cb = None

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.LIGHT_GRAY_minus), 0.5))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.restore()
        super(Hierarchy_branches_delegate, self).paint(painter, option, index)



    def createEditor(self, parent, option, index):

        cb = QtWidgets.QComboBox(parent)
        cb.setStyleSheet("")
        cb.setEditable(True)

        roles = [cfg.Hierarcy_options.ASK_USER] + self.parent().branches
        cb.addItems(roles)
        return cb

    def setEditorData(self, editor, index):
        cb = editor
        string = index.data(QtCore.Qt.EditRole)
        i = cb.findText(string)
        if i >= 0:
            cb.setCurrentIndex(i)
        else:
            cb.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        cb = editor
        model.setData(index, cb.currentText(), QtCore.Qt.EditRole)

class Hierarchy_name_delegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.cb = None

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.LIGHT_GRAY_minus), 0.5))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.restore()
        super(Hierarchy_name_delegate, self).paint(painter, option, index)


    def createEditor(self, parent, option, index):

        cb = QtWidgets.QComboBox(parent)
        cb.setStyleSheet("")
        cb.setEditable(True)

        roles = [str(index.data()), cfg.Hierarcy_options.ASK_USER]
        cb.addItems(roles)
        return cb

    def setEditorData(self, editor, index):
        cb = editor
        string = str(index.data(QtCore.Qt.EditRole))
        i = cb.findText(string)
        if i >= 0:
            cb.setCurrentIndex(i)
        else:
            cb.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        cb = editor
        model.setData(index, cb.currentText(), QtCore.Qt.EditRole)


class Hierarchy_quantitiy_delegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.cb = None

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.LIGHT_GRAY_minus), 0.5))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.restore()
        super(Hierarchy_quantitiy_delegate, self).paint(painter, option, index)


    def createEditor(self, parent, option, index):

        cb = QtWidgets.QComboBox(parent)
        cb.setStyleSheet("")
        roles = [cfg.Hierarcy_options.SINGLE, cfg.Hierarcy_options.MULTIPLE]
        cb.addItems(roles)
        return cb

    def setEditorData(self, editor, index):
        cb = editor
        string = index.data(QtCore.Qt.EditRole)
        i = cb.findText(string)
        if i >= 0:
            cb.setCurrentIndex(i)
        else:
            cb.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        cb = editor
        model.setData(index, cb.currentText(), QtCore.Qt.EditRole)

class RoleComboBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.cb = None

    def createEditor(self, parent, option, index):

        cb = QtWidgets.QComboBox(parent)
        roles = permissions.Permissions.roles.keys()
        cb.addItems(roles)
        return cb

    def setEditorData(self, editor, index):
        cb = editor
        string = index.data(QtCore.Qt.EditRole)
        i = cb.findText(string)
        if i >= 0:
            cb.setCurrentIndex(i)
        else:
            cb.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        cb = editor
        model.setData(index, cb.currentText(), QtCore.Qt.EditRole)


class LinkProjectButtonDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):


            id = self.parent().model().mapToSource(index)
            project = self.parent().model().sourceModel().getNode(id)
            if not project.online():
                label = "Link"
                icon = cfg.link_off_icon
                func = self.parent().linkProject
            else:
                label = "Online"
                icon = cfg.link_on_icon
                func = self.parent().dummy


            button = QtWidgets.QPushButton(
                label,
                index.data(),
                self.parent(),
                clicked=func
            )
            button.setStyleSheet(cfg.table_button_stylesheet)
            button.setIconSize(QtCore.QSize(20, 20))
            button.setIcon(QtGui.QIcon(icon))
            self.parent().setIndexWidget(index, button)

class EditProjectButtonDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            label = "Edit"
            icon = cfg.edit_icon

            button = QtWidgets.QPushButton(
                label,
                index.data(),
                self.parent(),
                clicked=self.parent().editProject
            )

            button.setIconSize(QtCore.QSize(20, 20))
            button.setIcon(QtGui.QIcon(icon))
            button.setStyleSheet(cfg.table_button_stylesheet)


            index_ = self.parent().model().mapToSource(index)
            project = self.parent().model().sourceModel().getNode(index_)
            enable = True
            if project.project_users:

                user = self.parent().parent.pipeline_window.settings.user[0]
                password = self.parent().parent.pipeline_window.settings.user[1]
                role = project.validate_user(user, password)
                if role != 'administrator':
                    enable = False

            button.setEnabled(enable)


            self.parent().setIndexWidget(index, button)


class SetProjectButtonDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            label = "Set project"
            icon = cfg.set_icon

            button = QtWidgets.QPushButton(
                label,
                index.data(),
                self.parent(),
                clicked=self.parent().setProject
            )

            button.setIconSize(QtCore.QSize(20, 20))
            button.setIcon(QtGui.QIcon(icon))
            button.setStyleSheet(cfg.table_button_stylesheet)
            self.parent().setIndexWidget(index, button)


# class Notes_View(QtWidgets.QTableView):
#     def __init__(self, parent=None):
#         super(Notes_View, self).__init__(parent)
#         self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         self.setWordWrap(True)
#
#     def setModel(self, model=None):
#         super(Notes_View, self).setModel(model)
#
#         self.horizontalHeader().resizeSection(0, 50)
#
#         QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)
#
#
#         self.horizontalHeader().resizeSection(1, 100)
#         QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)
#
#         QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.ResizeToContents)
#
#
#         self.horizontalHeader().setStretchLastSection(True)
#

# class Project_Levels_View(QtWidgets.QTableView):
#     def __init__(self, parent=None):
#         super(Project_Levels_View, self).__init__(parent)
#
#         self.verticalHeader().setHidden(True)
#         self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
#
#     def setModel(self, model=None):
#         super(Project_Levels_View, self).setModel(model)
#
#
#         self.horizontalHeader().resizeSection(0, 30)
#
#         QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)
#
#         for i in range(1, self.horizontalHeader().count()):
#
#             QtCompat.setSectionResizeMode(self.horizontalHeader(), i, QtWidgets.QHeaderView.ResizeToContents)
#
#         self.horizontalHeader().setStretchLastSection(True)
#

class Project_Users_View(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(Project_Users_View, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)


    def setModel(self, model=None):
        super(Project_Users_View, self).setModel(model)
        self.setItemDelegateForColumn(2, RoleComboBoxDelegate(self))

        QtCompat.setSectionResizeMode(self.horizontalHeader(), QtWidgets.QHeaderView.Stretch)
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

    def contextMenuEvent(self, event):

        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()

        actions = []
        actions.append(QtWidgets.QAction("New user", menu, triggered=functools.partial(self.new_user, index)))
        actions.append(QtWidgets.QAction("Import users from a json file", menu, triggered=self.import_users))

        if index.isValid():
            actions.append(QtWidgets.QAction("Remove user", menu, triggered=functools.partial(self.remove_user, index)))
        menu.addActions(actions)

        menu.exec_(event.globalPos())
        event.accept()  # TELL QT IVE HANDLED THIS THING
        return

    def remove_user(self, index):
        row = index.row()
        parent = index.parent()
        self.model().removeRows(row, 1, parent)

    def new_user(self, index):
        user = dt.UserNode("New user", "1234", cfg._admin_)
        if index.isValid():
            row = index.row()
        else:
            row = len(self.model().items)

        self.model().insertRows(row + 1, 1, QtCore.QModelIndex(), node=user)

    def import_users(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Select the users file", filter="json files (*.json)")
        if path[0]:
            users_file = serializer.JSONSerializer(path=str(path[0]))
            users_file = users_file.read()
            print users_file, "="
            self.setModel(None)
            users = []
            for key in users_file:
                users.append(dt.UserNode(key, users_file[key][0], users_file[key][1]))

            if users:
                self.setModel(models.Users_Model(users))



class Hierarcy_components_view(QtWidgets.QTableView):
    def __init__(self, parentWidget=None, parent=None, branches = list()):
        super(Hierarcy_components_view, self).__init__(parent)

        self.branches = branches
        self.parent = parent
        self.parentWidget = parentWidget
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.setShowGrid(False)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def clearModel(self):
        self.setModel(None)

    def setModel_(self, model=None,  delegates = True):
        self.clearModel()
        if model:
            self.setModel(model)
            # size the load button column

            self.horizontalHeader().resizeSection(5, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(4, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(3, 60)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(2, 120)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(0, 30)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            if delegates:
                self.setItemDelegateForColumn(1, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(2, Hierarchy_branches_delegate(self))
                self.setItemDelegateForColumn(3, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(4, Hierarchy_file_type_delegate(self))
                self.setItemDelegateForColumn(5, Hierarchy_file_type_delegate(self))
            else:
                self.setItemDelegateForColumn(1, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(2, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(3, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(4, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(5, Preset_generator_table_Delegate(self))


            self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

            return True

        self.setModel(None)
        return None

    def contextMenuEvent(self, event):

        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        if index.isValid():
            # actions = []
            menu.addAction(QtWidgets.QAction("Remove component", menu, triggered=functools.partial(self.remove, index)))

        menu.addAction(QtWidgets.QAction("Add component", menu, triggered=functools.partial(self.add, index)))
        # menu.addActions(actions)

        menu.exec_(event.globalPos())
        event.accept()  # TELL QT IVE HANDLED THIS THING
        return


    def remove(self, index):
        row = index.row()
        parent = index.parent()
        self.model().removeRows(row, 1, parent)

    def add(self, index):

        cat = dt.Hierarcy_component_node(name=cfg.Hierarcy_options.ASK_USER ,branch=cfg.Hierarcy_options.ASK_USER)
        if self.model():

            if index.isValid():
                row = index.row()
            else:
                row = len(self.model().items)

            self.model().insertRows(row + 1, 1, QtCore.QModelIndex(), node=cat)
        else:
            self.setModel_(models.Hierarchy_component_Model([cat]))

class Hierarcy_catagories_view(QtWidgets.QTableView):
    def __init__(self, parentWidget=None, parent=None):
        super(Hierarcy_catagories_view, self).__init__(parent)

        self.parent = parent
        self.parentWidget = parentWidget
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.setShowGrid(False)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def clearModel(self):
        self.setModel(None)

    def setModel_(self, model=None, delegates = True):
        self.clearModel()
        if model:
            self.setModel(model)
            # size the load button column
            self.horizontalHeader().resizeSection(7, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 6, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(6, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 6, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(5, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 5, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(4, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 4, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(3, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(2, 150)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(1, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            self.horizontalHeader().resizeSection(0, 30)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            if delegates:

                self.setItemDelegateForColumn(1, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(2, Hierarchy_quantitiy_delegate(self))
                self.setItemDelegateForColumn(3, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(4, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(5, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(6, Hierarchy_name_delegate(self))
                self.setItemDelegateForColumn(7, Hierarchy_name_delegate(self))

            else:
                self.setItemDelegateForColumn(7, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(6, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(5, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(4, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(3, Preset_generator_table_Delegate(self))
                self.setItemDelegateForColumn(1, Preset_generator_table_Delegate(self))
                self.setColumnHidden(2, True)

            self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

            return True

        self.setModel(None)
        return None

    def contextMenuEvent(self, event):

        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        if index.isValid():
            # actions = []
            menu.addAction(QtWidgets.QAction("Move up", menu, triggered=functools.partial(self.move_up, index)))
            menu.addAction(QtWidgets.QAction("move down", menu, triggered=functools.partial(self.move_down, index)))
            menu.addSeparator()
            menu.addAction(QtWidgets.QAction("Remove category level", menu, triggered=functools.partial(self.remove, index)))

        menu.addAction(QtWidgets.QAction("Add category level", menu, triggered=functools.partial(self.add, index)))
        # menu.addActions(actions)

        menu.exec_(event.globalPos())
        event.accept()  # TELL QT IVE HANDLED THIS THING
        return


    def remove(self, index):
        row = index.row()
        parent = index.parent()
        self.model().removeRows(row, 1, parent)

    def add(self, index):
        cat = dt.Hierarcy_folder_node(name=cfg.Hierarcy_options.ASK_USER ,quantity=cfg.Hierarcy_options.SINGLE)
        if self.model():
            if index.isValid():
                row = index.row()
            else:
                row = len(self.model().items)

            self.model().insertRows(row + 1, 1, QtCore.QModelIndex(), node=cat)
        else:
            self.setModel_(models.Hierarchy_folders_Model([cat]))

    def move_up(self, index):
        self.model().move_up(index.row())

    def move_down(self, index):
        self.model().move_down(index.row())


class Projects_View(QtWidgets.QTableView):
    def __init__(self, parentWidget=None, parent=None):
        super(Projects_View, self).__init__(parent)

        self.parent = parent
        self.parentWidget = parentWidget
        self.setShowGrid(False)
        # self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setWordWrap(True)

        QtCompat.setSectionResizeMode(self.verticalHeader(), QtWidgets.QHeaderView.Fixed)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setSortingEnabled(True)

        # Set the delegate for column 0 of our table
        self._proxyModel = None

    def addSlider(self):

        self._slider = IconScaleSlider(self)
        self.parentWidget.layout().addWidget(self._slider)
        self._slider.listSlider.sliderMoved.connect(self.icons_size)

        self.icons_size(32)

    def icons_size(self, int):
        self.setIconSize(QtCore.QSize(int, int))
        self.update()

    def clearModel(self):
        self.setModel(None)
        if self._proxyModel:
            self._proxyModel.setSourceModel(None)
            self._proxyModel = None

    def setModel_(self, model=None):
        self.clearModel()
        if model:
            self._proxyModel = models.Projects_ProxyModel()
            self._proxyModel.setSourceModel(model)
            self.setModel(self._proxyModel)
            # size the load button column
            self.horizontalHeader().resizeSection(3, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 4, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(2, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(1, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Fixed)
            #
            # self.horizontalHeader().resizeSection(0, 30)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            # setup the buttons for loading and more options with delegates
            # self.setItemDelegateForColumn(0, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(1, Standard_table_Delegate(self))
            self.setItemDelegateForColumn(2, LinkProjectButtonDelegate(self))
            self.setItemDelegateForColumn(3, EditProjectButtonDelegate(self))
            self.setItemDelegateForColumn(4, SetProjectButtonDelegate(self))

            self.setCurrentIndex(self.model().sourceModel().index(0, 0, None))

            self.setColumnHidden(0, True)

            return True

        self.setModel(None)
        return None
        # self.setCurrentIndex(self.model().index(0,0, None))

    def editProject(self):
        button = self.sender()
        index = self.indexAt(button.pos())
        index = self.model().mapToSource(index)
        if self.model().sourceModel().items[0].typeInfo() == cfg._new_:
            self.model().sourceModel().items[0].parent().initialVersion()
        else:
            self.model().sourceModel().getNode(index).edit()
            self.setCurrentIndex(index)

    def setProject(self):

        button = self.sender()
        index = self.indexAt(button.pos())
        index = self.model().mapToSource(index)
        if self.model().sourceModel().items[0].typeInfo() == cfg._new_:
            self.model().sourceModel().items[0].parent().initialVersion()
        else:
            self.model().sourceModel().getNode(index).set()
            self.setCurrentIndex(index)

    def linkProject(self):

        button = self.sender()
        index = self.indexAt(button.pos())
        index = self.model().mapToSource(index)
        project = self.model().sourceModel().getNode(index)
        project.link()
        self.model().sourceModel().reset()
        self.viewport().repaint()

    # def asModelIndex(self, index):
    #     return self.proxyModel.mapToSource(index)
    #
    # def asModelNode(self, index):
    #     return self.sourceModel.getNode(index)

    def contextMenuEvent(self, event):

        handled = True
        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            src = self._proxyModel.mapToSource(index)
            node = self._proxyModel.sourceModel().getNode(src)

        def_actions = list()

        if node:
            def_actions.append(QtWidgets.QAction("Explore...", menu,
                                                 triggered=functools.partial(self.explore, node)))
        else:
            event.accept()
            return

        menu.addActions(def_actions)
        menu.exec_(event.globalPos())
        event.accept()

        return

    def explore(self, node):
        node.explore()

    def dummy(self):
        pass



class Run_scripts_View(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(Run_scripts_View, self).__init__(parent)

        # self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.verticalHeader().setHidden(True)


    def setModel(self, model=None):

        super(Run_scripts_View, self).setModel(model)
        # self.horizontalHeader().resizeSection(0, 35)  # self._slider.listSlider.value())
        QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Stretch)

        self.horizontalHeader().resizeSection(1, 80)
        QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)

        # self.horizontalHeader().setStretchLastSection(False)

        # QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)

    #     self.setItemDelegateForColumn(2, RoleComboBoxDelegate(self))
    #
    #     QtCompat.setSectionResizeMode(self.horizontalHeader(), QtWidgets.QHeaderView.Stretch)
    #     self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

    # def contextMenuEvent(self, event):
    #
    #     index = self.indexAt(event.pos())
    #     menu = QtWidgets.QMenu()
    #
    #     actions = []
    #     actions.append(QtWidgets.QAction("New user", menu, triggered=functools.partial(self.new_user, index)))
    #     actions.append(QtWidgets.QAction("Import users from a json file", menu, triggered=self.import_users))
    #
    #     if index.isValid():
    #         actions.append(QtWidgets.QAction("Remove user", menu, triggered=functools.partial(self.remove_user, index)))
    #     menu.addActions(actions)
    #
    #     menu.exec_(event.globalPos())
    #     event.accept()  # TELL QT IVE HANDLED THIS THING
    #     return

    # def remove_user(self, index):
    #     row = index.row()
    #     parent = index.parent()
    #     self.model().removeRows(row, 1, parent)
    #
    # def new_user(self, index):
    #     user = dt.UserNode("New user", "1234", cfg._admin_)
    #     if index.isValid():
    #         row = index.row()
    #     else:
    #         row = len(self.model().items)
    #
    #     self.model().insertRows(row + 1, 1, QtCore.QModelIndex(), node=user)
    #
    # def import_users(self):
    #     path = QtWidgets.QFileDialog.getOpenFileName(self, "Select the users file", filter="json files (*.json)")
    #     if path[0]:
    #         users_file = serializer.JSONSerializer(path=str(path[0]))
    #         users_file = users_file.read()
    #         print users_file, "="
    #         self.setModel(None)
    #         users = []
    #         for key in users_file:
    #             users.append(dt.UserNode(key, users_file[key][0], users_file[key][1]))
    #
    #         if users:
    #             self.setModel(models.Users_Model(users))



class HoverDelegate(QtWidgets.QStyledItemDelegate ): #QStyledItemDelegate
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.hovered_row = -1

    def hover_signal_change(self, row):
        self.hovered_row = row

    def paint(self, painter, option, index):

        if index.row() == self.hovered_row:
            painter.save()
            painter.fillRect(option.rect, QtGui.QColor('#646464') )
            painter.setBrush(QtGui.QColor('#000'))
            painter.setPen(QtGui.QColor("#000000"))
            value = index.data(QtCore.Qt.DisplayRole)
            value = str(value) if value else ''

            painter.translate(5, 8)
            # font = QtGui.QFont()
            # font.setPointSize(9)
            # painter.setFont(font)
            painter.drawText(option.rect, QtCore.Qt.AlignLeft, value)
            painter.restore()
        else:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)


class loadButtonDelegate(QtWidgets.QItemDelegate):
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """

    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.hovered_row = -1



    def hover_signal_change(self, row):
        self.hovered_row = row

    def eventFilter(self, sender, event):

        if event.type() == QtCore.QEvent.Leave:
            self.parent().hover_signal.emit(-1)
            return True


        if event.type() == QtGui.QMouseEvent:
            self.parent().mouseMoveEvent(event)
            return True
        # if event.type() == QtCore.QEvent.Enter:
        #     self.parent().mouseMoveEvent(event)
        #     return True

        return False

    def paint(self, painter, option, index):
        # This method will be called every time a particular cell is
        # in view and that view is changed in some way. We ask the 
        # delegates parent (in this case a table view) if the index
        # in question (the table cell) already has a widget associated 
        # with it. If not, create one with the text for this index and
        # connect its clicked signal to a slot in the parent view so 
        # we are notified when its used and can do something.

        # painter.save()
        # painter.setPen(QtGui.QColor(cfg.colors.LIGHT_GRAY))
        # painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        # painter.restore()
        if index.row() == self.hovered_row:
            painter.fillRect(option.rect, QtGui.QColor('#646464'))
        else:
            pass

        if not self.parent().indexWidget(index):
            soure_index = self.parent().model().mapToSource(index)
            if self.parent().model().sourceModel().getNode(soure_index).typeInfo() == cfg._new_:
                label = ""
                icon = cfg.new_icon
            if self.parent().model().sourceModel().getNode(soure_index).typeInfo() == cfg._playblast_:
                label = ""
                icon = cfg.play_icon
            if self.parent().model().sourceModel().getNode(
                    soure_index).typeInfo() == cfg._version_ or self.parent().model().sourceModel().getNode(
                    soure_index).typeInfo() == cfg._master_:
                label = ""
                icon = self.parent().model().sourceModel().getNode(soure_index).status_icon

            button = QtWidgets.QPushButton(
                label,
                self.parent(),
                clicked=self.parent().MultiButtonClicked
            )
            button.setStyleSheet(cfg.table_button_stylesheet)
            button.setIconSize(QtCore.QSize(20, 20))

            button.setMouseTracking(True)
            button.setAttribute(QtCore.Qt.WA_Hover, True)
            button.installEventFilter(self)

            table_button_stylesheet = '''
                        QPushButton{
                        border: 0px none;
                        border-radius: 0px;
                        border-bottom: 1px solid #555555;
                        background-color: transparent;
                        }
                        QPushButton::hover {
                        background-color: #808080;
                        }
                        QPushButton::pressed {
                        background-color: #484848;
                        }
                        '''

            button.setStyleSheet(table_button_stylesheet)

            button.setIcon(QtGui.QIcon(icon))
            self.parent()._buttons.append(button)
            self.parent().setIndexWidget(index, button)


class Library_delegate(QtWidgets.QItemDelegate):
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """

    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QtWidgets.QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        # This method will be called every time a particular cell is
        # in view and that view is changed in some way. We ask the
        # delegates parent (in this case a table view) if the index
        # in question (the table cell) already has a widget associated
        # with it. If not, create one with the text for this index and
        # connect its clicked signal to a slot in the parent view so
        # we are notified when its used and can do something.
        if not self.parent().indexWidget(index):
            soure_index = self.parent().model().mapToSource(index)

            label = ""
            icon = cfg.load_icon#self.parent().model().sourceModel().getNode(soure_index).status_icon

            button = QtWidgets.QPushButton(
                label,
                self.parent(),
                clicked=self.parent().MultiButtonClicked
            )

            button.setIconSize(QtCore.QSize(20, 20))
            button.setStyleSheet(cfg.table_button_stylesheet)
            button.setIcon(QtGui.QIcon(icon))
            self.parent()._buttons.append(button)
            self.parent().setIndexWidget(index, button)






class Preset_generator_table_Delegate(QtWidgets.QItemDelegate):


    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):

        if index.column() > 2:
            editor = QtWidgets.QSpinBox(parent)
            editor.setMinimum(0)
            editor.setMaximum(999)

        else:
            editor = QtWidgets.QLineEdit(parent)

        return editor

    def setEditorData(self, editor, index):
        if index.column() > 2:
            value = int(index.model().data(index, QtCore.Qt.EditRole)) if index.model().data(index, QtCore.Qt.EditRole) != '' else 0
            editor.setValue(value)
        else:
            value = index.model().data(index, QtCore.Qt.EditRole)
            editor.setText(value)

    def setModelData(self, editor, model, index):
        if index.column() > 2:
            editor.interpretText()
            value = editor.value()
            model.setData(index, value, QtCore.Qt.EditRole)
        else:
            value = editor.text()
            if misc.validation_no_special_chars(value):
                model.setData(index, value, QtCore.Qt.EditRole)
            else:
                model.setData(index, 'NO_SPECIAL_CHARS', QtCore.Qt.EditRole)

    def paint(self, painter, option, index):

        painter.save()

        input_type = index.data(200)
        value = index.data(QtCore.Qt.EditRole)
        value = str(value)

        painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.LIGHT_GRAY_minus), 0.5))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        if input_type == cfg.Hierarcy_options.ASK_USER and value == '':

            painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.LIGHT_PURPLE), 0.5))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        if input_type == cfg.Hierarcy_options.ASK_USER and value != '':

            painter.setPen(QtGui.QPen(QtGui.QColor(cfg.colors.DARK_GRAY_MINUS), 0.5))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())


        painter.setPen(QtGui.QPen(QtCore.Qt.white))
        painter.translate(5, 8)
        painter.drawText(option.rect, QtCore.Qt.AlignLeft, value)
        painter.restore()


class Standard_table_Delegate(QtWidgets.QItemDelegate):
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """

    def __init__(self, parent):
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        QtWidgets.QItemDelegate.__init__(self, parent)
    #
    # def paint(self, painter, option, index):
    #     # set background color
    #     # painter.setPen(QtWidgets.QPen(QtCore.Qt.NoPen))
    #     # if option.state & QStyle.State_Selected:
    #     #     painter.setBrush(QBrush(Qt.red))
    #     # else:
    #     painter.save()
    #     role = index.data(200)
    #     value = index.data(QtCore.Qt.EditRole)
    #     value = str(value)
    #     if role == cfg.Hierarcy_options.ASK_USER and value == '':
    #         painter.setPen(QtWidgets.QPen(QtGui.QColor(cfg.colors.LIGHT_PURPLE_plus), 3.0))
    #         painter.drawRect(option.rect)
    #
    #     if role == cfg.Hierarcy_options.ASK_USER and value != '':
    #         painter.setPen(QtWidgets.QPen(QtGui.QColor(cfg.colors.LIGHT_PURPLE), 3.0))
    #         painter.drawRect(option.rect)
    #
    #     painter.setPen(QtWidgets.QPen(QtCore.Qt.white))
    #
    #     painter.translate(5, 8)
    #     painter.drawText(option.rect, QtCore.Qt.AlignLeft, value)
    #
    #     painter.restore()

        # painter.save()
        #
        # # set background color
        # painter.setPen(QPen(Qt.NoPen))
        # if option.state & QStyle.State_Selected:
        #     painter.setBrush(QColor("#3399FF"))
        # else:
        #     painter.setBrush(QBrush(Qt.white))
        # painter.drawRect(option.rect)
        #
        # # set text color
        # value = index.data(Qt.DisplayRole)
        # if option.state & QStyle.State_Selected:
        #     painter.setPen(QPen(Qt.white))
        # else:
        #     painter.setPen(QPen(Qt.black))
        #
        # # Left indent
        # painter.translate(3, 0)
        #
        # painter.drawText(option.rect, Qt.AlignLeft, value)
        #
        # painter.restore()


        # super(Standard_table_Delegate, self).paint(painter, option, index)
        # return
        # logger.info("working....")
        # painter.save()
        # painter.setPen(QtGui.QColor(cfg.colors.LIGHT_GRAY))
        # painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        # painter.restore()

        # if not self.parent().indexWidget(index):
        #
        #     if self.parent().model().data(index, QtCore.Qt.DecorationRole):
        #         super(Standard_table_Delegate, self).paint(painter, option, index)
        #
        #     else:
        #         # node = self.parent().model().sourceModel().getNode(soure_index)
        #         label = QtWidgets.QLabel((str(self.parent().model().data(index, QtCore.Qt.DisplayRole))))
        #         label.setMargin(5)
        #         self.parent().setIndexWidget(index, label)


        # def paint(self, painter, option, index):
    #
    #     # super(Standard_table_Delegate, self).paint(painter, option, index)
    #     # return
    #     # logger.info("working....")
    #     # painter.save()
    #     painter.setPen(QtGui.QColor(cfg.colors.LIGHT_GRAY))
    #     painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
    #     # painter.restore()
    #
    #     if not self.parent().indexWidget(index):
    #
    #         if self.parent().model().data(index, QtCore.Qt.DecorationRole):
    #             super(Standard_table_Delegate, self).paint(painter, option, index)
    #
    #         else:
    #             # node = self.parent().model().sourceModel().getNode(soure_index)
    #             label = QtWidgets.QLabel((str(self.parent().model().data(index, QtCore.Qt.DisplayRole))))
    #             label.setMargin(5)
    #             self.parent().setIndexWidget(index, label)


            # soure_index = self.parent().model().mapToSource(index)
            #
            # if self.parent().model().sourceModel().data(soure_index, QtCore.Qt.DecorationRole):
            #     super(Standard_table_Delegate, self).paint(painter, option, index)
            # else:
            #     # node = self.parent().model().sourceModel().getNode(soure_index)
            #     label = QtWidgets.QLabel((str(self.parent().model().sourceModel().data(soure_index, QtCore.Qt.DisplayRole))))
            #     label.setMargin(5)
            #     if self.parent().model().sourceModel().data(soure_index, QtCore.Qt.FontRole):
            #         label.setFont(self.parent().model().sourceModel().data(soure_index, QtCore.Qt.FontRole))
            #
            #     self.parent().setIndexWidget(index, label)
            #
            #
            #



class NoteDelegate(QtWidgets.QStyledItemDelegate):
    """
    A delegate that places a fully functioning QPushButton in every
    cell of the column to which it's applied
    """

    def __init__(self, parent):
        super(NoteDelegate, self).__init__(parent)
        # The parent is not an optional argument for the delegate as
        # we need to reference it in the paint method (see below)
        # QtWidgets.QItemDelegate.__init__(self, parent)
        # css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        # self.setStyleSheet(css)
        self.hovered_row = -1


    def hover_signal_change(self, row):
        self.hovered_row = row

    # def paint(self, painter, option, index):
    #
    #
    #     # painter.save()
    #     painter.setPen(QtGui.QColor(cfg.colors.LIGHT_GRAY))
    #     painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
    #     # painter.restore()
    #     super(NoteDelegate, self).paint(painter, option, index)
    #     # QtWidgets.QItemDelegate.paint(self, painter, option, index)

    def paint(self, painter, option, index):

        # painter.setPen(QtGui.QColor(cfg.colors.LIGHT_GRAY))
        # painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        # QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

        if index.row() == self.hovered_row:
            painter.save()

            painter.fillRect(option.rect, QtGui.QColor('#808080') )#'#646464'
            painter.setBrush(QtGui.QColor('#000'))
            painter.setPen(QtGui.QColor("#000000"))

            value = index.data(QtCore.Qt.DisplayRole)
            value = str(value) if value else 'Click to edit...'

            # font = QtGui.QFont()
            # font.setPointSize(9)
            # font.setItalic(True)
            # painter.setFont(font)

            text_rect = option.rect.adjusted(5, 8, 0, 0)
            painter.drawText(text_rect, QtCore.Qt.AlignLeft, value)

            painter.setClipRect(option.rect)
            painter.restore()

        else:
            painter.setPen(QtGui.QColor(cfg.colors.LIGHT_GRAY))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)




    def createEditor(self, parent, option, index):
        if index.column() == 1:
            source_index = self.parent().model().mapToSource(index)
            node = self.parent().model().sourceModel().getNode(source_index)
            note_inpute = inputs.MultilineInput(plainText=node.note, caption="Save note for {}".format(node.name))
            # note_inpute = inputs.MultilineInput(plainText = node.note, title = 'Commit massage', caption="Massage saved for {}".format(node.name), disabled = True)
            note = note_inpute.exec_()
            text = note_inpute.result()
            if note == QtWidgets.QDialog.Accepted:
                    # self.shot.note("versions",self.shot_version, note=text)



                # dlg = QtWidgets.QMessageBox()
                # dlg.exec_()
                # lineedit = QtWidgets.QLineEdit(parent)
                # soure_index = self.parent().model().mapToSource(index)
                self.parent().model().sourceModel().setData(source_index, text, role=QtCore.Qt.EditRole)
            # return lineedit
                return

        return

        # elif index.column() == 1:
        #     combo = QtGui.QComboBox(parent)
        #     return combo

    # def setEditorData(self, editor, index):
    #     row = index.row()
    #     column = index.column()
    #     soure_index = self.parent().model().mapToSource(index)
    #     # value = index.model().items[row][column]
    #     # if isinstance(editor, QtWidgets.QComboBox):
    #     #     editor.addItems(['Somewhere', 'Over', 'The Rainbow'])
    #     #     editor.setCurrentIndex(index.row())
    #     if isinstance(editor, QtWidgets.QLineEdit):
    #         editor.setText('Somewhere over the rainbow')


class Versions_View(QtWidgets.QTableView):
    hover_signal = QtCore.Signal(int)

    def __init__(self, parentWidget=None, parent=None, settings = None):
        super(Versions_View, self).__init__(parent)

        self.css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))

        self.role = settings.current_role
        self.permissions = permissions.Permissions

        self._buttons = []

        self.parent = parent
        self.parentWidget = parentWidget

        # self.setAlternatingRowColors(True)
        # self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setWordWrap(True)

        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.setSortingEnabled(True)

        self.setShowGrid(False)
        # self.setMouseTracking(True)

        # Set the delegate for column 0 of our table
        self._proxyModel = None
        self.horizontalHeader().setHidden(True)
        self.verticalHeader().setHidden(True)

        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.installEventFilter(self)

        self.setMouseTracking(True)
        self.viewport().setAttribute(QtCore.Qt.WA_Hover, True)

        # self.setStyleSheet('''
        #
        #     QTreeView::item:hover {
        #         background: #101010;
        #     }
        #     QTreeView {
        #         outline: 0;
        #     }
        #     ''')

    def eventFilter(self, sender, event):

        if event.type() == QtCore.QEvent.Leave:
            self.hover_signal.emit(-1)
            return True

        return False

    def mouseMoveEvent(self, event):

        row = self.indexAt(event.pos()).row()
        self.hover_signal.emit(row)

    def addSlider(self):

        self._slider = IconScaleSlider(self)

        self.parentWidget.layout().addWidget(self._slider)

        self._slider.listSlider.sliderMoved.connect(self.icons_size)

        self.icons_size(32)


    def icons_size(self, int):
        self.setIconSize(QtCore.QSize(int, int))
        self.horizontalHeader().resizeSection(0, int)
        self.verticalHeader().setDefaultSectionSize(int)

        # QtCompat.setSectionResizeMode(self.header(), 0, QtWidgets.QHeaderView.Fixed)

        try:

            self.model().sourceModel()._rowHeight = int
        except:
            pass
        #
        # self.update(QtCore.QModelIndex())

    def clearModel(self):
        self._buttons = []
        '''
        THIS IS CRASHING PySide2 and looks fine without this so so be it :)
        '''
        if isinstance(self._proxyModel, models.Versions_ProxyModel) or isinstance(self._proxyModel, models.Masters_ProxyModel) or isinstance(self._proxyModel, models.Playblasts_ProxyModel) \
                or isinstance(self._proxyModel, models.Simple_ProxyModel):
            m = self._proxyModel.sourceModel()
            self._proxyModel.setSourceModel(None)
            del m
            self.setModel(None)
            self._proxyModel = None



        # self.setModel(None)
        # if self._proxyModel:
        #     self._proxyModel.setSourceModel(None)
        #     self._proxyModel = None

    def setModel_(self, model=None):
        self.clearModel()
        if model:
            # model._rowHeight = self._slider.listSlider.value()
            self._proxyModel = models.Versions_ProxyModel()
            self._proxyModel.setSourceModel(model)

            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            self.setModel(self._proxyModel)

            # self.setIndentation(0)

            self.proxyModel = self.model()
            self.sourceModel = self.proxyModel.sourceModel()

            self.horizontalHeader().resizeSection(0, 35)#self._slider.listSlider.value())
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            # self.horizontalHeader().resizeSection(1, 32)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().setStretchLastSection(False)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            self.horizontalHeader().resizeSection(2, 100)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(3, 80)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(4, 60)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 4, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(5, 32)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 5, QtWidgets.QHeaderView.Fixed)

            row_del = HoverDelegate(self)
            note_del = NoteDelegate(self)
            load_del = loadButtonDelegate(self)

            self.hover_signal.connect(row_del.hover_signal_change)
            self.hover_signal.connect(note_del.hover_signal_change)
            self.hover_signal.connect(load_del.hover_signal_change)

            self.setItemDelegate(row_del)

            # setup the buttons for loading and more options with delegates
            self.setItemDelegateForColumn(5, load_del)

            # note delegate
            self.setItemDelegateForColumn(1, note_del)


            self.sortByColumn(0, QtCore.Qt.DescendingOrder)
            self.verticalHeader().setDefaultSectionSize(32)

            '''
            This is to hide the author column if no users are in the active project
            '''
            if not self.parent.project.users:
                self.setColumnHidden(4, True)
            else:
                self.setColumnHidden(4, False)


            # self.update()

    def MultiButtonClicked(self):
        # This slot will be called when our button is clicked.
        # self.sender() returns a refence to the QPushButton created
        # by the delegate, not the delegate itself.
        button = self.sender()
        index = self.indexAt(button.pos())
        index = self.model().mapToSource(index)
        if self.model().sourceModel().getNode(index).typeInfo() == cfg._new_:
            node = self.model().sourceModel().getNode(index).parent()
            node.initialVersion()
            self._proxyModel.invalidate()

        else:
            if self.model().sourceModel().getNode(index).load():
                pass
                # self.parent.set_thumbnail(self.model().sourceModel().getNode(index).resource)
                # self.parent.version = self.model().sourceModel().getNode(index)
                # self.setCurrentIndex(self.model().mapFromSource(index))
                # for btn in self._buttons:
                #     btn.setIcon(QtGui.QIcon(cfg.folder_open_icon))
                #
                # button.setIcon(QtGui.QIcon(cfg.reload_icon))



            # try:
            #     version_buttons = self.parent.mastersView._buttons
            #     for btn in self.version_buttons:
            #         btn.setIcon(QtGui.QIcon(cfg.open_icon))
            # except:
            #     print "can not reset versions table"

    def contextMenuEvent(self, event):

        handled = True
        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            src = self.asModelIndex(index)
            node = self.asModelNode(src)


        rows = self.selectionModel().selectedRows()
        if rows:
            node = [self.asModelNode(self.asModelIndex(r)) for r in rows]




        actions = list()
        def_actions = list()

        if node:

            # if node.typeInfo() == cfg._version_:
            if isinstance(node, list):
                if len(node)==1:

                    if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.reference_version):
                        actions.append(QtWidgets.QAction("Reference {} into the current scene".format(node[0].fullName), menu,triggered=functools.partial(self.reference_, node)))

                    if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.import_version):
                        actions.append(QtWidgets.QAction("Import {} into the current scene".format(node[0].fullName), menu,triggered=functools.partial(self.import_, node)))

            if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.delete):
                actions.append(QtWidgets.QAction("Delete...", menu,triggered=functools.partial(self.delete, node)))

            def_actions.append(QtWidgets.QAction("Explore...", menu,triggered=functools.partial(self.explore, node)))


        else:

            if self.parent.current_component:
                pass
                # actions.append(QtWidgets.QAction("Explore...", menu,
                #                                  triggered=functools.partial(self.explore, self.parent.current_component)))
            else:
                event.accept()
                return




        menu.addActions(actions)
        menu.addSeparator()
        menu.addActions(def_actions)
        menu.setStyleSheet(self.css)
        menu.exec_(event.globalPos())
        event.accept()

        return

    def delete(self, node):

        if massage.warning("warning", "Delete", "Are you sure you want to delete these versions?"):
            if isinstance(node, list):
                for n in node:
                    n.delete()

            self.parent.current_component.refresh()
            # logger.info(self.parent.current_component.name)


    def explore(self, node):
        if isinstance(node, list):
            node[0].explore()

    def reference_(self, node):
        if isinstance(node, list):
            node[0].reference_()

    def import_(self, node):
        if isinstance(node, list):
            node[0].import_()


    # def deletActionClicked(self):
    #     # This slot will be called when our button is clicked.
    #     # self.sender() returns a refence to the QPushButton created
    #     # by the delegate, not the delegate itself.
    #     button = self.sender().parent()
    #     index = self.indexAt(button.pos())
    #     index = self.model().mapToSource(index)
    #     self.model().sourceModel().getNode(index).delete_me()

    def asModelIndex(self, index):
        return self.proxyModel.mapToSource(index)

    def asModelNode(self, index):
        return self.sourceModel.getNode(index)

    @property
    def proxyModel(self):
        return self._proxyModel

    @proxyModel.setter
    def proxyModel(self, model):
        self._proxyModel = model

    @property
    def sourceModel(self):
        return self._sourceModel

    @sourceModel.setter
    def sourceModel(self, model):
        self._sourceModel = model


class Masters_View(Versions_View):
    def __init__(self, parentWidget=None, parent=None, settings = None):
        super(Masters_View, self).__init__(parentWidget, parent, settings)

    def setModel_(self, model=None):
        self.clearModel()
        if model:
            # model._rowHeight = self._slider.listSlider.value()
            self._proxyModel = models.Masters_ProxyModel()
            self._proxyModel.setSourceModel(model)

            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            self.setModel(self._proxyModel)

            # self.setIndentation(0)

            self.proxyModel = self.model()
            self.sourceModel = self.proxyModel.sourceModel()

            self.horizontalHeader().resizeSection(0, 32)  # self._slider.listSlider.value())
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            # self.horizontalHeader().resizeSection(1, 32)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().setStretchLastSection(False)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            self.horizontalHeader().resizeSection(2, 60)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(3, 110)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(4, 80)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 4, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(5, 60)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 5, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(6, 32)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 6, QtWidgets.QHeaderView.Fixed)

            row_del = HoverDelegate(self)
            note_del = NoteDelegate(self)
            load_del = loadButtonDelegate(self)

            self.hover_signal.connect(row_del.hover_signal_change)
            self.hover_signal.connect(note_del.hover_signal_change)
            self.hover_signal.connect(load_del.hover_signal_change)

            self.setItemDelegate(row_del)

            # setup the buttons for loading and more options with delegates
            self.setItemDelegateForColumn(6, load_del)

            # note delegate
            self.setItemDelegateForColumn(1, note_del)

            # setup the buttons for loading and more options with delegates
            # self.setItemDelegateForColumn(6, loadButtonDelegate(self))
            # self.setItemDelegateForColumn(1, NoteDelegate(self))

            # self.setItemDelegateForColumn(0, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(2, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(3, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(4, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(5, Standard_table_Delegate(self))


            self.sortByColumn(0, QtCore.Qt.DescendingOrder)
            self.verticalHeader().setDefaultSectionSize(32)

            '''
            This is to hide the author column if no users are in the active project
            '''
            if not self.parent.project.users:
                self.setColumnHidden(4, True)
            else:
                self.setColumnHidden(4, False)

            if model.items[0].number == 0:
                self.setColumnHidden(0, True)
            else:
                self.setColumnHidden(0, False)

    def contextMenuEvent(self, event):

        handled = True
        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            src = self.asModelIndex(index)
            node = self.asModelNode(src)

        rows = self.selectionModel().selectedRows()
        if rows:
            node = [self.asModelNode(self.asModelIndex(r)) for r in rows]

        actions = list()
        def_actions = list()

        if node:

            # if node.typeInfo() == cfg._version_:
            if isinstance(node, list):
                if len(node) == 1:


                    if node[0].number is not 0:
                        if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.revert_master):
                            actions.append(QtWidgets.QAction("Revert master to {}".format(node[0].fullName), menu, triggered=functools.partial(self.revert_, node)))

                    if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.reference_version):
                        actions.append(QtWidgets.QAction("Reference {} into the current scene".format(node[0].fullName), menu,triggered=functools.partial(self.reference_, node)))

                    if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.import_version):
                        actions.append(QtWidgets.QAction("Import {} into the current scene".format(node[0].fullName), menu,triggered=functools.partial(self.import_, node)))

            if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.delete):
                actions.append(QtWidgets.QAction("Delete...", menu,triggered=functools.partial(self.delete, node)))

            def_actions.append(QtWidgets.QAction("Explore...", menu,
                                             triggered=functools.partial(self.explore, node)))

        else:

            if self.parent.current_component:
                pass
                # actions.append(QtWidgets.QAction("Explore...", menu,
                #                                  triggered=functools.partial(self.explore, self.parent.current_component)))
            else:
                event.accept()
                return

        menu.addActions(actions)
        menu.addSeparator()
        menu.addActions(def_actions)
        menu.setStyleSheet(self.css)
        menu.exec_(event.globalPos())
        event.accept()

        return

    def revert_(self, node):
        if isinstance(node, list):
            msg = "Are you sure you want to revert your master to {}?".format(node[0].fullName)
            prompt = massage.PromptUser(self, prompt=msg, override_yes_text="Yes", override_no_label="No")
            result = prompt.exec_()
            # logger.info(result)
            # logger.info()

            if result == 0:
                node[0].revert_()

        # self.update()

                # def setModel_(self, model=None):
    #     self.clearModel()
    #     if model:
    #         model._rowHeight = self._slider.listSlider.value()
    #         self._proxyModel = models.Masters_ProxyModel()
    #         self._proxyModel.setSourceModel(model)
    #         self._proxyModel.setDynamicSortFilter(True)
    #         self._proxyModel.setSortRole(models.Masters_Model.sortRole)
    #         self.setModel(self._proxyModel)
    #
    #         self.setIndentation(0)
    #         self.expandAll()
    #
    #         self.header().resizeSection(0, self._slider.listSlider.value())
    #
    #         QtCompat.setSectionResizeMode(self.header(), 0, QtWidgets.QHeaderView.Fixed)
    #         self.header().resizeSection(1, 32)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 1, QtWidgets.QHeaderView.Fixed)
    #
    #         self.header().setStretchLastSection(False)
    #
    #
    #         QtCompat.setSectionResizeMode(self.header(), 2, QtWidgets.QHeaderView.Stretch)
    #         QtCompat.setSectionResizeMode(self.header(), 3, QtWidgets.QHeaderView.Stretch)
    #         QtCompat.setSectionResizeMode(self.header(), 4, QtWidgets.QHeaderView.Stretch)
    #
    #         self.header().resizeSection(5, 50)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 5, QtWidgets.QHeaderView.Fixed)
    #         self.header().resizeSection(6, 32)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 6, QtWidgets.QHeaderView.Fixed)
    #         self.header().resizeSection(7, 32)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 7, QtWidgets.QHeaderView.Fixed)
    #
    #         self.setItemDelegateForColumn(7, loadButtonDelegate(self))
    #
    #         self.sortByColumn(1, QtCore.Qt.DescendingOrder)
    #
    #         self.proxyModel = self.model()
    #         self.sourceModel = self.proxyModel.sourceModel()
    #         # self.update()

    # def MultiButtonClicked(self):
    #     # This slot will be called when our button is clicked.
    #     # self.sender() returns a refence to the QPushButton created
    #     # by the delegate, not the delegate itself.
    #     button = self.sender()
    #     index = self.indexAt(button.pos())
    #     index = self.model().mapToSource(index)
    #     if self.model().sourceModel().getNode(index).typeInfo() == cfg._new_:
    #         parent_index = index.parent()
    #         node = self.model().sourceModel().getNode(index).parent()
    #         self.model().sourceModel().removeRows(index.row(), 1, parent_index)
    #         node.initialVersion()
    #     else:
    #         self.model().sourceModel().getNode(index).load()
    #         self.parent.set_thumbnail(self.model().sourceModel().getNode(index).resource)
    #         self.parent.version = self.model().sourceModel().getNode(index)
    #         self.setCurrentIndex(self.model().mapFromSource(index))
    #         for btn in self._buttons:
    #             btn.setIcon(QtGui.QIcon(cfg.open_icon))
    #
    #         button.setIcon(QtGui.QIcon(cfg.reload_icon))
    #         # try:
    #         #     version_buttons = self.parent.versionsView._buttons
    #         #     for btn in self.version_buttons:
    #         #         btn.setIcon(QtGui.QIcon(cfg.open_icon))
    #         # except:
    #         #     print "can not reset versions table"
    #
    # def contextMenuEvent(self, event):
    #
    #     handled = True
    #     index = self.indexAt(event.pos())
    #     menu = QtWidgets.QMenu()
    #     node = None
    #
    #     if index.isValid():
    #         src = self.asModelIndex(index)
    #         node = self.asModelNode(src)
    #
    #     actions = []
    #
    #     if node and not node._deathrow:
    #
    #         if node.typeInfo() == cfg._master_:
    #
    #             actions.append(QtWidgets.QAction("Explore...", menu,
    #                                          triggered=functools.partial(self.explore, src)))
    #         else:
    #
    #             event.accept()
    #             return
    #
    #     else:
    #         event.accept()
    #         return
    #
    #     menu.addActions(actions)
    #
    #     menu.exec_(event.globalPos())
    #     event.accept()
    #
    #     return


class Playblasts_View(Versions_View):
    def __init__(self, parentWidget=None, parent=None, settings = None):
        super(Playblasts_View, self).__init__(parentWidget, parent, settings)

    def setModel_(self, model=None):
        self.clearModel()
        if model:

            self._proxyModel = models.Playblasts_ProxyModel()
            self._proxyModel.setSourceModel(model)

            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            self.setModel(self._proxyModel)

            # self.setIndentation(0)

            self.proxyModel = self.model()
            self.sourceModel = self.proxyModel.sourceModel()

            self.horizontalHeader().resizeSection(0, 32)  # self._slider.listSlider.value())
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            # self.horizontalHeader().resizeSection(1, 32)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().setStretchLastSection(False)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            self.horizontalHeader().resizeSection(2, 110)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(3, 80)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(4, 60)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 4, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().resizeSection(5, 32)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 5, QtWidgets.QHeaderView.Fixed)


            row_del = HoverDelegate(self)
            note_del = NoteDelegate(self)
            load_del = loadButtonDelegate(self)

            self.hover_signal.connect(row_del.hover_signal_change)
            self.hover_signal.connect(note_del.hover_signal_change)
            self.hover_signal.connect(load_del.hover_signal_change)

            self.setItemDelegate(row_del)

            # setup the buttons for loading and more options with delegates
            self.setItemDelegateForColumn(5, load_del)

            # note delegate
            self.setItemDelegateForColumn(1, note_del)

            # # setup the buttons for loading and more options with delegates
            # self.setItemDelegateForColumn(5, loadButtonDelegate(self))
            # self.setItemDelegateForColumn(1, NoteDelegate(self))

            # self.setItemDelegateForColumn(0, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(2, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(3, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(4, Standard_table_Delegate(self))



            self.sortByColumn(0, QtCore.Qt.DescendingOrder)
            self.verticalHeader().setDefaultSectionSize(32)

            '''
            This is to hide the author column if no users are in the active project
            '''
            if not self.parent.project.users:
                self.setColumnHidden(4, True)
            else:
                self.setColumnHidden(4, False)

            if model.items[0].number == 0:
                self.setColumnHidden(0, True)
            else:
                self.setColumnHidden(0, False)




            # self._proxyModel = models.Masters_ProxyModel()
            # self._proxyModel.setSourceModel(model)
            #
            # self._proxyModel.setDynamicSortFilter(True)
            # self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            # self.setModel(self._proxyModel)

            # self._proxyModel = models.Playblasts_ProxyModel()
            # self._proxyModel.setSourceModel(model)
            # self._proxyModel.setDynamicSortFilter(True)
            # self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            # self.setModel(self._proxyModel)
            # model._rowHeight = self._slider.listSlider.value()
            # self.setIndentation(0)
            # self.expandAll()

            # self.header().resizeSection(0, self._slider.listSlider.value())

            # QtCompat.setSectionResizeMode(self.header(), 0, QtWidgets.QHeaderView.Fixed)
            # self.header().resizeSection(1, 32)
            #
            # QtCompat.setSectionResizeMode(self.header(), 1, QtWidgets.QHeaderView.Fixed)
            #
            # self.header().setStretchLastSection(False)
            #
            #
            # QtCompat.setSectionResizeMode(self.header(), 2, QtWidgets.QHeaderView.Stretch)
            # QtCompat.setSectionResizeMode(self.header(), 3, QtWidgets.QHeaderView.Stretch)
            # QtCompat.setSectionResizeMode(self.header(), 4, QtWidgets.QHeaderView.Stretch)
            # self.header().resizeSection(5, 32)
            #
            # QtCompat.setSectionResizeMode(self.header(), 5, QtWidgets.QHeaderView.Fixed)
            # self.header().resizeSection(6, 32)
            # QtCompat.setSectionResizeMode(self.header(), 6, QtWidgets.QHeaderView.Fixed)
            #
            #
            # self.setItemDelegateForColumn(6, loadButtonDelegate(self))
            #
            # self.sortByColumn(1, QtCore.Qt.DescendingOrder)
            #
            # self.proxyModel = self.model()
            # self.sourceModel = self.proxyModel.sourceModel()
            # self.update()

    def contextMenuEvent(self, event):

        handled = True
        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            src = self.asModelIndex(index)
            node = self.asModelNode(src)

        rows = self.selectionModel().selectedRows()
        if rows:
            node = [self.asModelNode(self.asModelIndex(r)) for r in rows]

        actions = list()
        def_actions = list()

        if node:

            # if node.typeInfo() == cfg._version_:
            if isinstance(node, list):
                if len(node) == 1:

                    if node[0].number is not 0:
                        if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.revert_master):
                            actions.append(QtWidgets.QAction("Revert master playblast to {}".format(node[0].fullName), menu,triggered=functools.partial(self.revert_, node)))
                pass

            if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.delete):
                actions.append(QtWidgets.QAction("Delete...", menu, triggered=functools.partial(self.delete, node)))

            def_actions.append(QtWidgets.QAction("Explore...", menu, triggered=functools.partial(self.explore, node)))

        else:

            if self.parent.current_component:
                pass
                # actions.append(QtWidgets.QAction("Explore...", menu,
                #                                  triggered=functools.partial(self.explore, self.parent.current_component)))
            else:
                event.accept()
                return


        menu.addActions(actions)
        menu.addSeparator()
        menu.addActions(def_actions)
        menu.setStyleSheet(self.css)
        menu.exec_(event.globalPos())
        event.accept()

        return

    def MultiButtonClicked(self):
        # This slot will be called when our button is clicked.
        # self.sender() returns a refence to the QPushButton created
        # by the delegate, not the delegate itself.
        button = self.sender()
        index = self.indexAt(button.pos())
        index = self.model().mapToSource(index)
        if self.model().sourceModel().getNode(index).typeInfo() == cfg._playblast_:
            parent_index = index.parent()
            node = self.model().sourceModel().getNode(index)
            #     self.model().sourceModel().removeRows(index.row(),1, parent_index)
            node.play()


    def revert_(self, node):
        if isinstance(node, list):
            msg = "Are you sure you want to revert your master playblast to {}?".format(node[0].fullName)
            prompt = massage.PromptUser(self, prompt=msg, override_yes_text="Yes", override_no_label="No")
            result = prompt.exec_()
            # logger.info(result)
            # logger.info()

            if result == 0:
                node[0].revert_()
            # node[0].revert_()

            # else:
            #     self.model().sourceModel().getNode(index).load()
            #     self.parent.set_thumbnail(self.model().sourceModel().getNode(index).resource)
            #     self.parent.version = self.model().sourceModel().getNode(index)
            #     self.setCurrentIndex(self.model().mapFromSource(index))

    # def contextMenuEvent(self, event):
    #
    #     handled = True
    #     index = self.indexAt(event.pos())
    #     menu = QtWidgets.QMenu()
    #     node = None
    #
    #     if index.isValid():
    #         src = self.asModelIndex(index)
    #         node = self.asModelNode(src)
    #
    #     actions = []
    #
    #     if node and not node._deathrow:
    #
    #         if node.typeInfo() == cfg._playblast_:
    #
    #             actions.append(QtWidgets.QAction("Explore...", menu,
    #                                          triggered=functools.partial(self.explore, src)))
    #         else:
    #
    #             event.accept()
    #             return
    #
    #     else:
    #         event.accept()
    #         return
    #
    #     menu.addActions(actions)
    #
    #     menu.exec_(event.globalPos())
    #     event.accept()
    #
    #     return


class Library_View(Versions_View):
    def __init__(self, parentWidget=None, parent=None, settings = None):
        super(Library_View, self).__init__(parentWidget, parent, settings)

        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)



    def setModel_(self, model=None):
        self.clearModel()
        if model:
            # model._rowHeight = self._slider.listSlider.value()
            self._proxyModel = models.Simple_ProxyModel()
            self._proxyModel.setSourceModel(model)

            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSortRole(models.Versions_Model.sortRole)
            self.setModel(self._proxyModel)

            # self.setIndentation(0)

            self.proxyModel = self.model()
            self.sourceModel = self.proxyModel.sourceModel()

            self.horizontalHeader().resizeSection(0, 32)  # self._slider.listSlider.value())
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 0, QtWidgets.QHeaderView.Fixed)

            # self.horizontalHeader().resizeSection(1, 32)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Fixed)

            self.horizontalHeader().setStretchLastSection(False)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 1, QtWidgets.QHeaderView.Stretch)

            QtCompat.setSectionResizeMode(self.horizontalHeader(), 2, QtWidgets.QHeaderView.Stretch)

            self.horizontalHeader().resizeSection(3, 32)
            QtCompat.setSectionResizeMode(self.horizontalHeader(), 3, QtWidgets.QHeaderView.Fixed)

            # self.horizontalHeader().resizeSection(4, 40)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 4, QtWidgets.QHeaderView.Fixed)
            #
            # self.horizontalHeader().resizeSection(5, 50)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 5, QtWidgets.QHeaderView.Fixed)
            #
            # self.horizontalHeader().resizeSection(6, 32)
            # QtCompat.setSectionResizeMode(self.horizontalHeader(), 6, QtWidgets.QHeaderView.Fixed)

            # setup the buttons for loading and more options with delegates
            self.setItemDelegateForColumn(3, Library_delegate(self))
            # self.setItemDelegateForColumn(0, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(1, Standard_table_Delegate(self))
            # self.setItemDelegateForColumn(2, Standard_table_Delegate(self))


            # self.setItemDelegateForColumn(1, NoteDelegate(self))
            self.sortByColumn(1, QtCore.Qt.DescendingOrder)
            self.verticalHeader().setDefaultSectionSize(32)

            '''
            This is to hide the author column if no users are in the active project
            '''
            # if not self.parent.project.users:
            #     self.setColumnHidden( 4, True)
            # else:
            #     self.setColumnHidden(4, False)
            #
            # if model.items[0].number == 0:
            #     self.setColumnHidden(0, True)
            # else:
            #     self.setColumnHidden(0, False)

    def contextMenuEvent(self, event):
        handled = True
        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            src = self.asModelIndex(index)
            node = self.asModelNode(src)
            # node = self.asModelNode(id)

        top_actions = list()
        def_actions = list()

        if node:

            if self.permissions.has_permissions(role_string=self.role(), action=self.permissions.reference_version):
                def_actions.append(QtWidgets.QAction("Reference to current scene", menu, triggered=functools.partial(self.reference, node)))

            def_actions.append(QtWidgets.QAction("Explore...", menu,
                                                 triggered=functools.partial(self.explore, node)))

        else:

            event.accept()
            return

        menu.addActions(top_actions)
        menu.addSeparator()
        menu.addActions(def_actions)
        menu.setStyleSheet(self.css)
        menu.exec_(event.globalPos())
        event.accept()

    def explore(self, node):

        if node:
            try:
                node.master_model().items[0].explore()
            except:
                pass


    def reference(self, node):
        if node:
            try:
                node.master_model().items[0].reference()
            except:
                pass

    def MultiButtonClicked(self):
        # This slot will be called when our button is clicked.
        # self.sender() returns a refence to the QPushButton created
        # by the delegate, not the delegate itself.
        button = self.sender()
        index = self.indexAt(button.pos())
        index = self.model().mapToSource(index)

        self.model().sourceModel().getNode(index).master_model().items[0].reference()



        # self.update()

                # def setModel_(self, model=None):
    #     self.clearModel()
    #     if model:
    #         model._rowHeight = self._slider.listSlider.value()
    #         self._proxyModel = models.Masters_ProxyModel()
    #         self._proxyModel.setSourceModel(model)
    #         self._proxyModel.setDynamicSortFilter(True)
    #         self._proxyModel.setSortRole(models.Masters_Model.sortRole)
    #         self.setModel(self._proxyModel)
    #
    #         self.setIndentation(0)
    #         self.expandAll()
    #
    #         self.header().resizeSection(0, self._slider.listSlider.value())
    #
    #         QtCompat.setSectionResizeMode(self.header(), 0, QtWidgets.QHeaderView.Fixed)
    #         self.header().resizeSection(1, 32)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 1, QtWidgets.QHeaderView.Fixed)
    #
    #         self.header().setStretchLastSection(False)
    #
    #
    #         QtCompat.setSectionResizeMode(self.header(), 2, QtWidgets.QHeaderView.Stretch)
    #         QtCompat.setSectionResizeMode(self.header(), 3, QtWidgets.QHeaderView.Stretch)
    #         QtCompat.setSectionResizeMode(self.header(), 4, QtWidgets.QHeaderView.Stretch)
    #
    #         self.header().resizeSection(5, 50)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 5, QtWidgets.QHeaderView.Fixed)
    #         self.header().resizeSection(6, 32)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 6, QtWidgets.QHeaderView.Fixed)
    #         self.header().resizeSection(7, 32)
    #
    #         QtCompat.setSectionResizeMode(self.header(), 7, QtWidgets.QHeaderView.Fixed)
    #
    #         self.setItemDelegateForColumn(7, loadButtonDelegate(self))
    #
    #         self.sortByColumn(1, QtCore.Qt.DescendingOrder)
    #
    #         self.proxyModel = self.model()
    #         self.sourceModel = self.proxyModel.sourceModel()
    #         # self.update()

    # def MultiButtonClicked(self):
    #     # This slot will be called when our button is clicked.
    #     # self.sender() returns a refence to the QPushButton created
    #     # by the delegate, not the delegate itself.
    #     button = self.sender()
    #     index = self.indexAt(button.pos())
    #     index = self.model().mapToSource(index)
    #     if self.model().sourceModel().getNode(index).typeInfo() == cfg._new_:
    #         parent_index = index.parent()
    #         node = self.model().sourceModel().getNode(index).parent()
    #         self.model().sourceModel().removeRows(index.row(), 1, parent_index)
    #         node.initialVersion()
    #     else:
    #         self.model().sourceModel().getNode(index).load()
    #         self.parent.set_thumbnail(self.model().sourceModel().getNode(index).resource)
    #         self.parent.version = self.model().sourceModel().getNode(index)
    #         self.setCurrentIndex(self.model().mapFromSource(index))
    #         for btn in self._buttons:
    #             btn.setIcon(QtGui.QIcon(cfg.open_icon))
    #
    #         button.setIcon(QtGui.QIcon(cfg.reload_icon))
    #         # try:
    #         #     version_buttons = self.parent.versionsView._buttons
    #         #     for btn in self.version_buttons:
    #         #         btn.setIcon(QtGui.QIcon(cfg.open_icon))
    #         # except:
    #         #     print "can not reset versions table"
    #
    # def contextMenuEvent(self, event):
    #
    #     handled = True
    #     index = self.indexAt(event.pos())
    #     menu = QtWidgets.QMenu()
    #     node = None
    #
    #     if index.isValid():
    #         src = self.asModelIndex(index)
    #         node = self.asModelNode(src)
    #
    #     actions = []
    #
    #     if node and not node._deathrow:
    #
    #         if node.typeInfo() == cfg._master_:
    #
    #             actions.append(QtWidgets.QAction("Explore...", menu,
    #                                          triggered=functools.partial(self.explore, src)))
    #         else:
    #
    #             event.accept()
    #             return
    #
    #     else:
    #         event.accept()
    #         return
    #
    #     menu.addActions(actions)
    #
    #     menu.exec_(event.globalPos())
    #     event.accept()
    #
    #     return




class IconScaleSlider(QtWidgets.QWidget):
    def __init__(self, parent):
        super(IconScaleSlider, self).__init__(parent)

        self.large_lable = QtWidgets.QLabel()
        self.large_lable.setMaximumSize(QtCore.QSize(16, 16))
        self.large_lable.setPixmap(cfg.large_icon)
        self.small_lable = QtWidgets.QLabel()
        self.small_lable.setMaximumSize(QtCore.QSize(16, 16))
        self.small_lable.setPixmap(cfg.small_icon)
        self.slideWidget = QtWidgets.QWidget()
        self.slideWidget.setMaximumHeight(20)
        self.slideLayout = QtWidgets.QHBoxLayout()
        self.slideLayout.setContentsMargins(0, 0, 0, 0)

        self.slideLayout.setAlignment(QtCore.Qt.AlignRight)

        self.listSlider = QtWidgets.QSlider()
        self.listSlider.setOrientation(QtCore.Qt.Horizontal)
        self.listSlider.setMaximumWidth(80)
        self.listSlider.setMinimumWidth(80)
        self.listSlider.setMaximumHeight(25)
        self.listSlider.setMinimum(32)
        self.listSlider.setMaximum(96)
        self.listSlider.setValue(32)

        self.slideLayout.addWidget(self.small_lable)
        self.slideLayout.addWidget(self.listSlider)
        self.slideLayout.addWidget(self.large_lable)

        self.setMinimumHeight(25)
        self.setLayout(self.slideLayout)


#
# class Project_Tree_View(QtWidgets.QTreeView):
#     percentage_complete = QtCore.Signal(int)
#     update_view = QtCore.Signal()
#
#     def __init__(self, parent=None):
#         super(Project_Tree_View, self).__init__(parent)
#
#         global counter
#
#         # display options
#
#         self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
#         self.setAlternatingRowColors(True)
#         self.setSortingEnabled(True)
#         self.setDragEnabled(True)
#         self.setAcceptDrops(True)
#         self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
#         self.setDropIndicatorShown(True)
#         self.resizeColumnToContents(True)
#
#         # self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
#
#         # local variables
#         self.pipelineUI = self.parent()
#         self._ignoreExpentions = False
#         self._expended_states = None
#         self._userSelection = None
#         self._tableView = None
#         self._proxyModel = None
#         self._sourceModel = None
#         self._tree_as_flat_list = None
#
#         self.setStyleSheet('''
#
#                            QTreeView::item:focus {
#                            }
#                            QTreeView::item:hover {
#                                 background: #101010;
#                            }
#                            QTreeView {
#                                 outline: 0;
#                            }
#                            QTreeView::branch:has-siblings:!adjoins-item {
#                                 border-image:url(''' + cfg.vline + ''') 0;
#                            }
#
#                            QTreeView::branch:has-siblings:adjoins-item {
#                                 border-image:url(''' + cfg.branch_more + ''') 0;
#                            }
#
#                            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
#                                 border-image:url(''' + cfg.branch_end + ''') 0;
#                            }
#
#                            QTreeView::branch:has-children:!has-siblings:closed,
#                            QTreeView::branch:closed:has-children:has-siblings {
#                                 border-image: none;
#                                 image:url(''' + cfg.branch_closed + ''') 0;
#                            }
#
#                            QTreeView::branch:open:has-children:!has-siblings,
#                            QTreeView::branch:open:has-children:has-siblings  {
#                                 border-image: none;
#                                 image: url(''' + cfg.branch_open + ''') 0;
#                            }''')
#         #
#
#         self.changed = False
#         self.update_view.connect(self.model_changed)
#
#     def model_changed(self):
#         if self.changed == False:
#             self.changed = True
#
#     def setModel(self, model):
#
#         super(Project_Tree_View, self).setModel(model)
#
#         if model:
#             self.changed = False
#
#             self.proxyModel = self.model()
#             self.sourceModel = self.proxyModel.sourceModel()
#
#             '''
#             this will expend the tree only on the first level, which should be
#             the projects name folder
#             the rest will be collapsed
#             '''
#
#             self.initialExpension()
#
#             '''
#             save the expended state of the tree
#             '''
#             self.saveState()
#
#             self.header().setStretchLastSection(False)
#             QtCompat.setSectionResizeMode(self.header(), 0, QtWidgets.QHeaderView.Stretch)
#
#
#             self.header().resizeSection(1, 100)
#             QtCompat.setSectionResizeMode(self.header(), 1, QtWidgets.QHeaderView.Fixed)
#
#
#     def initialExpension(self):
#         if self.model():
#             self.collapseAll()
#             return
#             for row in range(self.model().rowCount(self.rootIndex())):
#                 x = self.model().index(row, 0, self.rootIndex())
#                 self.setExpanded(x, True)
#
#     @property
#     def tableView(self):
#         return self._tableView
#
#     @tableView.setter
#     def tableView(self, view):
#         self._tableView = view
#
#     @property
#     def proxyModel(self):
#         return self._proxyModel
#
#     @proxyModel.setter
#     def proxyModel(self, model):
#         self._proxyModel = model
#
#     @property
#     def sourceModel(self):
#         return self._sourceModel
#
#     @sourceModel.setter
#     def sourceModel(self, model):
#         self._sourceModel = model
#
#     @property
#     def userSelection(self):
#         return self._userSelection
#
#     @userSelection.setter
#     def userSelection(self, selection):
#         self._userSelection = selection
#
#     def asProxyIndex(self, index):
#         return self.proxyModel.index(0, 0, index)
#
#     def asModelIndex(self, index):
#         return self.proxyModel.mapToSource(index)
#
#     def fromProxyIndex(self, index):
#         return self.proxyModel.mapFromSource(index)
#
#     def asModelNode(self, index):
#         return self.sourceModel.getNode(index)
#
#     def modelIndexFromNode(self, node):
#         return self.sourceModel.indexFromNode(node, self.rootIndex())
#
#     def selectRoot(self):
#
#         self.setCurrentIndex(self.asProxyIndex(self.rootIndex()))
#         # self.tableView.update(self.selectionModel().selection())
#         self.saveSelection()
#
#     def saveSelection(self):
#
#         if len(self.selectedIndexes()) > 0:
#             self.userSelection = self.asModelIndex(self.selectedIndexes()[0])
#
#     def saveState(self):
#
#         '''
#         recursive function to save the expention state fo the tree to a dictionary
#         '''
#
#         if self._ignoreExpentions == True:
#             return
#
#         def rec(dict, mdl, index):
#
#             for row in range(mdl.rowCount(index)):
#
#                 i = mdl.index(row, 0, index)
#                 node = mdl.data(i, 165)
#
#                 if self.isExpanded(i):
#                     dict[node] = True
#                 else:
#                     dict[node] = False
#
#                 rec(dict, mdl, i)
#
#         self._expended_states = {}
#         rec(self._expended_states, self.proxyModel, self.rootIndex())
#
#     def restoreState(self):
#
#         '''
#         recursive function to restore the expention state fo the tree to a dictionary
#         '''
#
#         def rec(mdl, index):
#
#             for row in range(mdl.rowCount(index)):
#
#                 i = mdl.index(row, 0, index)
#                 node = mdl.data(i, 165)
#
#                 if node in self._expended_states:
#                     if self._expended_states[node] == True:
#                         self.setExpanded(i, True)
#
#                 rec(mdl, i)
#
#         self.collapseAll()
#         rec(self.proxyModel, self.rootIndex())
#         self.restoreSelection()
#
#     def restoreSelection(self):
#
#         index = self.fromProxyIndex(self.userSelection)
#         self.select(index)
#         self.updateTable(index)
#         # self.selectionModel().select(index, QtWidgets.QItemSelectionModel.ClearAndSelect)
#
#     def select(self, index):
#         '''
#         selects a tree branch and expand the parant branch to see the selected branch
#         '''
#         modelIndex = self.sourceModel.parent(self.asModelIndex(index))
#         proxyIndex = self.fromProxyIndex(modelIndex)
#         self.setExpanded(proxyIndex, True)
#         self.selectionModel().select(index, QtWidgets.QItemSelectionModel.ClearAndSelect)
#
#     def dropEvent(self, event):
#
#         super(Project_Tree_View, self).dropEvent(event)
#         # QTreeView.dropEvent(self, evt)
#         if not event.isAccepted():
#             # qdnd_win.cpp has weird behavior -- even if the event isn't accepted
#             # by target widget, it sets accept() to true, which causes the executed
#             # action to be reported as "move", which causes the view to remove the
#             # source rows even though the target widget didn't like the drop.
#             # Maybe it's better for the model to check drop-okay-ness during the
#             # drag rather than only on drop; but the check involves not-insignificant work.
#             event.setDropAction(QtCore.Qt.IgnoreAction)
#
#         '''
#         if the drop is coming from the contents view - this is how i handle this...
#         it's UGLY, but for now it's the only way i can make this work...
#         '''
#         # print event.possibleActions() , "<<"
#         if event.source().__class__.__name__ == 'PipelineContentsView':
#
#             i = self.indexAt(event.pos())
#             model_index = self.asModelIndex(i)
#             model_id = self.sourceModel.getNode(model_index).id
#             model_node = self.sourceModel.getNode(model_index)
#
#             if model_index.isValid():
#
#                 mime = event.mimeData()
#                 source = event.source()
#
#                 item = cPickle.loads(str(mime.data('application/x-qabstractitemmodeldatalist')))
#                 item_index = self.sourceModel.indexFromNode(item, QtCore.QModelIndex())
#                 item_parent = self.sourceModel.parent(item_index)
#                 item_id = item.id
#
#                 '''
#                 ignore drops of folders into assets
#                 '''
#                 if model_node.typeInfo() == cfg._asset_:
#                     if item.typeInfo() == cfg._folder_ or item.typeInfo() == cfg._asset_:
#                         event.setDropAction(QtCore.Qt.IgnoreAction)
#                         event.ignore()
#                         return
#
#                 '''
#                 this is to make sure the dropped item is not already a child in the downstream of branches
#                 '''
#                 descending_id = []
#                 for i in self.sourceModel.listHierarchy(item_index):
#                     descending_id.append(self.sourceModel.getNode(i).id)
#
#                 if model_id in descending_id:
#
#                     event.setDropAction(QtCore.Qt.IgnoreAction)
#                     event.ignore()
#                     return
#
#                 else:
#
#                     source.clearModel()
#                     self.sourceModel.removeRows(item_index.row(), 1, item_parent)
#                     self._proxyModel.invalidate()
#
#                     self.sourceModel.dropMimeData(mime, event.dropAction, 0, 0, model_index)
#                     source.restoreTreeViewtSelection()
#                     return
#
#                     # this was required when i misused the insert rows function of the model...
#                     # self._proxyModel.invalidate()
#
#     '''
#     here i am detecting if a drop is coming from the contents view, to mark it as acepted, otherwise the drop will be blocked.
#     it's UGLY, but for now it's the only way i can make this work...
#     '''
#
#     def dragEnterEvent(self, event):
#
#         super(Project_Tree_View, self).dragEnterEvent(event)
#
#         if event.source().__class__.__name__ == 'PipelineContentsView':
#             return event.setAccepted(True)
#
#     '''
#     def dragMoveEvent(self, event):
#
#         super(pipelineTreeView,self).dragMoveEvent(event)
#         #return event.setAccepted(True)
#     '''
#
#     def projectRootIndex(self):
#         modelRootIndex = self.asModelIndex(self.rootIndex())
#         return modelRootIndex
#         # get the first childe of the model's root
#         # return self.sourceModel.index(0,0,modelRootIndex)
#
#     # def mouseReleaseEvent(self, event):
#     #
#     #     super(pipelineTreeView, self).mouseReleaseEvent(event)
#     #     self.saveSelection()
#     #     #self.tableView.update(self.selectionModel().selection())
#     #     event.accept
#
#     def contextMenuEvent(self, event):
#
#         handled = True
#         index = self.indexAt(event.pos())
#         menu = QtWidgets.QMenu()
#         node = None
#
#         if index.isValid():
#             src = self.asModelIndex(index)
#             node = self.asModelNode(src)
#
#         actions = []
#
#         if node and not node._deathrow:
#
#             if node.typeInfo() != cfg._stage_:
#
#                 level_name, level_type = node.level_options
#
#                 if node.typeInfo() == cfg._root_:
#                     actions.append(QtWidgets.QAction("Create tree...", menu,
#                                                  triggered=functools.partial(self.create_new_tree, src)))
#
#                 if level_type == cfg._folder_:
#                     actions.append(
#                         QtWidgets.QAction("Create new {0}".format(level_name), menu,
#                                       triggered=functools.partial(self.create_new_folder, src, level_name)))
#
#                 elif level_type == cfg._asset_:
#                     actions.append(QtWidgets.QAction("Create new {0}".format(level_name), menu,
#                                                  triggered=functools.partial(self.create_new_asset, src, level_name)))
#
#                 elif level_type == cfg._stage_:
#                     actions.append(QtWidgets.QAction("Create new {0}".format(level_name), menu,
#                                                  triggered=functools.partial(self.create_new_stage, src)))
#
#                 elif node.typeInfo() == cfg._asset_:
#                     actions.append(QtWidgets.QAction("Create new %s" % (cfg._stage_), menu,
#                                                  triggered=functools.partial(self.create_new_stage, src)))
#
#             if not node.typeInfo() == cfg._root_:
#                 actions.append(QtWidgets.QAction("Delete", menu, triggered=functools.partial(self.delete, src)))
#
#             actions.append(QtWidgets.QAction("Explore...", menu,
#                                          triggered=functools.partial(self.explore, src)))
#         else:
#             event.accept()
#             return
#
#         menu.addActions(actions)
#
#         menu.exec_(event.globalPos())
#         event.accept()
#
#         return
#
#     '''
#     functions to add/remove tree nodes
#     this is we will want some user input...
#
#     '''
#
#     def explore(self, index):
#         node = self.asModelNode(index)
#         node.explore()
#
#     def delete(self, index):
#         # clear the table view
#         # self.tableView.update(QtWidgets.QItemSelection())
#
#         node = self.asModelNode(index)
#         node.deathrow()
#         # parentIndex = self.sourceModel.parent(index)
#         # self.sourceModel.removeRows(node.row(),1,parentIndex, kill=True)
#         self._proxyModel.invalidate()
#         #
#         # self.updateTable( self.fromProxyIndex(parentIndex))
#         self.update_view.emit()
#         return True
#
#     def create_new_tree(self, parent):
#         global counter
#         global total_items
#         counter = 0
#         total_items = 0
#         parent_node = self.sourceModel.getNode(parent)
#
#         depth_list = self.sourceModel.listAncestos(parent)
#         ancestors = []
#         for i in depth_list:
#             ancestors.append(self.sourceModel.getNode(i))
#
#         def rec(items, p, stages, name_format):
#
#             global counter
#             global total_items
#             """ recursive function for generating a tree out of the instructions list called items
#             the function creates nodes by instruction in the first item in the list, then while the list is longer then 1,
#             it sends the list againg but without the current item
#             the parent is the currently created node"""
#             times = items[0][2]
#             start = items[0][3]
#             name = items[0][1]
#             padding = items[0][4]
#
#             for i in range(times):
#                 base_folder_name = name
#
#                 number = files.set_padding(start + i, padding)
#                 if base_folder_name != "":
#                     folder_name = "{0}{1}".format(base_folder_name, number) if padding > 1 else base_folder_name
#                 else:
#                     folder_name = "{0}".format(number) if times > 1 else "unnamed_folder"
#
#                 skip = False
#                 for child in p.children:
#                     if child.name == folder_name:
#                         skip = True
#                 if skip:
#                     print "folder exists!"
#                     continue
#
#                 i = self.sourceModel.indexFromNode(p, QtCore.QModelIndex())
#                 depth_list = self.sourceModel.listAncestos(i)
#
#                 path = os.path.join(p.path, folder_name)
#
#                 if len(items) == 1:
#                     node = assets.AssetNode(folder_name, path=path, parent=p, virtual=True,
#                                             section=p.section)
#
#                     self.sourceModel.insertRows(0, 0, parent=i, node=node)
#                     self._proxyModel.invalidate()
#                     counter += 1
#                     # QtWidgets.QApplication.processEvents()
#                     # #print remap(current, 0, total_items, 0, 100)
#                     # self.percentage_complete.emit(remap(current, 0, total_items, 0, 100))
#
#                     '''for an asset, generate stages:'''
#
#                     new_index = self.sourceModel.indexFromNode(node, QtCore.QModelIndex())
#                     for s in stages:
#                         if stages[s]:
#                             path = os.path.join(p.path, folder_name, s)
#                             # formatDepth
#                             stageNode = pipeline.libs.nodes.stages.StageNode(s, parent=node, path=path, virtual=True,
#                                                                              name_format=name_format, section=p.section,
#                                                                              project=self.pipelineUI.project, depth=len(depth_list))
#                             # if node is not False:
#                             self._sourceModel.insertRows(0, 0, parent=new_index, node=stageNode)
#                             self._proxyModel.invalidate()
#                             # counter += 1
#                             # QtWidgets.QApplication.processEvents()
#                             # #print remap(current, 0, total_items, 0, 100)
#                             # self.percentage_complete.emit(remap(current, 0, total_items, 0, 100))
#
#                 else:
#                     node = dt.FolderNode(folder_name, path=path, parent=p, virtual=True,
#                                          section=p.section, project=self.pipelineUI.project,
#                                          depth=len(depth_list))
#
#                     self.sourceModel.insertRows(0, 0, parent=i, node=node)
#                     self._proxyModel.invalidate()
#                     counter += 1
#
#                 if len(items) > 1:
#
#                     QtWidgets.QApplication.processEvents()
#
#                     # print remap_value(counter, 0, total_items, 0, 100), "--->", counter, "--->", total_items
#                     self.percentage_complete.emit(misc.remap_value(counter, 0, total_items, 0, 100))
#                     l = list(items[1:])
#                     rec(l, node, stages, name_format)
#                 else:
#                     pass
#
#         folderDlg = outliner.newTreeDialog(project=self.pipelineUI.project, section=parent_node.section)
#         result = folderDlg.exec_()
#         res = folderDlg.result()
#         if result == QtWidgets.QDialog.Accepted:
#             levels = res["levels"]
#
#             total_current_level = levels[0][2]
#             total_items = total_current_level
#
#             for i in range(1, len(levels)):
#                 total_current_level = (total_current_level * levels[i][2])
#                 total_items += total_current_level
#
#             rec(levels, parent_node, res["stages"], res["name_format"])
#             self.update_view.emit()
#             self.percentage_complete.emit(0)
#
#     def create_new_folder(self, parent, string):
#
#         parent_node = self.sourceModel.getNode(parent)
#
#         depth_list = self.sourceModel.listAncestos(parent)
#         ancestors = []
#         for i in depth_list:
#             ancestors.append(self.sourceModel.getNode(i))
#
#         folderDlg = outliner.newFolderDialog(string=string)
#         result = folderDlg.exec_()
#         res = folderDlg.result()
#         if result == QtWidgets.QDialog.Accepted:
#             base_folder_name = res["name"]
#
#             for i in range(0, res["quantity"]):
#                 QtWidgets.QApplication.processEvents()
#                 self.percentage_complete.emit(misc.remap_value(i, 0, res["quantity"], 0, 100))
#
#                 number = files.set_padding(res["from"] + i, res["padding"])
#                 if base_folder_name != "":
#                     folder_name = "{0}{1}".format(base_folder_name, number) if res["padding"] > 0 else base_folder_name
#                 else:
#                     folder_name = "{0}".format(number) if res["quantity"] > 1 else "unnamed_folder"
#
#                 skip = False
#                 for child in parent_node.children:
#                     if child.name == folder_name:
#                         skip = True
#                 if skip:
#                     print "folder exists!"
#                     continue
#
#                 path = os.path.join(parent_node.path, folder_name)
#                 node = dt.FolderNode(folder_name, path=path, parent=parent_node, virtual=True,
#                                      section=parent_node.section, project=self.pipelineUI.project, depth=len(ancestors))
#
#                 self.sourceModel.insertRows(0, 0, parent=parent, node=node)
#                 self._proxyModel.invalidate()
#
#             self.update_view.emit()
#             self.percentage_complete.emit(0)
#
#     def create_new_asset(self, parent, string):
#         parent_node = self.sourceModel.getNode(parent)
#
#         depth_list = self.sourceModel.listAncestos(parent)
#         ancestors = []
#         for i in depth_list:
#             ancestors.append(self.sourceModel.getNode(i))
#
#         assetDlg = outliner.newAssetDialog(stages=self.pipelineUI.project.stages[parent_node.section], ancestors=ancestors,
#                                       string=string, project=self.pipelineUI.project)
#         result = assetDlg.exec_()
#         res = assetDlg.result()
#         if result == QtWidgets.QDialog.Accepted:
#             base_folder_name = res["name"]
#             for i in range(0, res["quantity"]):
#                 QtWidgets.QApplication.processEvents()
#                 self.percentage_complete.emit(misc.remap_value(i, 0, res["quantity"], 0, 100))
#                 number = files.set_padding(res["from"] + i, res["padding"])
#                 if base_folder_name != "":
#                     folder_name = "{0}{1}".format(base_folder_name, number) if res["padding"] > 1 else base_folder_name
#                 else:
#                     folder_name = "{0}".format(number) if res["quantity"] > 1 else "unnamed_folder"
#
#                 skip = False
#                 for child in parent_node.children:
#                     if child.name == folder_name:
#                         skip = True
#                 if skip:
#                     print "folder exists!"
#                     continue
#
#                 path = os.path.join(parent_node.path, folder_name)
#                 node = assets.AssetNode(folder_name, path=path, parent=parent_node, virtual=True,
#                                         section=parent_node.section)
#                 # if node is not False:
#                 self.sourceModel.insertRows(0, 0, parent=parent, node=node)
#                 self._proxyModel.invalidate()
#
#                 new_index = self.sourceModel.indexFromNode(node, QtCore.QModelIndex())
#                 for s in res["stages"]:
#                     if res["stages"][s]:
#                         path = os.path.join(parent_node.path, folder_name, s)
#                         # formatDepth
#                         stageNode = pipeline.libs.nodes.stages.StageNode(s, parent=node, path=path, virtual=True,
#                                                                          name_format=res["name_format"], section=parent_node.section,
#                                                                          project=self.pipelineUI.project, depth=len(ancestors))
#                         # if node is not False:
#                         self._sourceModel.insertRows(0, 0, parent=new_index, node=stageNode)
#                         self._proxyModel.invalidate()
#
#             self.update_view.emit()
#             self.percentage_complete.emit(0)
#
#     def create_new_stage(self, parent):
#
#         parent_node = self.sourceModel.getNode(parent)
#
#         depth_list = self.sourceModel.listAncestos(parent)
#         ancestors = []
#         for i in depth_list:
#             ancestors.append(self.sourceModel.getNode(i))
#
#         new_stages = []
#         for stage in self.pipelineUI.project.stages[parent_node.section]:
#             if stage not in parent_node.stages:
#                 new_stages.append(stage)
#
#         if new_stages:
#
#             assetDlg = outliner.newStageDialog(parent_name=parent_node.name, stages=new_stages, ancestors=ancestors,
#                                           project=self.pipelineUI.project)
#             result = assetDlg.exec_()
#             res = assetDlg.result()
#             if result == QtWidgets.QDialog.Accepted:
#                 for s in res["stages"]:
#                     if res["stages"][s]:
#                         path = os.path.join(parent_node.path, s)
#                         # formatDepth
#
#                         stageNode = pipeline.libs.nodes.stages.StageNode(s, parent=parent_node, asset_name=parent_node.name, path=path,
#                                                                          virtual=True, name_format=res["name_format"],
#                                                                          section=parent_node.section, settings=self.pipelineUI.settings)
#                         # if node is not False:
#                         self._sourceModel.insertRows(0, 0, parent=parent, node=stageNode)
#                         self._proxyModel.invalidate()
#
#                 self.update_view.emit()
#
#     @property
#     def tree_as_flat_list(self):
#         return self._tree_as_flat_list
#
#     @tree_as_flat_list.setter
#     def tree_as_flat_list(self, list):
#         self._tree_as_flat_list = list
#
#     def list_flat_hierarchy(self):
#
#         list = []
#         for i in self.sourceModel.listHierarchy(QtCore.QModelIndex()):
#             list.append(self.sourceModel.getNode(i))
#
#         self.tree_as_flat_list = list
#
#     def filterContents(self):
#
#         if self.tree_as_flat_list:
#             # self.tableView.clearModel()
#
#             model = models.PipelineContentsModel(self.tree_as_flat_list)
#             # self.tableView.populateTable(model)
#
#     def commit(self):
#         print "commit tree:"
#         self.sourceModel.rootNode.commit()
#         self.changed = False
#

# class Dresser_View(Project_Tree_View):
#     def __init__(self, parent=None):
#         super(Dresser_View, self).__init__(parent)
#
#
#     def setModel(self, model):
#
#         QtWidgets.QTreeView.setModel(self, model)
#
#         # super(Dresser_View, self).setModel(model)
#
#         if model:
#             self.changed = False
#
#             self.proxyModel = self.model()
#             self.sourceModel = self.proxyModel.sourceModel()
#
#             '''
#             this will expend the tree only on the first level, which should be
#             the projects name folder
#             the rest will be collapsed
#             '''
#             self.initialExpension()
#             '''
#             save the expended state of the tree
#             '''
#             self.saveState()
#
#             self.header().setStretchLastSection(False)
#             QtCompat.setSectionResizeMode(self.header(), 0, QtWidgets.QHeaderView.Stretch)
#
#
#             self.header().resizeSection(1, 100)
#             QtCompat.setSectionResizeMode(self.header(), 1, QtWidgets.QHeaderView.Fixed)
#
#
#     def initialExpension(self):
#
#         if self.model():
#             self.collapseAll()
#             for row in range(self.model().rowCount(self.rootIndex())):
#                 x = self.model().index(row, 0, self.rootIndex())
#                 self.setExpanded(x, True)
#
#     def contextMenuEvent(self, event):
#
#         handled = True
#         index = self.indexAt(event.pos())
#         menu = QtWidgets.QMenu()
#         node = None
#
#         if index.isValid():
#             src = self.asModelIndex(index)
#             node = self.asModelNode(src)
#
#         actions = []
#
#         if node:
#
#             if node.typeInfo() == cfg._master_:
#
#                 actions.append(QtWidgets.QAction("Load", menu,
#                                              triggered=functools.partial(self.load, src)))
#
#                 actions.append(QtWidgets.QAction("Reference to current", menu,
#                                              triggered=functools.partial(self.reference_to_current, src)))
#
#                 actions.append(QtWidgets.QAction("Explore...", menu,
#                                              triggered=functools.partial(self.explore, src)))
#             else:
#
#                 event.accept()
#                 return
#
#         else:
#             event.accept()
#             return
#
#         menu.addActions(actions)
#
#         menu.exec_(event.globalPos())
#         event.accept()
#
#         return
#
#     def explore(self, index):
#         node = self.asModelNode(index)
#         node.explore()
#
#     def load(self, index):
#         node = self.asModelNode(index)
#         node.load()
#
#     def reference_to_current(self, index):
#         node = self.asModelNode(index)
#         node.reference()
#

