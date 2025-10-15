# tool_simulation_evaluation

[![Docker Image CI](https://https://github.com/KIT-HYD/simulation_evaluation/blob/combined-data/.github/workflows/docker-image.yml/badge.svg)](https://github.com/KIT-HYD/simulation_evaluation/blob/combined-data/.github/workflows/docker-image.yml)


This is a containerized Python tool following the Tool Specification for reusable research software using Docker.

Data:
CAMELS-DE: hydrometeorological time series and attributes for 1582 catchments in Germany
A. Dolich et al.
https://doi.org/10.5281/zenodo.13837553

Model code and software:
Hy2DL: Hybrid Hydrological modeling using Deep Learning methods
Eduardo Acuña Espinoza et al.
https://github.com/KIT-HYD/Hy2DL/tree/v1.1

## Description

The simulation evaluation tool is designed to assess the performance of hydrological simulations against observed hydrological data. It automates the process
of loading data from multiple catchments, computing key evaluation metrics, and generating visualizations for a comprehensive analysis. The tool outputs an
interactive HTML report containing performance summaries, time series plots, and statistical comparisons. The tool also outputs a .csv file conatining all the
metrics for the cathcments.

## Key features

## 1. Data loading and preprocessing

- Supports loading both simulation and observation data from CSV or Parquet files.
- Allows flexible structure
    - Separate files for observed and simulated data
    - A single file containing both observations and simulations
- Uses wildcards to match multiple files within directories.

## 2. Performance metrics
 - For each catchment, the tool calculates the most frequently used hydrological performance metrics, such as:
    - Nash-Sutcliffe Efficiency (NSE)
    - Kling-Gupta Efficiency (KGE)
    - Coefficient of determination (R2)
    - Mean Squared Error (MSE)
    - Root Mean Squared Error (RMSE)

## 3. Output generation

- Saves results in .csv and .json formats:
    - metrics_summary.csv - A summary of computed metrics for all cathcments
    - metrics_summary.json - JSON representation for programmatic access
- Generates an HTML report containing:
    - Time series plots for catcments
    - Performance metric tables


## How generic?

Tools using this template can be run by the [toolbox-runner](https://github.com/hydrocode-de/tool-runner). 
That is only convenience, the tools implemented using this template are independent of any framework.

The main idea is to implement a common file structure inside container to load inputs and outputs of the 
tool. The template shares this structures with the [R template](https://github.com/vforwater/tool_template_r),
[NodeJS template](https://github.com/vforwater/tool_template_node) and [Octave template](https://github.com/vforwater/tool_template_octave), 
but can be mimiced in any container.

Each container needs at least the following structure:

```
/
|- in/
|  |- parameters.json
|- out/
|  |- ...
|- src/
|  |- tool.yml
|  |- run.py
```

* `parameters.json` are parameters. Whichever framework runs the container, this is how parameters are passed.
* `tool.yml` is the tool specification. It contains metadata about the scope of the tool, the number of endpoints (functions) and their parameters
* `run.py` is the tool itself, or a Python script that handles the execution. It has to capture all outputs and either `print` them to console or create files in `/out`

## How to build the image?

You can build the image from within the root of this repo by
```
docker build -t tbr_python_tempate .
```

Use any tag you like. If you want to run and manage the container with [toolbox-runner](https://github.com/hydrocode-de/tool-runner)
they should be prefixed by `tbr_` to be recognized. 

Alternatively, the contained `.github/workflows/docker-image.yml` will build the image for you 
on new releases on Github. You need to change the target repository in the aforementioned yaml.

## How to run?

This template installs the json2args python package to parse the parameters in the `/in/parameters.json`. This assumes that
the files are not renamed and not moved and there is actually only one tool in the container. For any other case, the environment variables
`PARAM_FILE` can be used to specify a new location for the `parameters.json` and `TOOL_RUN` can be used to specify the tool to be executed.
The `run.py` has to take care of that.

To invoke the docker container directly run something similar to:
```
docker run --rm -it -v /path/to/local/in:/in -v /path/to/local/out:/out -e TOOL_RUN=foobar tbr_python_template
```

Then, the output will be in your local out and based on your local input folder. Stdout and Stderr are also connected to the host.

With the [toolbox runner](https://github.com/hydrocode-de/tool-runner), this is simplyfied:

```python
from toolbox_runner import list_tools
tools = list_tools() # dict with tool names as keys

foobar = tools.get('foobar')  # it has to be present there...
foobar.run(result_path='./', foo_int=1337, foo_string="Please change me")
```
The example above will create a temporary file structure to be mounted into the container and then create a `.tar.gz` on termination of all 
inputs, outputs, specifications and some metadata, including the image sha256 used to create the output in the current working directory.

## What about real tools, no foobar?

Yeah. 

1. change the `tool.yml` to describe your actual tool
2. add any `pip install` or `apt-get install` needed to the dockerfile
3. add additional source code to `/src`
4. change the `run.py` to consume parameters and data from `/in` and useful output in `out`
5. build, run, rock!

