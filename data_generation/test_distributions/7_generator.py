from generation_module import *


num_distbs_a_generar = 100
num_distbs_limite = 100

contador = 0
for (nbar,g2) in parametros_mediciones[3636:4155]:
    t1 = time()
    filepaths = filepaths_complete_distributions[(nbar,g2)]
    num_distbs_a_generar_por_filepath = num_distbs_a_generar//len(filepaths)

    realizaciones = X_realizaciones.rvs(size=30).astype(int)
    num_distbs_a_generar_por_rlzs = {}
    
    for rlzs in realizaciones:
        
        num_lineas_actuales = 0
        try:
            with open(f"{nbar}_{g2}_{rlzs:d}.txt", "r") as outfile:
                for line in outfile:
                    num_lineas_actuales += 1
        except FileNotFoundError:
            pass

        num_distbs_a_generar_por_rlzs[rlzs] = max(
			min(
				num_distbs_a_generar_por_filepath,
				num_distbs_limite-num_lineas_actuales
			)
			,
			0
		)

    for filepath in filepaths:

        generar_distbs_para_DB(filepath, realizaciones, num_distbs_a_generar_por_rlzs)

    contador += 1
    t2 = time()
    print(f"Pasaron {(t2-t1)/60:.2f} min. Van {contador} parámetros cubiertos", flush=True)