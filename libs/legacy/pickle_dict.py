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
import pickle
import json
import logging

logger = logging.getLogger(__name__)

class pickleDict():
    def __init__(self, **kwargs):

        '''
        pickle file Class
        @input:
            **keyword args:
                path(string): path to file
        @retun: class object of the file
        '''


        self.path = None
        self.data = None
        for key in kwargs:
            if key == "path":
                self.path = kwargs[key]

    def create(self, path, data):
        '''
        Create's a pickle file and stores a dict in it
        @input:
            *args:
                path(string): path to new file
                data(dict): data to create in file
        @retun: class object of the file
        '''
        if not os.path.isfile(path):
            self.path = path
            with open(path, "w") as pickleFile:
                pickle.dump(data, pickleFile)
            return self
        else:
            raise ValueError('cant overwrite files')

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
            with open(path, "r+") as pickleFile:
                if args:
                    data = pickle.load(pickleFile)
                    for a in args:
                        if a in data:
                            del data[a]

                    pickleFile.seek(0)
                    pickleFile.truncate()
                    pickle.dump(data,pickleFile)
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
            with open(path, "r+") as pickleFile:
                if args:
                    try:
                        data = pickle.load(pickleFile)
                    except:
                        data = {}

                    for a in args:
                        for key in a:
                            if key in data:
                                del data[key]
                                data[key] = a[key]
                            else:
                                data[key] = a[key]

                    pickleFile.seek(0)
                    pickleFile.truncate()
                    pickle.dump(data,pickleFile)
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
        if os.path.isfile(path):
            with open(path, "r") as pickleFile:
                if args:
                    data = {}
                    for a in args:
                        try:
                            data[a] = pickle.load(pickleFile)[a]
                        except:
                            print "no key in file"
                else:
                    try:
                        data = pickle.load(pickleFile)
                    except:
                        print "file is empty"

                try:
                    return data
                except:
                    print "no data was read"
        else:
            raise ValueError( ' file dose not exists ')
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
