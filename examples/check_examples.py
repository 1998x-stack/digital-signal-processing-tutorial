"""Run the ten deterministic standard-library numerical experiments."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parent
for i,name in enumerate(("pipeline","sequences","convolution","sampling_alias","ztransform","dtft","dft","fft","fir","iir","structures","multirate","cic","statistics","lms"),start=1):
    file=root/f"{i:02d}_{name}.py"
    assert file.is_file(),file
    print("Checking",file.name)
    runpy.run_path(str(file),run_name="__main__")
print("PASS: all fifteen numerical experiments")
