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
import pipeline.libs.data as dt
import pipeline.libs.nodes.elements as elements
import pipeline.libs.files as files
import pipeline.libs.serializer as serializer
import pipeline.libs.misc as misc
import pipeline.apps.massage as massage
import pipeline.apps.users as users


from pipeline.libs.Qt import QtWidgets, QtCore

logger = logging.getLogger(__name__)

class RootNode(dt.Node):

    def __init__(self, name, parent=None, **kwargs):

        super(RootNode, self).__init__(name, parent, **kwargs)

        self.name = name
        self.resource = cfg.folder_icon
        self.data_file = None
        self.data_file_path = None
        self._settings = None
        self._project = None
        self._ui = None

        for key in kwargs:
            if key == "path":
                self._path = kwargs[key]
                self.data_file_path = os.path.join(kwargs[key], "%s.%s" % (os.path.split(kwargs[key])[1], "json"))
            if key == "project":
                self._project = kwargs[key]
            if key == "settings":
                self._settings = kwargs[key]
            if key == "ui":
                self._ui = kwargs[key]

        if self.data_file_path:
            self.set_data_file(self.data_file_path)

    @property
    def path(self):
        return os.path.normpath(self._path)

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def settings(self):
        return self._settings

    @property
    def color(self):
        if self.approved_stage:
            return QtWidgets.QColor("#00fa9a")
        else:
            return QtWidgets.QColor("white")

    @property
    def relative_path(self):
        if self.path and self._project:
            return files.reletive_path(self._project.path, self.path)

    @property
    def ansestors(self):
        try:
            ansestors = files.splitall(self.relative_path)
            # ansestors.reverse()
            return ansestors
        except:
            return None

    def ansestor(self, int):
        ansestors = self.ansestors
        if ansestors and len(ansestors) >= int:
            return self.ansestors[int]

        return None

    def typeInfo(self):
        return cfg._root_

    def set_data_file(self, path):
        if os.path.isfile(path):
            self.data_file = serializer.JSONSerializer(path=path)

            return True
        else:
            pass

    def create(self, path=None):
        if files.create_directory(path):
            self.path = path
            return self
        else:
            return False




