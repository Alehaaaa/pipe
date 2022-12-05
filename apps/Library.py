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

import sys
import logging
import os
import re
import threading
import traceback


import pipeline.libs.views as views
import pipeline.libs.misc as misc
import pipeline.libs.models as models
import pipeline.libs.nodes.elements as stages
import pipeline.widgets.comboBox as comboBox
import pipeline.widgets.inputs as inputs
import pipeline.libs.config as cfg
from pipeline.libs.Qt import QtWidgets, QtCore



logger = logging.getLogger(__name__)

class FilterComboWidget(comboBox.ComboWidget):

    changed = QtCore.Signal(str)

    def __init__(self,
                 items=None,
                 path = None,
                 parent_layout=None,
                 parent=None):

        super(FilterComboWidget, self).__init__(parent_layout, parent)

        self.setMaximumHeight(30)
        self.setMinimumHeight(30)
        self.setMaximumWidth(150)
        self.setMinimumWidth(150)

        self.label.setParent(None)
        self.label.deleteLater()

        self.parent = parent
        self.setHidden(False)

        # self.comboBox.currentIndexChanged.connect(self.update)
        # logger.info("connecting to {}".format(self.parent))
        # self.changed.connect(self.parent.set_view_root)


    def update(self):
        return
        # logger.info("updating with {}".format(self.comboBox.currentText()))
        # path = os.path.join(self._path,self.comboBox.currentText()) if self._path else self.comboBox.currentText()
        # self.changed.emit(path)
        # self.parent.address_label.setText(self.comboBox.currentText())


    def set_branch(self, string):
        return

        if comboBox.setComboValue(self.comboBox, string):
            # logger.info("branch set to {}".format(string))
            self.update()

    def set_root(self, path):
        return
        if path:
            self._path = path
            self.listDirectory()
            self.createModel()
            # self.update()
        else:
            self.comboBox.clear()


    def createModel(self):
        return

        self.comboBox.clear()
        # dt.CatagoryNode(name, path=path, project = self.parent.parent.project)

        li = []
        # p = self._parent_box.folderView.selectionModel()
        if self._subdirectories:

            # p = self._parent_box.selected_node if self._parent_box else None

            for dir in sorted(self._subdirectories):
                n = os.path.split(dir)[1]

                path = os.path.join(self._path, dir)

                if misc.branch_dir(path):
                    li.append(pipeline.libs.nodes.stages.BranchNode(n, path=path, project = self.project))

            if li:
                self.comboBox.setModel(models.List_Model(li))
                return True

        return False



