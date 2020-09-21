'''
this is a script to generate a markdown view of the diy resources stored in our wasibi static object store.

to run this script have python installed plus the aws package (pip3 install boto3)

then run it while setting the access_key and secret: AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=YYY python3 generate_wiki_from_bucket.py
'''

import boto3
import urllib.parse

s3 = boto3.resource('s3', endpoint_url='https://s3.eu-central-1.wasabisys.com')


my_bucket = s3.Bucket('scanlines-other')

with open("Output.txt", "w") as text_file:
    text_file.write("# DIY RESOURCES\n")

    for index, my_bucket_object in enumerate(my_bucket.objects.all()):
        # print(my_bucket_object.key.split('/'))
        folder_split = my_bucket_object.key.split('/')
        if folder_split[-1] == '':
            if index > 0:
                text_file.write('</details>')
            path = '/'.join(folder_split[1:-1])
            print('Header: ', path)
            text_file.write(f"\n<details><summary>{path}</summary>\n\n")
        elif '.' in folder_split[-1]:
            path = '/'.join(folder_split[2:])
            text_file.write(f" - [{path}](https://s3.eu-central-1.wasabisys.com/scanlines-other/{urllib.parse.quote(my_bucket_object.key)})\n")
            print('File: ', '/'.join(folder_split[1:]))
        else:
            print('dunno what: ', folder_split)
    text_file.write('</details>')
