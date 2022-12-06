# Entity Standardizer
[Back to main page](https://github.com/konveyor/tackle-container-advisor#table-of-contents)

Each folder contains a different approach to perform entity standardization.

1. tfidf - A supervised approach that computes tfidf vectors for a given training dataset.
2. wdapi - An unsupervised approach based on wikidata autocomplete api.

### Input data from
 ``data/tca and data/wikidata``

### For configuration see
 `config/tca/tfidf.ini` and `config/wikidata/wdapi.ini`

### Models saved in
  ``models/tca/``

### To generate training and inference data (run from top level folder).
Training data will be stored inside ``data/tca/train.json`` and inference data for evaluation will
be stored at ``data/tca/infer.json``

```
python benchmarks/generate_data.py
```

### Evaluate entity standardization models (from top level folder)

```
python benchmarks/run_models.py -mode tca
```
Usage

```
usage: run_models.py [-h] [-model_type MODEL_TYPE] [-mode MODE]

Train and evaluate TCA entity standardization models

optional arguments:
  -h, --help               show this help message and exit
  -model_type MODEL_TYPE   tf_idf (default) | wiki_data_api | all
  -mode MODE               deploy (default) | tca

```

### Model comparison (04/14/2022)
<p><table> <thead>
<tr><th>Method</th><th>top-1</th><th>top-3</th><th>top-5</th><th>top-10</th><th>top-inf(count)</th><th>False positive rate</th><th>Runtime (on cpu)</th></tr>
</thead>
<tbody>
<tr><td>tfidf</td><td>0.63</td><td>0.77</td><td>0.79</td><td>0.81</td><td>0.81 (2415/2976)</td><td>0.00(0/0)</td><td>70.63s</td></tr>
<tr><td>wdapi</td><td>0.44</td><td>0.58</td><td>0.63</td><td>0.65</td><td>0.71 (1832/2566)</td><td>0.87(358/410)</td><td>2349.05s</td></tr>
</tbody>
</table></p>
