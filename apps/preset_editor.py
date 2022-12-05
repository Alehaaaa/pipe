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
import functools

import pipeline.libs.config as cfg
import pipeline.libs.data as dt
import pipeline.libs.files as files
import pipeline.libs.models as models
import pipeline.libs.views as views
import pipeline.widgets.gui as gui
import pipeline.libs.serializer as serializer
import pipeline.libs.nodes.elements as elements
import pipeline.libs.misc as misc
import pipeline.widgets.inputs as inputs
reload(inputs)
import pipeline.apps.massage as massage
from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
import pipeline.CSS
from pipeline.CSS import loadCSS

logger = logging.getLogger(__name__)

class Preset_dialog(QtWidgets.QMainWindow): #QtWidgets.QDialog):


    animation_basic_preset = {

        'categories' : [
            {"name": "SEQ", "from": cfg.Hierarcy_options.ASK_USER, "to": cfg.Hierarcy_options.ASK_USER, "padding": 3, "quantity": cfg.Hierarcy_options.MULTIPLE},
            {"name": "SHOT", "from": cfg.Hierarcy_options.ASK_USER, "to": cfg.Hierarcy_options.ASK_USER, "padding": 3, "quantity": cfg.Hierarcy_options.MULTIPLE}
        ],

        'branches' : {
            "render": { "lightning":{"format":2},
                        },

            "animation": {
                "layout": {"format": 2},
                "anim": {"format": 2}
            }

        }
    }
    character_basic_preset = {

        'categories' : [
            {"name": "Characters", "from": 0, "to": 0, "padding": 0, "quantity": cfg.Hierarcy_options.SINGLE},
            {"name": cfg.Hierarcy_options.ASK_USER, "from": 0, "to": 0, "padding": 0,
             "quantity": cfg.Hierarcy_options.SINGLE}
        ],

        'branches' : {
            "assets": { "model":{"format":2},
                        "rig": {"format": 2},
                        "blendshapes": { "format":2},
                        "shading": { "format":2}
                        }

        }
    }

    def __init__(self, parent, **kwargs):

        super(Preset_dialog, self).__init__(parent)


        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.pipeline_window = None
        if 'pipeline_window' in kwargs:
            self.pipeline_window = kwargs['pipeline_window']



        self.setMinimumHeight(650)
        self.setMinimumWidth(800)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.center_to_maya_window()



        self.main_widget = QtWidgets.QWidget(self)

        self.setCentralWidget(self.main_widget)

        # self.setStyleSheet(cfg.stylesheet)
        css = loadCSS.loadCSS(os.path.join(os.path.dirname(pipeline.CSS.__file__), 'mainWindow.css'))
        self.setStyleSheet(css)

        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        # self.setLayout(self.layout)

        self.setWindowTitle("Preset editor")

        self.header = gui.Title(self, label="Tree construction preset")
        self.header.setMaximumHeight(40)
        self.layout.addWidget(self.header)


        self.editor_tables_widget = QtWidgets.QWidget(self)
        self.editor_tables_widget_layout = QtWidgets.QVBoxLayout(self.editor_tables_widget)
        self.editor_tables_widget_layout.setContentsMargins(5, 5, 5, 5)
        self.editor_tables_widget_layout.setSpacing(10)
        self.layout.addWidget(self.editor_tables_widget)

        self.hierarchy_table_view = views.Hierarcy_catagories_view(parent=self, parentWidget=self.editor_tables_widget)
        self.hierarchy_table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        branches = [os.path.split(p)[1] for p in self.pipeline_window.project.branches] if self.pipeline_window else list()

        self.components_table_view = views.Hierarcy_components_view(parent=self, parentWidget=self.editor_tables_widget, branches = branches)
        self.components_table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


        self.hierarchy_label = gui.Title(self, label="Tree hierarchy", seperator=False)
        # self.hierarchy_label.setMaximumHeight(30)
        self.components_label = gui.Title(self, label="Child omponents", seperator=False)
        # self.components_label.setMaximumHeight(30)

        self.hierarchy_help_label = QtWidgets.QLabel()
        self.hierarchy_help_label.setText("Use right click for options.\n"
                                     "Each category will be generated under it's parent category.\n\n"
                                     "{} = during creation the user will be prompt to enter a value.".format(cfg.Hierarcy_options.ASK_USER))

        italic = QtGui.QFont()
        italic.setItalic(True)

        self.hierarchy_help_label.setFont(italic)

        self.components_help_label = QtWidgets.QLabel()
        self.components_help_label.setText("Components and categories will be generated for the defined branch,\n"
                                "under the lower category.\n\n"
                                           "Branches will be created if they are not exists in the project.")

        italic = QtGui.QFont()
        italic.setItalic(True)

        self.components_help_label.setFont(italic)



        self.editor_tables_widget_layout.addWidget(self.hierarchy_label)
        self.editor_tables_widget_layout.addWidget(self.hierarchy_help_label)
        self.editor_tables_widget_layout.addWidget(self.hierarchy_table_view)
        self.editor_tables_widget_layout.addWidget(self.components_label)
        self.editor_tables_widget_layout.addWidget(self.components_help_label)
        self.editor_tables_widget_layout.addWidget(self.components_table_view)


        self.actions_widget = QtWidgets.QWidget(self)
        self.actions_widget_layout = QtWidgets.QHBoxLayout(self.actions_widget)
        self.actions_widget_layout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.actions_widget)

        self.save_preset_btn = QtWidgets.QPushButton("Save preset")
        self.save_preset_btn.setIcon(QtGui.QIcon(cfg.save_icon))
        self.save_preset_btn.setIconSize(QtCore.QSize(20, 20))

        self.load_preset_btn = QtWidgets.QPushButton("Load preset")
        self.load_preset_btn.setIcon(QtGui.QIcon(cfg.folder_open_icon))
        self.load_preset_btn.setIconSize(QtCore.QSize(20, 20))
        self.load_preset_btn.setStyleSheet('''
                                            QPushButton::menu-indicator{
                                            image: url(none.jpg);
                                            }
                                            ''')
        self.set_preset_menu()
        # self.menu = QtWidgets.QMenu(self.load_preset_btn)
        # self.menu.addAction(QtWidgets.QAction("Load from file...", self.menu, triggered=self.load_preset))
        # self.menu.addSeparator()
        #
        # for p in self.list_saved_presets():
        #     self.menu.addAction(QtWidgets.QAction(p[1], self.menu, triggered=functools.partial(self.set_preset, p[0])))
        #
        # self.menu.addSeparator()
        # self.menu.addAction(QtWidgets.QAction("Clear", self.menu, triggered=self.clear_preset))
        # self.load_preset_btn.setMenu(self.menu)
        #



        self.actions_widget_layout.addWidget(self.save_preset_btn)
        self.actions_widget_layout.addWidget(self.load_preset_btn)
        self.save_preset_btn.clicked.connect(self.save_preset)
        # self.load_preset_btn.clicked.connect(self.load_preset)

        # self.populate_preset(Preset_dialog.preset)


    def set_preset_menu(self):

        self.menu = None
        self.menu = QtWidgets.QMenu(self.load_preset_btn)
        self.menu.addAction(QtWidgets.QAction("Load from file...", self.menu, triggered=self.load_preset))
        self.menu.addSeparator()

        for p in self.list_saved_presets():
            self.menu.addAction(QtWidgets.QAction(p[1], self.menu, triggered=functools.partial(self.set_preset, p[0])))

        self.menu.addSeparator()
        self.menu.addAction(QtWidgets.QAction("Clear", self.menu, triggered=self.clear_preset))
        self.load_preset_btn.setMenu(self.menu)

    @classmethod
    def list_saved_presets(self):
        presets_list = list()
        presets = files.list_directory(os.path.join(cfg.script_dir(), 'presets'), 'json')
        if presets:
            for p in presets:
                presets_list.append([p, files.file_name_no_extension(files.file_name(p))])

            return presets_list
        else:
            return list()

    def center_to_maya_window(self):
        # self.move(self.pipeline_window.maya_main.window().frameGeometry().topLeft() + self.pipeline_window.maya_main.window().rect().center() - self.rect().center())

        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


    def populate_hierarchy_table(self, data):
        if not data:
            self.hierarchy_table_view.setModel_(None)
            return

        catagory_nodes = list()
        for c in data:
            name = c["name"] if 'name' in c.keys() else ''
            quantity = c["quantity"] if 'quantity' in c.keys() else ''
            start = c["from"] if 'from' in c.keys() else 0
            end = c["to"] if 'to' in c.keys() else 0
            padding = c["padding"] if 'padding' in c.keys() else 0
            trailing = c["trailing"] if 'trailing' in c.keys() else 0
            step = c["step"] if 'step' in c.keys() else 1
            catagory_nodes.append(dt.Hierarcy_folder_node(name=name,quantity=quantity, start=start, end=end, padding=padding, trailing=trailing, step=step))

        mdl = models.Hierarchy_folders_Model(catagory_nodes)
        self.hierarchy_table_view.setModel_(mdl)
        return

    def populate_component_table(self, data):
        if not data:
            self.components_table_view.setModel_(None)
            return

        components = list()
        for branch in data:
            for c in data[branch]:

                if "version_file_type" in data[branch][c].keys():
                    vft = data[branch][c]["version_file_type"]
                else:
                    vft = 'mayaAscii'

                if "master_file_type" in data[branch][c].keys():
                    mft = data[branch][c]["master_file_type"]
                else:
                    mft = 'mayaAscii'

                components.append(dt.Hierarcy_component_node(name=c,
                                                             branch=branch,
                                                             format=data[branch][c]["format"],
                                                             version_file_type = vft,
                                                             master_file_type = mft))

         # = [dt.Hierarcy_component_node(name=cfg.Hierarcy_options.ASK_USER, branch=cfg.Hierarcy_options.ASK_USER)]
        mdl = models.Hierarchy_component_Model(components)
        self.components_table_view.setModel_(mdl)
        return

    # def closeEvent(self, ev):
    #     del self.parent().preset_dialog

    def populate_preset(self, preset):

        self.populate_hierarchy_table(None)
        self.populate_component_table(None)

        if not preset: return

        if ('categories' in preset) and ('branches' in preset):
            self.populate_hierarchy_table(preset['categories'])
            self.populate_component_table(preset['branches'])
        else:
            self.populate_hierarchy_table(None)
            self.populate_component_table(None)


    def load_preset(self):
        # logger.info("load preset")
        def_dir = ''
        if self.pipeline_window:
            def_dir = self.pipeline_window.project.path if self.pipeline_window.project else ''

        # path = QtWidgets.QFileDialog.getOpenFileName(self, "Load preset file", dir = os.path.join(cfg.script_dir(), 'presets'), filter="*.json")
        path = inputs.FileDialog.get_file(caption='Select preset file', filter='*.json', dir = os.path.join(cfg.script_dir(), 'presets'))
        if path:
            try:
                logger.info("Loading preset from {}".format(path))
                preset = serializer.JSONSerializer(path=path).read()
                self.populate_preset(preset)
                return True
            except Exception, err:
                logger.info(err)
                logger.info("Can't parse preset from {}".format(path))
                return False

    def save_preset(self):
        # logger.info("save preset")

        catagories_model = self.hierarchy_table_view.model()
        branches_model = self.components_table_view.model()

        cataories = list()
        branches = dict()
        if catagories_model:
            for cat in catagories_model.items:
                cataories.append({'name': cat.name, 'from': cat._from, 'to': cat._to, 'padding': cat._padding, 'quantity': cat._quantity, 'trailing': cat._trailing, 'step': cat._step})

        if branches_model:
            # logger.info(branches_model.items)
            for br in branches_model.items:
                # logger.info('working on branches[{}]'.format(br._branch))
                # logger.info('adding {}'.format(br.name))
                # if br._branch in branches:
                #     branches[br._branch].update({br.name: {'format': br._format}})
                # else:
                #     branches[br._branch] = {br.name: {'format': br._format}}

                if br._branch in branches:
                    branches[br._branch].update({br.name: {'format': br._format,
                                                           'master_file_type': br._master_file_type,
                                                           'version_file_type': br._version_file_type}})
                else:
                    branches[br._branch] = {
                        br.name: {'format': br._format, 'master_file_type': br._master_file_type,
                                  'version_file_type': br._version_file_type}}

                # logger.info('now looking like: {}'.format(branches[br._branch]))


        preset = dict()
        preset['categories'] = cataories
        preset['branches'] = branches

        # for k, v in preset.iteritems():
        #     logger.info(k)
        #     if isinstance(v, list):
        #         for x in v:
        #             logger.info("{}".format(x))
        #
        #     if isinstance(v, dict):
        #         for xx, vv in v.iteritems():
        #             logger.info("{} {}".format(xx, vv))

        def_dir = ''
        if self.pipeline_window:
            def_dir = self.pipeline_window.project.path if self.pipeline_window.project else ''

        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save preset file", dir = os.path.join(os.path.join(cfg.script_dir(), 'presets', "preset")), filter="*.json")
        if path[0]:
            try:
                logger.info("Saving your preset to {}".format(path[0]))
                serializer.JSONSerializer().create(path[0], preset, force=True)
                self.set_preset_menu()

            except Exception, err:
                logger.info(err)
                logger.info("Can't save preset to {}".format(path[0]))


    def set_character_basic_preset(self):
        try:
            character_basic_preset = serializer.JSONSerializer(path = os.path.join(cfg.script_dir(),'presets','character_basic_preset.json')).read()
        except Exception:
            serialize_data_file = serializer.JSONSerializer().create(os.path.join(cfg.script_dir(), 'presets', 'character_basic_preset.json'), Preset_dialog.character_basic_preset )
            character_basic_preset = serialize_data_file.read()

        self.populate_preset(character_basic_preset)

    def set_animation_basic_preset(self):
        try:
            animation_basic_preset = serializer.JSONSerializer(path=os.path.join(cfg.script_dir(), 'presets', 'animation_basic_preset.json')).read()
        except Exception:
            serialize_data_file = serializer.JSONSerializer().create(os.path.join(cfg.script_dir(), 'presets', 'animation_basic_preset.json'), Preset_dialog.animation_basic_preset )
            animation_basic_preset = serialize_data_file.read()

        self.populate_preset(animation_basic_preset)

    def set_preset(self, preset_file):
        try:
            preset = serializer.JSONSerializer(path=preset_file).read()
        except Exception:
            logger.info("could not set preset from {}".format(preset_file))

        self.populate_preset(preset)

    def clear_preset(self):
        self.populate_preset(None)




