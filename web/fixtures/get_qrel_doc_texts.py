#!/cvmfs/soft.computecanada.ca/easybuild/software/2020/avx2/Core/ipykernel/2022a/bin/ipython --ipython-dir=/tmp
#SBATCH --array=0-280
#SBATCH --time=1:00:00
#SBATCH --mem-per-cpu=8GB
#SBATCH --cpus-per-task=2
#SBATCH --account=rrg-smucker
#SBATCH --output=slurm-%A_%a.out
import csv
import glob
import os
from pathlib import Path
import numpy as np
import pandas as pd
# from pyspark.sql import SparkSession
# from pyspark.sql.types import StructType, IntegerType, StringType, StructField
from tqdm import tqdm

# %%
files = sorted(list(
    Path('/project/6004803/smucker/group-data/c4_2022/commoncrawl_c4noclean_sanitized2/').rglob('*.jsonl.gz')
))

# qrels = pd.read_csv("/home/avakilit/resources21/qrels/qrels-35topics.txt",
#                     header=None,
#                     names="topic iter docno usefulness supportiveness credibility".split(),
#                     sep=' ')

qrels = pd.read_csv("document_list.csv",
                    header=None,
                    names=["docno"])


n = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0))
k = 200
# k = 10

files = files[n * k:n * k + k]

def func(file):
    df = pd.read_json(file, lines=True)
    df = df.merge(qrels, on="docno", how="inner")
    return df


from multiprocessing import Pool


# def parallelize_dataframe(files, func, n_cores=24):
#     pool = Pool(n_cores)
#     df = pd.concat(pool.imap(func, tqdm(files)))
#     pool.close()
#     pool.join()
#     return df



def parallelize_dataframe(files, func):
    df = pd.concat(list(map(func, tqdm(files))))
    return df

df = parallelize_dataframe(files, func)
df = df.reset_index(drop=True)
path = Path(f'/project/6004803/smucker/group-data/c4_2022/linhnhi_subset/{n:03}-of-{int(56000/k)-1}.csv')
path.parent.mkdir(parents=True, exist_ok=True)
# df["docno title text".split()].to_parquet(path)
df["docno title url text".split()].to_csv(path, index=False, header=None, quoting=csv.QUOTE_NONNUMERIC)

# df = pd.read_parquet('/project/6004803/smucker/group-data/c4_2022/qrels2022_subset.jsonl.gz',
#            orient='records', lines=True, compression='gzip')

# %% SPARK VERSION
# spark = SparkSession.builder.appName("MyApp").getOrCreate()
#
# schema = StructType([
#     StructField("topic", IntegerType(), True),
#     StructField("iter", IntegerType(), True),
#     StructField("docno", StringType(), True),
#     StructField("usefulness", IntegerType(), True),
#     StructField("supportiveness", IntegerType(), True),
#     StructField("credibility", IntegerType(), True)
# ])
# schema2 = StructType([
#     StructField("docno", StringType(), True),
#     StructField("title", StringType(), True),
#     StructField("text", StringType(), True),
#     StructField("url", StringType(), True),
#     StructField("fetch_time", StringType(), True),
# ])
#
# df = spark.read.json(
#     "/project/6004803/smucker/group-data/c4_2022/commoncrawl_c4noclean_processed_dake",
#     schema=schema2, recursiveFileLookup=True)
#
# qrels = spark.read.csv(
#     "/home/avakilit/resources21/qrels/qrels-35topics.txt",
#     header=False,
#     schema=schema
# )
#
# df = df.limit(100000).join(qrels, "docno", "inner")
