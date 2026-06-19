#!/usr/bin/env bash

unzip -n experiment_num-clicks_series/experiment_num-clicks_series.zip -d experiment_num-clicks_series

python -m data_generation.complete_distributions.generator_of_generators

scripts=$(ls data_generation/complete_distributions/*.py | grep -E '[0-9]+_generator\.py$')

for script in $scripts; do
    python "$script" &
done

wait

for script in $scripts; do
    rm "$script"
done