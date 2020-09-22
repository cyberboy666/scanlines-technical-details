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


def add_to_this_folder(current_subsytem, path):
    if len(path) == 1:
        # if end of path list then it is a file. add this file to the filesystem
        if path[0]:
            current_subsytem.append(('file', f'<a target="_blank" href="https://s3.eu-central-1.wasabisys.com/scanlines-other/{urllib.parse.quote(my_bucket_object.key)}">{path[0]}</a>'))
    else:
        # if not end of path list then it is a folder, check if the folder is already in the file system:
        if not any(True for item in current_subsytem if item[0] == path[0]):
            # if the folder is not in the file system add it now
            current_subsytem.append((path[0], []))

        # jump into this folder for the next item in the path list
        next_subsystem = [item[1] for item in current_subsytem if item[0] == path[0]][0]
        add_to_this_folder(next_subsystem, path[1:])

def convert_object_to_markdown(file_system):
    # write the files system object into markdown recursively
    for item in file_system:
        if item[0] == 'file':
            # if item is a file then add a new list element
            text_file.write(f'<li>{item[1]}</li>\n')
        else:
            # otherwise if item is a folder add a new detail element and add content of this folder inside it
            text_file.write(f'<li><details><summary>{item[0]}</summary><ul>')
            convert_object_to_markdown(item[1])
            text_file.write(f'</ul></details></li>\n')

file_system = []
all_objects = [obj for obj in my_bucket.objects.all()]

# generate the file system recusively
for my_bucket_object in all_objects:
    path = my_bucket_object.key.split('/')
    add_to_this_folder(file_system, path)

print('\n\nfile_system: ', file_system)
# skip the first folder (diy resources)
file_system = file_system[0][1]

# convert to markdown and write to file
with open("Output.txt", "w") as text_file:
    text_file.write(f'# DIY RESOURCES\n\n')
    text_file.write("<ul>")
    convert_object_to_markdown(file_system)
    text_file.write("</ul>")
