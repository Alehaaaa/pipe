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
import pipeline.libs.files as files
import pipeline.libs.legacy.pickle_dict as pickle
import pipeline.libs.projects as projects
import pipeline.libs.nodes.elements as elements


logger = logging.getLogger(__name__)

class Legacy_project(object):
    def __init__(self, pipelineUI = None, path = None):

        self.project = None
        self.path = path
        self.pipelineUI = pipelineUI
        self.data = pickle.pickleDict(path=path)


    def convert(self):
        if self.data:
            self.converted_data = dict()
            self.project_data = self.data.read()

            logging.info(
                "Converting {}, Original files will remain unchaged. New project will be created without users".format(
                    self.project_data["project_name"]))

            self.converted_data["project_name"] = self.project_data["project_name"]
            self.converted_data["padding"] = self.project_data["padding"]
            self.converted_data["fps"] = self.project_data["fps"]
            self.converted_data["defult_file_type"] = self.project_data["defult_file_type"]
            self.converted_data["project_key"] = self.project_data["project_key"]
            self.converted_data["users"] = None

            logging.info(os.path.dirname(self.path))
            self.project = projects.ProjectNode(self.converted_data["project_name"], pipelineUI = self.pipelineUI).create(
                nice_name=self.converted_data["project_name"],
                path=os.path.dirname(self.path),
                padding=self.converted_data["padding"],
                fps=self.converted_data["fps"],
                file_type=self.converted_data["defult_file_type"],
                users=self.converted_data["users"])

        self.convert_assets_tree()
        self.convert_scenes_tree()



    def convert_assets_tree(self):
        if self.project:

            for cat in files.list_dir_folders(os.path.join(self.project.path, "assets")):

                # logger.info("{} / {}".format("assets", cat))

                cat_path = os.path.join(self.project.path, "assets", cat)

                cat_node = elements.CatagoryNode(cat, path=cat_path, project=self.project).create(path=cat_path)

                for ast in files.list_dir_folders(os.path.join(self.project.path, "assets", cat)):

                    # logging.info("{} / {} / {}".format("assets", cat, ast))

                    ast_path = os.path.join(self.project.path, "assets", cat, ast)

                    ast_node = elements.CatagoryNode(ast, path=ast_path, project=self.project).create(path=ast_path)


                    for comp in files.list_dir_folders(os.path.join(self.project.path, "assets", cat, ast)):

                        comp_path = os.path.join(self.project.path, "assets", cat, ast, comp, "{}.pipe".format(comp))
                        comp_node = Legacy_component(path=comp_path, project = self.project)
                        # logging.info("{} / {} / {} / {} IS COMPONENT".format("assets", cat, ast, comp))


    def convert_scenes_tree(self):
        if self.project:

            for seq in files.list_dir_folders(os.path.join(self.project.path, "scenes")):

                # logging.info("{} / {}".format("scenes", seq))

                seq_path = os.path.join(self.project.path, "scenes", seq)
                # logger.info("SEQ > {}".format(seq_path))
                seq_node = elements.CatagoryNode(seq, path=seq_path, project=self.project).create(path=seq_path)


                for shot in files.list_dir_folders(os.path.join(self.project.path, "scenes", seq)):

                    shot_path = os.path.join(self.project.path, "scenes", seq, shot, "{}.pipe".format(shot))
                    logger.info(shot_path)
                    shot_node = Legacy_component(path=shot_path, project = self.project)
                    # logging.info("{} / {} / {} IS COMPONENT".format("assets", seq, shot))

class Legacy_component(object):
    def __init__(self, path=None, project = None):
        self.component = None
        data = pickle.pickleDict(path=path)
        if data:
            self.converted_data = dict()
            self.component_data = data.read()

            # logging.info(
            #     "Converting {}, Original files will remain unchaged. New project will be created without users".format(
            #         self.component_data["project_name"]))

            self.converted_data["component_name"] = os.path.split(os.path.dirname(path))[1]

            # self.converted_data["versions"] = None
            # self.converted_data["masters"] = None
            # self.converted_data["playblasts"] = None

            if "versions" in self.component_data:
                self.converted_data["versions"] = dict()
                for k, v in self.component_data["versions"].iteritems():

                    self.converted_data["versions"][int(k)] = dict()
                    for x, y in self.component_data["versions"][k].iteritems():

                        if x == "date_created":
                            self.converted_data["versions"][int(k)]["date"] = y
                        if x == "author":
                            self.converted_data["versions"][int(k)]["author"] = y
                        if x == "note":
                            self.converted_data["versions"][int(k)]["note"] = y if y != "No notes" else ""
            else:
                self.converted_data["versions"] = None

            if "masters" in self.component_data:
                self.converted_data["masters"] = dict()
                for k, v in self.component_data["masters"].iteritems():

                    self.converted_data["masters"][int(k)] = dict()
                    for x, y in self.component_data["masters"][k].iteritems():

                        if x == "date_created":
                            self.converted_data["masters"][int(k)]["date"] = y
                        if x == "author":
                            self.converted_data["masters"][int(k)]["author"] = y
                        if x == "note":
                            self.converted_data["masters"][int(k)]["note"] = y if y != "No notes" else ""

            else:
                self.converted_data["masters"] = None

            if "playblasts" in self.component_data:
                self.converted_data["playblasts"] = dict()
                for k, v in self.component_data["playblasts"].iteritems():

                    self.converted_data["playblasts"][int(k)] = dict()
                    for x, y in self.component_data["playblasts"][k].iteritems():

                        if x == "date_created":
                            self.converted_data["playblasts"][int(k)]["date"] = y
                        if x == "author":
                            self.converted_data["playblasts"][int(k)]["author"] = y
                        if x == "note":
                            self.converted_data["playblasts"][int(k)]["note"] = y if y != "No notes" else ""
            else:
                self.converted_data["playblasts"] = None

            # logging.info(os.path.dirname(path))

            self.component = elements.ComponentNode(self.converted_data["component_name"], path=os.path.dirname(path), format=1, project=project).create(path=os.path.dirname(path))

            if self.converted_data["versions"]: self.component.versions_data = self.converted_data["versions"]
            if self.converted_data["playblasts"]: self.component.playblasts_data = self.converted_data["playblasts"]
            if self.converted_data["masters"]: self.component.masters_data = self.converted_data["masters"]

            old_thumbnail = os.path.join(os.path.dirname(path), "tumbnails", "{}.png".format(self.converted_data["component_name"]))
            if os.path.isfile(old_thumbnail):
                converted_thumbnail_path = os.path.join(os.path.dirname(path),"{}.png".format(self.converted_data["component_name"]))
                files.file_copy(old_thumbnail, converted_thumbnail_path)