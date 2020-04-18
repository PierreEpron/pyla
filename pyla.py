import numpy as np
import pandas as pd
from skimage import io, img_as_ubyte, color, exposure
import os
from pathlib import Path

def get_meta(name):
    #       Cam n°   Year       Month      Day         Hour         Min 
    return [name[3], name[4:6], name[6:8], name[8:10], name[10:12], name[12:14]]
    
def get_sums(px):
    return np.array([px[:,:,0].sum(), px[:,:,1].sum(), px[:,:,2].sum()])

def get_pc(px):
    tot = px[:,:,0] + px[:,:,1] + px[:,:,2]
    return np.array([
        np.ma.log(px[:,:,0] / tot).sum(),
        np.ma.log(px[:,:,1] / tot).sum(),
        np.ma.log(px[:,:,2] / tot).sum()
    ])

def get_ex(px):
    return np.array([
        (2 * px[:,:,0] - px[:,:,1] - px[:,:,2]).sum(),
        (2 * px[:,:,1] - px[:,:,0] - px[:,:,2]).sum(),
        (2 * px[:,:,2] - px[:,:,0] - px[:,:,1]).sum()
    ])

def get_nd(px):
    return np.array([
        np.ma.fix_invalid((px[:,:,0] - px[:,:,1]) / (px[:,:,0] + px[:,:,1]), fill_value=0).sum(),
        np.ma.fix_invalid((px[:,:,0] - px[:,:,2]) / (px[:,:,0] + px[:,:,2]), fill_value=0).sum(),
        np.ma.fix_invalid((px[:,:,1] - px[:,:,2]) / (px[:,:,1] + px[:,:,2]), fill_value=0).sum()
    ])

def make_csv(dir_path):
    bbox = (10, 10, 1910, 1070)
    rows = []
    for root, dirs, files in os.walk(dir_path):
        i = 0
        for file in files:
            try:
                img_path = Path(os.path.join(root, file))
                img = img_as_ubyte(io.imread(img_path))[bbox[1]:bbox[3],bbox[0]:bbox[2],:].astype(int)
                img_hsv = (color.rgb2hsv(img) * (359, 100, 100)).astype(int)
                c = img.shape[0] * img.shape[1]
                rgb = get_sums(img)
                hsv = get_sums(img_hsv)
                rows.append(
                    get_meta(img_path.name) +
                    list(rgb / c) + list(hsv / c) + [rgb.sum() / c] +
                    list(get_pc(img) / c) +
                    list(get_ex(img) / c) +
                    list(get_nd(img) / c)
                )
                print('%s/%s done'%(i, len(files)))
                i += 1
            except Exception as e:
                print(file)
                print(e)
    pd.DataFrame(
        rows, 
        columns=
        [
            'cam', 'year', 'month', 'day', 'hour', 'min',
            'r', 'g', 'b', 'h', 's', 'v', 'tot', 
            'r_pc', 'g_pc', 'b_pc', 
            'r_ex', 'g_ex', 'b_ex',
            'n_rg_d', 'n_rb_d', 'n_gb_d'
        ]).to_csv('%s.csv'%dir_path.split('/')[-1], ';', index=False, encoding='utf-8')


# r_hist = exposure.histogram(img[bbox[0]:bbox[2],bbox[1]:bbox[3],0])
# g_hist = exposure.histogram(img[bbox[0]:bbox[2],bbox[1]:bbox[3],1])
# b_hist = exposure.histogram(img[bbox[0]:bbox[2],bbox[1]:bbox[3],2])

# h_hist = exposure.histogram(img_hsv[bbox[0]:bbox[2],bbox[1]:bbox[3],0])
# s_hist = exposure.histogram(img_hsv[bbox[0]:bbox[2],bbox[1]:bbox[3],1])
# v_hist = exposure.histogram(img_hsv[bbox[0]:bbox[2],bbox[1]:bbox[3],2])

make_csv('img/lila_2015')
make_csv('img/lila_2014')
make_csv('img/lila_2016') 
make_csv('img/lila_2017')  
make_csv('img/lila_2018') 