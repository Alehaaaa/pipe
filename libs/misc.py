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


import os
import re
import pipeline.libs.config as cfg
import pipeline.libs.files as files
import pipeline.libs.serializer as serializer

def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def human_sort(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=natural_keys)
    return l


def validation_no_special_chars(string):
    m = re.match("^[a-zA-Z0-9_]*$", string)
    if not m:
        return False
    else:
        if string != '':
            return True
        else:
            return False


def stageDir(dir):
    if os.path.exists(dir):
        if os.path.isfile(os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json"))):
            '''
            further verify if the stage.json file is actually related to the path
            '''
            j = serializer.Metadata_file(path=os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json")))
            info = j.data_file.read()
            if info:
                typeInfo = info["typeInfo"]
                if typeInfo == cfg._stage_:
                    return True

    return False


def dir_verify(dir, type):
    if os.path.exists(dir):
        if os.path.isfile(os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json"))):
            '''
            further verify if the stage.json file is actually related to the path
            '''
            j = serializer.Metadata_file(path=os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json")))
            info = j.data_file.read()
            if info:
                typeInfo = info["typeInfo"]
                if typeInfo == type:
                    return True

    return False

def catagory_dir(dir):
    return dir_verify(dir, cfg._catagory_)

def branch_dir(dir):
    return dir_verify(dir, cfg._branch_)

def component_dir(dir):
    return dir_verify(dir, cfg._component_)

def json_status(path):
    try:
        info = serializer.Metadata_file(path=path).data_file.read()
        # if info["status"] == cfg._approved_:
        return info["status"]
    except:
        return False


def assetDir(dir):
    if os.path.exists(dir):
        if os.path.isfile(os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json"))):
            '''
            further verify if the asset.json file is actually related to the path
            '''
            j = serializer.Metadata_file(path=os.path.join(dir, "%s.%s" % (os.path.split(dir)[1], "json")))
            info = j.data_file.read()
            if info:
                typeInfo = info["typeInfo"]
                if typeInfo == cfg._asset_:
                    return True

    return False


def set_padding(int, padding):
    return str(int).zfill(padding)


def exctract_current_file_elements(file, project, master=True, from_dresser_tree=True):
    name = files.file_name_no_extension(files.file_name(file))
    elements = name.split("_")

    if cfg.enable_undercore_for_asset_names:
        relative_path = files.relpath_wrapper(file, project.path)
        depth_folders = files.splitall(relative_path)  # exctract_current_path_levels( file, self.project.path)

        '''THIS WILL GIVE ME THE LENGHT OF THE PARTS SEPERATED WITH AN UNDERSCORE BEFORE THE ASSET NAME:
        depth_folder[2:-2] will crop 'assets_lib' and 'assets' from the start, and file name and stage from the end
        Then, i will add 1 for the project prefix'''
        if from_dresser_tree:
            dynamic_length = len(depth_folders[2:-2]) + 1
        else:
            '''HERE WE NEED TO CONSIDE FOR THE PATH NAME THAT INCLUDES THE ASSET NAME, PLUS STAGE, AND NOT THE assets_lib and assets that will not exist when
            coming from the nodes that were generated by the dresser'''
            dynamic_length = len(depth_folders[:-3])

        dynamic_part = name.split("_")[:dynamic_length]
        static_part = "_".join(name.split("_")[dynamic_length:])
        dynamic_part.append(static_part)
        elements = dynamic_part

    return elements


def remap_to_file_convention(elements):  # elements is instance of list
    ''' CORRECT THE ELEMENTS FROM THE DICTIONARY RULES '''
    for key, value in cfg.directory_name_dictionary.iteritems():
        for index, x in enumerate(elements):
            if x == key:
                elements[index] = value
                # [value if x == key else x for x in elements]

    return elements


def remap_to_directory_convention(elements):  # elements is instance of list
    ''' CORRECT THE ELEMENTS FROM THE DICTIONARY RULES '''
    for key, value in cfg.directory_name_file.iteritems():
        for index, x in enumerate(elements):
            if x == key:
                elements[index] = value
                # [value if x == key else x for x in elements]
    return elements


def remap_value(x, oMin, oMax, nMin, nMax):
    # range check
    if oMin == oMax:
        print "Warning: Zero input range"
        return None

    if nMin == nMax:
        print "Warning: Zero output range"
        return None

    # check reversed input range
    reverseInput = False
    oldMin = min(oMin, oMax)
    oldMax = max(oMin, oMax)
    if not oldMin == oMin:
        reverseInput = True

    # check reversed output range
    reverseOutput = False
    newMin = min(nMin, nMax)
    newMax = max(nMin, nMax)
    if not newMin == nMin:
        reverseOutput = True

    portion = (x - oldMin) * (newMax - newMin) / (oldMax - oldMin)
    if reverseInput:
        portion = (oldMax - x) * (newMax - newMin) / (oldMax - oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result

def version_string(version):
    ver_strings = [str(i) for i in version]
    return ".".join(ver_strings)