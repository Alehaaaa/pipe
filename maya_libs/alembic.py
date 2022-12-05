import logging
logger = logging.getLogger(__name__)
import maya.cmds as cmds
import maya.mel as mel

class Alembic_handler(object):
    '''

    USAGE:
    import pipeline2_sb.maya_libs.alembic as alembic
    alembic.Alembic_handler.export(frameRange=[0,20],attrs=['version','rig'], root = '|kermit_rig_MASTER:kermit_render_grp', filename = 'C:/Users/liorbh/Documents/pipeline_sandbox/projects/iterations/cache/alembic/shot_2_kermit_auto.abc')


    '''
    def __init__(self):
        pass

    @staticmethod
    def export(frameRange = [0,0], attrs = list(), root = None, filename = ''):

        root_pointer = ''
        if root:
            if not cmds.objExists(root):
                logger.info("root is not in scene")
                return

            root_pointer = " -root {}".format(root)

        start = 0
        end = 120
        range = "-frameRange {0} {1} ".format(start, end)

        vars = ""
        if attrs:
            for a in attrs:
                vars += " -attr {}".format(a)


        save_name = " -file {}".format(filename)
        uv = " -uvWrite"
        ws = " -worldSpace"
        dataFormat = ' -dataFormat ogawa'
        command = range + vars + root_pointer + dataFormat + uv + ws + save_name

        # logger.info(command)


        cmds.AbcExport(j=command)