class ProjectNode(RootNode):
    loaded = QtCore.Signal(dict)

    def __init__(self, name, parent=None, **kwargs):

        super(ProjectNode, self).__init__(name, parent, **kwargs)

        self.project_file = None
        if self.data_file:
            self.project_file = self.data_file.read()

        self.pipelineUI = None
        for key in kwargs:
            if key == "pipelineUI":
                self.pipelineUI = kwargs[key]
                self.loaded.connect(self.pipelineUI.updateCurrentProject)

    def create(self,
               nice_name = None,
               path=None,
               padding=3,
               fps=25,
               file_type = "ma",
               users={"0": ["Admin", "1234", "admin"]},
               branches = ["scenes", "assets"],
               playblasts_root = cfg.playblast_save_options.PROJECT_ROOT,
               prefix=None):

        file_type = "ma"

        project_key = serializer.id_generator()
        project_data = {}

        project_data["nice_name"] = nice_name if nice_name else self.name
        project_data["project_name"] = self.name
        project_data["project_key"] = project_key
        project_data["padding"] = padding
        project_data["fps"] = fps
        project_data["defult_file_type"] = file_type
        project_data["users"] = users
        project_data["playblasts_root"] = playblasts_root
        # project_data["prefix"] = prefix
        # project_data["playblast_outside"] = playblast_outside

        folders = ["scenes", "assets","images", "sourceimages", "data", "autosave", "movies", "scripts",
                   "sound", "clips", "renderData", "cache"]

        for folder in folders:
            # project_data[folder] = folder
            files.create_directory(os.path.join(path, folder))

        # render folders:
        r_folders = ["renderData", "depth", "iprimages", "shaders"]
        for r_folder in r_folders[1:]:
            files.create_directory(os.path.join(path, r_folders[0], r_folder))

        fur_folders = ["renderData", "fur", "furFiles", "furImages", "furEqualMap", "furAttrMap", "furShadowMap"]
        for f_folder in fur_folders[2:]:
            files.create_directory(os.path.join(path, fur_folders[0], fur_folders[1], f_folder))

        # cache folders:
        c_folders = ["cache", "particles", "nCache", "bifrost"]
        for c_folder in c_folders[1:]:
            files.create_directory(os.path.join(path, c_folders[0], c_folder))

        fl_folders = ["cache", "nCache", "fluid"]
        for fl_folder in fl_folders[2:]:
            files.create_directory(os.path.join(path, fl_folders[0], fl_folders[1], fl_folder))


        self.path = path
        data_path = os.path.join(path, "%s.%s" % (self.name, "json"))
        self.data_file_path = data_path
        self.data_file = serializer.JSONSerializer().create(self.data_file_path, project_data)
        self.project_file = self.data_file.read()

        for branch in branches:
            elements.BranchNode(branch, path=os.path.join(path, branch), project = self).create(path=os.path.join(path, branch))
            # elements.BranchNode("assets", path=os.path.join(path, "assets"), project = self).create(path=os.path.join(path, "assets"))

        if playblasts_root == cfg.playblast_save_options.PROJECT_ROOT:
            files.create_directory(os.path.join(path, "playblasts"))

        if playblasts_root == cfg.playblast_save_options.PROJECT_SISTER:
            try:
                files.create_directory(os.path.join(os.path.dirname(path), "{}_playblasts".format(self.name)))
            except:
                logger.info("Could not create Playblasts folder at: {}".format(os.path.dirname(path)))

        return self

    def online(self):
        if os.path.isdir(self.path):
            if os.path.isfile(self.data_file_path):
                return True

        return False

    def edit(self):
        logger.info(self.edit.__name__)

        # _users = True if self.project_users else False

        user = self.pipelineUI.settings.user[0]
        password =self.pipelineUI.settings.user[1]


        projectDlg = project_editor.Project_edit_Dialog(project=self, user_data = [user, password])
        result = projectDlg.exec_()
        res = projectDlg.result()
        if result == QtWidgets.QDialog.Accepted:
            # logger.info(res)

            self.nice_name = res["nice_name"]
            if res["users_mode"]:
                self.users = res["users"]
            else:
                self.users = None

            if res["playblasts_root"] != self.project_playblasts_root:
                self.set_playblasts_root(res["playblasts_root"])

            self.set(user = [user,password])
            self.pipelineUI.navigate_to_current_file()


    def validate_user(self, username=None, password=None):
        for key in self.users:
            if self.users[key][0] == username and self.users[key][1] == password:
                role = self.users[key][2]
                if role == 'admin':
                    role = 'administrator'

                return role

        return ''

    def link(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None,  "Select Pipeline project file", filter = "*.*")
        if path[0]:

            project_path = os.path.dirname(path[0])

            self.path = project_path
            self.data_file_path = path[0]
            self.set_data_file(self.data_file_path)
            self.project_file = self.data_file.read()
            self.pipelineUI.link_project(self)


    def set(self, **kwargs):

        user = ''
        password = ''
        role = ''

        if 'user' in kwargs:
            user = kwargs['user'][0]
            password = kwargs['user'][1]


        if self.data_file:
            _users = True if self.project_users else False




            if self.project_users:
                # the project is permission based
                if user == '':
                    # no user was called with the function, need to prompt for credentials
                    login = users.LoginWindow()
                    result = login.exec_()
                    user, password = login.result()
                    if result == QtWidgets.QDialog.Accepted:
                        # user entered credentials

                        role = self.validate_user(user, password)
                        # from user+password, return the role
                        if role == '':
                            # if no role was return there is no such user
                            logger.info("invalid username or password")
                            return False
                        else:
                            # recived valid role, set the user as current in the settings
                            self.pipelineUI.settings.user = [user, password]
                    else:
                        # user aborted, exit
                        return False
                else:
                    # the function was called with a user+password, let's get their role
                    role = self.validate_user(user, password)
                    self.pipelineUI.settings.user = [user, password]
                    if role == '':
                        # if no role was return there is no such user
                        logger.info("invalid username or password")
                        return False


            import pymel.core as pm
            import maya.mel as mel

            pm.workspace.open(self.path)
            pm.workspace.chdir(self.path)

            raw_project_path = self.path.replace("\\", "\\\\")
            melCmd = "setProject \"" + raw_project_path + "\";"
            try:
                mel.eval(melCmd)
            except:
                pass

            logger.info("Project changed to: {} ({})".format(self.nice_name, self.name))

            self.loaded.emit({'users': _users,'user': user, 'role': role})
            return True



    def project_file_key(self, key=None):
        if self.project_file:
            return self.project_file[key]
        else:
            return None


    def set_playblasts_root(self, new_root):

        project_root = cfg.playblast_save_options.PROJECT_ROOT
        project_sister = cfg.playblast_save_options.PROJECT_SISTER
        component_root = cfg.playblast_save_options.COMPONENT

        def get_fullpath_if_is_component(dir):
            if os.path.exists(dir):
                if os.path.isfile(os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json"))):
                    j = serializer.Metadata_file(path=os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json")))
                    info = j.data_file.read()
                    if info:

                        if info["typeInfo"] == cfg._component_:
                            return "_".join(info["fullpath"])

            return False

        def move_playblasts_into_components(move_from):
            # logger.info("move_playblasts_into_components from {}, to {}".format(move_from, "components"))

            for branch in self.branches:

                for root, subFolders, _files in os.walk(branch):

                    for s in subFolders:
                        p = os.path.join(root, s)

                        fullpath = get_fullpath_if_is_component(p)

                        if fullpath:

                            b = os.path.split(branch)[1]

                            master_avi = os.path.join(move_from, b, "{}_MASTER.avi".format(fullpath))
                            master_mov = os.path.join(move_from, b, "{}_MASTER.mov".format(fullpath))
                            versions_dir = os.path.join(move_from, b, "versions", fullpath)

                            if os.path.isfile(master_avi):
                                logger.info("*.avi master from: {}".format(master_avi))

                                target_master_avi = os.path.join(p, "{}_MASTER.avi".format(fullpath))
                                logger.info("will move to: {}".format(target_master_avi))
                                files.dir_move(master_avi, target_master_avi)

                            if os.path.isfile(master_mov):
                                logger.info("*.mov master from: {}".format(master_mov))

                                target_master_mov = os.path.join(p, "{}_MASTER.mov".format(fullpath))
                                logger.info("will move to: {}".format(target_master_mov))
                                files.dir_move(master_mov, target_master_mov)

                            if os.path.isdir(versions_dir):
                                logger.info("playblasts versions folder from: {}".format(versions_dir))

                                target_dir = os.path.join(p, "playblasts")
                                logger.info("will move to: {}".format(target_dir))
                                files.dir_move(versions_dir, target_dir)

            logger.info("<>")
            logger.info(os.listdir(os.path.join(move_from, b, "versions")))

            if not os.listdir(os.path.join(move_from, b, "versions")): files.delete(os.path.join(move_from, b, "versions"))
            if not os.listdir(os.path.join(move_from, b)): files.delete(os.path.join(move_from, b))
            if not os.listdir(move_from): files.delete(move_from)


        def move_playblasts_to_single_folder(move_to):
            # logger.info("move_playblasts_to_single_folde from {}, to {}".format(current_root, move_to))

            for branch in self.branches:
                b = os.path.split(branch)[1]

                for root, subFolders, _files in os.walk(branch):

                    for s in subFolders:
                        p = os.path.join(root, s)

                        fullpath = get_fullpath_if_is_component(p)

                        if fullpath:

                            master_avi = os.path.join(p, "{}_MASTER.avi".format(fullpath))
                            master_mov = os.path.join(p, "{}_MASTER.mov".format(fullpath))
                            versions_dir = os.path.join(p, "playblasts")

                            if os.path.isfile(master_mov):
                                target_master_mov = os.path.join(move_to, b, "{}_MASTER.mov".format(fullpath))

                                files.assure_folder_exists(os.path.join(move_to, b))

                                files.dir_move(master_mov, target_master_mov)

                            if os.path.isfile(master_avi):
                                target_master_avi = os.path.join(move_to, b, "{}_MASTER.avi".format(fullpath))

                                files.assure_folder_exists(os.path.join(move_to, b))

                                files.dir_move(master_avi, target_master_avi)

                            if os.path.isdir(versions_dir):
                                target_dir = os.path.join(move_to, b,"versions", fullpath)

                                files.assure_folder_exists(os.path.join(move_to, b ,"versions"))

                                files.dir_move(versions_dir, target_dir)


        current_root = self.project_playblasts_root

        msg = "You are about to move your playblasts folder from {0}, to {1}.\n" \
              "This may take a few minutes.".format(current_root, new_root)

        prompt = massage.PromptUser(self.pipelineUI, prompt=msg, override_yes_text="Proceed", override_no_label="Don't move",
                                    cancel_button=False)

        result = prompt.exec_()
        if result == 0:

            if (current_root == project_root) or (current_root == project_sister):

                if (new_root == project_root) or (new_root == project_sister):

                    current_playblasts_folder = self.playblasts_path
                    self.project_playblasts_root = new_root
                    files.dir_move(current_playblasts_folder, self.playblasts_path)
                    return

                else:

                    move_playblasts_into_components(self.playblasts_path)
                    self.project_playblasts_root = new_root
                    return
            else:

                if (new_root == project_root) or (new_root == project_sister):

                    self.project_playblasts_root = new_root
                    move_playblasts_to_single_folder(self.playblasts_path)
                    return


    def explore(self):
        files.explore(self.path)

    @property
    def branches(self):
        branches = list()
        for dir in files.list_dir_folders(self.path):
            if misc.branch_dir(os.path.join(self.path, dir)):
                branches.append(os.path.join(self.path, dir))

        return branches

    @property
    def nice_name(self):
        if self.project_file:
            try:
                return self.project_file["nice_name"]
            except:
                return self.name
        else:
            return self.name

    @nice_name.setter
    def nice_name(self, nice_name):

        if self.data_file:
            data = {}
            data["nice_name"] = nice_name
            self.data_file.edit(data)
            self.project_file = self.data_file.read()

    @property
    def project_name(self):
        if self.project_file:
            return self.project_file["project_name"]
        else:
            return None

    @property
    def project_fps(self):
        if self.project_file:
            if "fps" in self.project_file.keys():
                return self.project_file["fps"]
            else:
                return None
        else:
            return None

    @project_fps.setter
    def project_fps(self, fps):

        if self.data_file:
            data = {}
            data["fps"] = fps
            self.data_file.edit(data)
            self.project_file = self.data_file.read()

    @property
    def project_key(self):
        if self.project_file:
            return self.project_file["project_key"]
        else:
            return None

    @property
    def project_padding(self):
        if self.project_file:
            return self.project_file["padding"]
        else:
            return None

    @property
    def project_file_type(self):
        if self.project_file:
            return self.project_file["defult_file_type"]
        else:
            return None

    @project_file_type.setter
    def project_file_type(self, type):

        if self.data_file:
            data = {}
            data["defult_file_type"] = type
            self.data_file.edit(data)
            self.project_file = self.data_file.read()

    @property
    def project_playblasts_root(self):
        if self.project_file:
            if "playblasts_root" in self.project_file:
                return self.project_file["playblasts_root"]

        return cfg.playblast_save_options.PROJECT_ROOT

    @project_playblasts_root.setter
    def project_playblasts_root(self, root_type):

        if self.data_file:
            data = {}
            data["playblasts_root"] = root_type
            self.data_file.edit(data)
            self.project_file = self.data_file.read()

    #
    # @property
    # def movie_file_type(self):
    #     if self.project_file:
    #         return "mov"
    #     else:
    #         return None

    @property
    def project_users(self):
        if self.project_file:
            if "users" in self.project_file.keys():
                return self.project_file["users"]
            else:
                return None
        else:
            return None

    @project_users.setter
    def project_users(self, users):

        if self.data_file:
            data = {}
            data["users"] = users
            self.data_file.edit(data)
            self.project_file = self.data_file.read()

    # @property
    # def playblast_outside(self):
    #     if self.project_file:
    #         if "playblast_outside" in self.project_file.keys():
    #             return self.project_file["playblast_outside"]
    #         else:
    #             return False
    #     else:
    #         return None
    #
    # @playblast_outside.setter
    # def playblast_outside(self, playblast_outside):
    #
    #     old_path = self.playblasts_path
    #
    #     if self.data_file:
    #         data = {}
    #         data["playblast_outside"] = playblast_outside
    #         self.data_file.edit(data)
    #         self.project_file = self.data_file.read()
    #
    #         files.dir_move(old_path, self.playblasts_path)

    @property
    def playblasts_path(self):
        if self.project_file:
            if self.project_playblasts_root == cfg.playblast_save_options.PROJECT_ROOT:
                return os.path.join(self.path, "playblasts")
            if self.project_playblasts_root == cfg.playblast_save_options.PROJECT_SISTER:
                return os.path.join(os.path.dirname(self.path), "{}_playblasts".format(self.name))

        return ""


    @property
    def users(self):
        if self.project_file:
            return self.project_file["users"]
        else:
            return None

    @users.setter
    def users(self, dict):
        if self.data_file:
            data = {}
            data["users"] = dict
            self.data_file.edit(data)
            self.project_file = self.data_file.read()

    # @property
    # def prefix(self):
    #     if self.project_file:
    #         return self.project_file["prefix"]
    #     else:
    #         return None
    #



class Dummy_project(object):

    dummy_project_name = "dummy"
    dummy_project_nice_name = "Dummy project"
    dummy_ma_file = os.path.join(os.path.dirname(__file__), "debug", "dummy_scene.ma")

    def __init__(self):
        pass


    @classmethod
    def create_dummy_project(cls, pipeline_window):
        path_query = str(QtWidgets.QFileDialog.getExistingDirectory(pipeline_window, "Select Directory"))
        path = os.path.join(path_query, Dummy_project.dummy_project_name)

        project = ProjectNode(Dummy_project.dummy_project_name, None, pipelineUI=pipeline_window).create(
            nice_name=Dummy_project.dummy_project_nice_name,
            path=path)



        #assets branch

        for i in range(0, 6):
            catagory_name = "cat_{}".format(i)
            catagory_path = os.path.join(path, "assets", catagory_name)
            elements.CatagoryNode(catagory_name, path=catagory_path, project=project).create(path=catagory_path)

            for y in range(0,3):
                subcatagory_name = "subcat_{}".format(y)
                subcatagory_path = os.path.join(path, "assets", catagory_name, subcatagory_name)
                elements.CatagoryNode(subcatagory_name, path=subcatagory_path, project=project).create(path=subcatagory_path)

                for z in range(0,2):

                    comp_name = "comp_{}".format(z)
                    comp_path = os.path.join(path, "assets", catagory_name, subcatagory_name, comp_name)
                    comp_node = elements.ComponentNode(comp_name, path=comp_path, format=1,
                                                      project=project).create(path=comp_path)

                    comp_node.save_version(method="From File", debug = True, file_path = Dummy_project.dummy_ma_file)

        pipeline_window.new_project(project)
        project.set()


