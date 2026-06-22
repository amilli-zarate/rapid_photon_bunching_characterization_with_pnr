#!/usr/bin/env bash

python -m data_generation.incomplete_distributions.generator_of_generators

scripts=$(ls data_generation/incomplete_distributions/*.py | grep -E '[0-9]+_generator\.py$')

for script in $scripts; do
    python "$script" &
done

wait

for script in $scripts; do
    rm "$script"
done