# qsb-modified-prosit
A minimally modified version of the open source Prosit code for optimised performance on HPC.

## Purpose

This is a slightly modified version of the code available at (https://github.com/kusterlab/prosit). We are making this code available because so that results presented from our group are fully reproducible and because it may be useful to others who wish to run Prosit on their HPC system.

This code has only been slightly altered and we do not claim credit for the outstanding work from the kusterlab team.

We also do not guarantee that this code will work on every hpc system. It was developed for use on GWDG Göttingen cluster and has not been applied elsewhere.

The key changes that we have implemented are:

* converting the docker image to a singularity image.
* allowing the user to run single python jobs to generate predictions for specific spectra rather than running a web server.
* allowing an option for faster execution by not calculating m/z values for all fragments (we find it more efficient to calculate these downstream).
* adding the predicted iRT to msp output format (this modified version only supports msp output).

## Installation

We have converted the original docker image to a singularity image which can be provided upon request but cannot be made available here due to limits on file storage. This file should be placed in the prosit/ folder.

## Execution

All commands should be executed from the terminal within prosit/ folder of this repository.

Load singularity:

```
module load singularity
```

Submit a job to slurm, creating an interactive shell and using the prosit singularity image (in this example requesting 5 minutes of run time.).

```
srun -p gpu -G 1 -t 00:05:00 --pty singularity shell -B /cm/local/apps prosit_image.sif -nv
```

Then execute the server.py script specifying an I/O folder containing a prositInput.csv file. The prositPredictions.msp file will be written to that folder.

```
time python server.py --io_folder example_io_folder 
```

There are also a number of optional command line arguments which you may find useful:

| Command Line Argument   | Description   |
|-------|---------------|
| io_folder  | This should be the path to a folder containing a prositInput.csv file. |
| output_format | Choose from msp (standard format), msp_redux (writes in msp format but all fragment m/z values are left at zero, this saves a lot of time on GPU), minimal (returns only a list of the top 5 ions predicted by Prosit). |
| chunk_size | If you have a large ammount of data in your prositInput.csv file, processing it in chunks is more efficient, escpecially if you are not using msp_redux. 100000 is a reasonable setting. |
| chunks_processed | If your job crashed at a certain point (for example if you underestimated the time required and slurm cancelled your job) but you had already processed most of the chunks of the data, this allows you to restart and process the remaining chunks. |