class Preset_generation_dialog(Preset_dialog):
    def __init__(self, parent=None, preset_file = None, **kwargs):
        super(Preset_generation_dialog, self).__init__(parent, **kwargs)
        self.setWindowTitle("Preset generation")

        self.hierarchy_label.setMaximumHeight(30)
        self.components_label.setMaximumHeight(30)

        self.hierarchy_help_label.setHidden(True)
        self.components_help_label.setHidden(True)

        self.save_preset_btn.setHidden(True)
        self.load_preset_btn.setHidden(True)

        self.generate_preset_btn = QtWidgets.QPushButton("Generate tree")
        self.generate_preset_btn.setIcon(QtGui.QIcon(cfg.creation_icon))
        self.generate_preset_btn.setIconSize(QtCore.QSize(20, 20))

        self.actions_widget_layout.addWidget(self.generate_preset_btn)
        self.generate_preset_btn.clicked.connect(self.generate_preset)

        if preset_file:
            self.set_preset(preset_file)
            self.show()
        else:
            if self.load_preset():
                self.show()
            else:
                pass


    def closeEvent(self, ev):
        del self.parent().preset_generation_dialog



    def populate_hierarchy_table(self, data):
        if not data:
            self.hierarchy_table_view.setModel_(None)
            return

        catagory_nodes = list()
        for c in data:
            name = c["name"] if 'name' in c.keys() else ''
            quantity = c["quantity"] if 'quantity' in c.keys() else ''
            start = c["from"] if 'from' in c.keys() else 0
            end = c["to"] if 'to' in c.keys() else 0
            padding = c["padding"] if 'padding' in c.keys() else 0
            trailing = c["trailing"] if 'trailing' in c.keys() else 0
            step = c["step"] if 'step' in c.keys() else 1
            catagory_nodes.append(dt.Hierarcy_folder_node(name=name,quantity=quantity, start=start, end=end, padding=padding, trailing=trailing, step=step))

            # catagory_nodes.append(dt.Hierarcy_folder_node(name=c["name"],quantity=c["quantity"], start=c["from"], end=c["to"], padding=c["padding"]))

        mdl = models.Hierarchy_folders_generation_Model(catagory_nodes)
        self.hierarchy_table_view.setModel_(mdl, delegates = False)
        return

    def populate_component_table(self, data):
        if not data:
            self.components_table_view.setModel_(None)
            return

        components = list()
        for branch in data:
            for c in data[branch]:

                if "version_file_type" in data[branch][c].keys():
                    vft = data[branch][c]["version_file_type"]
                else:
                    vft = 'mayaAscii'

                if "master_file_type" in data[branch][c].keys():
                    mft = data[branch][c]["master_file_type"]
                else:
                    mft = 'mayaAscii'

                components.append(dt.Hierarcy_component_node(name=c,
                                                             branch=branch,
                                                             format=data[branch][c]["format"],
                                                             version_file_type = vft,
                                                             master_file_type = mft))

                # components.append(dt.Hierarcy_component_node(name=c, branch=branch, format=data[branch][c]["format"]))

         # = [dt.Hierarcy_component_node(name=cfg.Hierarcy_options.ASK_USER, branch=cfg.Hierarcy_options.ASK_USER)]
        mdl = models.Hierarchy_component_generation_Model(components)
        self.components_table_view.setModel_(mdl, delegates=False)
        return


    def generate_preset(self):


        all_input = True

        def getIndex(model, item, column):
            return model.index(model.items.index(item),column,QtCore.QModelIndex())

        catagories_model = self.hierarchy_table_view.model()
        branches_model = self.components_table_view.model()

        cataories = list()
        branches = dict()
        if catagories_model:
            for cat in catagories_model.items:
                # logger.info(">>>")
                # logger.info(cat.name)
                # logger.info(cat._padding)
                # logger.info(cat._quantity)
                # logger.info(cat._from)
                # logger.info(cat._to)
                if cat._name_ == cfg.Hierarcy_options.ASK_USER and cat.name == cfg.Hierarcy_options.ASK_USER: all_input = False# logger.info('name')
                if cat._from_ == cfg.Hierarcy_options.ASK_USER and cat._from == cfg.Hierarcy_options.ASK_USER: all_input = False#logger.info('f')
                if cat._to_ == cfg.Hierarcy_options.ASK_USER and cat._to == cfg.Hierarcy_options.ASK_USER: all_input = False#logger.info('t')
                if cat._padding_ == cfg.Hierarcy_options.ASK_USER and cat._padding == cfg.Hierarcy_options.ASK_USER: all_input = False#logger.info('p')
                if cat._trailing_ == cfg.Hierarcy_options.ASK_USER and cat._trailing == cfg.Hierarcy_options.ASK_USER: all_input = False
                if cat._step_ == cfg.Hierarcy_options.ASK_USER and cat._step == cfg.Hierarcy_options.ASK_USER: all_input = False
                # if cat._quantity_ == cfg.Hierarcy_options.ASK_USER and cat._quantity: logger.info('q')
                # if cat.name == '' or cat._from == '' or cat._to == '' or cat._padding == '' or cat._quantity == '' or \
                #     cat.name == cfg.Hierarcy_options.ASK_USER or cat._from == cfg.Hierarcy_options.ASK_USER or  \
                #     cat._to == cfg.Hierarcy_options.ASK_USER or cat._padding == cfg.Hierarcy_options.ASK_USER or \
                #     cat._quantity == cfg.Hierarcy_options.ASK_USER:

                    # logger.info(":")
                    # logger.info(self.components_table_view.model().index(catagories_model.items.index(cat),0,QtCore.QModelIndex()))

                # logger.info(getIndex(catagories_model, cat, 0))

                cataories.append({'name': cat.name, 'from': cat._from, 'to': cat._to, 'padding': cat._padding, 'quantity': cat._quantity, 'trailing': cat._trailing, 'step': cat._step})

        if branches_model:
            # logger.info(branches_model.items)
            for br in branches_model.items:

                if br._name_ == cfg.Hierarcy_options.ASK_USER and br.name == cfg.Hierarcy_options.ASK_USER: all_input = False
                if br._branch_ == cfg.Hierarcy_options.ASK_USER and br._branch == cfg.Hierarcy_options.ASK_USER: all_input = False
                if br._format_ == cfg.Hierarcy_options.ASK_USER and br._format == cfg.Hierarcy_options.ASK_USER: all_input = False
                # logger.info('working on branches[{}]'.format(br._branch))
                # logger.info('adding {}'.format(br.name))
                if br._branch in branches:
                    branches[br._branch].update({br.name: {'format': int(br._format), 'master_file_type': br._master_file_type, 'version_file_type': br._version_file_type}})
                else:
                    branches[br._branch] = {br.name: {'format': int(br._format), 'master_file_type': br._master_file_type, 'version_file_type': br._version_file_type}}

                # logger.info('now looking like: {}'.format(branches[br._branch]))


        preset = dict()
        preset['categories'] = cataories
        preset['branches'] = branches


        for k, v in preset.iteritems():
            logger.info(k)
            if isinstance(v, list):
                for x in v:
                    logger.info("{}".format(x))

            if isinstance(v, dict):
                for xx, vv in v.iteritems():
                    logger.info("{} {}".format(xx, vv))


        for k, v in branches.iteritems():
            logger.info("{}: {}".format(k, v))

        status = False

        if all_input:
            status = Preset_generator().create(preset=preset, parent=self, project=self.pipeline_window.project)
        else:
            massage.massage(cfg.text_icon, 'Missing input','Please fill all input fields', parent=self)

        if status:
            self.pipeline_window.navigator.set_branch_root(self.pipeline_window.project.path)

        self.close()

