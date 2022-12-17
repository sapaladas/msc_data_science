#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import confusion_matrix, classification_report

def cross_validate_models(x_train:pd.DataFrame,
                          y_train:pd.Series,
                          models:list):
    
    # create a dataframe to store the results
    index = [model[0] for model in models]
    columns = ['Precision', 'Recall', 'F1 Score', 'AUC', 'Accuracy']
    cv_scores = pd.DataFrame(data=np.nan, index=index, columns=columns)
    
    # create a StratifiedKFold instance
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)

    # loop through classifiers
    for name, model in models:

        # cross validate
        scoring = ['precision', 'recall', 'f1', 'roc_auc', 'accuracy']
        scores = cross_validate(model, x_train, y_train, scoring=scoring, cv=cv, error_score='raise')

        # evaluate
        avg_precision = scores['test_precision'].mean()
        avg_recall = scores['test_recall'].mean()
        avg_f1 = scores['test_f1'].mean()
        avg_roc = scores['test_roc_auc'].mean()
        avg_accuracy = scores['test_accuracy'].mean()
        
        # # print results
        # print('='*30)
        # print(f'{name}')
        # print('-'*30)
        # print(f'Precision: {avg_precision}')
        # print(f'Recall:    {avg_recall}')
        # print(f'F1 Score:  {avg_f1}')
        # print(f'AUC:       {avg_roc}')
        # print(f'Accuracy:  {avg_accuracy}\n')
        
        # store results
        cv_scores.loc[name, 'Precision'] = avg_precision
        cv_scores.loc[name, 'Recall'] = avg_recall
        cv_scores.loc[name, 'F1 Score'] = avg_f1
        cv_scores.loc[name, 'AUC'] = avg_roc
        cv_scores.loc[name, 'Accuracy'] = avg_accuracy

    return cv_scores

def grid_search_tune_models(x_train:pd.DataFrame,
                            y_train:pd.Series,
                            models:list,
                            param_grid:list,
                            scoring:str='f1'):
    
    # create a dataframe to store the results
    index = [model[0] for model in models]
    columns = [scoring]
    gs_scores = pd.DataFrame(data=np.nan, index=index, columns=columns)
    
    # create a StratifiedKFold instance
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)

    # loop through classifiers
    for index, model in enumerate(models):
        
        # gridsearchCV
        grid = GridSearchCV(model[1], param_grid[index][1], scoring=scoring, cv=cv)
        grid.fit(x_train, y_train)
        
        # evaluate
        best_score = grid.best_score_
        best_params = grid.best_params_
        best_estimator = grid.best_estimator_
        
        # print results
        print('='*117)
        print(f'{index+1}. {model[0]}')
        print('-'*117)
        print(f'Best grid score: {best_score}')
        print(f'Best grid params: {best_params}')
        print(f'Best estimator: {best_estimator}', end='\n\n')
        
        # store results
        gs_scores.loc[model[0], scoring] = best_score

    return gs_scores

def make_predictions(x_train:pd.DataFrame,
                     x_test:pd.DataFrame,
                     y_train:pd.Series,
                     y_test:pd.Series,
                     models:list):

    # create a dataframe to store the results
    index=[model[0] for model in models]
    columns=['Precision', 'Recall', 'F1 Score', 'AUC', 'Accuracy']
    prediction_scores = pd.DataFrame(np.nan, index=index, columns=columns)
    
    # loop through classifiers
    for i, (name, model) in enumerate(models):
        
        # fit and predict
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        
        # evaluate
        preds = model.predict(x_test)
        precision = precision_score(y_test, preds)
        recall = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, preds)
        accuracy = accuracy_score(y_test, preds)
        tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()
        
        # print results
        print('='*117)
        print(f'{i+1}. {name}')
        print('-'*117)
        # print(f'Precision: {precision}')
        # print(f'Recall:    {recall}')
        # print(f'F1 Score:  {f1}')
        # print(f'AUC:       {auc}')
        # print(f'Accuracy:  {accuracy}')
        # print(f'{confusion_matrix(y_test, preds)}')
        print(f' True Positives: {tp}')
        print(f' True Negatives: {tn}')
        print(f'False Positives: {fp}')
        print(f'False Negatives: {fn}')
        print('-'*53)
        print(f'{classification_report(y_test, preds)}')
        
        # store results
        prediction_scores.loc[name, 'Precision'] = precision
        prediction_scores.loc[name, 'Recall'] = recall
        prediction_scores.loc[name, 'F1 Score'] = f1
        prediction_scores.loc[name, 'AUC'] = auc
        prediction_scores.loc[name, 'Accuracy'] = accuracy

    return prediction_scores