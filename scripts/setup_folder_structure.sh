#!/usr/bin/env bash

BENCHMARK_DATASET_DL_ID="1tcMf_g671ptGwdhIaU0fwfIZwCJGaAqy"

set -xeu

# check if gdown is installed
if ! command -v gdown &> /dev/null; then
    echo "gdown could not be found, please install it using 'pip install gdown'"
    exit 1
fi

mkdir -p data/benchmarks
mkdir -p data/scores
mkdir -p data/predictions

gdown $BENCHMARK_DATASET_DL_ID -O data/benchmarks/mixed_50.jsonl