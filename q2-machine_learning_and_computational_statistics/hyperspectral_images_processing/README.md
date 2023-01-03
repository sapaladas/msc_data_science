# *Hyperspectral Images Processing*

![hyperspectral image](./images/hyperspectral_image.jpeg)

## *Table of Contents*
- [***Introduction***](#introduction)
- [***Project Overview***](#project-overview)
- [***Data***](#data)
- [***Part 1 - Spectral Unmixing***](#part-1---spectral-unmixing)
- [***Part 2 - Classification***](#part-2---classification)
- [***Conclusion***](#conclusion)

## *Introduction*

- A hyperspectral image depicts a specific scene at several $(L)$ narrow continuous spectral bands
- It can be represented by a $M \times N \times L$ three dimensional cube
- The first two dimensions correspond to the spatial information
- The third dimension corresponds to the spectral information
- Thus, the $(i,j)$ pixel in such an image, $i=1,...,M$, $j=1,...,N$, is represented by an $L$-dimensional vector
- This $L$-dimensional vector is called the ***spectral signature*** of the pixel

![spectral signature](./images/spectral_signature.png)

- In several remote sensing applications, the hyperspectral images are taken from satellites
- In such cases, they depict specific scenes of the earth surface at a specific spatial resolution
- That is, a single pixel may represent an area from $3 \times 3m^{2}$ to $100 \times 100m^{2}$ or more
- Each pixel is likely to depict more than one materials depicted in the corresponding area of the scene
- Such pixels are called ***mixed pixels*** and they are the vast majority of the pixels in the image
- On the other hand, there are (usually) a few pixels that depict a single material, called ***pure pixels***

![mixed and pure pixels](./images/mixed_pure_pixels.png)

## *Project Overview*

- In this project, we dealt with the usual procedures for processing hyperspectral images
- The usual processing procedures follow two main directions, the ***spectral unmixing*** and the ***classification***

#### *Spectral Unmixing*

- Assume that a set of $m$ spectral signatures corresponding to the pure pixels in the HSI under study is given
- For a given pixel, the aim is to determine the percentage to which each material contributes in its formation
- These percentages are known as the ***abundance maps*** for the given pixel
- Therefore it is clear that spectral unmixing provides ***sub-pixel information*** for a given pixel

#### *Classification*

- Assume that all pixels in the HSI under study are known to belong to one out of $m$ ***known classes***
- Given a specific pixel, the aim is to determine the most suitable class to assign it

## *Data*

- The data were provided in the context of the course content
- The data refer to the so called ***"Salinas" HSI***, which depicts an area of the Salinas valley in California, USA
- It is a $220 \times 120$ spatial resolution HSI
- It consists of $204$ spectral bands (from $0.2μm$ – $2.4μm$) and its spatial resolution is $3.7m$
- That is, the HSI is a $220 \times 120 \times 204$ cube
- The data are in the files `Salinas_cube.mat` (the Salinas hypercube) and `Salinas_gt.mat` (the class label for each pixel)

## *Part 1 - Spectral Unmixing*

- The "Salinas" HSI includes ***7 endmembers***
- Each one corresponds to a certain material, or cultivation in our case
- The cultivations are *grapes, broccoli, fallow 1, fallow 2, fallow3, stubble, celery*
- The aim was to perform unmixing on each one of the pixels in the image with **non-zero label**, with respect to the 7 endmembers
- For this task, the following five different spectral unmixing methods was used:
  - *Least squares*
  - *Least squares imposing the sum-to-one constraint*
  - *Least squares imposing the non-negativity constraint on the entries of θ*
  - *Least squares imposing both the non-negativity and the sum-to-one constraint on the entries of θ*
  - *LASSO, i.e., impose sparsity on θ via L1 norm minimization*
- For each method:
  - We derived the corresponding ***7 abundance maps*** (one for each endmember/material)
  - We computed for each pixel $y_{i}$ the ***reconstruction error***

### *Abundance Maps*

![abundance maps 1](./images/abundance_maps_ls.svg)
![abundance maps 2](./images/abundance_maps_ls_sum_to_one.svg)
![abundance maps 3](./images/abundance_maps_ls_non_negativity.svg)
![abundance maps 4](./images/abundance_maps_ls_non_negativity_and_sum_to_one.svg)
![abundance maps 5](./images/abundance_maps_lasso.svg)

### *Reconstruction Errors*

![reconstruction error](./images/reconstruction_errors_per_method.svg)

#### *Comment*

In general, the optimal spectral unmixing method should result in abundance maps where each of them depicts only the pixels corresponding to the respective class. In our case, by comparing the results obtained from the different methods, we can clearly observe that there are two methods that perform significantly better than the others. In particular, Non-Negative LS and LASSO managed to separate the material to a great extent. On the other hand, when we consider the reconstruction error of each method, we have a completely different story. OLS yields the lowest reconstruction error, while both Non-Negative LS and LASSO have by far the worst performance.

This strange behavior might have an explanation. LS methods with inequality constraints and regularizations are much more difficult to solve as a minimization problem than those with equality or no constraints at all. Therefore, this could lead us to the conclusion that the reconstruction error might not be the right source of truth when it comes to measure the spectral unmixing performance, and that the abundance maps obtained from constrained LS methods return a better representation of the ground truth.

## *Part 2 - Classification*

- In this case, we considered also the image pixels with **non-zero class labels**
- The task was to assign each one of them to the most appropriate class, among the ***7 known classes***
- To this end, four classifiers were used:
  - *The Naive Bayes classifier*
  - *The Minimum Euclidean Distance classifier*
  - *The K-Nearest Neighbor classifier*
  - *The Bayesian Classifier*
- For each classifier:
  - We trained it based on the training set performing a 10-fold cross validation
  - We reported the estimated validation error as the mean of the ten resulting error values
  - We computed, also, the associated standard deviation
  - We used the whole training set to train the classifier and evaluate their performance on the test set
  - We computed the success rate (sum of the diagonal elements divided by the sum of all elements of the confusion matrix)

### *Performance*

![classification results](./images/classification_results.svg)

#### *Comments*

- Comparing the results, we see that there are great differences between their respective errors
- However, if we compare their success rates, we see that their performance is almost at the same level
- Therefore, if we take into account both their errors and their success rates, we see that we have a clear winner
- KNN classifier not only has the best overall success rate, but also the lowest error
- On the other hand, the worst performing classifier seems to be the Minimum Euclidean Distance classifier
- It is clear from the graph above that it ranks last in terms of error and success rate
- The same conclusion can, also, be drawn if we look at its confusion matrix in the [notebook](https://github.com/sapaladas/msc_data_science/blob/main/q2-machine_learning_and_computational_statistics/hyperspectral_images_processing/main.ipynb)
- It has more non-diagonal values than the other classifiers, which means that it has more misclassified data

## *Conclusion*

In the project, we focused on hyperspectral images processing and performed spectral unmixing and classification tasks. In the fist part, spectral unmixing, we used various least squares methods (both ordinary and constrained) to estimate the relationship between the 7 endmembers and the spectral signature of each pixel in the image. In the second part, classification, we used 4 different classification algorithms and tried to predict the class to which each pixel in the given test set belongs.

Having performed both tasks, we can see some correlation between the results obtained from the spectral unmixing procedure and those obtained from the classification. By deriving the abundance maps for each endmember, what we tried to do is that we tried to classifiy each pixel into one of the 7 endmembers (classes). So, in effect, by deriving the abundance maps we tried to show where in the image (on the ground) we have finally classified (placed) each of the 7 endmembers (materials).
