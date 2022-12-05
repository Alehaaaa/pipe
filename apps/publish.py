import logging
import re
import os

import pipeline.libs.config as cfg
import pipeline.widgets.gui as gui
import pipeline.widgets.inputs as inputs
import pipeline.apps.massage as massage
import pipeline.libs.files as files
import pipeline.libs.views as views
import pipeline.libs.data as dt
import pipeline.libs.models as models
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.CSS
from pipeline.CSS import loadCSS


logger = logging.getLogger(__name__)

class Publish_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None, origin = '', settings = {}, **kwargs):
        super(Publish_Dialog, self).__init__(parent)

        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5,5,5,5)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.setMinimumWidth(400)
        self.setWindowTitle('Save master')
        # self.title = gui.Title(self, label="Save master")
        # self.layout.addWidget(self.title)
        self.center_to_maya_window()



        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.main_widget_layout.setSpacing(2)
        self.main_widget_layout.setContentsMargins(5,5,5,5)
        self.layout.addWidget(self.main_widget)


        self.options_widget = QtWidgets.QWidget()

        self.options_widget_layout = QtWidgets.QVBoxLayout(self.options_widget)
        self.options_widget_layout.setSpacing(2)
        self.options_widget_layout.setContentsMargins(2,2,2,2)
        self.options_widget_layout.setAlignment(QtCore.Qt.AlignTop)

        self.scripts_table_label = QtWidgets.QLabel('Execute scripts')
        self.scripts_table_view = views.Run_scripts_View(parent=self)
        self.scripts_table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.scripts_table_toolbar = QtWidgets.QToolBar(self.main_widget)
        self.scripts_table_toolbar.setIconSize(QtCore.QSize(20,20))



        add = self.scripts_table_toolbar.addAction(QtGui.QIcon(cfg.simple_add_icon), '',self.add_script)
        add.setToolTip('Add script')
        rm = self.scripts_table_toolbar.addAction(QtGui.QIcon(cfg.simple_rm_icon), '', self.remove_script)
        rm.setToolTip('Remove script')

        self.scripts_table_toolbar.addAction(QtGui.QIcon(cfg.simple_up_icon), '', self.move_up)
        self.scripts_table_toolbar.addAction(QtGui.QIcon(cfg.simple_dn_icon), '', self.move_down)


        self.scripts_table_toolbar.setStyleSheet('''
        QToolButton{
        border: none;
        }
        QToolButton::hover {
        background-color: ''' + cfg.colors.LIGHT_GRAY_plus + ''';
        border none;
        }

        ''')

        self.label_Note = QtWidgets.QLabel('Note')
        self.textNote = QtWidgets.QTextEdit(self)
        self.textNote.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.textNote.setMaximumHeight(100)

        self.remember = inputs.GroupInput(self.options_widget,"Remember these settings for {}".format(origin), QtWidgets.QCheckBox(), ic=cfg.save_icon)
        self.remember_input = self.remember.input
        self.remember_input.setCheckState(QtCore.Qt.Checked)


        self.open_after = inputs.GroupInput(self.options_widget,"Open master after save", QtWidgets.QCheckBox(), ic=cfg.save_icon)
        self.open_after_input = self.open_after.input
        self.open_after_input.setCheckState(QtCore.Qt.Checked)

        self.main_widget_layout.addWidget(self.options_widget)

        space1 = gui.HLine()
        space1.setMinimumHeight(20)
        self.main_widget_layout.addWidget(space1)

        self.main_widget_layout.addWidget(self.scripts_table_label)
        self.main_widget_layout.addWidget(self.scripts_table_toolbar)
        self.main_widget_layout.addWidget(self.scripts_table_view)

        space2 = gui.HLine()
        space2.setMinimumHeight(20)
        self.main_widget_layout.addWidget(space2)

        self.main_widget_layout.addWidget(self.label_Note)
        self.main_widget_layout.addWidget(self.textNote)
        self.main_widget_layout.addWidget(self.remember)
        self.main_widget_layout.addWidget(self.open_after)



        self.import_references = inputs.GroupInput(self.options_widget,"Import references", QtWidgets.QCheckBox(), ic=cfg.creation_icon)
        self.import_references_input = self.import_references.input
        self.import_references_input.setCheckState(QtCore.Qt.Checked)
        self.options_widget_layout.addWidget(self.import_references)


        self.delete_namespaces = inputs.GroupInput(self.options_widget, "Delete namespaces", QtWidgets.QCheckBox(),ic=cfg.creation_icon)
        self.delete_namespaces_input = self.delete_namespaces.input
        self.delete_namespaces_input.setCheckState(QtCore.Qt.Checked)
        self.options_widget_layout.addWidget(self.delete_namespaces)


        self.clean_up = inputs.GroupInput(self.options_widget,"Optimize scene", QtWidgets.QCheckBox(), ic=cfg.creation_icon)
        self.clean_up_input = self.clean_up.input
        self.clean_up_input.setCheckState(QtCore.Qt.Checked)
        self.options_widget_layout.addWidget(self.clean_up)

        self.delete_ng = inputs.GroupInput(self.options_widget,"Delete ngSkinTools nodes", QtWidgets.QCheckBox(), ic=cfg.creation_icon)
        self.delete_ng_input = self.delete_ng.input
        self.delete_ng_input.setCheckState(QtCore.Qt.Checked)
        self.options_widget_layout.addWidget(self.delete_ng)

        # buttons = QtWidgets.QDialogButtonBox(
        #     QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
        #     QtCore.Qt.Horizontal, self)
        #
        # buttons.accepted.setText('Save')
        # buttons.accepted.connect(self.accept)
        # buttons.rejected.connect(self.reject)

        save = QtWidgets.QPushButton("Save")

        canc = QtWidgets.QPushButton("Cancel")
        canc.setDefault(True)

        buttons = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal)
        buttons.addButton(save, QtWidgets.QDialogButtonBox.AcceptRole)
        buttons.addButton(canc, QtWidgets.QDialogButtonBox.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.main_widget_layout.addWidget(buttons)

        model = models.Script_files_Model(list())
        self.scripts_table_view.setModel(model)

        # logger.info(settings)
        stat = QtCore.Qt.Checked if settings['import_ref'] else QtCore.Qt.Unchecked
        self.import_references_input.setCheckState(stat)

        stat = QtCore.Qt.Checked if settings['delete_ns'] else QtCore.Qt.Unchecked
        self.delete_namespaces_input.setCheckState(stat)

        stat = QtCore.Qt.Checked if settings['optimize'] else QtCore.Qt.Unchecked
        self.clean_up_input.setCheckState(stat)

        if settings['scripts']:
            items = list()
            for s in settings['scripts']:
                items.append(dt.ScriptFileNode(name='script', path=s))

            model = models.Script_files_Model(items)
        else:
            model = models.Script_files_Model(list())

        self.scripts_table_view.setModel(model)


        stat = QtCore.Qt.Checked if settings['remember_settings'] else QtCore.Qt.Unchecked
        self.remember_input.setCheckState(stat)

        stat = QtCore.Qt.Checked if settings['open_after'] else QtCore.Qt.Unchecked
        self.open_after_input.setCheckState(stat)


    def add_script(self, *args):
        path = QtWidgets.QFileDialog.getOpenFileName(None, "Select script file", filter="*.*")
        if path[0]:

            typ = files.extension(files.file_name(path[0]))
            if  typ == ".py" or typ == ".mel":
                item = dt.ScriptFileNode(name='script', path=path[0])
            else:
                return
        else:
            return


        scripts_model = self.scripts_table_view.model()
        scripts_model.insertRows(0, 1, QtCore.QModelIndex(), node=item)


        return



    def remove_script(self, *args):
        rows = self.scripts_table_view.selectionModel().selectedRows()
        # logger.info(rows)
        if rows:
            # index = rows[0].row()
            self.scripts_table_view.model().removeRows(rows[0].row(), 1, parent=QtCore.QModelIndex())

    def move_up(self, *args):
        rows = self.scripts_table_view.selectionModel().selectedRows()
        # logger.info(rows)
        if rows:
            # index = rows[0].row()
            self.scripts_table_view.model().move_up(rows[0].row())
            ind = self.scripts_table_view.model().index(rows[0].row()-1,0,QtCore.QModelIndex())
            self.scripts_table_view.selectionModel().setCurrentIndex(ind, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows)

    def move_down(self, *args):
        rows = self.scripts_table_view.selectionModel().selectedRows()
        # logger.info(rows)
        if rows:
            # row = rows[0].row()
            self.scripts_table_view.model().move_down(rows[0].row())
            ind = self.scripts_table_view.model().index(rows[0].row() + 1, 0, QtCore.QModelIndex())
            self.scripts_table_view.selectionModel().setCurrentIndex(ind, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows)

    def result(self):
        res = dict()

        res['import_ref'] = True if self.import_references_input.checkState() == QtCore.Qt.Checked else False
        res['delete_ns'] = True if self.delete_namespaces_input.checkState() == QtCore.Qt.Checked else False
        res['optimize'] = True if self.clean_up_input.checkState() == QtCore.Qt.Checked else False
        res['delete_ng'] = True if self.delete_ng_input.checkState() == QtCore.Qt.Checked else False
        res['scripts'] = [s._path for s in self.scripts_table_view.model().items]
        res['massage'] = self.textNote.toPlainText()
        res['remember_settings'] = True if self.remember_input.checkState() == QtCore.Qt.Checked else False
        res['open_after'] = True if self.open_after_input.checkState() == QtCore.Qt.Checked else False

        return res


    def center_to_maya_window(self):

        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
