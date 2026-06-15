import numpy as np
import os
import pickle
import pandas as pd
from matplotlib.pyplot import *
from time import time


def leer_linea_doc_DB(linea, n_limite=10):
    
    valores = linea.split()

    if n_limite>len(valores)-1:
        raise ValueError(f"La base de datos solo cuenta valores de P(n) desde n=0 hasta n={len(valores)-1:d}")
    
    distb_incompleta = {}

    for n in range(n_limite+1):
        distb_incompleta[f'P({n:d})'] = float(valores[n])
    
    return distb_incompleta


def leer_varias_lineas_doc_DB(num_lineas, nbar, g2, realizaciones, linea_inicio=0, n_limite=10,
                              directory="data_generation/incomplete_distributions/"):
    
    datos = []

    filename = f"{nbar:.2f}_{g2:.2f}_{realizaciones:d}.txt"

    with open(directory+filename, "r") as file:
        
        contador = 0
        for i, linea in enumerate(file):
            if i<linea_inicio:
                continue
            try:
                distb_incompleta = leer_linea_doc_DB(linea, n_limite)
            except ValueError:
                print(f"ERROR DE FORMATO en la línea {linea} de {filename}.")
            distb_incompleta['nbar'] = float(nbar)
            distb_incompleta['g2'] = float(g2)
            distb_incompleta['realizaciones'] = int(realizaciones)
            datos.append( distb_incompleta )
            contador += 1
            if contador==num_lineas:
                return datos

    print(f"Se solicitó leer la línea {linea_inicio+num_lineas-1:d} pero el documento correspondiente a  nbar={nbar:.2f} , g2={g2:.2f} , realizaciones={realizaciones:d} solo llega hasta la línea {linea_inicio+contador-1:d}.")

    return datos  


def leer_parametros(filename):

    params = filename.split('.txt')[0]
    nbar, g2, rlzs = params.split('_')
    return float(nbar), float(g2), int(rlzs)


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


directory = "data_generation/test_distributions/"

parametros_para_tests = [];

for filename in os.listdir(directory)[:]:

    if len(filename.split(".txt")) > 1 :
    
        nbar, g2, rlzs = leer_parametros(filename)
    
        if rlzs>5000 and 0.5<=nbar<=1.5:
            
            parametros_para_tests.append(
            {'nbar':nbar, 'g2':g2, 'rlzs':rlzs}
            )



# ----- for Maximum Likelihood Estimation ---


def minimizar_en_malla(fun):
    """
    'fun' debe ser una función de (nbar,g2)=theta
    """
    puntos_malla = [(nbar,g2) for nbar in nbars for g2 in g2s_para_cada_nbar[nbar]]
    valores_fun = [] ; nbar_values = [] ; g2_values = []

    for nbarp, g2p in puntos_malla:

        nbar_values.append(nbarp)
        g2_values.append(g2p)
        valores_fun.append(
            fun(nbarp,g2p)
        )

    puntos_ordenados = sorted( zip(puntos_malla,valores_fun), key=lambda dupla:dupla[1] )
    nbar_critico, g2_critico = puntos_ordenados[0][0]

    return nbar_critico, g2_critico


def get_Pn_completa(nbar, g2, n_limite=10):

    directory = "data_generation/complete_distributions/"

    with open(directory+f"{nbar:.2f}_{g2:.2f}.txt",'r') as file:
        
        lineas = file.readlines()
        idx = np.random.randint(len(lineas))
        P = [float(Pn) for n,Pn in enumerate(lineas[idx].split()) if n<=n_limite]
        if len(P)<n_limite+1:
            for n in range(len(P),n_limite+1):
                P.append(0.)

    sum_P = sum(P)
    return [Pn/sum_P for Pn in P]


def verosimilitud(pdf_completa, pdf_muestra):

    if len(pdf_muestra)!=len(pdf_completa):
        raise ValueError("El tamaño de las distribuciones no coincide")

    sumandos = []
    
    for n in range(len(pdf_muestra)):
        if pdf_completa[n]==0:
            sumandos.append(0)
        else:
            sumandos.append( pdf_muestra[n]*np.log(pdf_completa[n]) )
    
    return sum(sumandos)


def argmax_verosimilitud(pdf_muestra):

    def fun_a_minimizar(nbar, g2):
        pdf_completa = get_Pn_completa(nbar, g2, n_limite=len(pdf_muestra)-1)
        return 1.-verosimilitud(pdf_completa, pdf_muestra)

    return minimizar_en_malla(fun_a_minimizar)



