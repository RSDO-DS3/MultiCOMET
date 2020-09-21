# MultiCOMET

MultiCOMET provides the user with the tools to train and test their own model for commonsense descriptions in natural language, supporting multilingual input and ouptput.
The training is performed based on a dataset of sentences,labelled with values of 9 tags, describing a commonsense understanding of the sentence.
The dataset format is based on the [ATOMIC](https://arxiv.org/pdf/1811.00146.pdf) dataset. The model is trained with code from the [COMET](https://github.com/atcbosselut/comet-commonsense) project.

## Getting Started

These instructions will get you a copy of the project on your local machine for development and testing purposes. 

### Prerequisites

Installed [Git Bash](https://git-scm.com/downloads)  
Installed [Anaconda](https://www.anaconda.com/products/individual)  
20 GB of Storage

### Installing
After initializing your terminal to run Conda,
Open your terminal as administrator and create a new Conda environment for the project with Python 3.6:
```
conda create --name multicomet python=3.6
```
Ensure this environment is activated before executing any project code  

Open your Conda terminal as administrator, activate your new environment and install the following dependencies inside:

```
conda activate multicomet
pip install tensorflow
pip install ftfy==5.1
conda install -c conda-forge spacy
python -m spacy download en
pip install tensorboardX
pip install tqdm
pip install pandas
pip install ipython
conda install -c pytorch pytorch
```
Clone the repository:
```
git clone https://github.com/AMGrobelnik/MultiComet
```
Navigate into the project's root directory and run the Github setup script (Downloads larger project files):
```
cd MultiComet
bash Setup/GithubSetup.sh
```
## Changing Parameters

### Model Training Parameters
To view default Model training parameters go to:
```
config\default.json  
config\atomic\default.json
```
To modify the parameters go to:
```
config\atomic\changes.json
```
The JSON keys numbered from 0 to 3 are different experiments each with their independent set of parameters that can be used to train models.  
You can select which experiment to use for training with the ***--experiment_num*** parameter in ***Running Model Tests***
## Training Your Own Model  
### Custom Data  
To use your own training/testing/development data, replace the files
```
data/atomic/v4_atomic_dev.csv  (data for development)
data/atomic/v4_atomic_trn.csv  (training data)
data/atomic/v4_atomic_tst.csv  (data for testing/evaluation)
```
with your own CSV files with exactly the same names and formats

### Making Your Own Data Loader  
In the project's root directory, run:
```
python scripts/data/make_atomic_data_loader.py
```
Save the relative file path for the data loader given in the terminal output for later use.

### Training The Model  
In the project's root directory, run:
```
python src/main.py --experiment_type atomic --experiment_num YOUR_EXPERIMENT_NUMBER --loader_path PATH_TO_YOUR_LOADER
```
***--experiment_num*** can be changed to train the model with a different experiment's parameters  
***--loader_path*** can be changed to train the model with a different data Loader  
For Example:
```
python src/main.py --experiment_type atomic --experiment_num 1 --loader_path MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Loader_It50k_maxE50.pickle
```
See **Model Training Paramters** to modify more training parameters

## Running Model Tests
The file **InputEvents.txt** in the project's root directory should include all the events your model will be tested on.  
The events are separated by a new line.  
For example:
```
PersonX goes to the store
PersonX is very happy 
PersonX is a big deal
```
In the project's root directory, run:
```
python scripts/interactive/atomic_single_example.py --model_file PATH_TO_YOUR_MODEL --loader_path PATH_TO_YOUR_LOADER
```
***--model_file*** path to the model you would like to test  
***--loader_path*** path to the same loader your model was trained on  
For example:
```
python scripts/interactive/atomic_single_example.py --model_file MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Model_It50k_maxE50.pickle --loader_path MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Loader_It50k_maxE50.pickle
```
As the model creates tags for the events, they will be output to **COMETTags.json** in the project's root directory
## Evaluating Models
As the metric of evaluation, we recommend using precision @5 comparing the top 5 labels for each tag given by the model for an event in the test dataset, with the top 5 manually provided labels.

## Built With

* [ATOMIC](https://arxiv.org/pdf/1811.00146.pdf) - dataset of 24,000 labelled sentences for commonsense descriptions in natural language 
* [COMET](https://github.com/atcbosselut/comet-commonsense) - Deep learning for English commonsense descriptions of sentences
* [Pytorch](https://pytorch.org/) - Used for training models - open source machine learning library

## Authors

* **Adrian Mladenic Grobelnik** - *Software development and research* - [AMGrobelnik](https://github.com/AMGrobelnik)
* [**Dunja Mladenic**](https://ailab.ijs.si/dunja_mladenic/) - *Research and developemnt*
* [**Marko Grobelnik**](https://ailab.ijs.si/marko_grobelnik/) - *Software design and research*

## License

## Acknowledgments
This project was co-financed by the Republic of Slovenia and the European Union under the European Regional Development Fund. The operation is carried out under the Operational Programme for the Implementation of the EU Cohesion Policy 2014–2020.

We would like to thank the authors of COMET and ATOMIC:  

- Antoine Bosselut and Hannah Rashkin and Maarten Sap and Chaitanya Malaviya and Asli Çelikyilmaz and Yejin Choi (2019), COMET: Commonsense Transformers for Automatic Knowledge Graph Construction, Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL).
- Maarten Sap, Ronan Le Bras, Emily Allaway, Chandra Bhagavatula, Nicholas Lourie, Hannah Rashkin, Brendan Roof, Noah A. Smith, Yejin Choi (2019), ATOMIC: An Atlas of Machine Commonsense for If-Then Reasoning, arXiv:1811.00146v3 [cs.CL] 7 Feb 2019.


