#!/usr/bin/env bash

cd data_generation/complete_distributions/

python generator_of_generators.py

scripts=$(printf '%s\n' *.py | grep -E '^[0-9]+_generator\.py$')

for script in $scripts; do
    python "$script" &
done

wait

for script in $scripts; do
    rm "$script"
done