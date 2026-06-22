import numpy as np
from scipy import stats
from time import time
import os
import re
from pathlib import Path

directory = Path(__file__).resolve().parent
directory_complete_distributions = directory.parent/"complete_distributions/"
directory_generation = directory


def distribucion_experimental(filepath):
	"""
	Esta función construye la distribución de probabilidad resultante de todos 
	los conteos de números de fotones realizados experimentalmente
	"""
	with open(filepath,'r') as file:
		distb = file.readline().split()
		P = {i:float(distb[i]) for i in range(len(distb))}
		return P


def variable_aleatoria_experimental(filepath):
	"""
	Esta función genera una variable aleatoria a partir de la distribución
	de número de fotones obtenida del experimento
	"""
	distb = distribucion_experimental(filepath)
	ns = list(distb.keys())
	Ps = [distb[n] for n in ns]
	return stats.rv_discrete(values=(ns,Ps))


def obtener_Pn_incompleta(variable_aleatoria, realizaciones=10000, n_limite=10):
	"""
	Esta función crea una distribución incompleta a partir de un conjunto
	de realizaciones de una distribución completa, obtenida del experimento,
	construyendo las probabilidades de forma frecuentista.
	"""
	ocurrencias = list(variable_aleatoria.rvs(size=realizaciones))
	P_incompleta = {}
	for n in range(n_limite+1):
		P_incompleta[n] = ocurrencias.count(n)/realizaciones
	return P_incompleta


def leer_parametros(filepath):

	patron = r'(\d\.\d{2})_(\d\.\d{2}).txt$'
	nbar, g2 = re.search(patron, filepath).groups()
	return nbar, g2


def generar_distbs_para_DB(filepath, realizaciones, dic_num_distbs_por_rlzs={},
						   n_limite=10, directory_DB=directory_generation):
	"""
	Esta función crea un documento de texto donde cada renglón corresponde
	a una distribución incompleta de número de fotones.
	Las columnas del documento corresponden a las probabilidades P(n)
	"""
	default_dic_num_distbs_por_rlzs = { rlzs:10000 for rlzs in realizaciones }
	num_distbs_por_rlzs = { **default_dic_num_distbs_por_rlzs, **dic_num_distbs_por_rlzs }

	nbar, g2 = leer_parametros(str(filepath))
	X = variable_aleatoria_experimental(filepath)

	for rlzs in realizaciones:

		generated_filepath = directory_DB/f"{nbar}_{g2}_{rlzs}.txt"

		with open(generated_filepath, "a") as outfile:

			contador = 0
			for i in range(num_distbs_por_rlzs[rlzs]):
				contador += 1

				distb_incompleta = obtener_Pn_incompleta(X, rlzs, n_limite)

				for n in range(n_limite+1):
					if n in distb_incompleta.keys():
						outfile.write( f"{distb_incompleta[n]}\t" )
					else:
						outfile.write( f"{0}\t" )

				outfile.write("\n")

				if contador==1000:
					contador = 0
					outfile.flush()
					os.fsync(outfile.fileno())

		print(f"Éxito al escribir archivo para nbar~{nbar} , g2~{g2}, rlzs={rlzs}.")

	return generated_filepath



filepaths_complete_distributions = {}

for file in os.listdir(directory_complete_distributions):
	
	filepath = directory_complete_distributions/Path(file)

	if filepath.suffix=='.txt':

		nbar, g2 = leer_parametros(filepath.name)

		if float(nbar)<=1.5:

			if (nbar,g2) not in filepaths_complete_distributions.keys():
				filepaths_complete_distributions[(nbar,g2)] = [filepath]
			else:
				filepaths_complete_distributions[(nbar,g2)].append(filepath)

parametros_mediciones = tuple( filepaths_complete_distributions.keys() )