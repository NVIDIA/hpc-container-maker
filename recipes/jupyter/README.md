# Containerizing Jupyter Notebooks

This example demonstrates how to generate a container for a Jupyter
notebook.

The `jupyter.py` script outputs a container specification file that
can be built into a container image.  Use `--help` to list all the
script command line options.

The example includes a very simple Jupyter notebook and `requirements.txt`
for illustrative purposes.

## Docker

```
$ jupyter.py --notebook notebook.py --requirements requirements.txt > Dockerfile
$ sudo docker build -t jupyter:example -f Dockerfile .
$ sudo docker run --rm -p 8888:8888 jupyter:example
```

## Singularity

```
$ jupyter.py --notebook notebook.py --requirements requirements.txt --format singularity > Singularity.def
$ sudo singularity build jupyter-example.sif Singularity.def
$ singularity run jupyter-example.sif
```
