# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 00:37:05 2022

@author: LinhNhiPM
"""

# module load StdEnv gcc cuda/11 faiss arrow/8 python java
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import re


files = sorted(list(
    Path('/home/lnphanmi/projects/rrg-smucker/smucker/group-data/c4_2022/commoncrawl_c4noclean_processed_dake/').rglob('*.jsonl.gz')
))

doc_list = pd.read_csv("/home/lnphanmi/projects/rrg-smucker/lnphanmi/thesis/document_list.csv",
                       header=None,
                       names="docno".split())


def func(file):
    df = pd.read_json(file, lines=True)
    df = df.merge(doc_list, on="docno", how="inner")
    return df


from multiprocessing import Pool


def parallelize_dataframe(files, func, n_cores=28):
    pool = Pool(n_cores)
    df = pd.concat(pool.imap(func, tqdm(files)))
    pool.close()
    pool.join()
    return df


df = parallelize_dataframe(files, func)
df = df.reset_index(drop=True)

for i, rows in df.iterrows():
    df['text'][i] = re.sub(r'\n{3}', '\n\n', df['text'][i])

# To csv file
df["docno title url text".split()].to_csv('/home/lnphanmi/projects/rrg-smucker/lnphanmi/thesis/trec2021_subset_c4_passages.csv.gz', index=False)

# To json-lines
df.to_json('/home/lnphanmi/projects/rrg-smucker/lnphanmi/thesis/trec2021_subset_c4_passages.jsonl.gz', orient='records', lines=True, compression='gzip')
