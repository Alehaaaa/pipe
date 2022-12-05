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
import random
import string
import json

import maya.cmds as cmds
import maya.mel as mel

import maya.OpenMaya as OpenMaya

import pipeline.apps.massage as massage
import pipeline.apps.project_outliner as outliner
import pipeline.libs.config as cfg
import pipeline.libs.files as files

if cfg.DEBUG:
    reload(cfg)
    reload(files)
    reload(outliner)

logger = logging.getLogger(__name__)

def gMainWindow():
    return mel.eval("$tempVar = $gMainWindow")

def viewport_massage(string):
    cmds.inViewMessage(amg='<hl>{}</hl>'.format(string), pos='midCenter', fade=True)

def menuItem_enable(menuItem, bool):
    try:
        cmds.menuItem(menuItem, e=True, en=bool)
    except:
        pass

def maya_api_version():
    return int(cmds.about(api=True))


def new_scene():
    state = checkState()
    if state == 'save':
        save_scene()
    elif state == 'cancel':
        return

    return os.path.normpath(cmds.file(new=True, f=True))


def rewind():
    cmds.currentTime(1)
    cmds.playbackOptions(minTime=1)


def file_type_parse(file_type_string):
    if file_type_string == '.ma': return 'mayaAscii'
    else: return 'mayaBinary'

def save_scene_as(path=None, file_name=None):
    if os.path.exists(path):
        if file_name:
            extension = files.extension(file_name)
            # print extension, '<<'
            fullpath = os.path.join(path, file_name)
            cmds.file(rename=fullpath)
            path = os.path.normpath(cmds.file(f=True, s=True, type=file_type_parse(extension), op="v=1"))
            insert_recent_file(path)
            viewport_massage("{} Saved".format(os.path.basename(path)))
            logger.info("{} Saved".format(path))
            return path

def open_scene(path=None):
    if os.path.exists(path):

        state = checkState()
        if state == 'save':
            save_scene()
        elif state == 'cancel':
            return

        r_path = path
        try:
            def foo(retCode, fileObject, clientData):
                newName = fileObject.rawFullName()
                newName = str( newName )
                try:
                    newName = os.path.join([i for i in json.load(open(os.path.join(os.environ['MAYA_APP_DIR'],cmds.about(v=True),'prefs','pipeline2_settings.json')))['projects']][0],newName.split('/TMH/')[1])
                except:
                    cmds.error( "Errors while changing reference locations" )
                newName = newName.replace("\\","/")
                print ( newName )
                fileObject.setRawFullName( newName )
                OpenMaya.MScriptUtil.setBool( retCode, True )
	
            id = OpenMaya.MSceneMessage.addCheckFileCallback(OpenMaya.MSceneMessage.kBeforeReferenceCheck, foo)
            
            _path = os.path.normpath(cmds.file(r_path, o=True, f=True, esn=True, options="v=1"))
            r_path = _path
        except Exception, err:
            logger.info(err)


        viewport_massage("{} Loaded".format(os.path.basename(r_path)))
        logger.info("{} Loaded".format(r_path))
        if current_open_file() == r_path:
            insert_recent_file(r_path)
            return r_path
    return False


def current_open_file():
    file = os.path.normpath(cmds.file(q=True, sn=True))
    # logger.info(file)
    if file == ".":
        return ""
    return file


def save_scene():
    cmds.SaveScene()

def file_modifed():
    fileCheckState = cmds.file(q=True, modified=True)
    return fileCheckState

# def checkState():
#     # check if there are unsaved changes
#
#
#     # if there are, save them first ... then we can proceed
#     if file_modifed():
#         # import pipeline.apps.project_outliner as outliner
#         # This is maya's native call to save, with dialogs, etc.
#         # No need to write your own.
#         if massage.warning("warning", "Scene Not Saved", "Scene Not Saved, Do you want to save it first?"):
#             save_scene()
#             return True
#
#     else:
#         return False
def checkState():
    # check if there are unsaved changes
    if file_modifed():

        prompt = massage.PromptUser(None, title='Scene not saved', prompt='Scene not saved, Do you want to save it?', override_yes_text='Yes', override_no_label='No',override_cancel_label='Cancel', cancel_button=True)
        result = prompt.exec_()
        logger.info(result)

        if result == 0:
            return 'save'
        elif result == 1:
            return 'dont save'
        else:
            logger.info("Canceled...")
            return 'cancel'

