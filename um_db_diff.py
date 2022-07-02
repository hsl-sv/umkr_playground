import glob
import json
import pathlib

florig = glob.glob('../../20220621/*.json')
flmod = glob.glob('../../20220627/*.json')

diff = lambda l1,l2: [x for x in l1 if x not in l2]

for (j, fid) in enumerate(florig):
    fname = pathlib.Path(fid).stem
    fid_orig = open(fid, 'r', encoding='utf-8') 
    fid_mod = open(flmod[j], 'r', encoding='utf-8')
    j1 = json.load(fid_orig)
    j2 = json.load(fid_mod)
    fid_orig.close()
    fid_mod.close()

    # diff
    if j1 is not None and j2 is not None:
        d1_2 = diff(j1, j2)
        d2_1 = diff(j2, j1)

    with open(fname + '_1_2.txt', 'w', encoding='utf-8') as fid_diff1_2:
        for (i, diff1_2) in enumerate(d1_2):
            fid_diff1_2.write(str(diff1_2) + '\n')

    fid_diff1_2.close()

    with open(fname + '_2_1.txt', 'w', encoding='utf-8') as fid_diff2_1:        
        for (i, diff2_1) in enumerate(d2_1):
            fid_diff2_1.write(str(diff2_1) + '\n')

    fid_diff2_1.close()