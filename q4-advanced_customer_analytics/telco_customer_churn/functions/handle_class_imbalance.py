#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid

def cluster_the_majority_class_and_keep_only_the_centroids(x_train:pd.DataFrame, y_train:pd.Series):
    
    # get the two classes and their values
    index1, value1 = y_train.value_counts().index[0], y_train.value_counts()[0]
    index2, value2 = y_train.value_counts().index[1], y_train.value_counts()[1]
    
    # find the minority and majority class
    # and their respective values
    if value1 < value2:
        minority_class, minority_value = index1, value1
        majority_class, majority_value = index2, value2
    if value1 > value2:
        minority_class, minority_value = index2, value2
        majority_class, majority_value = index1, value1

    # keep records of the minority class
    idx_min = y_train[y_train.values == minority_class].index
    x_train_min = x_train[x_train.index.isin(idx_min)]
    y_train_min = y_train[y_train.index.isin(idx_min)]
    
    # keep records of the majority class
    idx_maj = y_train[y_train.values == majority_class].index
    x_train_maj = x_train[x_train.index.isin(idx_maj)]
    y_train_maj = y_train[y_train.index.isin(idx_maj)]
    
    # initialize a clustering instance
    # using as n_clusters the value of the minority class
    model = AgglomerativeClustering(n_clusters=minority_value, linkage='ward')
    
    # fit the clustering instance to the majority class
    # and assign each record 
    clusters = model.fit_predict(x_train_maj)
    
    # get the centroid of each class
    clf = NearestCentroid()
    clf.fit(x_train_maj, clusters)
    centroids = clf.centroids_
    
    # add centroids to a new dataframe
    df_centroids = pd.DataFrame(columns=x_train.columns, data=centroids)
    
    # concat records from the minority class
    # with the centroids of the clusters of the datapoints of the majority class
    x_train_balanced = pd.concat([x_train_min, df_centroids])
    
    # create a Series containing only the label of the majority class
    # as much times as the value of the minority class
    y_train_maj_values_to_append = pd.Series([majority_class]*minority_value)
    
    # concat the labels of both the minority and majority class
    y_train_balanced = pd.concat([y_train_min, y_train_maj_values_to_append])
    
    return x_train_balanced, y_train_balanced, clusters