<p align="center">
  <img width=200 src="./figures/icon.png">
</p>


<div align="center"><p>
    <a href="https://github.com/judgo-system/judgo/pulse">
      <img alt="Last commit" src="https://img.shields.io/github/last-commit/judgo-system/judgo"/>
    </a>
    <a href="https://github.com/judgo-system/judgo/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/judgo-system/judgo?style=flat-square&logo=MIT&label=License" alt="License"
    />
    </a>
</p>

</div>

<div align="center">
	<a href="https://judgo-system.github.io/">Introduction</a>
  <span> • </span>
    	<a href="https://judgo-system.github.io/install.html">Install</a>
  <span> • </span>
       	<a href="https://judgo-system.github.io/usage.html">Usage</a>
  <p></p>
</div>

## Introduction

> For Python >= 3.8

JUDGO is a python framework for ranking documents based on users' preference and has been used in [TREC 2022 Health Misinformation Track](https://trec-health-misinfo.github.io).

<h4>Main features:</b></h4>
							<ul>
								<li><b>Novel preference judgment algorithm</b>: The system is supported by a proprietary algorithm that enables it to accurately rank documents based on user preferences.</li>
								<li><b>Enriched UI features</b>: The system has a user-friendly interface with advanced features that accelerate the decision-making process.</li>
								<li><b>User behavior tracking</b>: The system tracks user behavior to gain a deeper understanding of their preferences and make more accurate recommendations.</li>
								<li><b>Flexible configuration</b>: The system has a flexible configuration that allows administrators to customize the settings and parameters to meet the specific needs of their organization.</li>
								<li><b>Crowdsourcing support</b>: The system is designed to be used in crowdsourcing settings, allowing multiple users to provide input and rankings.</li>
							</ul> 
 

## Install 
Visit <a href="https://judgo-system.github.io/">JUDGO</a> website for usage and installation instruction. 


## Creators

This framework has been designed and developed by the [Data System Group](https://uwaterloo.ca/data-systems-group/) at [University of Waterloo](https://uwaterloo.ca/). 


## Paper

```

@inproceedings{10.1145/3539618.3591801,
author = {Seifikar, Mahsa and Phan Minh, Linh Nhi and Arabzadeh, Negar and Clarke, Charles L. A. and Smucker, Mark D.},
title = {A Preference Judgment Tool for Authoritative Assessment},
year = {2023},
isbn = {9781450394086},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3539618.3591801},
doi = {10.1145/3539618.3591801},
abstract = {Preference judgments have been established as an effective method for offline evaluation of information retrieval systems with advantages to graded or binary relevance judgments. Graded judgments assign each document a pre-defined grade level, while preference judgments involve assessing a pair of items presented side by side and indicating which is better. However, leveraging preference judgments may require a more extensive number of judgments, and there are limitations in terms of evaluation measures. In this study, we present a new preference judgment tool called JUDGO, designed for expert assessors and researchers. The tool is supported by a new heap-like preference judgment algorithm that assumes transitivity and allows for ties. An earlier version of the tool was employed by NIST to determine up to the top-10 best items for each of the 38 topics for the TREC 2022 Health Misinformation track, with over 2,200 judgments collected. The current version has been applied in a separate research study to collect almost 10,000 judgments, with multiple assessors completing each topic. The code and resources are available at https://judgo-system.github.io.},
booktitle = {Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval},
pages = {3100–3104},
numpages = {5},
keywords = {pairwise preference, offline evaluation, relevance judgment},
location = {Taipei, Taiwan},
series = {SIGIR '23}
}


```

