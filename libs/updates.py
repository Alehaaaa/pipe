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
import threading

import pipeline

import pipeline.maya_libs.maya_qt as maya_qt
import pipeline.libs.requests as requests
import pipeline.libs.ehp.ehp as ehp
import pipeline.apps.update_window as update_window
import pipeline.libs.misc as misc



logger = logging.getLogger(__name__)



class Update_checker(object):

    LOOKING = "Connecting to pipeline server..."
    NO_CONNECTION = "There is no internet connection"
    NO_RESPOSE = "No response from the pipeline server"
    UP_TO_DATE = "No updates available, your version is up to date"
    LIGHT_BLUE = "#077fff"
    link = '''<font color=''' + LIGHT_BLUE + '''>pipeline.nnl.tv</font>'''
    UPDATE_AVILABLE = "A new version of pipeline is available! go get it at " + link#pipeline.nnl.tv"

    result_no_connection = 0
    result_no_response = 1
    result_no_update = 2
    result_new_update = 3

    def __init__(self, current_version):


        self.response_massage = Update_checker.LOOKING
        self.results = Update_checker.result_no_update
        self.server_version = None
        self.current_version = current_version

    def compare(self):
        if self.server_version:
            new = self.server_version
            current = self.current_version
            update = False

            if new[0] > current[0]:
                update = True

            if new[1] > current[1]:
                update = True

            if new[2] > current[2]:
                update = True


            if new[0] == current[0] and new[1] == current[1] and new[2] == current[2]:
                if len(new) < len(current):
                    update = True

            if update:
                self.results = Update_checker.result_new_update
                self.response_massage = "{} {} {}".format(Update_checker.UPDATE_AVILABLE, "The latest version is", misc.version_string(new) )

            else:
                self.results = Update_checker.result_no_update
                self.response_massage = Update_checker.UP_TO_DATE

        else:
            self.response_massage = Update_checker.NO_RESPOSE
            self.results = Update_checker.result_no_response

        return


    def find_version(self, html):
        try:
            dom = ehp.Html().feed(html)

            for ind in dom.match(('id', 'version')):
                ver = ind.text()
                ver_elements = ver.split(".")

                '''
                version can be in 3 or 4 items long, and if it's 4 items the last one needs to be a string
                '''

                if len(ver_elements) == 3:

                    self.server_version = [int(i)for i in ver_elements]

                elif len(ver_elements) == 4:

                    items = [int(ver_elements[i])for i in range(0,3)]
                    items.append(ver_elements[-1])

                    self.server_version = items

        except:

            return None


    def check(self):

        try:
            response = requests.get('https://liorbenhorin.github.io/pipeline_server/', timeout=2)

            if response.status_code == 200:

                self.find_version(response.content)
                self.compare()
                return

            else:
                self.response_massage = Update_checker.NO_RESPOSE
                self.results = Update_checker.result_no_response
                return

        except (requests.ConnectionError, requests.HTTPError, requests.Timeout):

            self.response_massage = Update_checker.NO_CONNECTION
            self.results = Update_checker.result_no_connection

            return


class Update_check_thread(threading.Thread):

    def __init__(self, silent = True):
        threading.Thread.__init__(self)

        self.silent = silent
        self.dispay = update_window.Update_window(maya_qt.maya_main_window())
        self.query = Update_checker(pipeline.__version__)
        # self.dispay.ok.clicked.connect(self.join)

        if not silent:
            self.dispay.show_with_massage(self.query.response_massage)

    def run(self):
        # print 'update thread'
        # logger.info("Checking for updates...")
        try:
            self.query.check()

            if (not self.silent) or (self.query.results == Update_checker.result_new_update):

                '''
                Has to be a batter way to show this only if the window was not closed by the user earlier...
                '''
                try:
                    self.dispay.dismiss_label()
                    self.dispay.show_with_massage(self.query.response_massage)
                except:
                    pass

        except Exception,err:
            # print err
            logger.info(err)
            return None