# ----- for Cramér Rao Bound ---


def fisher_information_of_g2_per_sample(nbar, n_limite=10):

    Ps_como_funcion_de_g2 = [[] for n in range(n_limite+1)]
    
    for g2 in g2s_para_cada_nbar[nbar]:
        pdf_completa = get_Pn_completa(nbar, g2, n_limite)
        for n in range(n_limite+1):
            Ps_como_funcion_de_g2[n].append(pdf_completa[n])

    derivadas_Ps_como_funcion_de_g2 = [
        np.gradient(Ps_como_funcion_de_g2[n], g2s_para_cada_nbar[nbar])
        for n in range(n_limite+1)
    ]

    fisher_info_as_function_of_g2_per_sample = []
    
    for i,g2 in enumerate(Ps_como_funcion_de_g2[0]):
        sumandos = []
        for n in range(n_limite+1):
            if Ps_como_funcion_de_g2[n][i]==0:
                sumandos.append(0)
            else:
                sumandos.append( derivadas_Ps_como_funcion_de_g2[n][i]**2/Ps_como_funcion_de_g2[n][i] )
        fisher_info_of_g2_per_sample = sum(sumandos)
        fisher_info_as_function_of_g2_per_sample.append( float(fisher_info_of_g2_per_sample) )
        
    return fisher_info_as_function_of_g2_per_sample


n_limite = 10


fisher_info_malla = []
for nbar in nbars:
    fisher_info_malla += fisher_information_of_g2_per_sample(nbar, n_limite)
        
cramer_rao_bound_per_sample = float(1/np.mean(fisher_info_malla))



# ----- HERE IR WHERE TESTING HAPPENS ---


with open("scaler.pickle", 'rb') as scaler_file, open("regressor.pickle", 'rb') as regressor_file:
    scaler = pickle.load(scaler_file)
    regressor = pickle.load(regressor_file)


num_pruebas = 10_000
metodos = ('directo','NNregressor','maxlikelihood')

muestra_parametros = []

for i in range(num_pruebas):
    idx_parametros = np.random.randint(len(parametros_para_tests))
    nbar, g2, rlzs = parametros_para_tests[idx_parametros].values()
    muestra_parametros.append( (nbar, g2, rlzs) )

muestra_parametros = sorted(muestra_parametros, key=lambda params:int(params[2]))

t0 = time()
g2s_reales = []
realizaciones_reales = []
g2s_guessed = {metodo:[] for metodo in metodos}
nbars_guessed = {metodo:[] for metodo in metodos}
t1s = {metodo:[] for metodo in metodos}
t2s = {metodo:[] for metodo in metodos}
results_outofsample = {metodo:{} for metodo in metodos}


for i in range(num_pruebas):

    # Obtención de Pn incompleta
    nbar, g2, rlzs = muestra_parametros[i]
    g2s_reales.append(g2)
    realizaciones_reales.append(rlzs)
    idx_aleatorio = np.random.randint(0,99)
    distb_incompleta = pd.DataFrame(
        leer_varias_lineas_doc_DB(1, nbar, g2, rlzs, linea_inicio=idx_aleatorio, n_limite=n_limite, directory="data_generation/test_distributions/")
    )
    nrange = range(n_limite+1)
    pdf_incompleta = [distb_incompleta[f'P({n:d})'].iloc[0] for n in nrange]

    # Cálculo directo
    t1s['directo'].append( time() )
    nbar_aprox = np.dot( nrange, pdf_incompleta )
    nbars_guessed['directo'].append( nbar_aprox )
    varianza_aprox = np.dot( np.array(nrange)**2, pdf_incompleta ) - nbar_aprox**2
    g2_aprox = 1 + (varianza_aprox-nbar_aprox)/nbar_aprox**2
    g2s_guessed['directo'].append( g2_aprox )
    t2s['directo'].append( time() )
    
    # Guess del NNregressor
    t1s['NNregressor'].append( time() )
    X_g2 = distb_incompleta.drop(['g2','nbar'], axis='columns')
    X_g2_scaled = scaler.transform(X_g2)
    g2_guessed = regressor.predict(X_g2_scaled)[0]
    g2s_guessed['NNregressor'].append( g2_guessed )
    t2s['NNregressor'].append( time() )

    # Guess de Maximum likelihood Estimation
    t1s['maxlikelihood'].append( time() )
    nbar_guessed, g2_guessed = argmax_verosimilitud(pdf_incompleta)
    nbars_guessed['maxlikelihood'].append( nbar_guessed )
    g2s_guessed['maxlikelihood'].append( g2_guessed )
    t2s['maxlikelihood'].append( time() )
   
    tf = time()
    if (i%1000)==999:
        print(f"Prueba {i+1:d} terminada. Correspondiente a rlzs={rlzs}. Han pasado {(tf-t0)/60:.2f} min.",
              flush=True)

    for metodo in metodos:

        results_outofsample[metodo]['error'] = [ g2_1-g2_2 for g2_1,g2_2 in zip(g2s_guessed[metodo],g2s_reales) ]
        results_outofsample[metodo]['error_cuadratico'] = [ err**2 for err in results_outofsample[metodo]['error'] ]
        results_outofsample[metodo]['tiempo'] = [ t2-t1 for t2,t1 in zip(t2s[metodo],t1s[metodo]) ]


