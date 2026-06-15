#!/usr/bin/env bash

cd data_generation/complete_distributions/

python generator_of_generators.py

for script in $(ls | grep -E '^[0-9]+_generator\.py$'); do
    python "$script" &
done

wait