def reference_scene(path=None):
    if os.path.exists(path):
        namesspace = files.file_name_no_extension(files.file_name(path))
        path = "$TMH" + path.split("TMH_Project")[1]
        return os.path.normpath(cmds.file(path, r=True, f=True, ns=namesspace, esn=False))


def import_scene(path=None):
    if os.path.exists(path):
        namesspace = files.file_name_no_extension(files.file_name(path))
        return os.path.normpath(cmds.file(path, i=True, f=True, ns=namesspace, esn=False, preserveReferences=True))


def reference_file_paths():
    def ref_path(ref):
        try:
            return os.path.normpath(cmds.referenceQuery(ref, filename=True))
        except:
            logger.info(" somthing is wrong with {}".format(ref))
            return None

    li = [ref_path(ref) for ref in cmds.ls(rf=True)]
    return [path for path in li if path]


def list_referenced_files():
    results = []
    links = cmds.filePathEditor(query=True, listDirectories="")
    for link in links:
        pairs = cmds.filePathEditor(query=True, listFiles=link, withAttribute=True, status=True)
        '''
        paris: list of strings ["file_name node status ...", "file_name node status ...",...]
        we need to make this large list of ugly strings (good inforamtion seperated by white space) into a dictionry we can use
        '''
        l = len(pairs)
        items = l / 3
        order = {}
        index = 0

        '''
        order: dict of {node: [file_name, status],...}
        '''

        for i in range(0, items):
            order[pairs[index + 1]] = [os.path.join(link, pairs[index]), pairs[index + 1], pairs[index + 2]]
            index = index + 3

        for key in order:
            # for each item in the dict, if the status is 0, repath it
            if order[key][2] == "1":
                results.append([order[key][0], cmds.nodeType(order[key][1])])

    return results


def relink_pathes(project_path=None):
    results = []
    links = cmds.filePathEditor(query=True, listDirectories="")
    for link in links:
        pairs = cmds.filePathEditor(query=True, listFiles=link, withAttribute=True, status=True)
        '''
        paris: list of strings ["file_name node status ...", "file_name node status ...",...]
        we need to make this large list of ugly strings (good inforamtion seperated by white space) into a dictionry we can use
        '''
        l = len(pairs)
        items = l / 3
        order = {}
        index = 0

        '''
        order: dict of {node: [file_name, status],...}
        '''

        for i in range(0, items):
            order[pairs[index + 1]] = [pairs[index], pairs[index + 2]]
            index = index + 3

        for key in order:
            # for each item in the dict, if the status is 0, repath it
            if order[key][1] == "0":
                if repath(key, order[key][0], project_path):
                    results.append(key)

    return results


def repath(node, file, project_path):
    matches = []
    for root, dirnames, filenames in os.walk(project_path):
        for x in filenames:
            if x == file:
                matches.append([root, os.path.join(root, x)])
            elif x.split(".")[0] == file.split(".")[
                0]:  # ---> this second option is used when a file is useing ##### padding, we can match by name only

                x_ext = x.split(".")[len(x.split(".")) - 1]
                file_ext = file.split(".")[len(file.split(".")) - 1]
                if x_ext == file_ext:
                    matches.append([root, os.path.join(root, x)])

    if len(matches) > 0:
        return cmds.filePathEditor(node, repath=matches[0][0])

    return None


def snapshot(path=None, width=96, height=96):
    current_image_format = cmds.getAttr("defaultRenderGlobals.imageFormat")
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)  # *.png
    # path = "/Users/liorbenhorin/Library/Preferences/Autodesk/maya/2015-x64/scripts/pipeline/thumb.png"
    cmds.playblast(cf=path, fmt="image", frame=cmds.currentTime(query=True), orn=False, wh=[width, height], p=100,
                   v=False)
    cmds.setAttr("defaultRenderGlobals.imageFormat", current_image_format)

    if os.path.isfile(path):
        return path
    else:
        return False


def playblast_snapshot(path=None, format=None, compression=None, hud=None, offscreen=None, range=None, scale=None):
    current_image_format = cmds.getAttr("defaultRenderGlobals.imageFormat")
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)  # *.png

    if range is None:

        range = playback_selection_range()
        print range
        if range is None:
            start = cmds.playbackOptions(q=True, min=True)
            end = cmds.playbackOptions(q=True, max=True)
            range = [start, end]

    cmds.playblast(frame=int((range[0] + range[1]) / 2), cf=path, fmt="image", orn=hud, os=offscreen,
                   wh=scene_resolution(), p=scale, v=False)

    cmds.setAttr("defaultRenderGlobals.imageFormat", current_image_format)


