'''
this is a script to generate a markdown view of the diy resources stored in our wasibi static object store.

to run this script have python installed plus the aws package (pip3 install boto3)

then run it while setting the access_key and secret: AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=YYY python3 generate_wiki_from_bucket.py
'''

import boto3
import urllib.parse
import os

s3 = boto3.resource('s3', endpoint_url='https://s3.eu-central-1.wasabisys.com')
my_bucket = s3.Bucket('scanlines-other')

# generate the file system recusively
file_system = []

def dict_at_this_slice(current_subsystem, slice_list):
    # find the subsystem of the file system by searching through with a slice list
    if len(slice_list) == 0 or len(current_subsystem) == 0:
        # if at end of the list or empty then return
        return current_subsystem
    # the next level is found based on first item in the slice list
    next_subsystem = [item[1] for item in current_subsystem if item[0] == slice_list[0]][0]
    if len(slice_list) == 1:
        # if we are now at the end of slice list then return this subsystem
        return next_subsystem
    else:
        # otherwise go deeper into in as per the slice list
        return dict_at_this_slice(next_subsystem, slice_list[1:])

def add_to_this_folder(path_beginning, path):
    # use the path_beginning list to seek to current subsystem
    current_depth = dict_at_this_slice(file_system, path_beginning)
    if len(path) == 1:
        # if end of path list then it is a file. add this file to the filesystem
        if path[0]:
            current_depth.append(('file', f'<a target="_blank" href="https://s3.eu-central-1.wasabisys.com/scanlines-other/{urllib.parse.quote(my_bucket_object.key)}">{path[0]}</a>'))
    else:
        # if not end of path list then it is a folder, check if the folder is already in the file system:
        if not any(True for item in current_depth if item[0] == path[0]):
            # if the folder is not in the file system add it now
            current_depth.append((path[0], []))

        # this folder is added to the path_beggining and we enter next the recursive layer (for the next item in after this folder in the path list)
        path_beginning.append(path[0])
        add_to_this_folder(path_beginning, path[1:])

def convert_object_to_markdown(file_system):
    for item in file_system:
        if item[0] == 'file':
            text_file.write(f'<li>{item[1]}</li>\n')
        else:
            text_file.write(f'<li><details><summary>{item[0]}</summary><ul>')
            convert_object_to_markdown(item[1])
            text_file.write(f'</ul></details></li>\n')

all_objects = [obj for obj in my_bucket.objects.all()]

for my_bucket_object in all_objects:
    path = my_bucket_object.key.split('/')
    add_to_this_folder([], path)
print('file_system: ', file_system)
# jump into the first folder (diy resources)
file_system = file_system[0][1]

with open("Output.txt", "w") as text_file:
    text_file.write(f'# DIY RESOURCES\n\n')
    text_file.write("<ul>")
    convert_object_to_markdown(file_system)
    text_file.write("</ul>")

