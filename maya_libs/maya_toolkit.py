import logging
logger = logging.getLogger(__name__)
import os
import pipeline.libs.config as cfg
import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm
# import pipeline.libs.meta as meta
import pipeline.maya_libs.maya_warpper as maya
import pymel.core.nodetypes as nt


# def create_group(name, parent='', w=False, em=True):
#     if cmds.objExists(name):
#         logger.info("{} - exists - skipping".format(name))
#         return
#     else:
#         if parent:
#             pm.group(n =name, parent=parent, em=True)
#
#             logger.info("{} - created".format(name))
#             return
#         if w:
#             pm.group(n = name, w=True, em=True)
#
#             logger.info("{} - created".format(name))
#             return



# def export_high_group(asset_name = '', path = ''):
#     render_grp = '{}{}'.format(asset_name, cfg._render_grp).lower()
#
#     try:
#         dup = pm.duplicate(render_grp)
#         pm.parent(dup, w=True)
#         dup[0].rename(render_grp)
#         pm.select(dup[0], hi=True)
#
#         exported_file = cmds.file(path, type='mayaAscii', exportSelected=True, expressions=False, constraints=False,
#                   channels=False, constructionHistory=False, shader=True, force=True)
#
#         pm.delete(dup[0])
#
#         return os.path.normpath(exported_file)
#     except:
#         logger.info("failed to export selection on {}".format(maya.current_open_file()))
#         return None

# def create_modeling_defaults(name = 'name'):
#     name_lower = name.lower()
#
#     create_group(name_lower,w=True)
#
#     high_group = '{}_{}_{}'.format(name_lower, cfg.high, cfg.group)
#     low_group = '{}_{}_{}'.format(name_lower, cfg.low, cfg.group)
#     bsp_group = '{}_{}_{}'.format(name_lower, cfg.blendshape, cfg.group)
#
#     create_group(high_group,parent=name_lower)
#     create_group(low_group, parent=name_lower)
#     create_group(bsp_group, parent=name_lower)
#

#
# def clean_meta_nodes(node_name = ''):
#     logger.info("remove unused meta nodes")
#     nodes = meta.Component_Meta.getMetaNodes()
#     for node in nodes:
#         if node.shortName() != node_name:
#             node.delete()


def cleanup_scene():
    logger.info("Cleaning up scene ---------------------------------")

    # import pymel.core as pm
    #
    # import pymel.core.nodetypes as nt

    nodes = pm.ls(type=nt.Unknown)
    for n in nodes:
        pm.delete(n)

    mel_cleanup  = '''
    source cleanUpScene;
    deleteUnusedTrax( "clips" );
    deleteUnusedTrax( "poses" );
    deleteUnusedDeformers();
    deleteInvalidNurbs(0);
    MLdeleteUnused();
    removeDuplicateShadingNetworks(0);
    RNdeleteUnused();
    deleteUnusedBrushes();
    deleteEmptyGroups();
    deleteEmptyLayers("Display");
    deleteEmptyLayers("Render");
    deleteUnusedExpressions();
    deleteUnusedLocators();
    deleteUnusedPairBlends();
    deleteUnusedSets();
    deleteUnusedConstraints();
    deleteUnusedInUnusedHierarchy( "nurbsCurve", 0,(uiRes("m_cleanUpScene.kDeletingUnusedNurbsCurves2")));
    deleteUnusedCommon( "animCurve", 0 , (uiRes("m_cleanUpScene.kDeletingUnusedAnimationCurves")));
    deleteUnusedCommon("groupId", 0, (uiRes("m_cleanUpScene.kDeletingUnusedGroupIDNodes")));
    hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");
    '''
    try:
        mel.eval(mel_cleanup)
    except:
        logger.info("Scene clean up failed")



# import maya.cmds as cmds

def ns_keys(text):
    return len(text.split(':'))

def ns_sort(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=ns_keys)

    return l


def remove_ref():
    logger.info("Importing references ---------------------------------")

    try:
        mel.eval('RNdeleteUnused();')

        sorted_references = ns_sort(cmds.ls(type='reference'))

        for i in sorted_references:
            print i
            rFile = cmds.referenceQuery(i, f=True)
            cmds.file(rFile, importReference=True, mnr = True, f = True)
    except Exception, err:
        logger.info(err)
        logger.info("Import references failed")


def delete_ns():
    logger.info("Deleting namespaces ----------------------------------")

    try:
        defaults = ['UI', 'shared']
        # Used as a sort key, this will sort namespaces by how many children they have.
        def num_children(ns):
            return ns.count(':')
        namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
        # We want to reverse the list, so that namespaces with more children are at the front of the list.
        namespaces.sort(key=num_children, reverse=True)
        for ns in namespaces:
            if namespaces.index(ns)+1 < len(namespaces):
                parent_ns = namespaces[namespaces.index(ns)+1]
                cmds.namespace(mv=[ns,parent_ns], f=True)
                cmds.namespace(rm=ns)
            else:
                cmds.namespace(mv=[ns,":"], f=True)
                cmds.namespace(rm=ns)
    except Exception, err:
        logger.info(err)
        logger.info("Delete namespaces failed")

def delete_ngSKinToolsNodes():
    logger.info("Removing ngSkinsTools nodes --------------------------")

    try:
        # remove ngSkinTools custom nodes
        from ngSkinTools.layerUtils import LayerUtils
        LayerUtils.deleteCustomNodes()
    except:
        logger.info("ngSkinsTools not installed / no ngSkinTools nodes in the scene")


def run_script(path, script_type):
    logger.info("Running script ---------------------------------------")
    logger.info("{} ---------------------------------------------------".format(path))

    if os.path.exists(path):
        if script_type == 'py':
            try:
                execfile(path)
            except Exception, err:
                logger.info(err)
                return
        elif script_type == 'mel':
            try:
                cmd = 'source "{}";'.format(path)
                mel.eval(cmd)
            except Exception, err:
                logger.info(err)
                return

                # import pymel.core as pm
#
# import pymel.core.nodetypes as nt
#
# nodes = pm.ls(type=nt.Unknown)
# for n in nodes:
# 	pm.delete(n)



#
# '''