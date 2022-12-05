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
import os

import pipeline.apps.project_editor as project_editor
import pipeline.libs.config as cfg
import pipeline.libs.files as files
import pipeline.libs.projects as projects
import pipeline.libs.views as views
import pipeline.widgets.gui as gui
import pipeline.libs.legacy.projects as legacy_projects
import pipeline.apps.massage as massage
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.widgets.inputs as inputs
reload(inputs)
import pipeline.CSS
from pipeline.CSS import loadCSS

logger = logging.getLogger(__name__)

class ProjectsDialog(QtWidgets.QMainWindow): #QtWidgets.QDialog):
    def __init__(self, parent=None):

        super(ProjectsDialog, self).__init__(parent)

        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)

        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.pipeline_window = self.parent()

        self.setMinimumHeight(600)
        self.setMinimumWidth(600)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.center_to_maya_window()



        self.main_widget = QtWidgets.QWidget(self)

        self.setCentralWidget(self.main_widget)

        # self.setStyleSheet(cfg.stylesheet)

        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        # self.setLayout(self.layout)

        self.setWindowTitle("Projects")

        self.header = gui.Title(self, label="Current Projects")
        self.header.setMaximumHeight(40)
        self.layout.addWidget(self.header)

        self.project_table_widget = QtWidgets.QWidget(self)
        self.projects_table_widget_layout = QtWidgets.QVBoxLayout(self.project_table_widget)
        self.projects_table_widget_layout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.project_table_widget)

        self.projects_table_view = views.Projects_View(parent=self, parentWidget=self.project_table_widget)
        self.project_table_widget.layout().addWidget(self.projects_table_view)
        self.projects_table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.projects_table_view.setModel_(self.pipeline_window.projects)


        self.actions_widget = QtWidgets.QWidget(self)
        self.actions_widget_layout = QtWidgets.QHBoxLayout(self.actions_widget)
        self.actions_widget_layout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.actions_widget)

        self.create_project_btn = QtWidgets.QPushButton("Create Project")#inputs.NiceQLabelButton("Create new Project")#
        self.create_project_btn.setIcon(QtGui.QIcon(cfg.new_icon))
        self.create_project_btn.setIconSize(QtCore.QSize(20, 20))

        self.load_project_btn = QtWidgets.QPushButton("Load Project")
        self.load_project_btn.setIcon(QtGui.QIcon(cfg.load_icon))
        self.load_project_btn.setIconSize(QtCore.QSize(20, 20))

        self.unload_project_btn = QtWidgets.QPushButton("Unload Project")
        self.unload_project_btn.setIcon(QtGui.QIcon(cfg.unload_icon))
        self.unload_project_btn.setIconSize(QtCore.QSize(20, 20))

        self.actions_widget_layout.addWidget(self.create_project_btn)
        self.actions_widget_layout.addWidget(self.load_project_btn)
        self.actions_widget_layout.addWidget(self.unload_project_btn)

        self.create_project_btn.clicked.connect(self.create_project)
        self.load_project_btn.clicked.connect(self.load_project)
        self.unload_project_btn.clicked.connect(self.unload_project)

    def center_to_maya_window(self):
        # self.move(self.pipeline_window.maya_main.window().frameGeometry().topLeft() + self.pipeline_window.maya_main.window().rect().center() - self.rect().center())

        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def closeEvent(self, ev):
        del self.parent().projects_dialog

    def create_project(self):

        project = ProjectsDialog._create_project(self.pipeline_window)
        if project:
        # logger.info(self.create_project.__name__)
        #
        # projectDlg = project_editor.ProjectDialog()
        # result = projectDlg.exec_()
        # res = projectDlg.result()
        # if result == QtWidgets.QDialog.Accepted:
        #
        #     project_path = os.path.join(res["path"],res["name"])
        #     project_name = res["name"]
        #     padding = res["padding"]
        #     # file_type = "ma"
        #     fps = 25
        #
        #     if res["fps"] == "PAL (25fps)":
        #         fps = 25
        #     if res["fps"] == "Film (24fps)":
        #         fps = 24
        #     if res["fps"] == "NTSC (30fps)":
        #         fps = 30
        #
        #     users = res["users"] if res["users_mode"] == True else None
        #     # prefix = res["prefix"]
        #     branches = res["branches"]
        #     # logger.info(bra/nches)
        #     nice_name = res["nice_name"]
        #
        #     playblasts_root = res["playblasts_root"]
        #
        #
        #     project = projects.ProjectNode(project_name, None, pipelineUI=self.pipeline_window).create(
        #                                                                             nice_name=nice_name,
        #                                                                             path=project_path,
        #                                                                             padding=padding,
        #                                                                             fps=fps,
        #                                                                             users=users,
        #                                                                             branches = branches,
        #                                                                             playblasts_root = playblasts_root)
        #
        #
        #     self.pipeline_window.new_project(project)
        #     project.set()

            if not self.projects_table_view.model():
                self.projects_table_view.setModel_(self.pipeline_window.projects)

            QtWidgets.QDialog.raise_(self)




    @staticmethod
    def _create_project(pipelineUI = None):
        # logger.info(self.create_project.__name__)

        projectDlg = project_editor.ProjectDialog()
        result = projectDlg.exec_()
        res = projectDlg.result()
        if result == QtWidgets.QDialog.Accepted:

            project_path = os.path.join(res["path"],res["name"])
            project_name = res["name"]
            padding = res["padding"]
            # file_type = "ma"
            fps = 25

            if res["fps"] == "PAL (25fps)":
                fps = 25
            if res["fps"] == "Film (24fps)":
                fps = 24
            if res["fps"] == "NTSC (30fps)":
                fps = 30

            users = res["users"] if res["users_mode"] == True else None
            # prefix = res["prefix"]
            branches = res["branches"]
            # logger.info(bra/nches)
            nice_name = res["nice_name"]

            playblasts_root = res["playblasts_root"]


            project = projects.ProjectNode(project_name, None, pipelineUI=pipelineUI).create(
                                                                                    nice_name=nice_name,
                                                                                    path=project_path,
                                                                                    padding=padding,
                                                                                    fps=fps,
                                                                                    users=users,
                                                                                    branches = branches,
                                                                                    playblasts_root = playblasts_root)

            pipelineUI.new_project(project)

            if users:
                project.set(user = [users[0][0],users[0][1]])
            else:
                project.set()

            pipelineUI.populate_projects_button()

            return True

        return False




    def load_project(self):
        # logger.info(self.load_project.__name__)
        #
        # path = QtWidgets.QFileDialog.getOpenFileName(self, "Select Pipeline project file", filter = "*.*")
        # if path[0]:
        #
        #     logger.info(files.file_name(path[0]))
        #     logger.info(files.extension(files.file_name(path[0])))
        #     if files.extension(files.file_name(path[0])) == ".pipe":
        #         msg = "This project was created with an older version of Pipeline.\n\n" \
        #               "Pipeline data files needs to be converted.\n" \
        #               "Original files won't be changed."
        #         prompt = massage.PromptUser(self, prompt=msg,override_yes_text="Proceed", override_no_label="Cancel")
        #         result = prompt.exec_()
        #         if result == 0:
        #             legacy_projects.Legacy_project(path=str(path[0])).convert()
        #         else:
        #             logger.info("Abort project convertion")
        #             return
        #
        #
        #
        #     project_name = files.path.lastdir(os.path.dirname(path[0]))
        #     project_path = os.path.dirname(path[0])
        #     project = projects.ProjectNode(project_name, parent=None, pipelineUI=self.pipeline_window, path= project_path )
        #
        #     if project.set():
        #         self.pipeline_window.new_project(project)
        #
        #     self.pipeline_window.populate_projects_button()

        if self._load_project(self.pipeline_window):

            if not self.projects_table_view.model():
                self.projects_table_view.setModel_(self.pipeline_window.projects)

    @staticmethod
    def _load_project(pipelineUI = None):

        # path = QtWidgets.QFileDialog.getOpenFileName(pipelineUI, "Select Pipeline project file", filter="*.*")
        path = inputs.FileDialog.get_file(caption='Select Pipeline project file', filter='*.*')
        if path:

            logger.info(files.file_name(path))
            logger.info(files.extension(files.file_name(path)))
            if files.extension(files.file_name(path)) == ".pipe":
                msg = "This project was created with an older version of Pipeline.\n\n" \
                      "Pipeline data files needs to be converted.\n" \
                      "Original files won't be changed."
                prompt = massage.PromptUser(pipelineUI, prompt=msg, override_yes_text="Proceed",
                                            override_no_label="Cancel")
                result = prompt.exec_()
                if result == 0:
                    legacy_projects.Legacy_project(pipelineUI = pipelineUI, path=str(path)).convert()
                else:
                    logger.info("Abort project convertion")
                    return

            project_name = files.path.lastdir(os.path.dirname(path))
            project_path = os.path.dirname(path)
            project = projects.ProjectNode(project_name, parent=None, pipelineUI=pipelineUI,
                                           path=project_path)

            if project.set():
                pipelineUI.new_project(project)

            pipelineUI.populate_projects_button()

            return True

        return False



    def unload_project(self):

        logger.info(self.unload_project.__name__)

        index = self.projects_table_view.selectionModel().selectedRows()[0]
        index = self.projects_table_view.model().mapToSource(index)

        self.pipeline_window.remove_project(index)
        self.pipeline_window.populate_projects_button()

        if not self.projects_table_view.model().sourceModel().items:
            self.projects_table_view.setModel_(None)






