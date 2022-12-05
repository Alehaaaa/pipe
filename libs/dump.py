#from pipeline_main.PipelineUI:

# def propagate_current(self):
#     """
#     This function will start a dialog for propagating the current active scene in maya, into multiple shots.
#     The dialog window will return a dict with:
#     name for the new shot
#     range for creating them
#     the stages to create
#     and an class object for the parent scene.
#     """
#
#     propagteWindow = propagation_tool.PropagateWindow(self)
#     result = propagteWindow.exec_()
#     res, parent_node = propagteWindow.result()
#     if result == QtWidgets.QDialog.Accepted:
#         # print res, parent_node.name, parent_node._path, maya.current_open_file()
#
#         base_folder_name = res["name"]
#
#         exisiting = files.list_dir_folders(parent_node.path)
#
#         for i in range(0, res["quantity"]):
#
#             number = files.set_padding(res["from"] + i, res["padding"])
#             if base_folder_name != "":
#                 folder_name = "{0}{1}".format(base_folder_name, number) if res[
#                                                                                "padding"] > 1 else base_folder_name
#             else:
#                 folder_name = "{0}".format(number) if res["quantity"] > 1 else "sc"
#
#             if folder_name in exisiting:
#                 logger.info("folder {} exisits...".format(folder_name))
#                 continue
#
#             path = os.path.join(parent_node.path, folder_name)
#             node = assets.AssetNode(folder_name, path=path, parent=parent_node,
#                                     section=parent_node.section, settings=self.settings,
#                                     project=self.project).create(
#                 path=path)
#
#             for s in res["stages"]:
#                 if res["stages"][s]:
#                     path = os.path.join(parent_node.path, folder_name, s)
#                     stageNode = stages.StageNode(s, parent=node, path=path,
#                                                  name_format=res["name_format"], section=parent_node.section,
#                                                  project=self.project, settings=self.settings).cretae_from_file(
#                         path=path, file=maya.current_open_file())
#
#             logger.info("create asset {}...".format(folder_name))


#stages loading sequesnce
# import logging
# import os
# import socket
# import time
#
# import pipeline.apps.create_files as create
# import pipeline.apps.project_outliner as outliner
# import pipeline.libs.config as cfg
# import pipeline.libs.data as dt
# import pipeline.libs.files as files
# import pipeline.libs.locking as locking
# import pipeline.libs.misc as misc
# import pipeline.libs.models as models
# import pipeline.libs.nodes.working as working
# import pipeline.libs.serializer as serializer
# import pipeline.maya_libs.maya_warpper as maya
# import pipeline.widgets.inputs as inputs
#
# from pipeline.libs.Qt import QtGui, QtWidgets, QtCore
#
# #
# if cfg._dev:
#     reload(cfg)
#     reload(serializer)
#     reload(files)
#     reload(misc)
#     reload(models)
#     reload(locking)
#     reload(maya)
#     reload(working)
#     reload(create)
#     reload(inputs)
#     # reload(dt)
#
# logger = logging.getLogger(__name__)