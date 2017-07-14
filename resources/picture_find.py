import os
from shutil import copyfile

base_path = './taikotemp/inner/data.000'
extract_path = './taikotemp/just_pics'

if not os.path.exists(extract_path):
    os.mkdir(extract_path)

pic_files = [os.path.join(dirpath, f)
             for dirpath, _, files in os.walk(base_path)
             for f in files if f.endswith('.ntf')]

for pf in pic_files:
    new_fname = pf[len(base_path) + 1:].replace(os.sep, '__')
    copyfile(pf, os.path.join(extract_path, new_fname))
