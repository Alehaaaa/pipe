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

# import ast
import base64

def encode64(string):
    return base64.b64encode(string)


def decode64(string):
    return base64.b64decode(string)


# def decode_strings():
#     strings = []
#     strings.append(decode64(encoded_strings()[0]))
#     strings.append(decode64(encoded_strings()[1]))
#     strings.append(decode64(encoded_strings()[2]))
#     strings.append(decode64(encoded_strings()[3]))
#     strings.append(decode64(encoded_strings()[5]))
#     strings.append(ast.literal_eval(decode64(encoded_strings()[7])))
#     return strings
#
#
# def encoded_strings():
#     # snowball pipeline version
#     return ['cHJvamVjdHNfdG9vbHRpcF9sYWJlbA==',
#             'cHJvamVjdHNfdG9vbHRpcF93aWRnZXQ=',
#             'c2V0VGV4dA==',
#             'c2V0SGlkZGVu',
#             'Tm9uIGNvbW1lcmNpYWwgdmVyc2lvbiBvZiBwaXBlbGluZQ==',
#             'UGlwZWxpbmUgfCBTbm93YmFsbCBidWlsZA==',
#             'VHJ1ZQ==',
#             'RmFsc2U=']

    # NFR pipeline version
    # return ['cHJvamVjdHNfdG9vbHRpcF9sYWJlbA==',
    #         'cHJvamVjdHNfdG9vbHRpcF93aWRnZXQ=',
    #         'c2V0VGV4dA==',
    #         'c2V0SGlkZGVu',
    #         'Tm9uIGNvbW1lcmNpYWwgdmVyc2lvbiBvZiBwaXBlbGluZQ==',
    #         'TkZSIHZlcnNpb24gb2YgUGlwZWxpbmU=',
    #         'VHJ1ZQ==',
    #         'RmFsc2U=']