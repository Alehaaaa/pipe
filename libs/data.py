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
import pipeline.libs.config as cfg
import pipeline.libs.files as files
import pipeline.libs.serializer as serializer
from pipeline.libs.Qt import QtWidgets, QtCore



logger = logging.getLogger(__name__)


class Node(QtCore.QObject,  object):
    def __init__(self, name, parent=None, **kwargs):
        # super(Node, self).__init__()

        object.__init__(self)
        QtCore.QObject.__init__(self)

        self._name = name
        self._children = []
        self._parent = parent
        self.expendedState = False
        self._resource = cfg.branch_icon #cfg.folder_icon
        self._id = serializer.id_generator()
        self._virtual = False
        self._deathrow = False

        if parent is not None:
            parent.addChild(self)

    @property
    def children(self):
        return self._children

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, icon):
        self._resource = icon

    @property
    def expendedState(self):
        return self._expendedState

    @expendedState.setter
    def expendedState(self, state):
        self._expendedState = state

    @property
    def id(self):
        return self._id

    def explore(self):
        # logger.info(self._path)
        files.explore(self._path)

    def attrs(self):

        classes = self.__class__.__mro__

        kv = {}

        for cls in classes:
            for k, v in cls.__dict__.iteritems():
                if isinstance(v, property):
                    # print "Property:", k.rstrip("_"), "\n\tValue:", v.fget(self)
                    kv[k] = v.fget(self)

        return kv

    def asXml(self):

        doc = QtXml.QDomDocument()

        node = doc.createElement(self.typeInfo())
        doc.appendChild(node)

        attrs = self.attrs().iteritems()

        for k, v in attrs:
            node.setAttribute(k, v)

        for i in self._children:
            i._recurseXml(doc, node)

        return doc.toString(indent=4)

    def _recurseXml(self, doc, parent):
        node = doc.createElement(self.typeInfo())
        parent.appendChild(node)

        attrs = self.attrs().iteritems()

        for k, v in attrs:
            node.setAttribute(k, v)

        for i in self._children:
            i._recurseXml(doc, node)

    def typeInfo(self):
        return cfg._node_

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        if self._children != []:
            child = self._children.pop(position)
            # child.delete()
            child._parent = None

            return True
        else:
            return False

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):

        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "|------" + self._name + "\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"

        return output

    def data(self, column):

        if column is 0:
            return self.name
        elif column is 1:
            return self.typeInfo()  # len(self._children)

    def setData(self, column, value):
        # print value
        if column is 0:
            pass  # self.name = value
        elif column is 1:
            pass

    def delete(self):

        self.delete_me()

        for child in self._children:
            child.delete()

    def delete_me(self):

        if hasattr(self, '_path'):
            if self._path:
                files.delete(self._path)

        logger.info("Deleting {}, {}".format(self.name, self._path))
        # print "***DELETE ALL IN" + self._name + "\n"

    def commit(self):
        self.commit_me()
        if self._deathrow:
            self.delete()

            return False

        for child in self._children:
            child.commit()

    def commit_me(self):
        create = False
        if self.__class__.__name__ == "FolderNode":
            create = True
        elif self.__class__.__name__ == "AssetNode":
            create = True
        elif self.__class__.__name__ == "StageNode":
            create = True

        if create:
            create_mathod = getattr(self, "create", None)
            # print "calling create method:"
            if callable(create_mathod):
                if self._virtual:
                    self.create(path=self._path)
                    # print "creating! --> ", self._path, "<--"
                else:
                    pass
                    # print "already real --> ", self._path, "<--"
                return

    def deathrow(self):
        self.deathrow_me()

        for child in self._children:
            child.deathrow()  # print "not a folder"

    def deathrow_me(self):
        self._deathrow = True


# class RootNode(Node):
#
#     def __init__(self, name, parent=None, **kwargs):
#
#         super(RootNode, self).__init__(name, parent, **kwargs)
#
#         self.name = name
#         self.resource = cfg.folder_icon
#         self.data_file = None
#         self.data_file_path = None
#         self._settings = None
#         self._project = None
#         self._ui = None
#
#         for key in kwargs:
#             if key == "path":
#                 self._path = kwargs[key]
#                 self.data_file_path = os.path.join(kwargs[key], "%s.%s" % (os.path.split(kwargs[key])[1], "json"))
#             if key == "project":
#                 self._project = kwargs[key]
#             if key == "settings":
#                 self._settings = kwargs[key]
#             if key == "ui":
#                 self._ui = kwargs[key]
#
#         if self.data_file_path:
#             self.set_data_file(self.data_file_path)
#
#     @property
#     def path(self):
#         return self._path
#
#     @path.setter
#     def path(self, path):
#         self._path = path
#
#     @property
#     def settings(self):
#         return self._settings
#
#     @property
#     def color(self):
#         if self.approved_stage:
#             return QtWidgets.QColor("#00fa9a")
#         else:
#             return QtWidgets.QColor("white")
#
#     @property
#     def relative_path(self):
#         if self.path and self._project:
#             return files.reletive_path(self._project.path, self.path)
#
#     @property
#     def ansestors(self):
#         try:
#             ansestors = files.splitall(self.relative_path)
#             # ansestors.reverse()
#             return ansestors
#         except:
#             return None
#
#     def ansestor(self, int):
#         ansestors = self.ansestors
#         if ansestors and len(ansestors) >= int:
#             return self.ansestors[int]
#
#         return None
#
#     def typeInfo(self):
#         return cfg._root_
#
#     def set_data_file(self, path):
#         if os.path.isfile(path):
#             self.data_file = serializer.JSONSerializer(path=path)
#
#             return True
#         else:
#             pass
#
#     def create(self, path=None):
#         if files.create_directory(path):
#             self.path = path
#             return self
#         else:
#             return False