class Library(QtWidgets.QWidget):

    component_changed = QtCore.Signal()

    def __init__(self, parent = None, settings = None):
        super(Library, self).__init__(parent)

        self.setMinimumHeight(100)
        self.parent = parent
        self.layout =  QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)


        self.library_view = views.Library_View(self, settings = settings)
        self.layout.addWidget(self.library_view)

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.progressBar.setMaximumHeight(5)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet('''
        QProgressBar
        {
            border: 1px solid ''' + cfg.colors.DARK_GRAY_MINUS + ''';
        }
        QProgressBar::chunk
        {
            background-color:  ''' + cfg.colors.DARK_PURPLE + ''';
        }''')

        self.layout.addWidget(self.progressBar)

        self.address_widget = QtWidgets.QWidget(self)
        self.address_widget_layout = QtWidgets.QHBoxLayout(self.address_widget)
        self.address_widget_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.address_widget_layout.setContentsMargins(0, 3, 0, 0)
        self.layout.addWidget(self.address_widget)



        self.search_line = inputs.SuggestionSearchBar(self, label = "Search public components...")
        self.search_line.setMinimumHeight(30)
        self.address_widget_layout.addWidget(self.search_line)



        #

        self.comps = list()
        self.comp_hints = list()

        self.comps_model = None
        self.project = None

        self.scan = None

        #
        # self.search_line.set_suggestions_model(None)
        # self.library_view.setModel_(None)
        # self.populate()

        self.search_line.textChanged.connect(self.search_changed)

    def set_project(self, project):
        # logger.info(self.parent)
        self.project = None

        if project:
            self.project = project
            # self.root_path = os.path.join(self.project.path, "assets")

        # self.populate()

    def set_root(self, path):

        if self.scan:
            try:
                self.scan.kill()
            except:
                print traceback.print_exc()

        self.search_line.set_suggestions_model(None)
        self.library_view.setModel_(None)


        if path:
            if os.path.exists(path):
                self.root_path = path
                self.scan = Scan_masters_thread(path_to_dir=self.root_path, project=self.project)
                self.scan.update.connect(self.populate)
                self.scan.percent.connect(self.progressBar.setValue)
                self.scan.start()
                self.show_loader()
                # self.populate()

    def populate(self, items = None):
        # root = self.parent.project.path


        self.comps = list()
        self.comp_hints = list()
        self.comps_model = None

        self.search_line.set_suggestions_model(None)
        self.library_view.setModel_(None)

        if not items:
            self.hide_loader()
            if self.scan:
                self.scan.kill()
            self.scan = None
            return

        for item in items:

            node = stages.ComponentNode(item['name'], path=item['path'], project=self.project)
            self.comps.append(node)
            # self.comp_hints.append(node.name)
            self.comp_hints.extend(node.full_path_elements)

        comp_hints_no_duplicates = sorted(list(set(self.comp_hints)))

        self.search_line.set_suggestions_model(QtCore.QStringListModel(comp_hints_no_duplicates))

        self.comps_model = models.Library_Model(self.comps)

        self.library_view.setModel_(self.comps_model)

        self.hide_loader()

        if self.scan: self.scan.kill()


        return True



    def search_changed(self, str):
        if (self.search_line.text() != "") and (self.search_line.text() != self.search_line.label):
            self.filter(str)
            # logger.info("searching...")
            return
        else:

            self.library_view.setModel_(self.comps_model)
        # if self.rootFolder and (self.search_line.text() == ""):

        # if isinstance(self.results_folder, FolderStaticWidget):
        #     self.results_folder.remove()
        #     self.results_folder = None
        #
        # if isinstance(self.rootFolder, FolderDynamicWidget):
        #     self.rootFolder.hide(False)

        # logger.info("Not searching")
        # return

    def filter(self, string):
        filterd_comps = list()

        for comp in self.comps:

            f = None
            try:
                f = re.search(string, comp.nice_full_name)  # os.path.split(folder)[1])
            except:
                logger.info("This search pattern {} is invalid".format(string))

        # logger.info(search_in)

            if f:
                filterd_comps.append(comp)


        self.library_view.setModel_(models.Library_Model(filterd_comps))


    def hide_loader(self):
        # self.folder_view.setHidden(False)
        self.progressBar.setHidden(True)

    def show_loader(self):
        # self.folder_view.setHidden(False)
        self.progressBar.setHidden(False)
        self.progressBar.setValue(0)

def remap( x, oMin, oMax, nMin, nMax ):

    #range check
    if oMin == oMax:
        print "Warning: Zero input range"
        return None

    if nMin == nMax:
        print "Warning: Zero output range"
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result


class Scan_masters_thread(QtCore.QObject, threading.Thread):
    update = QtCore.Signal(object)
    percent = QtCore.Signal(int)

    def __init__(self, path_to_dir='.', project = None):

        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        self._path = path_to_dir
        self.project = project
        self.daemon = True
        self.killed = False

    def run(self):
        li = []
        try:
            li = self.createModel()
        except SystemExit:
            pass
            # print 'system exit at in {}.thread.run():'.format(self.__class__.__name__)
        except:
            print 'exceptions in {}.thread.run():'.format(self.__class__.__name__)
            print traceback.print_exc()
        finally:
            self.update.emit(li)
            return

    def calculate_total(self):
        total = 0
        for root, subFolders, _files in os.walk(self._path):

            for s in subFolders:
                total += 1
        return total

    def createModel(self):
        li = list()
        index = 0
        max = self.calculate_total()

        if not self.project: return li

        for root, subFolders, _files in os.walk(self._path):

            for s in subFolders:
                index += 1
                folder = os.path.join(root, s)

                comp = folder if misc.component_dir(folder) else None

                if comp:

                    node = stages.ComponentNode(os.path.split(comp)[1], path=comp, project=self.project)
                    if node.public:
                        li.append({"name": os.path.split(comp)[1], "path": comp})

                    del node
                val = remap(index, 0, max, 0, 100)
                self.percent.emit(val)

        return li


    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to

        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
    trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        try:
            self.update.disconnect()
            self.percent.disconnect()
        except:
            pass
        self.killed = True
