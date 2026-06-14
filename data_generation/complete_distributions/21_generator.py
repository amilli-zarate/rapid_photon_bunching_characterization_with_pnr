from module_generation import *

contador = 0; t1 = time()
for (nbar,g2) in parametros_mediciones[21:22]:

	add_file_DB_distbs_completas(nbar,g2)

	contador += 1
	t2 = time()
	print(f"Han pasado {(t2-t1)/60:.2f} min. Van {contador} parametros cubiertos", flush=True)