# Containerizing Jupyter Notebooks

This example demonstrates how to generate a container for a Jupyter
notebook.

The `jupyter.py` script outputs a container specification file that
can be built into a container image.  Use `--help` to list all the
script command line options.

The example includes a very simple Jupyter notebook, Conda environment
(`environment.yml`), and `requirements.txt` for illustrative purposes.

## Docker

Using pip:

```
$ jupyter.py --notebook notebook.py --requirements requirements.txt > Dockerfile
```

Using Anaconda:

```
$ jupyter.py --packager anaconda --notebook notebook.py --environment environment.yml > Dockerfile
```

Once the Dockerfile has been generated, the steps to build and run
the container are the same.

```
$ sudo docker build -t jupyter:example -f Dockerfile .
$ sudo docker run --rm -p 8888:8888 jupyter:example
```

## Singularity

Using pip:

```
$ jupyter.py --notebook notebook.py --requirements requirements.txt --format singularity > Singularity.def
```

Using Anaconda:
```
$ jupyter.py --packager anaconda --notebook notebook.py --environment.yml --format singularity > Singularity.def
```

Once the Singularity definition file has been generated the steps to
build and run the container are the same.

```
$ sudo singularity build jupyter-example.sif Singularity.def
$ singularity run jupyter-example.sif
```