def playblast(path=None, format=None, compression=None, hud=None, offscreen=None, range=None, scale=None):
    if range is None:

        range = playback_selection_range()
        print range
        if range is None:
            start = cmds.playbackOptions(q=True, min=True)
            end = cmds.playbackOptions(q=True, max=True)
            range = [start, end]

    #query users's focalLengthVisibility
    # focalLengthVisibility = cmds.optionVar(query="focalLengthVisibility")

    #set focalLengthVisibility On for the recording
    # mel.eval('setFocalLengthVisibility({})'.format(str(1)))
    #
    # if camera == 'Active camera':
    #     cam = ''
    # elif camera == 'Render camera':
    #     cam = ''

    if compression:
        cmds.playblast(startTime=range[0], endTime=range[1], f=path, fmt=format, orn=hud, os=offscreen,
                       wh=scene_resolution(), p=scale, qlt=90, c=compression, v=False, s = qeury_active_sound_node())
    else:
        cmds.playblast(startTime=range[0], endTime=range[1], f=path, fmt=format, orn=hud, os=offscreen,
                       wh=scene_resolution(), p=scale, qlt=90, v=False, s=qeury_active_sound_node())
    #restore focalLengthVisibility to users's prefs
    # mel.eval('setFocalLengthVisibility({})'.format(str(focalLengthVisibility)))


def playback_selection_range():
    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
    time_selection = cmds.timeControl(aPlayBackSliderPython, q=True, rng=True)[1:-1]
    start = round(float(time_selection.split(":")[0]))
    end = round(float(time_selection.split(":")[1]))

    if start + 1 == end:
        return None
    else:
        return [start, end]


# def getPlayblastOptions():
#     options = {}
#     options["format"] = cmds.playblast(q=True, fmt=True)
#     options["compression"] = cmds.playblast(q=True, c=True)
#     return options

def getPlayblastFormat():
    return cmds.playblast(q=True, fmt=True)

def getPlayblastCompression(format):
    '''

    This trick is cloned from maya-capture-gui by Marcus Ottosson

    '''
    cmd = 'playblast -format "{0}" -query -compression'.format(format)
    return mel.eval(cmd)


def qeury_active_sound_node():
    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
    sound = cmds.timeControl(aPlayBackSliderPython, q=1, s=1)
    if sound:
        return sound
    else:
        return None

