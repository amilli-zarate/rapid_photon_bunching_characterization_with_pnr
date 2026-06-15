#!/usr/bin/env python3

import os
from time import time
from pathlib import Path


def leer_parametros_DB_original(filepath):
    
	params = filepath.split('/')[-1].split('_')[4:]
	r0_y_prcnt = params[0].split('-')
	r0 = r0_y_prcnt[1].split('p')[0]
	prcnt = r0_y_prcnt[2]
	nbar = params[1].split('-')[1]
	g2_y_txt = params[2].split('-')[1]
	g2 = g2_y_txt.split('t')[0][:-1]
	return nbar, g2, r0, prcnt


def distribucion_experimental(filepath):
 
	N_mediciones = 0
	ns = []
	cuentas = {}
    
	with open(filepath) as file:
        
		serie_tiempo = file.read().strip().split(',')
        
		for n in serie_tiempo:
			N_mediciones += 1
			if n not in ns:
				ns.append(n)
				cuentas[n] = 0
			cuentas[n] += 1
        
		P = {}
		for n in sorted(cuentas.keys()):
			P[int(n)] = cuentas[n]/N_mediciones
        
		return P


directory = "experiment_num-clicks_series/"

filepaths_mediciones = {}

for filename in os.listdir(directory):

	file = Path(filename)
	if file.suffix=='.txt':
    
		nbar, g2 = leer_parametros_DB_original(filename)[0:2]
		
		if float(nbar)<=1.5:
			
			filepath = directory + filename
			
			if (nbar,g2) not in filepaths_mediciones.keys():
				filepaths_mediciones[(nbar,g2)] = [filepath]
			else:
				filepaths_mediciones[(nbar,g2)].append(filepath)

parametros_mediciones = tuple( filepaths_mediciones.keys() )


def add_file_DB_distbs_completas(nbar,g2):
    
	with open(f"{nbar}_{g2}.txt", 'w') as outfile:

		for filepath in filepaths_mediciones[(nbar,g2)]:
            
			P = distribucion_experimental(filepath)

			for n in range(max(P.keys())+1):
				if n in P.keys():
					outfile.write(f"{P[n]}\t")
				else:
					outfile.write(f"{0}\t")

			outfile.write("\n")