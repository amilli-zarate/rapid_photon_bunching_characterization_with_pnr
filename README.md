This repository contains the final version of the computer program written as part of
the original scientific research developed in the _Laboratorio de nano y micro fotónica_ group,
in the _Instituto de Ciencias Nucleares_, _UNAM_, intended to be published under the title
**Rapid photon bunching characterization via photon-number-resolved detection**.

The result yielded by this program demonstrates the proficiency of artificial
neural networks (ANNs) on the task of determining the second-order coherence parameter (g2) of
low-intensity light fields in real-time.
For this purpose, this software performs a three step process:

1. Based on a set of number-of-clicks series obtained from PNR experiments,
it computes all data needed for the ANN to be trained, and tested.
(The experimental data must be downloaded from
https://drive.google.com/file/d/16bXARn1yIWqVfgolvo4aquOKE0UoIGAk/view?usp=sharing
)

2. Trains an ANN model (whose architecture was previously chosen after an extensive work of
hyperparameter tunning) to give accurate predictions of g2 based on short-experiments number-of-clicks
distributions, which we call _incomplete distributions_.

3. Test the ANN against two different statistical parameter estimators.
One of them is the direct calculation (DC) using the incomplete distribution and the g2 formula
in terms of the photon statistics.
The other one is maximum likelihood estimation (MLE).
The ANN is also compared to the fundamental performance limit given by the Cramér-Rao Bound.

The outcome is presented as a plot, and demonstrates the main result sated in the research article.
To reproduce the result, follow the below instructions.


**INSTRUCTIONS**

0.1. Install Python 3 and all requirements listed in  requirements.txt .

0.2. The experiment number-of-detection series are stored in a cloud platform.
Download the zip file containing this data from
https://drive.google.com/file/d/16bXARn1yIWqVfgolvo4aquOKE0UoIGAk/view?usp=sharing
and place the file inside the folder
data_generation/complete_distributions/experiment_num-clicks_series/

1. Run  generate_data.sh    using bash.

2. Run  train_ann.py    using Python 3.

3. Run  test_ann.py     using Python 3.