class Preset_generator(object):
    def __init__(self):
        pass


    def create_catagory(self, name ='', path = '',  project = None):
        elements.CatagoryNode(name, path=path, project=project).create(path=path)

    def create_component(self, name ='', path = '', format = 1, project = None, version_file_type='ma', master_file_type='ma'):

        def file_type_parse(file_type_string):
            if file_type_string == 'mayaAscii':
                return 'ma'
            else:
                return 'mb'

        elements.ComponentNode(name, path=path, project=project, format=format,
                               version_file_type=file_type_parse(version_file_type),
                               master_file_type=file_type_parse(master_file_type)).create(path=path)

    def create_branch(self, name ='', path = '',  project = None):
        elements.BranchNode(name, path=path, project=project).create(path=path)

    def create(self, preset=None, parent=None, project=None):

        self.progress_bar_dialog = QtWidgets.QProgressDialog( "", "Abort operation", 0, 100, parent)
        self.progress_bar_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_bar_dialog.show()

        global proceed
        global counter
        global total_items

        proceed = True
        counter = 0
        total_items = 0


        def rec_total(catagories, branch):
            global total_items

            _from = int(catagories[0]['from'])
            _to = int(catagories[0]['to'])

            total = _to - _from

            for i in range(total + 1):

                if len(catagories) == 1:
                    # add folder
                    total_items +=1

                    for component in branch:
                        # add component
                        total_items += 1

                else:
                    # add folder
                    total_items += 1

                if len(catagories) > 1:

                    l = list(catagories[1:])
                    rec_total(l, branch)
                else:
                    pass

        def rec(catagories, p, branch, project):

            global proceed
            global counter
            global total_items

            if self.progress_bar_dialog.wasCanceled():
                proceed = False
                return


            """ recursive function for generating a tree out of the instructions list called items
            the function creates nodes by instruction in the first item in the list, then while the list is longer then 1,
            it sends the list againg but without the current item
            the parent is the currently created node"""
            _from = int(catagories[0]['from'])
            _to = int(catagories[0]['to'])
            name = catagories[0]['name']
            padding = int(catagories[0]['padding'])
            trailing = int(catagories[0]['trailing'])
            step = int(catagories[0]['step'])

            total = _to - _from

            for i in range(total+1):

                if (total > 0) and (padding == 0): padding += 1

                count = misc.set_padding((i+_from)*step, padding) if padding > 0 else ''
                trailing_ = '_{}'.format(misc.set_padding(0, trailing)) if trailing > 0 else ''
                folder_name = "{}{}{}".format(name, count, trailing_)

                path = os.path.join(p, folder_name)

                if len(catagories) == 1:
                    counter += 1
                    if not self.progress_bar_dialog.wasCanceled():
                        self.progress_bar_dialog.setValue(misc.remap_value(counter, 0, total_items, 0, 100))
                        QtWidgets.QApplication.processEvents()

                    if not os.path.isdir(path): self.create_catagory(name=folder_name,path=path,project=project)

                    # logger.info("-")
                    # logger.info("creating folder with components {}".format(path))

                    for component in branch:
                        counter += 1
                        if not self.progress_bar_dialog.wasCanceled():
                            self.progress_bar_dialog.setValue(misc.remap_value(counter, 0, total_items, 0, 100))
                            QtWidgets.QApplication.processEvents()
                        dir = os.path.join(path, component)
                        # logger.info("createing component {}".format(dir))
                        if not os.path.isdir(dir): self.create_component(name=component,
                                                                         path=dir,
                                                                         format=branch[component]['format'],
                                                                         project=project,
                                                                         master_file_type=branch[component]['master_file_type'],
                                                                         version_file_type=branch[component]['version_file_type'])

                else:
                    # pass
                    counter += 1
                    if not self.progress_bar_dialog.wasCanceled():
                        self.progress_bar_dialog.setValue(misc.remap_value(counter, 0, total_items, 0, 100))
                        QtWidgets.QApplication.processEvents()
                    # logger.info("-")
                    # logger.info("creating folder {}".format(path))
                    if not os.path.isdir(path): self.create_catagory(name=folder_name, path=path, project=project)

                if len(catagories) > 1:

                    l = list(catagories[1:])
                    rec(l, path, branch , project)
                else:
                    pass


        def remove_catagory(name, _from, _to, padding, step):

            total = _to - _from

            for i in range(total + 1):

                if (total > 0) and (padding == 0): padding += 1

                count = misc.set_padding((i + _from)*step, padding) if padding > 0 else ''
                folder_name = "{}{}".format(name, count)

                logger.info('removing {}'.format(folder_name))


        catagories = preset['categories']
        branches = preset['branches']

        for branch in branches:
            rec_total(catagories,  branches[branch])

        logger.info(total_items)


        new_branches = list()

        for branch in branches:

            parent_dir = os.path.join(project.path, branch)
            if not os.path.isdir(parent_dir):
                self.create_branch(name=branch, path=parent_dir, project=project)
                new_branches.append(parent_dir)

            rec(catagories, parent_dir, branches[branch], project)


        if not proceed:

            remove_catagory(catagories[0]['name'], int(catagories[0]['from']), int(catagories[0]['to']), int(catagories[0]['padding']), int(catagories[0]['step']))

            for folder in new_branches:
                files.delete(folder)

            return False

        self.progress_bar_dialog.hide()

        return True

