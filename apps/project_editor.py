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



import logging
import re
import os

import pipeline.libs.config as cfg
import pipeline.libs.data as dt
import pipeline.libs.models as models
import pipeline.libs.views as views
import pipeline.widgets.gui as gui
import pipeline.widgets.inputs as inputs
import pipeline.libs.misc as misc
import pipeline.libs.nodes.elements as elemtents
import pipeline.libs.branch_view as branch_view
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.CSS
from pipeline.CSS import loadCSS


logger = logging.getLogger(__name__)

class ProjectDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, **kwargs):
        super(ProjectDialog, self).__init__(parent)
        # self.setStyleSheet(cfg.stylesheet)

        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 10)
        # self.setMaximumHeight(150)
        self.setWindowTitle('Create new project')
        self.input_widget = QtWidgets.QWidget(self)
        self.input_layout = QtWidgets.QVBoxLayout(self.input_widget)

        self.title = gui.Title(self, label="New project")
        self.input_layout.addWidget(self.title)

        self.name_widget = inputs.GroupInput(self, label="Project name", inputWidget=QtWidgets.QLineEdit(self), ic=cfg.text_icon)
        self.name_input = self.name_widget.input
        self.input_layout.addWidget(self.name_widget)

        self.nice_name_widget = inputs.GroupInput(self, label="Nice name", inputWidget=QtWidgets.QLineEdit(self), ic=cfg.text_icon)
        self.nice_name_input = self.nice_name_widget.input
        self.input_layout.addWidget(self.nice_name_widget)


        self.path_widget = inputs.GroupInput(self, label="Project path", inputWidget=QtWidgets.QLineEdit(self), ic=cfg.text_icon)
        self.path_input = self.path_widget.input
        self.path_input.setEnabled(False)
        self.path_set_btn = QtWidgets.QPushButton()
        self.path_widget.layout.addWidget(self.path_set_btn)
        self.path_set_btn.setIcon(QtGui.QIcon(cfg.search_icon))
        self.path_set_btn.setIconSize(QtCore.QSize(20, 20))

        self.path_set_btn.clicked.connect(self.set_project_path)
        self.input_layout.addWidget(self.path_widget)

        self.input_padding_widget = inputs.GroupInput(self, label="Padding", inputWidget=QtWidgets.QSpinBox(self),
                                                      ic=cfg.counter_icon)

        self.padding_slider = self.input_padding_widget.input
        self.padding_slider.setMinimum(0)
        self.padding_slider.setMaximum(6)
        self.padding_slider.setValue(3)
        self.input_layout.addWidget(self.input_padding_widget)

        self.input_fps_widget = inputs.GroupInput(self, label="Default fps", inputWidget=QtWidgets.QComboBox(self),
                                                  ic=cfg.time_icon)
        self.fps_input = self.input_fps_widget.input
        self.fps_input.setEditable(False)
        rates = ["PAL (25fps)", "Film (24fps)", "NTSC (30fps)"]
        self.fps_input.addItems(rates)
        self.input_layout.addWidget(self.input_fps_widget)
        i = self.fps_input.findText(rates[0], QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.fps_input.setCurrentIndex(i)

        self.input_playblasts_switch_widget = inputs.GroupInput(self, label="Save playblast at", inputWidget=QtWidgets.QComboBox(self),
                                                                ic=cfg.icons.HDD)

        self.playblasts_switch_input = self.input_playblasts_switch_widget.input
        self.playblasts_switch_input.setEditable(False)
        rates = [cfg.playblast_save_options.PROJECT_ROOT, cfg.playblast_save_options.PROJECT_SISTER, cfg.playblast_save_options.COMPONENT]# "Projects root (Recommended)", "Project sister folder", "Component root"]
        self.playblasts_switch_input.addItems(rates)
        self.input_layout.addWidget(self.input_playblasts_switch_widget)
        i = self.playblasts_switch_input.findText(rates[0], QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.playblasts_switch_input.setCurrentIndex(i)

        # self.prefix_widget = inputs.GroupInput(self, label="Project prefix", inputWidget=QtWidgets.QLineEdit(self),
        #                                        ic=cfg.text_icon)
        # self.prefix_input = self.prefix_widget.input
        # self.input_layout.addWidget(self.prefix_widget)
        # self.playblasts_switch = inputs.GroupInput(self,label="Save playblasts to root folder",inputWidget= QtWidgets.QCheckBox(),ic = cfg.camrea_icon)
        # self.playblasts_switch_input = self.playblasts_switch.input
        # self.input_layout.addWidget(self.playblasts_switch)
        # self.playblasts_switch_input.stateChanged.connect(self.playblasts_switch_toggle)


        self.var_title = gui.Title(self, label="Project variables")
        self.input_layout.addWidget(self.var_title)

        self.layout.addWidget(self.input_widget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)


        self.tab_widgets = QtWidgets.QWidget(self)
        self.tab_widgets_layout = QtWidgets.QVBoxLayout(self.tab_widgets)
        self.tab_widgets_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widgets.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addWidget(self.tab_widgets)



        self.variable_tabs = gui.Tabs(self)
        self.tab_widgets_layout.addWidget(self.variable_tabs)

        self.branches_widget = QtWidgets.QWidget()

        self.branches_layout = QtWidgets.QVBoxLayout(self.branches_widget)
        # self.branches_widget.setMinimumHeight(600)
        self.branches_widget.setMinimumWidth(450)
        self.variable_tabs.tab_widget.addTab(self.branches_widget, "Branches")


        self.branches_view = branch_view.Branch_list_view(self)

        self.branches_layout.addWidget(self.branches_view)
        # self.branches_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


        self.users_widget = QtWidgets.QWidget()
        self.users_layout = QtWidgets.QVBoxLayout(self.users_widget)
        self.users_widget.setMinimumHeight(400)
        self.users_widget.setMinimumWidth(450)
        self.variable_tabs.tab_widget.addTab(self.users_widget, "Users")

        self.users_switch = inputs.GroupInput(self,label="Enable users",inputWidget= QtWidgets.QCheckBox(),ic = cfg.users_icon)
        self.users_swith_input = self.users_switch.input
        self.users_layout.addWidget(self.users_switch)
        self.users_swith_input.stateChanged.connect(self.users_table_toggle)
        self.users_tree = views.Project_Users_View(self.users_widget)
        self.users_layout.addWidget(self.users_tree)
        # self.users_tree.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)




        # self.list_view.setModel_(self.list_model)



        # self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.actions_widget = QtWidgets.QWidget(self)
        self.actions_widget_layout = QtWidgets.QVBoxLayout(self.actions_widget)
        self.actions_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.layout.addWidget(self.actions_widget)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.actions_widget_layout.addWidget(buttons)

        self.populate_brnaches()
        self.populated_users()

        # self.name_input.setText(cfg.preset["project_name"])
        self.padding_slider.setValue(3)
        # self.prefix_input.setText(cfg.preset["prefix"])

        self.name_input.textChanged.connect(self.name_changed)
        self.path_input.textChanged.connect(self.path_changed)


        self.users_swith_input.setCheckState(QtCore.Qt.Checked)
        self.users_table_toggle(QtCore.Qt.Checked)
        # self.playblasts_switch_input.setCheckState(QtCore.Qt.Checked)
        # self.playblasts_switch_toggle(QtCore.Qt.Checked)

        self.users_mode = True
        self.playblast_on_root = True

    def playblasts_switch_toggle(self, state):
        if state == QtCore.Qt.Checked:
            self.playblast_on_root = True
        else:
            self.playblast_on_root = False


    def users_table_toggle(self, state):
        if state == QtCore.Qt.Checked:
            self.users_tree.setEnabled(True)
            self.populated_users()
            self.users_mode = True
        else:
            self.users_tree.setEnabled(False)
            self.clear_users()
            self.users_mode = False


    def name_changed(self, str):
        self.name_input.setStyleSheet("")

    def path_changed(self, str):
        self.path_input.setStyleSheet("")


    def clear_users(self):
        try:
           del self.users_model
        except:
            pass
        self.users_tree.setModel(None)


    def populate_brnaches(self):
        branches = [dt.Node("assets"),dt.Node("scenes"),dt.Node("render")]
        self.branches_model = models.List_Model(branches)
        self.branches_view.setModel_(self.branches_model)


    def extract_branches_data(self):
        branches = list()
        if self.branches_model:
            for b in self.branches_model.items:
                branches.append(b.name)

        return branches

    def populated_users(self):

        user1 = dt.UserNode("administrator", "1234", "administrator")
        self.users_model = models.Users_Model([user1])
        self.users_tree.setModel(self.users_model)

    def exctract_users_data(self, model):
        if model:
            users = {}
            for index, user in enumerate(model.items):
                users[index] = [user.name, user._password, user._role]

            return users

    def set_project_path(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.path_input.setText(path)

    def accept(self):
        if (self.path_input.text() != ""):

            if (self.name_input.text() != ""):

                m = re.match("^[a-zA-Z0-9_-]*$", self.name_input.text())
                if not m:
                    self.name_input.setStyleSheet('''color: ''' + cfg.colors.WARNING_RED + ''';''')
                    logger.info("No special characters or whitespaces allowed")
                    return

                super(ProjectDialog, self).accept()

            else:

                self.name_input.setStyleSheet('''background: ''' + cfg.colors.WARNING_RED + ''';''')

                logger.info("Project needs a name")
                return

        else:

            self.path_input.setStyleSheet('''background: ''' + cfg.colors.WARNING_RED + ''';''')


            logger.info("Project a needs path")
            return

    # def accept(self):
    #
    #     m = re.match("^[a-zA-Z0-9_]*$", self.name_input.text())
    #     if not m:
    #         self.name_input.setStyleSheet("color: #CD5C5C;")
    #         logger.info("No special characters or whitespaces allowed")
    #     else:
    #         super(ProjectDialog, self).accept()


    def result(self):
        res = {}
        res["name"] = self.name_input.text()
        res["nice_name"] = self.nice_name_input.text()
        res["path"] = self.path_input.text()
        res["fps"] = self.fps_input.currentText()
        res["padding"] = self.padding_slider.value()
        res["users"] = self.exctract_users_data(self.users_tree.model())
        res["users_mode"] = self.users_mode
        res["branches"] = self.extract_branches_data()
        res["playblasts_root"] = self.playblasts_switch_input.currentText()

        return res

class Project_edit_Dialog(ProjectDialog):
    def __init__(self, parent=None, project=None, user_data = None, **kwargs):
        super(Project_edit_Dialog, self).__init__(parent, **kwargs)

        self.project = project
        self.user_data = user_data

        self.users_widget.setMinimumHeight(400)
        self.setWindowTitle('Edit project')
        self.title.label.setText("Edit project {} ({})".format(self.project.nice_name, self.project.project_name))
        self.name_widget.setHidden(True)
        self.nice_name_input.setText(self.project.nice_name)
        self.path_widget.setHidden(True)
        self.path_set_btn.setHidden(True)
        self.input_padding_widget.setHidden(True)
        self.input_fps_widget.setHidden(True)
        # self.input_playblasts_switch_widget.setHidden(True)

        # logger.info(self.project.users)
        if not self.project.users:
            self.users_swith_input.setCheckState(QtCore.Qt.Unchecked)
            self.users_table_toggle(QtCore.Qt.Unchecked)
        else:
            self.clear_users()
            self.populated_users()

        self.populate_brnaches()
        self.branches_view.dummy = False
        self.branches_view.project = self.project
        self.need_to_reload = False
        self.branches_view.edited.connect(self.set_need_to_reload_project)

        i = self.playblasts_switch_input.findText(self.project.project_playblasts_root, QtCore.Qt.MatchFixedString)
        if i >= 0:
            self.playblasts_switch_input.setCurrentIndex(i)



    def set_need_to_reload_project(self):
        self.need_to_reload = True

    def populate_brnaches(self):
        if hasattr(self, "project"):

            # logger.info(self.project.path)


            import pipeline.libs.files as files
            li = list()
            for dir in sorted(files.list_dir_folders(self.project.path)):
                path = os.path.join(self.project.path, dir)
                # logger.info(path)

                if misc.branch_dir(path):
                    li.append(elemtents.BranchNode(dir, path=path, project=self.project))

            if li:
                self.branches_model = models.List_Model(li)
                self.branches_view.setModel_(self.branches_model)



    def populated_users(self):
        if hasattr(self, "project"):
            if self.project.users:
                users_list = []
                users_dict = self.project.users


                '''
                dict structure

                {u'0': [u'root', u'1234', u'admin']}
                '''

                for k, v in users_dict.iteritems():
                    users_list.append(dt.UserNode(v[0], v[1], v[2]))


            #
            #
            # user1 = dt.UserNode("root", "1234", cfg._admin_)
                self.users_model = models.Users_Model(users_list)
                self.users_tree.setModel(self.users_model)
                return


        super(Project_edit_Dialog, self).populated_users()

    def reject(self):
        # logger.info("A")
        if self.need_to_reload:
            # logger.info("B")
            self.project.set(user=[self.user_data[0], self.user_data[1]])
            logger.info("need to reload")

        QtWidgets.QDialog.reject(self)

    def accept(self):
        # logger.info("~~~")
        # logger.info(self.user_data)
        # logger.info("Az")
        if self.need_to_reload:
            # logger.info("Bz")
            self.project.set(user=[self.user_data[0], self.user_data[1]])
            logger.info("need to reload")

        QtWidgets.QDialog.accept(self)

        # if (self.path_input.text() != "") and (self.name_input.text() != ""):
        #
        #     m = re.match("^[a-zA-Z0-9_]*$", self.name_input.text())
        #     if not m:
        #         self.name_input.setStyleSheet("color: #CD5C5C;")
        #         logger.info("No special characters or whitespaces allowed")
        #         return
        #
        #     super(ProjectDialog, self).accept()
        #
        # else:
        #     logger.info("Project must have a name and path")


    def result(self):
        res = {}
        # res["name"] = self.name_input.text()
        res["nice_name"] = self.nice_name_input.text()
        # res["path"] = self.path_input.text()
        # res["fps"] = self.fps_input.currentText()
        # res["padding"] = self.padding_slider.value()
        # res["prefix"] = self.prefix_input.text()
        res["users"] = self.exctract_users_data(self.users_tree.model())
        res["users_mode"] = self.users_mode
        res["playblasts_root"] = self.playblasts_switch_input.currentText()

        return res
