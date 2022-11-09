"""
This file contains:
- Main function to clean and preprocess data for predictions (customised for this project only)
"""

from functions.prepare_data_source import clean_and_preprocess_train_data
from functions.prepare_data_source import clean_and_preprocess_test_data

# ------------------------------------------------------------------------------
# Clean And Preprocess Data For Predictions
# ------------------------------------------------------------------------------

def clean_and_preprocess_data(train_data, test_data):
    """
    Main function to clean and preprocess train and test data for predictions
    Steps:
        1. Call function to clean and preprocess train data
        2. Call function to clean and preprocess test data
        3. Return train and test data
    """
    
    # Clean and preprocess train data
    train_data = clean_and_preprocess_train_data(train_data)
    
    # Clean and preprocess test data
    test_data = clean_and_preprocess_test_data(test_data)
    
    return train_data, test_data