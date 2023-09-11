# gpuutilz plotting script

Quick and dirty seaborn based plotting for [willfurnass/gpuutiliz](https://github.com/willfurnass/gpuutiliz) generated device data

## Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage

```bash
./plot-gpuutiliz.py --help
./plot-gpuutiliz.py -i sample/gpu-dev-util-sample.log -o sample/gpu-dev-util-sample.png
```
