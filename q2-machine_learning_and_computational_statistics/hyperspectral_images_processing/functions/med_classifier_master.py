"""
This file contains:
- Function to calculate the mean value of each class (endmember)
- Function to calculate the minimum euclidean distance between a data point (pixel) and the mean value of each class (endmember)
- Function to calculate the mean error of the minimum euclidean distance predictions
"""

import numpy as np

# -------------------------------------------------------------------------------------------------------
# Calculate the mean (color) value of each class (endmember)
# -------------------------------------------------------------------------------------------------------

def calculate_the_mean_color_value_of_each_class(x_train, y_train):
    """
    Function to calculate the mean (color) value of each class (endmember)
    Steps:
        1. Take as input the x_train and the y_train of each fold from cross validation
        2. Create an empty list to store the mean (color) value of each class (endmember)
        3. Loop through the classes (endmembers)
        4. Create an empty list to store the (color) values of the data points of the respective class (endmember) in loop
        5. Loop through the data points of the x_train
        6. Check if the class (endmember) of the data point in loop is equal to the outer class (endmember) in loop
        7. If the above step is true, append the (color) value of the data point in loop to the list created in step 4
        8. After looping through all the data points of the x_train, get the mean (color) value of the appended data points
        9. Repeat the process for the next classes (endmembers)
    """
    
    # create a list to store the mean (color) value of each class (endmember)
    class_means = []
    
    # loop through the classes (endmembers)
    for any_class in range(1,8):
        
        # create a list to store the (color) values of the data points of the respective class (endmember) in loop
        data_points_per_class = []
        
        # loop through the data points of the x_train
        for i in range(x_train.shape[0]):
            
            # check if the class (endmember) of the data point in loop is equal to the outer class (endmember) in loop
            if any_class == y_train[i]:
                
                # append the (color) value of the data point in loop
                data_points_per_class.append(x_train[i])
        
        # get the mean (color) value of the data points belonging to the outer class in loop
        class_means.append(np.mean(data_points_per_class, axis = 0))
    
    class_means = np.asarray(class_means)

    return class_means

# -------------------------------------------------------------------------------------------------------
# Calculate the minimum euclidean distance between a data point (pixel) and the mean value of each class
# -------------------------------------------------------------------------------------------------------

def calculate_the_minimum_euclidean_distance_and_predict_the_class(x_test, class_means):
    """
    Function to calculate the minimum euclidean distance and predict the class (endmember)
    Steps:
        1. Take as input the x_test and the mean (color) value of each class (endmember)
        2. Create an empty list to store the class predictions (based on the minimum euclidean distance criterion)
        3. Loop through the data poins of the x_test
        4. Create an empty list to store the euclidean distance of the (color) value of the data point in loop from the mean (color) value of the class (endmember) in loop
        5. Loop through the classes (endmembers)
        6. Calculate the euclidean distance between the data point in loop and the mean (color) value of the class (endmember) in loop
        7. Append the calculated euclidean distance(s) to the list created in step 4
        8. Append the minimum euclidean distance, which corresponds to the class (endmember) that the data points belongs, to the list created in step 2
        9. Repeat the process for the next data point(s)
    """
    
    # create a list to store the class predictions
    preds = []
    
    # loop through the data points of the x_test
    for i in range(x_test.shape[0]):
        
        # create an empty list to store the euclidean distance
        # of the (color) value of the data point in loop
        # from the mean (color) value of the class (endmember) in loop
        distances = []
        
        # loop through the classes (endmembers)
        for j in range(7):
            
            # calculate the euclidean distance between the data point in loop and the mean (color) value of the class (endmember) in loop
            euclidean_distance = np.linalg.norm(x_test[i] - class_means[j])
            
            # append the calculated euclidean distance(s)
            distances.append(euclidean_distance)
        
        # append the minimum euclidean distance (corresponding to the class (endmember) that the data points belongs)
        preds.append(np.argmin(distances) + 1)
        
    return preds

# -------------------------------------------------------------------------------------------------------
# Calculate the mean error of the minimum euclidean distance predictions
# -------------------------------------------------------------------------------------------------------

def calculate_the_mean_error_of_the_minimum_euclidean_distance_predictions(y_test, preds):
    """
    Function to calculate the mean error of the minimum euclidean distance predictions for each iteration in cross validation
    Steps:
        1. Take as input the y_test and the predictions made in the i-th iteration of the cross validation
        2. Calculate the mean error of the minimum euclidean distances calculated on the i-th iteration of the cross validation
    """
    
    # calculate the mean error
    error = sum(y_test - preds != 0) / len(y_test)
    
    return error
