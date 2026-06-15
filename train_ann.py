import numpy as np
import pandas as pd
from matplotlib.pyplot import *
from time import time
import os
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
import gc
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


def leer_linea_doc_DB(linea, n_limite=10):
    
    valores = linea.split()

    if n_limite>len(valores)-1:
        raise ValueError(f"La base de datos solo cuenta valores de P(n) desde n=0 hasta n={len(valores)-1:d}")
    
    distb_incompleta = {}

    for n in range(n_limite+1):
        distb_incompleta[f'P({n:d})'] = float(valores[n])
    
    return distb_incompleta


def leer_varias_lineas_doc_DB(num_lineas, nbar, g2, realizaciones, linea_inicio=0, n_limite=10,
                              delta_nbar=0.005, delta_g2=0.005, nbar_err=0.01, g2_err=0.01,
                              directory="data_generation/incomplete_distributions/"):

    nbars = [nbar]; g2s = [g2]
    delta = nbar_err
    while delta<=delta_nbar:
        nbars.append( nbar-delta)
        nbars.append( nbar+delta)
        delta += nbar_err
    delta = g2_err
    while delta<=delta_g2:
        g2s.append( g2-delta)
        g2s.append( g2+delta)
        delta += g2_err

    datos = []

    for nbarp in nbars:
        for g2p in g2s:

            filename = f"{nbarp:.2f}_{g2p:.2f}_{realizaciones:d}.txt"
            try:

                with open(directory+filename, "r") as file:
        
                    contador = 0
                    for i, linea in enumerate(file):
                        if i<linea_inicio:
                            continue
                        try:
                            distb_incompleta = leer_linea_doc_DB(linea, n_limite)
                        except ValueError:
                            print(f"ERROR DE FORMATO en la línea {linea} de {filename}.")
                        distb_incompleta['nbar'] = float(nbarp)
                        distb_incompleta['g2'] = float(g2p)
                        distb_incompleta['realizaciones'] = int(realizaciones)
                        datos.append( distb_incompleta )
                        contador += 1
                        if contador==num_lineas:
                            return datos
        
                print(f"Se solicitó leer la línea {linea_inicio+num_lineas-1:d} pero el documento correspondiente a  nbar={nbarp:.2f} , g2={g2p:.2f} , realizaciones={realizaciones:d} solo llega hasta la línea {linea_inicio+contador-1:d}.")
                return datos
            
            except FileNotFoundError:
                print(f"No se encontró archivo para nbar={nbarp:.2f} , g2={g2p:.2f} , rlzs = {realizaciones:d}")


posibles_nbar = np.arange(0.5,1.51,0.01)
posibles_g2 = np.arange(0.01,4.1,0.01)

directory = "data_generation/complete_distributions/"

g2s_para_cada_nbar = {}
for nbar in posibles_nbar:

    g2s = []
    
    for g2 in posibles_g2:
        
        try:
            with open(directory+f"{nbar:.2f}_{g2:.2f}.txt", "r") as outfile:
                g2s.append( round(g2,2) )
        
        except FileNotFoundError:
            pass

    if len(g2s)>0:
        g2s_para_cada_nbar[round(nbar,2)] = g2s

nbars = list( g2s_para_cada_nbar.keys() )


# -----HERE IS WHERE TRAINING STARTS----------


# ---First, the MinMax scaler is fit

num_distbs_por_parametro_por_batch = 500
num_distbs_por_archivo_en_db = 10_000
num_batches = num_distbs_por_archivo_en_db//num_distbs_por_parametro_por_batch
realizaciones = [c*1_000 for c in range(5,10)]+[c*10_000 for c in range(1,10)]+[100_000]

scaler = MinMaxScaler()
contador = 0

for num_batch in range(num_batches):

    t1 = time()

    datos = []
    gc.collect()

    for nbar in nbars:
        g2s = g2s_para_cada_nbar[nbar]
        for g2 in g2s:
            for rlzs in realizaciones:
                datos.append(
                    pd.DataFrame(
                        leer_varias_lineas_doc_DB(num_distbs_por_parametro_por_batch, nbar, g2, rlzs,
                            linea_inicio=contador
                            )
                    ,dtype=np.float32)   
                )
        
    datos = pd.concat(datos, axis=0)
    datos = datos.sample(frac=1, ignore_index=True)
    X = datos.drop(['nbar','g2'], axis='columns')
    scaler = scaler.partial_fit(X)

    t2 = time()
    print(f"batch {num_batch} completado. Pasaron {(t2-t1)/60:.2f} min.")

    contador += num_distbs_por_parametro_por_batch

print("scaler fit has finished.", flush=True)

with open("scaler.pickle", 'wb') as scalers_file:
    pickle.dump(scaler, scalers_file)


# ---Then, the ANN is trained

num_batches = 20
num_layers = (90,80,70)
alpha = 1e-5

regressor = MLPRegressor( activation='relu', solver='adam',
                         hidden_layer_sizes=num_layers,  alpha=alpha)

best_score = -np.inf
patience = 3
wait = 0

for num_batch in range(num_batches):
        
        t1 = time()
    
        datos = []
        gc.collect()
                
        for nbar in nbars:
            g2s = g2s_para_cada_nbar[nbar]
            for g2 in g2s:
                for rlzs in realizaciones:
                    datos.append(
                        pd.DataFrame(
                            leer_varias_lineas_doc_DB(num_distbs_por_parametro_por_batch, nbar, g2, rlzs,
                                linea_inicio=np.random.randint(num_distbs_por_archivo_en_db-num_distbs_por_parametro_por_batch)
                                )
                        ,dtype=np.float32)   
                    )
        
        datos = pd.concat(datos, axis=0)
        datos = datos.sample(frac=1, ignore_index=True)
        X = datos.drop(['nbar','g2'], axis='columns')
        X_scaled = scaler.transform(X)
        y = datos['g2']
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
    
        regressor.partial_fit(X_train, y_train)
    
        y_predicted = regressor.predict(X_test)
        score = -mean_absolute_error(y_test, y_predicted)
        print(f"score:\t{score:.4f}", flush=True)
    
        t2 = time()
        print(f"Entrenamiento para batch {num_batch} completado. Pasaron {(t2-t1)/60:.2f} min.",
              flush=True)

        if score > best_score + 1e-3:
            best_score = score
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                print("Early stopping: el modelo ya no mejora.", flush=True)
                break

with open("regressor.pickle", 'wb') as regressors_file:
    pickle.dump(regressor, regressors_file)