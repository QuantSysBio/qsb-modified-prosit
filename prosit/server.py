import argparse
import os
import shutil
import tempfile
import time
import warnings

import pandas as pd
import tensorflow as tf

import model
import tensorize
import prediction
import minimal_out
import msp

def parse_prosit_args():
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--io_folder",
        help="Folder from which to read prositInput and write prositPredictions",
        type=str
    )
    parser.add_argument(
        "--output_format",
        help="display a square of a given number",
        type=str,
        choices=[
            'msp',
            'msp_redux', 
            'minimal',
        ],
        default='msp',
    )
    parser.add_argument(
        "--chunk_size",
        help="Size of chunk to read in piece by piece.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--chunks_processed",
        help="Chunks already processed.",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--use_multi_file",
        help="Chunks already processed.",
        type=bool,
        default=False,
    )
    args = parser.parse_args()
    return args


def get_predictions(folder, results_filename, d_spectra, d_irt, out_type='msp', chunksize=None, chunks_processed=-1, use_multi_file=False):

    if use_multi_file:
        dfs = sorted(os.listdir(folder))
    else:
        dfs = pd.read_csv('{}/prositInput.csv'.format(folder), chunksize=chunksize)
        if chunksize is None:
            dfs = [dfs]

    temp_files = []
    for idx, df in enumerate(dfs):
        if idx < chunks_processed:
            continue
        if use_multi_file:
            df = pd.read_csv('{}/prositInput{}.csv'.format(folder, idx))
        seconds_at_start = time.time()
        data = tensorize.csv(df, out_type)
        seconds_after_preparation = time.time()
        print('Time preparing data for input {}'.format(seconds_after_preparation - seconds_at_start))
        data = prediction.predict(data, d_spectra)
        seconds_after_prediction = time.time()
        print('Time making predictions {}'.format(seconds_after_prediction - seconds_after_preparation))
        tmp_f = tempfile.NamedTemporaryFile(delete=True)

        if chunksize is None:
            out_file = results_filename
        else:
            out_file = results_filename.replace('.', '{}.'.format(idx))
            temp_files.append(out_file)
        print(out_file)
        if out_type in ('msp', 'msp_redux'):
            result = prediction.predict(data, d_irt)
            c = msp.Converter(result, tmp_f.name)
            c.convert(redux=(out_type=='msp_redux'))
            shutil.copy(tmp_f.name, out_file)
        elif out_type == 'minimal':
            write_header = (idx==0 or use_multi_file)
            c = minimal_out.Converter(data, tmp_f.name)

            c.convert(write_header)
            shutil.copy(tmp_f.name, out_file)

        seconds_after_output = time.time()
        print('Time writing output {}'.format(seconds_after_output - seconds_after_prediction))

    print(temp_files)
    if chunksize is not None and not use_multi_file:
        with open(results_filename, "wb") as outfile:
            for f in temp_files:
                with open(f, "rb") as infile:
                    outfile.write(infile.read())

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    global d_spectra
    global d_irt
    d_spectra = {}
    d_irt = {}

    args = parse_prosit_args()

    d_spectra["graph"] = tf.Graph()
    with d_spectra["graph"].as_default():
        d_spectra["session"] = tf.Session()
        with d_spectra["session"].as_default():
            d_spectra["model"], d_spectra["config"] = model.load(
                'model_spectra', trained=True
            )
            d_spectra["model"].compile(optimizer="adam", loss="mse")

    if args.output_format in ('msp', 'msp_redux'):
        d_irt["graph"] = tf.Graph()
        with d_irt["graph"].as_default():
            d_irt["session"] = tf.Session()
            with d_irt["session"].as_default():
                d_irt["model"], d_irt["config"] = model.load(
                    'model_irt', trained=True
                )
                d_irt["model"].compile(optimizer="adam", loss="mse")
        out_file_name = '{}/prositPredictions.msp'.format(args.io_folder)
    elif args.output_format == 'minimal':
        out_file_name = '{}/prositPredictions.csv'.format(args.io_folder)

    print(args.use_multi_file)
    get_predictions(
        args.io_folder,
        out_file_name,
        d_spectra,
        d_irt,
        args.output_format,
        chunksize=args.chunk_size,
        chunks_processed=args.chunks_processed,
        use_multi_file=args.use_multi_file
    )
