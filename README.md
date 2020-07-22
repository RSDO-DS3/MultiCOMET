# MultiCOMET

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project on your local machine for development and testing purposes. 

### Prerequisites

Installed [Git Bash](https://git-scm.com/downloads)  
25 GB of Storage

### Installing

Clone the repository
```
git clone https://github.com/AMGrobelnik/MultiComet
```
Navigate into the project's root directory:
```
cd MultiComet
```
Run the Github setup script (Downloads larger project files):
```
bash Setup/GithubSetup.sh
```
## Changing Parameters
### Model Data Parameters
### Model Training Parameters
## Training Your Own Model  
### Custom Data  
To use your own training/testing/development data, replace the files
```
data/atomic/v4_atomic_dev.csv  (data for development)
data/atomic/v4_atomic_trn.csv  (training data)
data/atomic/v4_atomic_tst.csv  (data for testing/evaluation0
```
with your own CSV files with the same names and formats

### Making Data The Data Loader  
In the project's root directory, run:
```
python scripts/data/make_atomic_data_loader.py
```
Save the relative file path to the data loader given for later use.

### Training Your Model  
In the project's root directory, run:
```
python src/main.py --experiment_type atomic --experiment_num YOUR_EXPERIMENT_NUMBER --loader_path PATH_TO_YOUR_LOADER_PATH
```
--experiment_num can be changed to train the model with different parameters
--loader_path can be changed to train the model with a different data Loader
For Example:
```
python src/main.py --experiment_type atomic --experiment_num 0 --loader_path MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Loader_It50k_maxE50.pickle
```
See "Model Training Paramters" to modify more training parameters

## Running Model Tests
The file "InputEvents.txt" in the project's root directory should include all the events your model should be tested on.
The sentences are separated by a Newline character
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
For example:
```
python scripts/interactive/atomic_single_example.py --model_file MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Model_It50k_maxE50.pickle --loader_path MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Loader_It50k_maxE50.pickle
```
As the module creates Tags for the events, they will be output to "COMETTags.json" in the project's root directory
## Evaluating Models

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Authors

* **Adrian Mladenic Grobelnik** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