#     # @staticmethod
#     def xx_create(self, preset):
#         catagories = preset['categories']
#         branches = preset['branches']
#
#         for branch in branches:
#             logger.info("createing branch {}".format(branch))
#
#             parent_dir = os.path.join(branch)
#
#             for catagory in catagories:
#                 _from = catagory['from']
#                 _to = catagory['to']
#                 if _from !=0:
#                     for i in range(_from, _to+1):
#                         dir = os.path.join(parent_dir, "{}{}".format(catagory['name'],i))
#                         logger.info("createing catagory {}".format(dir))
#                         parent_dir = dir
#                 else:
#                     dir = os.path.join(parent_dir, catagory['name'])
#                     logger.info("createing catagory {}".format(dir))
#                     parent_dir = dir
#
#             for component in branches[branch]:
#                 dir = os.path.join(parent_dir, component)
#                 logger.info("createing component {}".format(dir))
#
#
#
#             # while i < len(catagories):
#             #     logger.info("createing catagory {}/{}".format(branch, catagory['name']))
#             #
#             # for catagory in catagories:
#             #
#             #     logger.info("createing catagory {}/{}".format(branch, catagory['name']))
#             #
#             # logger.info()
#
#     # def create_catagory(self, node, index = None):
#     #
#     #     folderDlg = outliner.newFolderDialog(string="")
#     #     result = folderDlg.exec_()
#     #     res = folderDlg.result()
#     #     if result == QtWidgets.QDialog.Accepted:
#     #         logger.info(res)
#     #
#     #         base_folder_name = res["name"]
#     #
#     #         for i in range(0, res["quantity"]):
#     #
#     #             number = files.set_padding(res["from"] + i, res["padding"])
#     #
#     #             if base_folder_name != "":
#     #
#     #                 folder_name = "{0}{1}".format(base_folder_name, number) if res["quantity"] > 1 else "{0}".format(base_folder_name)
#     #
#     #             else:
#     #                 folder_name = "{0}".format(number) if res["quantity"] > 1 else "unnamed_folder"
#     #
#     #             if node:
#     #                 target_directory = node.path
#     #             else:
#     #                 target_directory = self.parent()._path
#     #
#     #             skip = False
#     #             if folder_name in files.list_dir_folders(target_directory):
#     #                 skip = True
#     #             if skip:
#     #                 logger.info("Folder named {0} exsits at {1}. skipping...".format(folder_name, target_directory))
#     #                 continue
#     #
#     #             path = os.path.join(target_directory, folder_name)
#     #             new_node = elements.CatagoryNode(folder_name, path=path, project=self.parent().parent.parent.project).create(path=path)
#     #
#     #             if not node:
#     #
#     #                 if self.model():
#     #                     self.model().sourceModel().insertRows(0, 1, node=new_node)
#     #                     self._proxyModel.invalidate()
#     #
#     #                 else:
#     #                     model = models.List_Model([new_node])
#     #                     logger.info(model)
#     #                     self.setModel_(model)
#     #
#     #         if node and index:
#     #             self.parent().update(index)
# #
# # class Progress_window(QtWidgets.QDialog):
# #     def __init__(self, parent=None, title = '', caption = '', min = 0, max = 100):
# #         super(Progress_window, self).__init__(parent)
# #         self.setStyleSheet(cfg.stylesheet)
# #         self.setMaximumWidth(300)
# #         self.setMinimumWidth(300)
# #         self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
# #
# #         self.setMinimumHeight(80)
# #         self.setMaximumHeight(80)
# #
# #         self.layout = QtWidgets.QVBoxLayout(self)
# #         self.layout.setContentsMargins(10, 10, 10, 10)
# #
# #         self.title = gui.Title(self, label=caption, seperator=False)
# #         self.title.setMaximumHeight(30)
# #         self.layout.addWidget(self.title)
# #
# #         self.progress_bar = QtWidgets.QProgressBar()
# #         self.progress_bar.setMinimum(min)
# #         self.progress_bar.setMaximum(max)
# #         self.progress_bar.setValue(0)
# #         self.layout.addWidget(self.progress_bar)
# #
# #     def setValue(self, value):
# #         self.progress_bar.setValue(value)