def scene_resolution():
    return [cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")]


def insert_recent_file(path):
    # logger.info('insert')
    _path = path
    platform = files.os_qeury()
    if platform == "win32":
        _path = path.replace('\\', '/')

    cmd = 'addRecentFile "{}" "mayaAscii";'.format(_path)
    # logger.info(cmd)
    mel.eval(cmd)
    # cmds.optionVar(stringValueAppend=('RecentFilesList', '{} {}'.format(path,"mayaAscii")))


def recent_files_list():
    return cmds.optionVar(query='RecentFilesList')


def create_scriptjob(parent=None, event=None, script=None):
    if event and script:
        return cmds.scriptJob(e=[event, script], ro=False, p=parent)


def kill_scriptjob(job=None):
    if job:
        return cmds.scriptJob(kill=job, f=True)


# def save_scene_script(parent=None, script=None):
#     return create_scriptjob(parent=parent, event="NewSceneOpened", script=script)
#

def new_scene_script(parent=None, script=None):
    return create_scriptjob(parent=parent, event="NewSceneOpened", script=script)


def open_scene_script(parent=None, script=None):
    return create_scriptjob(parent=parent, event="SceneOpened", script=script)


def flush_scene_script(parent=None, script=None):
    return create_scriptjob(parent=parent, event="flushingScene", script=script)


def new_scene_from_selection(project_path=None, mode="include"):
    temp_file = os.path.join(project_path, "scenes", "temp_%s.ma" % (id_generator()))
    logging.info(temp_file)
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        if mode == outliner.create_options.E_SELECTION_ALL:
            saved_file = os.path.normpath(
                cmds.file(temp_file, type='mayaAscii', exportSelected=True, expressions=True, constraints=True,
                          channels=True, constructionHistory=True, shader=True))
        if mode == outliner.create_options.D_SELECTION_ONLY:
            saved_file = os.path.normpath(
                cmds.file(temp_file, type='mayaAscii', exportSelected=True, expressions=False, constraints=False,
                          channels=False, constructionHistory=False, shader=True))

        if saved_file:
            open_scene(saved_file)
            return saved_file

    return None


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def maya_version():
    return cmds.about(version=True)


def set_fps(fps=None):
    fps_string = "pal"
    if fps == 25:
        fps_string = "pal"
    if fps == 24:
        fps_string = "film"
    if fps == 30:
        fps_string = "ntsc"
    cmds.currentUnit(t=fps_string)



def viewMassage(text=None):
    cmds.inViewMessage(amg="Pipeline: " + text, pos='topCenter', fade=True, fst=3000)


def userPrefDir():
    return cmds.internalVar(userPrefDir=True)



def import_obj(path=None, namespace = True):
    if os.path.exists(path):
        try:
            cmds.loadPlugin("objExport", qt=True)
            namesspace = files.file_name_no_extension(files.file_name(path))
            import_file = os.path.normpath(cmds.file(path, ns=namesspace, type="OBJ", i=True, esn=True, options = "mo=1;lo=0", ra=True, mergeNamespacesOnClash = False))

            if not namesspace:
                remove_all_namespaces()

            return import_file

        except:
            logger.info("could not import obj file: {}".format(path))


def import_fbx(path = None, namespace = True):
    if os.path.exists(path):
        try:
            cmds.loadPlugin("fbxmaya", qt=True)

            mel.eval('FBXImportMode -v Add') #--- why the 'exmerge' not working??
            mel.eval('FBXImportCacheFile -v true')
            mel.eval('FBXImportCameras -v true')
            mel.eval('FBXImportMergeAnimationLayers -v true')
            mel.eval('FBXImportProtectDrivenKeys -v true')
            mel.eval('FBXImportConvertDeformingNullsToJoint -v true')
            mel.eval('FBXImportMergeBackNullPivots -v false')
            mel.eval('FBXImportSetLockedAttribute -v true')
            mel.eval('FBXImportConstraints -v false')

            mel.eval('FBXImport -f "{}"'.format(path))

            if not namespace:
                remove_all_namespaces()
        except:
            logger.info("could not import fbx file: {}".format(path))

def remove_all_namespaces():
    # Used as a sort key, this will sort namespaces by how many children they have.
    def num_children(ns):
        return ns.count(':')

    defaults = ['UI', 'shared']

    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
    # We want to reverse the list, so that namespaces with more children are at the front of the list.
    namespaces.sort(key=num_children, reverse=True)

    for ns in namespaces:

        if namespaces.index(ns) + 1 < len(namespaces):
            parent_ns = namespaces[namespaces.index(ns) + 1]
            cmds.namespace(mv=[ns, parent_ns], f=True)
            cmds.namespace(rm=ns)
        else:
            cmds.namespace(mv=[ns, ":"], f=True)
            cmds.namespace(rm=ns)

'''

OBJ IMPORT EXPORT THAT WORKS SOMEHOW:

file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -type "OBJexport" -ea "/Users/liorbenhorin/Documents/maya/pipe2_projects/aaaaaa/scenes/balls_sep.obj";
// Result: /Users/liorbenhorin/Documents/maya/pipe2_projects/aaaaaa/scenes/balls_sep.obj //
file -f -new;
// Result: untitled //
file -import -type "OBJ" -ra true -mergeNamespacesOnClash false -namespace "balls_sep" -options "mo=1;lo=0"  -pr "/Users/liorbenhorin/Documents/maya/pipe2_projects/aaaaaa/scenes/balls_sep.obj";


cmds.pluginInfo( query=True, listPlugins=True )


cmds.unloadPlugin("objExport", f=True)
cmds.loadPlugin("objExport", qt=True)


cmds.unloadPlugin("fbxmaya", f=True)
cmds.loadPlugin("fbxmaya", qt=True)



'''


def clean_up_file():
    pass
    # import references

    refs = cmds.ls(type='reference')
    for i in refs:
        rFile = cmds.referenceQuery(i, f=True)
        cmds.file(rFile, importReference=True, mnr=True)

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

    # remove ngSkinTools custom nodes
    from ngSkinTools.layerUtils import LayerUtils
    LayerUtils.deleteCustomNodes()

    # remove RRM proxies
    if cmds.objExists("RRM_MAIN"):
        cmds.select("RRM_MAIN",hi=True)
        proxies = cmds.ls(sl=True)
        cmds.lockNode(proxies,lock=False)
        cmds.delete(proxies)

        if cmds.objExists("RRM_ProxiesLayer"):
            cmds.delete("RRM_ProxiesLayer")