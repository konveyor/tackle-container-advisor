# CoSiNES: Contrastive Siamese Network for Entity Standardization

This is the page for the paper ["CoSiNES: Contrastive Siamese Network for Entity Standardization"](https://arxiv.org/pdf/2306.03316.pdf). 

We share the data, models and code to reproduce the experiments in the paper.

## Dataset
Our proposed dataset is located in the data/esAppMod folder. The datasets from biomedical domain are located in the data/biomedical folder (unzip the data file) and are downloaded from [here](https://github.com/insilicomedicine/Fair-Evaluation-BERT). 

## Requirement
`pip install -r requirement.txt`

## Experiments
We perform hyper-parameter search on our proposed dataset, and directly use the same hyper-parameter for biomedical datasets. For more details, please refer to the [paper](https://arxiv.org/pdf/2306.03316.pdf). 

To run hyper-parameter search:

`python raytune_training.py`

To produce the results on esAppMod:

`python run_esAppMod.py`

To produce the results on biomedical datasets:

`python run_biomedical`

Note: modify the dataset name in the config.ini to get the result for each datasest. 


Please cite 
```
@inproceedings{yuan2023cosines,
  title={CoSiNES: Contrastive Siamese Network for Entity Standardization},
  author={Yuan, Jiaqing and Merler, Michele and Choudhury, Mihir and Pavuluri, Raju and Singh, Munindar P. and Vukovic, Maja},
  booktitle={Proceedings of the Matching Workshop at ACL},
  year={2023}
}
```
