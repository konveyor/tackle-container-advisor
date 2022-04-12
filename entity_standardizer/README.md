# entity_standardizer
Each folder contains a different approach to perform entity standardization.

1. tfidf - A supervised approach that computes tfidf vectors for a given training dataset.
2. wdapi - An unsupervised approach based on wikidata autocomplete api.

### Input data from
 ``data/tca and data/wikidata``
 
### For configuration see 
 ``config/tca/tfidf.ini and config/wikidata/wdapi.ini``

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

### Model comparison (03/23/2022)
<p><table> <thead> 
<tr><th>Method</th><th>top-1</th><th>top-3</th><th>top-5</th><th>top-10</th><th>top-inf(count)</th><th>False positive rate</th><th>Runtime (on cpu)</th></tr> 
</thead> <tbody> 
<tr><td>tfidf</td><td>0.63</td><td>0.75</td><td>0.76</td><td>0.77</td><td>0.77 (2285/2973)</td><td>0.00(0/0)</td><td>58.49s</td></tr> 
<tr><td>wdapi</td><td>0.44</td><td>0.58</td><td>0.63</td><td>0.65</td><td>0.71 (1830/2568)</td><td>0.87(354/405)</td><td>2483.35s</td></tr> 
</tbody> </table></p>
