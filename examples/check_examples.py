"""Run all deterministic DSP examples using Python standard library."""
from pathlib import Path
import runpy
root = Path(__file__).resolve().parent
for name in ("01_pipeline.py","02_sequences.py","03_convolution.py","04_sampling_alias.py","05_ztransform.py"):
    print("Checking", name)
    runpy.run_path(str(root/name),run_name="__main__")
print("PASS: five DSP examples")
