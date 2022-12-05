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
import string
import random
import json
import logging


logger = logging.getLogger(__name__)

import pipeline.libs.encryption as encryption

class JSONSerializer(object):
    
    
    def __init__(self, **kwargs): 

        '''
        json file Class
        @input: 
            **keyword args:
                path(string): path to file
        @retun: class object of the file
        '''

        self.path = None
        self.data = None
        self.encrypted = False

        for key in kwargs:
            if key == "path":
                self.path = kwargs[key]
            if key == "encrypted":
                self.encrypted = kwargs[key]
    '''
    @property
    def path(self):
        if self.path:
            return self.path  
    '''
    def create(self, path, data, force=False):
        '''
        Create's a json file and stores a dict in it
        @input: 
            *args:
                path(string): path to new file
                data(dict): data to create in file
        @retun: class object of the file
        '''

        # logger.info("<>")


        if not self.encrypted:
            if not os.path.isfile(path):
                self.path = path
                with open(path, "w") as jsonFile:
                    json.dump( data, jsonFile,  indent=4, sort_keys=True)
                return self
            else:
                if force:
                    self.path = path
                    with open(path, "w") as jsonFile:
                        json.dump(data, jsonFile, indent=4, sort_keys=True)
                    return self
                else:

                    data = JSONSerializer(path = path)
                    return data
                # raise ValueError('cant overwrite files')
                # logger.info("file already exists")
                # return False

        else:
            self.path = path
            string = json.dumps( data, indent=4, sort_keys=True)
            # logger.info(string)
            e_string = encryption.encode64(string)
            hex_string = e_string.encode("hex")
            # logger.info(hex_string)

            with open(path, "w") as jsonFile:
                jsonFile.write(hex_string)
                jsonFile.close()

            # logger.info("<>")
            logger.info(self)
            return self

    def remove_key(self, *args, **kwargs):
        '''
        Remove's a key from the file
        @input: 
            **keyword args:
                path(string): path to new file
            *args:
                keys (dict keys): keys to remove if exists
                
        @retun: class object of the file
        '''
        path = self.path
        for key in kwargs:
            if key == "path":
                path = kwargs[key]
                
        if os.path.isfile(path):
            with open(path, "r+") as jsonFile:
                if args:
                    data = json.load(jsonFile)
                    for a in args:
                        if a in data:                                                                
                            del data[a]
                                
                    jsonFile.seek(0)                    
                    jsonFile.truncate()    
                    json.dump( data, jsonFile,  indent=4, sort_keys=True)   
            return self            
        else:
            raise ValueError( ' file dose not exists ')
            
            
            
    def edit(self,*args,**kwargs):
        '''
        Edit key's values, if the key is not on the file it wold be added.
        @input: 
            **keyword args:
                path(string): path to new file
            *args:
                dicts(dict): dictioneries to add to file, if a dict exists in the file it would be overwritten
                
        @retun: class object of the file
        '''
        path = self.path
        for key in kwargs:
            if key == "path":
                path = kwargs[key] 

        if os.path.isfile(path):
            self.path = path
            with open(path, "r+") as jsonFile:
                if args:
                    try:
                        data = json.load(jsonFile)
                    except:
                        data = {}
                        
                    for a in args:
                        for key in a:
                            if key in data:                                                                
                                del data[key]
                                data[key] = a[key]
                            else:
                                data[key] = a[key]
                                
                    jsonFile.seek(0)                    
                    jsonFile.truncate()    
                    json.dump( data, jsonFile,  indent=4, sort_keys=True)  
            return self
        else:
            raise ValueError ('file dose not exists')
            
    def read(self, *args, **kwargs):
        '''
        Read all the file, if given keys will return only them
        @input: 
            **keyword args:
                path(string): path to new file
            *args:
                keys(dict keys): keys to read from the file
                
        @retun: data(dict)
        '''
        
        #print "READ CALL: ", self
        
        path = self.path
        for key in kwargs:
            if key == "path":
                path = kwargs[key]        
        #if path:   


        if not self.encrypted:
            if os.path.isfile(path):
                with open(path, "r") as jsonFile:
                    if args:
                        data = {}
                        for a in args:
                            try:
                                data[a] = json.load(jsonFile)[a]
                            except:
                                print "no key in file"
                    else:
                        try:
                            data = json.load(jsonFile)
                        except:
                            print "file is empty"

                    try:
                        return data
                    except:
                        print "no data was read"
            else:
                raise ValueError( ' file dose not exists ')
        else:
            if os.path.isfile(path):
                with open(path, "r") as jsonFile:
                    e_string = jsonFile.read()
                    try:
                        normal_string = e_string.decode("hex")

                        jsonFile.close()
                        # logger.info(e_string)

                        string = encryption.decode64(normal_string)
                        # logger.info(string)

                        return json.loads(string)
                    except:
                        logger.info("error reading file")
                        return {}
                    # logger.info("hello".encode("hex"))
                    # '68656c6c6f'
                    # logger.info("68656c6c6f".decode("hex"))
                    # 'hello'


        #else:
        #    raise ValueError ( ' path to file is needed ' )


    def clear(self):
        '''
        Clear the file
        @input: None
        @retun: None
        '''
        if self.path:
            if os.path.isfile(self.path):
                with open(path, "w") as file:
                    pass

    def print_nice(self):
        try:
            return json.dumps(self.read(),indent=2)
        except:
            import logging
            logging.info("can't print the data file")
                  


            
def edit_key(dict = None ,key = None ,value = None):
    
    if key in dict:                                                                
        del dict[key]
        dict[key] = value
        
        return dict
    else:
        return None
        
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Metadata_file(object):
    def __init__(self, **kwargs):

        self.data_file = None
        self.data_file_path = None
        self.encrypted = False

        for key in kwargs:
            if key == "path":
                self.data_file_path = os.path.join(kwargs[key])
            if key == "encrypted":
                self.encrypted = kwargs[key]

        if self.data_file_path:
            self.set_data_file(self.data_file_path)

    def set_data_file(self, path):
        if os.path.isfile(path):
            self.data_file = JSONSerializer(path=path, encrypted = self.encrypted)

            return True
        else:
            pass