#
# class DresserMasterNode(RootNode):
#     def __init__(self, name, parent=None, **kwargs):
#         super(DresserMasterNode, self).__init__(name, parent, **kwargs)
#
#         # self.resource = cfg.folder_icon if not self._virtual else  cfg.creation_icon
#         self.resource = cfg.cube_icon_full #if not self._virtual else  cfg.creation_icon
#
#     def typeInfo(self):
#         return cfg._master_
#
#     def explore(self):
#         files.explore(self.path)
#
#     def reference(self):
#         maya.reference_scene(self.path)
#
#     def load(self):
#
#         if locking.verifyLockFile(self.lockNodePath):
#             if maya.open_scene(self.path):
#                 maya.insert_recent_file(self.path)
#                 self.lockNode()
#
#             self.stage.currently_open = self
#         else:
#             print "This file might be open on a different machine and was locked."
#
#     @property
#     def lockNodePath(self):
#         folder = os.path.dirname(self.path)
#         filename = files.file_name_no_extension(files.file_name(self.path))
#         return os.path.join(folder, "{}.{}".format(filename, "lock"))
#
#     def lockNode(self):
#
#         dict = {}
#         dict["host"] = socket.gethostname()
#         lock_node = serializer.JSONSerializer().create(self.lockNodePath, dict)
#         return lock_node
#
#
# class CatagoryNode(Node):
#     def __init__(self, name, parent=None):
#         super(CatagoryNode, self).__init__(name, parent)
#
#         self.resource = cfg.dummy_icon
#
#     def typeInfo(self):
#         return cfg._catagory_


# class DummyNode(Node):
#     def __init__(self, name, parent=None):
#         super(DummyNode, self).__init__(name, parent)
#
#         self.resource = cfg.dummy_icon
#
#     def typeInfo(self):
#         return cfg._dummy_


# class LevelsNode(Node):
#     def __init__(self, name, parent=None):
#         super(LevelsNode, self).__init__(name, parent)
#
#         self.resource = cfg.dummy_icon
#         self._levels = []
#         for i in range(6):
#             self._levels.append("")
#
#     def setLevels(self, list):
#         for index, item in enumerate(list):
#             self._levels[index] = item
#
#     def typeInfo(self):
#         return cfg._dummy_


class UserNode(Node):
    def __init__(self, name, password=None, role=None, parent=None):
        super(UserNode, self).__init__(name, parent)

        self.resource = cfg.dummy_icon
        self._password = password
        self._role = role

    def setLevels(self, list):
        for index, item in enumerate(list):
            self._levels[index] = item

    def typeInfo(self):
        return cfg._dummy_

class ScriptFileNode(Node):
    def __init__(self, name, path = '', parent=None):
        super(ScriptFileNode, self).__init__(name, parent)

        self.resource = cfg.dummy_icon
        self._path = path
        self._lang = files.extension(os.path.basename(path))[1:]


    def typeInfo(self):
        return cfg._dummy_

class Hierarcy_folder_node(Node):

    def __init__(self, name=cfg.Hierarcy_options.ASK_USER, quantity=cfg.Hierarcy_options.SINGLE, start=0, end=0, padding=0, trailing=0, step =1):
        super(Hierarcy_folder_node, self).__init__(name, None)

        self.resource = cfg.folder_icon
        self._quantity = quantity
        self._from = start
        self._to = end
        self._padding = padding
        self._trailing = trailing
        self._step = step

        self._name_ = name
        self._quantity_ = quantity
        self._from_ = start
        self._to_ = end
        self._padding_ = padding
        self._trailing_ = trailing
        self._step_ = step

    def typeInfo(self):
        return cfg._heirarchy_folder_


class Hierarcy_component_node(Node):

    def __init__(self, name=cfg.Hierarcy_options.ASK_USER,
                 branch = cfg.Hierarcy_options.ASK_USER,
                 format=0,
                 version_file_type = 'mayaAscii',
                 master_file_type = 'mayaAscii'):

        super(Hierarcy_component_node, self).__init__(name, None)

        self.resource = cfg.square_file_icon
        self._branch = branch
        self._format = format
        self._version_file_type = version_file_type
        self._master_file_type = master_file_type

        self._name_ = name
        self._branch_ = branch
        self._format_ = format
        self._version_file_type_ = version_file_type
        self._master_file_type_ = master_file_type

    def typeInfo(self):
        return cfg._heirarchy_component_

# class ClientNode(Node):
#     def __init__(self, name, path=None, parent=None):
#         super(ClientNode, self).__init__(name, parent)
#         self._path = path
#
#         self.resource = cfg.client_icon
#
#     @property
#     def path(self):
#         return self._path
#
#     def typeInfo(self):
#         return cfg._dummy_
#
#
# class NewNode(Node):
#     def __init__(self, name, parent=None):
#         super(NewNode, self).__init__(name, parent)
#         self.resource = cfg.add_icon
#
#         # for key in kwargs:
#         #     if key == "name_format":
#         #         self._name_format = kwargs[key]
#         #     if key == "section":
#         #         self._section = kwargs[key]
#
#     def typeInfo(self):
#         return cfg._new_