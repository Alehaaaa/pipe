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

logger = logging.getLogger(__name__)

import pipeline.libs.data as dt
import pipeline.libs.config as cfg
import pipeline.libs.files as files
import pipeline.libs.misc as misc
import pipeline.libs.locking as locking
import pipeline.apps.massage as massage
import  pipeline.maya_libs.maya_warpper as maya



class VersionNode(dt.Node):
    def __init__(self, name, path=None, number=None, author=None, date=None, note=None, component=None, include=None,
                 parent=None):
        super(VersionNode, self).__init__(name, parent)

        self._path = path
        self._number = number
        self._date = date
        self._note = note
        self._author = author
        self._component = component
        self._include = include

        self.resource = cfg.large_image_icon_dark

        if os.path.isfile(self.thumbnail_file):
            self.resource = self.thumbnail_file

    @property
    def size(self):

        size_mb = files.file_size_mb(self.path)
        if size_mb:
            return "{} MB".format(("{0:.1f}".format(size_mb)))
        else:
            return "n/a"

    @property
    def thumbnail_file(self):
        filename = files.file_name(self._path)
        filename = files.file_name_no_extension(filename)
        path = os.path.join(self._component.tumbnails_path,
                            "%s.%s" % (filename, "png")) if self._component.tumbnails_path else ""
        # if os.path.isfile(path):
        return path
        # else:
        #     my_index = self.parent()._children.index(self)
        #     if my_index == 0:
        #         return ""
        #     if len(self.parent()._children)>=my_index:
        #         older_sister = self.parent()._children[my_index-1]
        #         return older_sister.thumbnail_file

    def snapshot(self):
        files.assure_path_exists(self.thumbnail_file)
        snapshot = maya.snapshot(path=self.thumbnail_file, width=96, height=96)
        self.resource = snapshot
        self.component.thumbnail = snapshot
        return snapshot

    @property
    def component(self):
        return self._component

    @property
    def include(self):
        return self._include

    @include.setter
    def include(self, data):
        self._include = data

    @property
    def number(self):
        return self._number #if self._number else None

    @property
    def date(self):
        return self._date if self._date else None

    @property
    def author(self):
        return self._author if self._author else None

    @property
    def note(self):
        return self._note if self._note else None

    @note.setter
    def note(self, note):
        self._note = note
        self.component.editVersionData(str(self.name), "note", note)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def fullName(self):
        # return self
        # return os.path.split(self.path)[1]
        return "Version {}".format(self.number)
        # return "%s . %s . %s %s" % (self.stage.parent().name, self.stage.name, "Version", self.number)

    @property
    def status_icon(self):

        if maya.current_open_file() == self.path:
            return cfg.reload_icon
        else:
            return cfg.folder_open_icon
        # parent = self.parent() if self.parent().typeInfo() == cfg._stage_ else self.parent().parent()
        # if parent.currently_open == self:
        #     return cfg.reload_icon
        # else:
        #     return cfg.open_icon

    @property
    def stage_status(self):
        """Will return true if (../{versions, masters}/self.path)<current_stage>.json file has an approved status"""
        try:
            dir = os.path.dirname(os.path.dirname(self.path))
            return misc.json_status(os.path.join(dir, "{}.json".format(self.parent().name)))
        except:
            return False

    def typeInfo(self):
        return cfg._version_

    def explore(self):
        files.explore(self.path)

    def import_(self):
        maya.import_scene(self.path)
        logger.info("import {}".format(self.fullName))

    def reference_(self):
        maya.reference_scene(self.path)
        logger.info("referece {}".format(self.fullName))

    def delete(self):
        self.delete_me()
        self.component.removeVersionData(str(self.name))


    def reference(self):
        maya.reference_scene(self.path)

    def load(self):

        try:
            result = maya.open_scene(self.path)
            self.component.loaded.emit(self.component)
            self.component.lock_node()
            return result
        except:
            logger.info("Error opening file {}".format(self.path))
            return False

    @property
    def note_decoration(self):
        if self._note:
            return cfg.comment_full_icon
        else:
            return None
            # return cfg.comment_icon


    def rename(self, new_name):

        version_number_padded = self.component.padding(self.name)
        file_name = "{0}_{1}{2}".format(self.component.format_file_name, cfg._version_pfx_, version_number_padded)
        updated_path = os.path.join(self.component.versions_path, files.file_name(self.path))
        files.file_rename(updated_path, file_name)
        # logger.info("renaming {} {}...".format(cfg._version_pfx_, self.name))





class MasterNode(VersionNode):
    def __init__(self, name, path=None, number=None, author=None, date=None, note=None, component=None, include=None, origin = None,
                 parent=None):
        super(MasterNode, self).__init__(name, path=path, number=number, author=author, date=date, note=note,
                                         component=component, include=include, parent=parent)

        self._origin = origin

        # logger.info("---")
        # logger.info(self.name)
        # logger.info(self.note)
        # logger.info(self._note)

    @property
    def origin(self):
        return self._origin

    @property
    def master_icon(self):
        return cfg.master_icon

    @property
    def note(self):
        return self._note if self._note else None


    @note.setter
    def note(self, note):
        self._note = note
        self.component.editMasterData(str(self.name), "note", note)

    @property
    def fullName(self):
        return "Master {}".format(self.number) if self.number is not 0 else "Master"
        # if len(self._children) > 0:
        #     return "%s > %s : %s" % (self.stage.parent().name, self.stage.name, "Master")
        # else:
        #     return "%s > %s : %s %s" % (self.stage.parent().name, self.stage.name, "Master V", self.number)

    def typeInfo(self):
        return cfg._master_

    def revert_(self):
        self.component.override_master(self)

    def rename(self, new_name):
        version_number_padded = self.component.padding(self.name)
        file_name = "{0}_{1}{2}".format(self.component.format_file_name, cfg._public_version_pfx_, version_number_padded)
        updated_path = os.path.join(self.component.masters_path, files.file_name(self.path))
        files.file_rename(updated_path, file_name)
        # logger.info("renaming {} {}...".format(cfg._public_version_pfx_, self.name))


