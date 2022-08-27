import os
import glob
import json
import pathlib
import shutil

florig = glob.glob('./a.json')

dumppath = 'D:\\Games\\Nox\\share\\ImageShare\\files\\dat'
snddir = 'E:\\OneDrive\\Documents\\Codes\\um_db\\sound'

for (j, fid) in enumerate(florig):
    fname = pathlib.Path(fid).stem
    fid_orig = open(fid, 'r', encoding='utf-8') 
    metadata = json.load(fid_orig)
    fid_orig.close()

    sndlist = []

    for k, meta in enumerate(metadata):
        if 'sound/b/' in meta['n'] or 'sound/l/' in meta['n']:
            sndlist.append(meta)

    for m, sndinfo in enumerate(sndlist):
        target = os.path.join(dumppath, sndinfo['h'][0:2], sndinfo['h'])
        destination = os.path.join(snddir, sndinfo['n'].split('/')[-1])

        shutil.copy(target, destination)

    d = 1