# Entity Standardizer
Entity standardizer is a core capability of TCA that is used to recognize standardized entities of technology
stack components from a natural language input. The models used for entity standardization are available for use
as a separate standalone python package.

Entity standardizer models available in the python package can be divided into two categories:

1. Single-shot models: These models are trained on a portion of the curated TCA knowledge base data. TFIDF and
Siamese models are examples of single-shot models.
2. Zero-shot models: These are pre-trained or unsupervised models that do not need to be trained on curated TCA
knowledge base data and can be used directly for inference. Wikidata autocomplete API is an example of this type
of model. Note: Although we cannot say with certainty that wikidata autocomplete API is strictly a zero-shot model,
it is used as a comparison point for zero-shot models that are used to standardize to Wikidata's vast knowledge base
of entities.

# Training and Inference with single-shot models
Entity standardizer package contains the following two single-shot models:

1. *siamese* - A supervised approach that uses BERT models connected in a Siamese network. The default model is the siamese model.
2. *tfidf* - A supervised approach that computes tfidf vectors for a given training dataset.

Use the following steps to install, train, and inference with the entity standardizer models as a standalone package.
The entity standardizer package requires python >= 3.9 environment.

1. Run *setup.sh* to install dependencies and entity standardizer package
```
bash setup.sh
```
Please make sure *setup.sh* finishes without any errors. You should
see a message at the end of the run suggesting TCA finished successfully.

2. Run *benchmarks/generate_data.py* to generate training and inference datasets from TCA knowledge base
```
python benchmarks/generate_data.py
```
The generated data will be stored in *data/tca*. Training data will be store in *train.json* and inference data in
*infer.json*

3. Run *benchmarks/run_models.py* to generate trained model and run inference on the trained models.
```
python benchmarks/run_models.py -mode tca -models all
```
The trained models will be stored in *models/tca*. ROC curves comparing *tfidf* and *siamese* models
will be generated and stored in *top1.png*. Hyperparametes for *tfidf* and *siamese* models can be found
in *config/tca/tfidf.ini* and *config/tca/siamese.ini*

# Inference with zero-shot models
Entity standardizer package contains the following zero-shot mode:

*wdapi* - An unsupervised approach based on wikidata autocomplete api.

Use the following steps to install entity standardizer package and inference
with zero-shot models. The entity standardizer package requires python >= 3.6 environment.

1. Run *setup.sh* to install dependencies and entity standardizer package
```
bash setup.sh
```
Please make sure *setup.sh* finishes without any errors. You should
see a message at the end of the run suggesting TCA finished successfully.

2. Run *benchmarks/generate_data.py* to generate training and inference datasets from TCA knowledge base
```
python benchmarks/generate_data.py
```
The generated data will be stored in *data/wikidata*. Inference data in *infer.json*

3. Run *benchmarks/run_models.py* to generate trained model and run inference on the trained models.
```
python benchmarks/run_models.py -mode wikidata
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
  -model_type MODEL_TYPE   tf_idf | wiki_data_api | siamese (default)| all
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
