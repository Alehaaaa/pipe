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

import pipeline.apps.project_outliner as outliner
import pipeline.libs.config as cfg


import pipeline.libs.data as dt
import pipeline.libs.nodes.elements as elements
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore, QtCompat
import pipeline.apps.massage as massage

#

logger = logging.getLogger(__name__)



class Branch_list_view(QtWidgets.QListView):

    edited = QtCore.Signal()


    def __init__(self, parent):
        super(Branch_list_view, self).__init__(parent)

        self.dummy = True
        self.project = None

    def setModel_(self, model):
        if model:

            self.setModel(model)

        else:
            pass
            # self.setModel(None)

    def contextMenuEvent(self, event):

        handled = True
        index = self.indexAt(event.pos())
        menu = QtWidgets.QMenu()
        node = None

        if index.isValid():
            node = self.model().getNode(index)

        # top_actions = list()
        def_actions = list()

        if node:

            def_actions.append(QtWidgets.QAction("Remove branch...", menu,
                                                 triggered=functools.partial(self.remove, node, index)))


        else:

            def_actions.append(QtWidgets.QAction("Add branch...", menu,
                                                 triggered=functools.partial(self.add, node)))

        menu.addActions(def_actions)

        menu.exec_(event.globalPos())
        event.accept()

        return


    def add(self, node):


        branch = outliner.New_branch_dialog(self)
        result = branch.exec_()
        res = branch.result()

        if result == QtWidgets.QDialog.Accepted:
            name = res["name"]
            branches =  [b.name for b in self.model().items]

            if not name in branches:


                if self.dummy:
                    new_branch = dt.Node(name)
                if not self.dummy and self.project:
                    new_branch = elements.BranchNode(name, path=os.path.join(self.project.path, name), project = self).create(path=os.path.join(self.project.path, name))


                self.model().insertRows(0, 1, parent=QtCore.QModelIndex(), node=new_branch)


                self.edited.emit()


            else:
                logger.info("A branch called {} exsists.".format(name))

            # logger.info("add branch...")

    def remove(self, node, index):
        if node.typeInfo() == cfg._node_:
            self.model().removeRows(0,1,QtCore.QModelIndex(),node)
            self.edited.emit()
        else:
            if not self.dummy:
                string = "Caution: This is not undoable,\nBranch {} and all of its contants will be deleted!".format(node.name)
                alert = massage.Prompt_alert(alert_string=string)
                result = alert.exec_()
                if result == QtWidgets.QDialog.Accepted:
                    node.delete_me()
                    self.model().removeRows(0, 1, QtCore.QModelIndex(), node)
                    self.edited.emit()


        # logger.info(node.name)
        # logger.info(index)
        # logger.info("rm branch...")
