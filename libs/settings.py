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

import pipeline.maya_libs.maya_warpper as maya
import pipeline.libs.serializer as serializer
import pipeline.maya_libs.maya_warpper as maya

logger = logging.getLogger(__name__)


def settings_node():
    """
    This function will find the setting file in the users maya prefs dir, and then ini the setting class from it.
    If no file will be found a new empty settings file will be created.
    """

    # logger.info("Initialized settings file")

    settings_file_name = 'pipeline2_settings.json'
    file = os.path.join(maya.userPrefDir(), settings_file_name)

    if os.path.isfile(file):
        return SettingsNode(path=file)
        # return True

    return SettingsNode().create(path=file)
    # return True




class SettingsNode(serializer.Metadata_file):

    def __init__(self, **kwargs):
        super(SettingsNode, self).__init__(**kwargs)
        # serializer.Metadata_file.__init__(self, **kwargs)

        self.settings_file = None
        if self.data_file:
            self.settings_file = self.data_file.read()

        self._current_role = None

    def create(self, path):

        projects = {}

        settings_data = {}
        settings_data["user"] = [None, None]
        settings_data["current_project"] = None
        settings_data["projects"] = projects
        settings_data["check_for_updates"] = True

        self.data_file = serializer.JSONSerializer().create(path, settings_data)
        self.settings_file = self.data_file.read()
        logger.info("Created pipeline settings file at: {}".format(path))
        return self

    # def project_path(self, project_key=None):
    #
    #     if self.settings_file:
    #         return self.projects[project_key][0]

    @property
    def projects(self):

        if self.settings_file:
            return self.settings_file["projects"]

    @projects.setter
    def projects(self, projects):

        if self.data_file:
            data = {}
            data["projects"] = projects
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()

    @property
    def user(self):

        if self.settings_file:
            return self.settings_file["user"]

    @user.setter
    def user(self, user):

        if self.data_file:
            data = {}
            data["user"] = user
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()


    def current_role(self):
        return self._current_role

    def set_current_role(self, role):
        self._current_role = role

    @property
    def check_for_updates(self):
        if self.settings_file:
            try:
                return self.settings_file["check_for_updates"]
            except:
                return True


    @check_for_updates.setter
    def check_for_updates(self, bool):
        if self.data_file:
            data = {}
            data["check_for_updates"] = bool
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()

    @property
    def playblast_format(self):
        if self.settings_file:
            try:
                # return 'movie'
                return self.settings_file["playblast_format"]
            except:
                # if files.os_qeury() == "win32":
                #     return "qt"
                # else:
                return "movie"

    @playblast_format.setter
    def playblast_format(self, format):
        if self.data_file:
            data = {}
            data["playblast_format"] = format
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()

    @property
    def playblast_compression(self):
        if self.settings_file:
            try:
                # return None
                return self.settings_file["playblast_compression"]
            except:
                available_formats = maya.getPlayblastCompression(self.playblast_format)
                if 'H.264' in available_formats:
                    return 'H.264'
                else:
                    return None

    @playblast_compression.setter
    def playblast_compression(self, type):
        if self.data_file:
            data = {}
            data["playblast_compression"] = type
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()

    @property
    def playblast_hud(self):
        if self.settings_file:
            try:
                return self.settings_file["playblast_hud"]
            except:
                return True

    @playblast_hud.setter
    def playblast_hud(self, type):
        if self.data_file:
            data = {}
            data["playblast_hud"] = type
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()


    # @property
    # def playblast_camera(self):
    #     if self.settings_file:
    #         try:
    #             return self.settings_file["playblast_camera"]
    #         except:
    #             return 'Active camera'
    #
    # @playblast_camera.setter
    # def playblast_camera(self, value):
    #     if self.data_file:
    #         data = {}
    #         data["playblast_camera"] = value
    #         self.data_file.edit(data)
    #         self.settings_file = self.data_file.read()

    @property
    def playblast_offscreen(self):
        if self.settings_file:
            try:
                return self.settings_file["playblast_offscreen"]
            except:
                return False

    @playblast_offscreen.setter
    def playblast_offscreen(self, type):
        if self.data_file:
            data = {}
            data["playblast_offscreen"] = type
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()

    @property
    def playblast_scale(self):
        if self.settings_file:
            try:
                return self.settings_file["playblast_scale"]
            except:
                return 100

    @playblast_scale.setter
    def playblast_scale(self, int):
        if self.data_file:
            data = {}
            data["playblast_scale"] = int
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()


    @property
    def project(self):
        if self.settings_file:
            try:
                return self.settings_file["project"]
            except:
                return None
        else:
            return None

    @project.setter
    def project(self, project_key):
        if self.data_file:
            data = {}
            data["project"] = project_key
            self.data_file.edit(data)
            self.settings_file = self.data_file.read()

