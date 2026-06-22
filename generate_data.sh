#!/usr/bin/env bash
echo "Starting to compute the complete distributions..."
bash data_generation/complete_distributions/compute_complete_distributions.sh

echo "Starting to compute the incomplete distributions..."
bash data_generation/incomplete_distributions/generate_incomplete_distributions.sh

echo "Starting to compute the test distributions..."
bash data_generation/test_distributions/generate_test_distributions.sh