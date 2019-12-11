import os, sys, colorsys, json, time, datetime, logging, csv
from PIL import Image
from PIL import ImageFile
from pathlib import *
ImageFile.LOAD_TRUNCATED_IMAGES = True

def setup_logger():
	logger = logging.getLogger('pyla')
	logger.setLevel(logging.DEBUG)

	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	fh = logging.FileHandler('pyla.log')
	fh.setLevel(logging.DEBUG)
	
	formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
	
	ch.setFormatter(formatter)
	fh.setFormatter(formatter)

	logger.addHandler(ch)
	logger.addHandler(fh)

	return logger
logger = setup_logger()

def compute(imnames, bbox, hsl_state, to_path):
	if imnames == None:
		return None
	logger.info('Start computing images at %s.'%(to_path))
	begin_time = time.clock()
	data = []
	for i in range(0, len(imnames)):
		data.append([])
		setup_data(data)
		set_meta(data, imnames[i].stem)
		im = Image.open('%s'%(str(imnames[i])))
		logger.info('Start computing %s :: %s/%s'%(imnames[i], i + 1, len(imnames)))
		for x in range(bbox[0], bbox[2]):
			for y in range(bbox[1], bbox[3]):
				rgb = im.getpixel((x, y))
				compute_rgb(data, rgb)
				if hsl_state:
					compute_hsl(data, rgb)
				compute_tot(data, rgb)
				compute_pc(data, rgb)
				compute_ex(data, rgb)
				compute_nd(data, rgb)
		scale_means(data, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
	end_time = time.clock() - begin_time
	logger.info('End in %ssc. %ssc by img.'%(datetime.timedelta(seconds = end_time), datetime.timedelta(seconds = end_time/len(imnames))))
	save_json(to_path, data)
	save_csv(to_path, data)

def setup_data(data):
	# META
	data[-1].append([])
	# HIST
	hist = []
	hist.append([0] * 360) # R
	hist.append([0] * 360) # V
	hist.append([0] * 360) # B
	hist.append([0] * 360) # H
	hist.append([0] * 360) # S
	hist.append([0] * 360) # L
	data[-1].append(hist)
	# MEANS
	data[-1].append([0] * 16)
def set_meta(data, name):
	data[-1][0].append(name[3])		# Cam n°
	data[-1][0].append(name[4:6])	# Year
	data[-1][0].append(name[6:8])	# Month
	data[-1][0].append(name[8:10])	# Day
	data[-1][0].append(name[10:12])	# Hour
	data[-1][0].append(name[12:14])	# Min

def compute_rgb(data, rgb):
	data[-1][1][0][rgb[0]] += 1
	data[-1][1][1][rgb[1]] += 1
	data[-1][1][2][rgb[2]] += 1
	data[-1][2][0] += rgb[0]
	data[-1][2][1] += rgb[1]
	data[-1][2][2] += rgb[2]
def compute_hsl(data, rgb):
	hsl = colorsys.rgb_to_hls(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
	data[-1][1][3][int(round(hsl[0] * 359))] += 1
	data[-1][1][4][int(round(hsl[2] * 100))] += 1
	data[-1][1][5][int(round(hsl[1] * 100))] += 1
	data[-1][2][3] += hsl[0] * 359
	data[-1][2][4] += hsl[2] * 100
	data[-1][2][5] += hsl[1] * 100
def compute_tot(data, rgb):
	tot = rgb[0] + rgb[1] + rgb[2]
	data[-1][2][6] += tot
def compute_pc(data, rgb):
	tot = rgb[0] + rgb[1] + rgb[2]
	if tot != 0:
		data[-1][2][7] += rgb[0] / tot
		data[-1][2][8] += rgb[1] / tot
		data[-1][2][9] += rgb[2] / tot
def compute_ex(data, rgb):
	data[-1][2][10] +=  2 * rgb[0] - rgb[1] - rgb[2]
	data[-1][2][11] +=  2 * rgb[1] - rgb[0] - rgb[2]
	data[-1][2][12] +=  2 * rgb[2] - rgb[0] - rgb[1]
def compute_nd(data, rgb):
	if rgb[0] + rgb[1] != 0: 	
		data[-1][2][13] += (rgb[0] - rgb[1]) / (rgb[0] + rgb[1])
	if rgb[0] + rgb[2] != 0:	
		data[-1][2][14] += (rgb[0] - rgb[2]) / (rgb[0] + rgb[2])
	if rgb[1] + rgb[2] != 0:	
		data[-1][2][15] += (rgb[1] - rgb[2]) / (rgb[1] + rgb[2])
def scale_means(data, c):
	for i in range(0, len(data[-1][2])):
		if data[-1][2][i] != 0:
			data[-1][2][i] /= c

def meta_tostr(meta):
	s = meta[0]
	for i in range(1, len(meta)):
		s = '%s_%s'%(s, meta[i])
	return s
def save_json(savepath, data):
	with open('%s.json'%(savepath), 'w') as f:
		f.write(json.dumps(data))
	logger.info('Json saved at %s.json.'%(savepath))			
def save_csv(savepath, data):
	row0 = ['date', 'R', 'G', 'B', 'H', 'S', 'L', 'Tot', 'Rpc', 'Gpc', 'Bpc', 'Rex', 'Gex', 'Bex', 'nRGd', 'nRBd', 'nGBd']
	with open('%s_means.csv'%(savepath), 'w', newline='') as f:
		writer = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(row0)
		for i in data:
			writer.writerow([meta_tostr(i[0])] + i[2])
	with open('%s_histogram.csv'%(savepath), 'w', newline='') as f:
		writer = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(row0[:1] + ['value'] + row0[1:7])
		for i in data:
			writer.writerow([meta_tostr(i[0]), 0, i[1][0][0], i[1][1][0], i[1][2][0], i[1][3][0], i[1][4][0], i[1][5][0]])
			for j in range(1, len(i[1][0])):
				writer.writerow([meta_tostr(i[0]), j, i[1][0][j], i[1][1][j], i[1][2][j], i[1][3][j], i[1][4][j], i[1][5][j]])
	logger.info('Means csv saved at %s_means.csv.'%(savepath))
	logger.info('Histogram csv saved at %s_histogram.csv.'%(savepath))			
