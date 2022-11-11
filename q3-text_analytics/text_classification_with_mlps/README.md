# Text Classification w. MLPs

*Text Analytics*  
*MSc in Data Science, Department of Informatics*  
*Athens University of Economics and Business*

![text classification](./images/banner.jpeg)

## *Table of Contents*

1. [Introduction](#introduction)
2. [Project Overview](#project-overview)
3. [Data](#data)
4. [Resources](#resources)
5. [Data Preprocessing](#data-preprocessing)
6. [Predictions](#predictions)

## *Introduction*

- **Natural language processing (NLP)** is a subfield of linguistics, computer science, and artificial intelligence
- NLP is concerned with the interactions between computers and human language
- Sentiment analysis is a NLP technique used to determine whether data is positive, negative or neutral
- It is performed on textual data to identify, extract, quantify, and study subjective information
- Furthermore, it helps businesses understand the social sentiment of their brand, product or service

## *Project Overview*

- The scope of this project was to develop a sentiment classifier for movie reviews
- For this purpose we used the [Large Movie Review Dataset](https://ai.stanford.edu/~amaas/data/sentiment/) by Andrew Maas
- First, we extracted some descriptive statistics such as vocabulary size, reviews length etc.
- Then, we preprocessed the reviews using mostly the `nltk` library
- We split the data into training $(70\\%)$, validation $(15\\%)$ and test $(15\\%)$ set
- Furthermore, we transformed the data using text vectorization and dimensionality reduction techniques
- We displayed baseline results using two classifiers
- Specifically, we used a dummy classifier and the best classifier from [text_classification_with_basic_models](https://github.com/sapaladas/msc_data_science/tree/main/q3-text_analytics/text_classification_with_basic_models)
- Then, we tuned the hyperparameters of the MLP model using `KerasClassifier` and `RandomizedSearchCV`
- In particular, we tuned the number of hidden layers, the number of neurons and the dropout rate
- We trained the MLP model using the `ModelCheckpoint` callback to save the best weights for each node
- Next we plotted the curves showing the accuracy and loss on training data as a function of epochs
- We evaluated the performance of the MLP model in the *test* set
- Finally, we plotted the *confusion matrix* and the *AUC curve*

## *Data*

- The data were acquired from [kaggle](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) and is the ["Large Movie Review Dataset"](https://ai.stanford.edu/~amaas/data/sentiment/) by Andrew Maas
- This is a dataset for binary sentiment classification which contains $50.000$ movie reviews
- The reviews were labelled either as positive or negative
- The two classes were balanced with each containing $25.000$ reviews

![classes](./images/reviews_length_distribution.svg)

## *Resources*

- Packages: `numpy`, `pandas`, `matplotlib`, `seaborn`, `sklearn`, `nltk`, `lightgbm`
- Software: Jupyter Notebook

## *Data Preprocessing*

### Data Cleansing

- The first step we took was to clean the data
- Therefore, we applied the following preprocessing steps to the reviews
  - Convert to lowercase
  - Replace accented characters
  - Expand contractions
  - Remove HTML tags
  - Replace non-alphabet characters with space
  - Remove stopwords
  - Remove words with less than 4 characters
  - Perform stemming
- Below you can find the function used to clean the reviews

``` python
def preprocess_data(review):

    # convert to lowercase
    review = review.strip().lower()

    # replace accented characters
    review = unidecode.unidecode(review)

    # expand contractions
    review = contractions.fix(review)

    # remove html tags
    review = re.sub(r'<.*?>', ' ', review)

    # replace non alphabet characters with space
    review = re.sub(r'[^a-z]', ' ', review)

    # split into words
    review = review.split()

    # remove stopwords
    review = [word for word in review if word not in stopwords.words('english')]

    # remove words with less than 3 chars
    review = [word for word in review if len(word) > 3]

    # stemming
    stemmer = PorterStemmer()
    review = [stemmer.stem(word) for word in review]

    # join the word to form the sentence
    review = ' '.join(review)

    return review

# execute function
df.review = df.review.apply(preprocess_data)
```

#### Example

*Sentence before preprocessing*

`A wonderful little production. <br /><br />The filming technique is very unassuming- very old-time-BBC fashion and gives a comforting, and sometimes discomforting, sense of realism to the entire piece. <br /><br />The actors are extremely well chosen- Michael Sheen not only "has got all the polari" but he has all the voices down pat too! You can truly see the seamless editing guided by the references to Williams' diary entries, not only is it well worth the watching but it is a terrificly written and performed piece. A masterful production about one of the great master's of comedy and his life. <br /><br />The realism really comes home with the little things: the fantasy of the guard which, rather than use the traditional 'dream' techniques remains solid then disappears. It plays on our knowledge and our senses, particularly with the scenes concerning Orton and Halliwell and the sets (particularly of their flat with Halliwell's murals decorating every surface) are terribly well done.`

*Sentence after preprocessing*

`wonder littl product film techniqu unassum time fashion give comfort sometim discomfort sens realism entir piec actor extrem well chosen michael sheen polari voic truli seamless edit guid refer william diari entri well worth watch terrificli written perform piec master product great master comedi life realism realli come home littl thing fantasi guard rather tradit dream techniqu remain solid disappear play knowledg sens particularli scene concern orton halliwel set particularli flat halliwel mural decor everi surfac terribl well done`

### Text Vectorization

- The next step was to vectorize the reviews into term-document matrices using TF-IDF
- We extracted the vectors for both unigrams and bigrams and consider only the top $10000$ features
- Finally, we applied sublinear TF scaling, i.e., replaced TF with $1 + log(TF)$

### Dimensionality Reduction

- Next, we performed dimensionality reduction on the vectors generated from the previous step
- Our goal was to reduce the number of features for our models
- In particular, we used the Truncated SVD transformer which works well with sparse matrices
- Due to time and resource limitation, we reduce the dimensionality to $2000$ features
- This resulted in an explained variance ration of $60\%$ of our initial vectors

## *Predictions*

### Baseline Results

- We displayed baseline results using two classifiers
- Specifically, we used a dummy classifier and the best classifier from [text_classification_with_basic_models](https://github.com/sapaladas/msc_data_science/tree/main/q3-text_analytics/text_classification_with_basic_models)
- Below you can find the results obtained from the baseline classifiers

![dummy classifier](./images/auc_curves_DummyClassifier.svg)
![logistic regression](./images/auc_curves_LogisticRegression.svg)

### MLP Hyperparameter Tuning

- The next step was to optimize some of the hyperparameters of the MLP model using the *validation* set
- Specifically, we tuned the *number of hidden layers*, the *number of neurons* and the *dropout rate*
- We used a `RandomizedSearchCV` along with a $5$-fold stratified cross validation
- Finally, we evaluated the scores obtained from cross validation using the *F1-Score* metric
- Below you can find the function used to tune the hyperparameters

``` python
def hyperparameter_tuning(x_valid, y_valid):

    # hyperparameters to test
    hidden_layers = [2,4,6]
    neurons = [128,256,512]
    dropout_rate = [0.2,0.5]

    # create the param grid
    param_grid = dict(hidden_layers=hidden_layers, neurons=neurons, dropout_rate=dropout_rate)

    def build_model(hidden_layers, neurons, dropout_rate):
        """
        Function to build a sequential MLP model.
        Inputs:
          - Number of hidden layers
          - Number of neurons in the first layer
          - Dropout rate
        Outputs:
          - MLP model
        """
        # initialize model
        model = Sequential()
        
        # loop to add N number of hidden layers
        for i in range(hidden_layers):
            
            if i == 0:
                # create first hidden layer with input dimensions
                model.add(Dense(neurons, input_dim=x_valid.shape[1], activation='relu'))
                model.add(Dropout(dropout_rate))
                neurons = neurons / 2
                
            else:
                # create next hidden layer
                model.add(Dense(neurons, activation='relu'))
                model.add(Dropout(dropout_rate))
                neurons = neurons / 2
                
        # output layer
        model.add(Dense(1, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
        return model

    # initialize the keras model
    model = KerasClassifier(build_fn=build_model, epochs=100, batch_size=250, verbose=0)

    # RandomizedSearchCV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)
    rs = RandomizedSearchCV(estimator=model, param_distributions=param_grid, scoring='f1', cv=cv, random_state=1, verbose=1, n_jobs=-1)
    rs.fit(x_valid, y_valid)

    # evaluate
    best_score = rs.best_score_
    best_params = rs.best_params_

    # print results
    print(f'Best grid score: {best_score}')
    print(f'Best grid params: {best_params}', end='\n\n')

    return None

# execute function
_ = hyperparameter_tuning(x_valid_svd, y_valid)
```

### Classification Results

- The final step was to train the MLP model using the hyperparameters obtained during tuning
- In addition, we used the `ModelCheckpoint` callback to save the best weights for the nodes
- We plotted the curves showing the accuracy and loss on training data as a function of epochs
- We evaluated the performance of the MLP model in the *test* set
- Finally, we plotted the *confusion matrix* and the *AUC curve*
- Below you can find the results obtained from each classifier on the test set

|     | Precision | Recall | F1-Score | Accuracy | Area Under Curve |
| :-- | :-------: | :----: | :------: | :------: | :-: |
| `DummyClassifier` | 0.25 | 0.50 | 0.33 | 0.50 | 0.75 |
| `LogisticRegression` | 0.89 | 0.89 | 0.89 | 0.89 | 0.96 |
| `MLP` | 0.89 | 0.89 | 0.89 | 0.89 | 0.91 |

![MLP 1](./images/MLP_accuracy_loss_curves.svg)
![MLP 2](./images/auc_curves_MLP.svg)
