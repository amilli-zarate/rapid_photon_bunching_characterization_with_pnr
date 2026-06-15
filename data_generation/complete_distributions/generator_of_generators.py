num_params_por_nucleo = [3]*8 # CHANGE TO ENCOMPASS THE 4155 PARAMS
intervalos = []
contador = 0
for num in num_params_por_nucleo:
	intervalos.append( (contador,contador+num) )
	contador += num

	
for i,intervalo in enumerate(intervalos):

	with open("base_file.py", 'r') as basefile, open(f"{i}_generator.py", "w") as genfile:

		for j,line in enumerate(basefile,1):
			if j==4:
				genfile.write(f"for (nbar,g2) in parametros_mediciones[{intervalo[0]}:{intervalo[1]}]:\n")
			else:
				genfile.write(line)