with open(f"results_outofsample.pickle", 'wb') as results_file:
    pickle.dump(results_outofsample, results_file)

with open(f"realizaciones_reales.pickle", 'wb') as realizaciones_file:
    pickle.dump(realizaciones_reales, realizaciones_file)



# ----- Producing results plot ---


num_windows = 1000
windows_scale = 2000

cantidades = ('error_cuadratico','tiempo')

labels = {'directo':"direct\ncalculation",
          'NNregressor':"NN\nregressor",
          'maxlikelihood':"maximum\nlikelihood"
         }
colores = {'directo':"tab:blue",
           'NNregressor':"tab:orange",
           'maxlikelihood':"tab:purple"
          }
axis_labels = {'error_cuadratico':r"$g^{{(2)}}$ mean squared"+"\nerror (sqrt.)",
               'tiempo':"mean computation\n"+r"time [$\mu s$]"
              }

windows_centers = np.logspace( np.log10(5000), 5, num_windows+2, dtype=int)[1:-1]
windows_sizes = np.logspace( np.log10(windows_scale), np.log10(windows_scale*windows_centers[-1]/windows_centers[0]), num_windows+2, dtype=int)[1:-1]
pm_sizes_windows = [round(size/2) for size in windows_sizes] 
windows = [ (center-pm_size,center+pm_size) for center,pm_size in zip(windows_centers,pm_sizes_windows) ]

results_outofsample_promedio = {

    metodo:{
        cantidad:{'mean':[],'std':[],'upper_dispersion':[],'lower_dispersion':[]}
        for cantidad in cantidades}
    
    for metodo in metodos
}

for lower_bound,upper_bound in windows:
    
    idxs = [i for (i,rlzs) in enumerate(realizaciones_reales) if lower_bound<=rlzs<=upper_bound]
    
    for metodo in metodos:
        for cantidad in cantidades:
            
            valores = results_outofsample[metodo][cantidad][idxs[0]:idxs[-1]+1]
            promedio = np.mean(valores)#,keepdims=True)
            std = np.std(valores)#,mean=promedio) [cambiar una vez actualizado numpy]
            
            results_outofsample_promedio[metodo][cantidad]['mean'].append(
                promedio
            )
            results_outofsample_promedio[metodo][cantidad]['std'].append(
                std
            )

rcParams.update({'font.size':8})
fig, axs = subplots(len(cantidades), 1, layout='constrained', figsize=(3.,3.))
lines = []

for i,cantidad in enumerate(cantidades):
    for metodo in metodos:

        if cantidad=='error_cuadratico':
            line = axs[i].plot(1e-3*windows_centers, [np.sqrt(r) for r in results_outofsample_promedio[metodo][cantidad]['mean']], color=colores[metodo], label=labels[metodo])
            lines.append(line[0])

        if cantidad=='tiempo':
            axs[i].plot(windows_centers, 1e6*np.array(results_outofsample_promedio[metodo][cantidad]['mean']), label=labels[metodo], color=colores[metodo])
            axs[i].set_ylim(10,10**7)

for i,cantidad in enumerate(cantidades):
    
    if cantidad=='error_cuadratico':
        line = axs[i].plot(1e-3*windows_centers, [np.sqrt(cramer_rao_bound_per_sample/rlzs) for rlzs in windows_centers],
                           lw=2., color='red', ls='dotted', label="Cramér-Rao\nbound")
        lines.append(line[0])
    if cantidad=='tiempo':
        axs[i].set_yscale('log')
        axs[i].set_xlabel("# detection windows")

fig.legend(handles=lines, loc=(0.,0.5), bbox_to_anchor=(1.03,0.5))
fig.savefig( "outofsample_comparison.pdf" , bbox_inches='tight')
close()