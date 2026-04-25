# Scripts

## run_baseline.py
Run BEFORE training. Saves results/baseline_results.json.
export HF_TOKEN=your_token
python scripts/run_baseline.py

## run_post_training.py
Run AFTER training with trained model. Saves results/post_training_results.json and prints improvement summary.
export HF_TOKEN=your_token
export MODEL_NAME=path/to/trained/model
python scripts/run_post_training.py

## generate_plots.py
Generate all comparison plots from result files. Can run with placeholder JSONs immediately.
python scripts/generate_plots.py
Plots saved to results/plots/