class PlayblastNode(VersionNode):
    def __init__(self, name, path=None, number=None, author=None, date=None, note=None, component=None, include=None,
                 parent=None):
        super(PlayblastNode, self).__init__(name, path=path, number=number, author=author, date=date, note=note,
                                            component=component, include=None, parent=parent)

        # self._origin = origin

    # @property
    # def thumbnail_file(self):
    #     if self.number == 0:
    #         thumbnail_file = self.component.playblast_thumb_path
    #         if os.path.isfile(thumbnail_file):
    #             return thumbnail_file
    #
    #
    #     else:
    #         version_number_padded = self.component.padding(self.number)
    #         file_name = "{0}_{1}{2}.zzz".format(self.component.format_file_name, cfg._playblast_pfx_, version_number_padded)
    #         thumbnail_file = os.path.join(self.component.playblasts_thumbnails_path, file_name)
    #         if os.path.isfile(thumbnail_file):
    #             return thumbnail_file
    #
    #     return ""
        #     # this one is the master, grab the image from the last child.
        #     if self._children:
        #         return self._children[-1].thumbnail_file
        #     else:
        #         return ""
        #
        # filename = files.file_name(self._path)
        # filename = files.file_name_no_extension(filename)
        # path = os.path.join(self._stage.playblasts_thumbnails_path, "{0}{1}.{2}".format(filename, cfg._thumb_,
        #                                                                                 "png")) if self._stage.playblasts_thumbnails_path else ""
        # return path

    # @property
    # def origin(self):
    #     return self._origin

    @property
    def playblast_icon(self):
        return cfg.camrea_icon

    @property
    def note(self):
        return self._note if self._note else None

    @note.setter
    def note(self, note):
        self._note = note
        self.component.editPlayblastData(str(self.name), "note", note)

    @property
    def fullName(self):
        return "Playblast {}".format(self.number) if self.number is not 0 else "Playblast"

        # if len(self._children) > 0:
        #     return "%s > %s : %s" % (self.stage.parent().name, self.stage.name, "Playblast")
        # else:
        #     return "%s > %s : %s %s" % (self.stage.parent().name, self.stage.name, "Playblast V", self.number)

    def play(self):
        logger.info("attempting to play {}".format(self.path))
        if os.path.isfile(self.path):
            try:
                files.run(self.path)
            except:
                print "can not run this file {}".format(self.path)

    # def refresh_thumbnail(self):
    #     self.resource = self.thumbnail_file

    def revert_(self):
        self.component.override_master_playblast(self)

    def rename(self, new_name):

        version_number_padded = self.component.padding(self.name)
        file_name = "{0}_{1}{2}".format(self.component.format_file_name_full, cfg._playblast_pfx_, version_number_padded)
        updated_path = os.path.join(self.component.playblasts_path, files.file_name(self.path))
        logger.info("upd: {} // new name: {}".format(updated_path, file_name))
        files.file_rename(updated_path, file_name)

        # rename also the thumbnail...
        # updated_path = os.path.join(self.component.playblasts_path, cfg._thumbnails_, "{}.png".format(files.file_name_no_extension(files.file_name(self.path))))
        # files.file_rename(updated_path, file_name)

        # logger.info("renaming {} {}...".format(cfg._playblast_pfx_, self.name))

    def typeInfo(self):
        return cfg._playblast_



class AlembicNode(VersionNode):
    def __init__(self, name, path=None, number=None, author=None, date=None, note=None, component=None, include=None, origin = None,
                 parent=None):
        super(AlembicNode, self).__init__(name, path=path, number=number, author=author, date=date, note=note,
                                         component=component, include=include, parent=parent)

        self._origin = origin

    @property
    def origin(self):
        return self._origin

    @property
    def master_icon(self):
        return cfg.master_icon

    @property
    def note(self):
        return self._note if self._note else None


    # @note.setter
    # def note(self, note):
    #     self._note = note
    #     self.component.editMasterData(str(self.name), "note", note)

    # @property
    # def fullName(self):
    #     return "Master {}".format(self.number) if self.number is not 0 else "Master"

    def typeInfo(self):
        return cfg.alembic

    # def revert_(self):
    #     self.component.override_master(self)
    #
    # def rename(self, new_name):
    #     version_number_padded = self.component.padding(self.name)
    #     file_name = "{0}_{1}{2}".format(self.component.format_file_name, cfg._public_version_pfx_, version_number_padded)
    #     updated_path = os.path.join(self.component.masters_path, files.file_name(self.path))
    #     files.file_rename(updated_path, file_name)
    #     # logger.info("renaming {} {}...".format(cfg._public_version_pfx_, self.name))
