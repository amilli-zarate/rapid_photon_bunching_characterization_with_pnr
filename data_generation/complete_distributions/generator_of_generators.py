from generation_module import parametros_mediciones

intervalos = [(i*1,(i+1)*1) for i in range(30)]  # CHANGE 1 -> 138
intervalos[-1] = (intervalos[-1][0],len(parametros_mediciones))

for i,intervalo in enumerate(intervalos):

	with open("base_file.py", 'r') as basefile, open(f"{i}_generator.py", "w") as genfile:

		for j,line in enumerate(basefile,1):
			if j==4:
				genfile.write(f"for (nbar,g2) in parametros_mediciones[{intervalo[0]}:{intervalo[1]}]:\n")
			else:
				genfile.write(line)
