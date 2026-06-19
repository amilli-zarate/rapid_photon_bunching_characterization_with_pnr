from messages import messages as msgs
from pathlib import Path

directory = Path(__file__).resolve().parent
num_params_per_thread = msgs.parallelization_query()

intervalos = []
contador = 0
for num in num_params_per_thread:
	intervalos.append( (contador,contador+num) )
	contador += num

for i,intervalo in enumerate(intervalos):

	with open(directory/"base_file.py", 'r') as basefile, open(
		directory/f"{i}_generator.py", "w") as genfile:

		for j,line in enumerate(basefile,1):
			if j==4:
				genfile.write(f"for (nbar,g2) in parametros_mediciones[{intervalo[0]}:{intervalo[1]}]:\n")
			else:
				genfile.write(line)
