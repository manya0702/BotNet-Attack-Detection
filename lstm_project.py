# -*- coding: utf-8 -*-
"""LSTM PROJECT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OCdVaTeDUvTVfPrpwIpDfInsphDade5_
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

"""## DATA PREPROCESSING"""

data = pd.read_csv('/content/drive/MyDrive/LSTM/X_train.csv')

data.columns

data['Attack'].unique()

data.shape

data.head(10)

data = data.sort_values(by='FLOW_DURATION_MILLISECONDS', ascending=True)
data

data = data.reset_index(drop=True)

data.Label.value_counts()

data.drop(columns=['IPV4_SRC_ADDR','IPV4_DST_ADDR'],inplace=True)

data['out-in_pkts']=data.OUT_PKTS-data.IN_PKTS

data['out-in_bytes']=data.OUT_BYTES-data.IN_BYTES

df = data.drop('Attack', axis=1)

df.corr()

x = df.drop('Label',axis=1).values.T
y = df.Label.values

# calculate R2 value
r = np.corrcoef(x, y)[0, 1]
r2 = r**2

print("R2 value:", r2)

df.describe()

plt.figure(figsize=(20, 10))

sns.heatmap(df.corr(),robust=True,cmap='viridis')

data.drop(columns=['OUT_PKTS','out-in_pkts'],axis=1,inplace=True)

data.corr()

data['out_in_bytes_time']=(data.OUT_BYTES/data.IN_BYTES)*(data.FLOW_DURATION_MILLISECONDS*0.001)

data.corr()

data.drop('out_in_bytes_time',axis=1,inplace=True)

data.columns

"""## note
we did an outlier detection using isolation forest, but not outlier was found
"""

column_to_encode = "Attack"

# One-hot encode the column
one_hot = pd.get_dummies(data[column_to_encode])

# Drop the original column
df2 = data.drop(column_to_encode, axis=1)

# Concatenate the one-hot encoded column back to the dataframe
df2 = pd.concat([df2, one_hot], axis=1)

column_to_encode = "Attack"

# One-hot encode the column
one_hot = pd.get_dummies(data[column_to_encode])

# Drop the original column
data = data.drop(column_to_encode, axis=1)

# Concatenate the one-hot encoded column back to the dataframe
data = pd.concat([data, one_hot], axis=1)

data.drop('Theft',axis=1,inplace=True)

data.shape

"""## ANOVA"""

data.drop('Unnamed: 0', axis=1, inplace=True)

data.columns

len(data.columns)

data.info()

X, y = data.drop(['Label', 'Benign', 'DDoS', 'DoS', 'Reconnaissance'], axis=1), df['Label']

X.columns

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

# Load the dataset
# X: input features, y: target variable
X, y = data.drop(['Label', 'Benign', 'DDoS', 'DoS', 'Reconnaissance'], axis=1), df['Label']

# Define the feature selection method
fvalue_selector = SelectKBest(f_classif, k=10)

# Apply the feature selection method to the dataset
X_kbest = fvalue_selector.fit_transform(X, y)
selected_features_num = fvalue_selector.get_support(indices=True)
X.columns[selected_features_num]

data.corr()['Label']

"""after ANOVA we finalised 10 features out of 12
- `'L4_SRC_PORT', 'L4_DST_PORT', 'PROTOCOL', 'L7_PROTO', 'IN_BYTES', 'OUT_BYTES', 'IN_PKTS', 'TCP_FLAGS', 'FLOW_DURATION_MILLISECONDS', 'out-in_bytes'`
"""

data.drop(['Benign', 'DDoS', 'DoS', 'Reconnaissance'], axis=1, inplace=True)

data.columns

df2=data.drop('Label',axis=1)
df2.head()

df2['FLOW_DURATION_MILLISECONDS']*=0.001

column = df2[["IN_PKTS", "IN_BYTES", "OUT_BYTES", "out-in_bytes"]] #"out-in_pkts"


# Normalize the column
normalized_column = (column - column.mean()) / column.std()

# Replace the original column with the normalized column
df2[["IN_PKTS", "IN_BYTES", "OUT_BYTES", "out-in_bytes"]] = normalized_column #"out-in_pkts"

df2.head()

df2.shape

df2=df2.values
df2 = df2.reshape(df2.shape[0], 10, 1)

df2.shape

# Define the percentage for training data
train_percentage = 0.8

# Calculate the index to split the data
split_index = int(df2.shape[0] * train_percentage)

# Split the data into training and validation sets
train_data = df2[:split_index]  # First 80% of data for training
val_data = df2[split_index:]  # Remaining 20% for validation

# If you also have target labels, you can split them accordingly
train_labels = data['Label'].values[:split_index]
val_labels = data['Label'].values[split_index:]

# Print the shapes of the resulting sets
print("X_train shape:", train_data.shape)
print("X_valid shape:", val_data.shape)

data['Label'].values[:384064]

#from sklearn.model_selection import train_test_split

# Split the data into a training set and a test set
#train_data, val_data, train_labels, val_labels = train_test_split(df2, data['Label'].values, test_size=0.2, random_state=0,stratify=data.Label)

"""## MODEL BUILDING : LABEL CLASSIFICATION"""

from keras.models import Sequential
from keras.layers import LSTM, Dense, Bidirectional,Dropout
from sklearn.naive_bayes import GaussianNB
from keras.layers import Input, Embedding, SpatialDropout1D, Bidirectional, LSTM, Dense, Dropout, BatchNormalization
from keras.models import Model
from keras.optimizers import Adam

def create_bilstm_model(input_shape):
    inputs = Input(shape=input_shape)

    # LSTM layers
    lstm_1 = Bidirectional(LSTM(128, return_sequences=True))(inputs)
    lstm_2 = Bidirectional(LSTM(256))(lstm_1)

    # Batch normalization
    batch_norm_1 = BatchNormalization()(lstm_2)

    # Dense layers with dropout
    dense_1 = Dense(128, activation='tanh')(batch_norm_1)
    dropout_1 = Dropout(0.5)(dense_1)

    dense_2 = Dense(64, activation='relu')(dropout_1)
    dense_3 = Dense(64, activation='tanh')(dense_2)
    dropout_2 = Dropout(0.25)(dense_3)

    # Output layer
    output = Dense(1, activation='sigmoid')(dropout_2)

    model = Model(inputs=inputs, outputs=output)

    return model
input_shape = (10, 1) #12
model = create_bilstm_model(input_shape)
print(model.summary())

# Define the Naive Bayes classifier
nb = GaussianNB()

from tensorflow.keras.metrics import Recall, AUC
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

early_stopping=EarlyStopping(monitor='val_loss',patience=5,restore_best_weights=True)
#EarlyStopping: Stop training when a monitored metric has stopped improving.

reduce_lr_on_plateau=ReduceLROnPlateau(monitor='val_loss',factor=0.1,patience=5)
#ReduceLROnPlateau: Reduce learning rate when a metric has stopped improving.
# Compile the BiLSTM model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy',Recall(),AUC()])

from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Assuming X_train, y_train are the training data and labels
class_weights = compute_class_weight(y=data['Label'],classes=np.unique(data['Label']),class_weight='balanced')
class_weights_dict = dict(enumerate(class_weights))
class_weight=class_weights_dict

# Train the BiLSTM model
model.fit(train_data, train_labels, epochs=40, batch_size=128, validation_data=[val_data,val_labels],class_weight=class_weights_dict,
         callbacks=[early_stopping,reduce_lr_on_plateau])

pickle.dump(model, open('/content/drive/MyDrive/LSTM/bilstm.pkl','wb'))

model= pickle.load(open(r'/content/drive/MyDrive/LSTM/bilstm.pkl',"rb"))

test_data=pd.read_csv(r'/content/drive/MyDrive/LSTM/X_test.csv')
test_data = test_data.sort_values(by='FLOW_DURATION_MILLISECONDS', ascending=True)
test_data = test_data.reset_index(drop=True)
test_data

td=test_data.copy()
test_data.drop(columns=['IPV4_SRC_ADDR','IPV4_DST_ADDR','Unnamed: 0'],inplace=True)
test_data['out-in_pkts']=test_data.OUT_PKTS-test_data.IN_PKTS
test_data['out-in_bytes']=test_data.OUT_BYTES-test_data.IN_BYTES
df3 = test_data.drop('Attack', axis=1)
test_data.drop(columns=['OUT_PKTS','out-in_pkts'],axis=1,inplace=True)

column_to_encode = "Attack"
# One-hot encode the column
one_hot = pd.get_dummies(test_data[column_to_encode])
# Drop the original column
df3 = test_data.drop(column_to_encode, axis=1)
# Concatenate the one-hot encoded column back to the dataframe
df3 = pd.concat([df3, one_hot], axis=1)

column_to_encode = "Attack"
# One-hot encode the column
one_hot = pd.get_dummies(test_data[column_to_encode])
# Drop the original column
test_data = test_data.drop(column_to_encode, axis=1)

# Concatenate the one-hot encoded column back to the dataframe
test_data = pd.concat([test_data, one_hot], axis=1)

test_data.drop('Theft',axis=1,inplace=True)
test_data.drop(columns=['Benign','DDoS','DoS','Reconnaissance'],axis=1,inplace=True)

df3=test_data.drop('Label',axis=1)
df3.head()

df3['FLOW_DURATION_MILLISECONDS']*=0.001

column = df3[["IN_PKTS", "IN_BYTES", "OUT_BYTES", "out-in_bytes"]] #"out-in_pkts"
# Normalize the column
normalized_column = (column - column.mean()) / column.std()

# Replace the original column with the normalized column
df3[["IN_PKTS", "IN_BYTES", "OUT_BYTES", "out-in_bytes"]] = normalized_column #"out-in_pkts"

df3=df3.values
df3 = df3.reshape(df3.shape[0], 10, 1)

test_data=df3

data_2d = df2.reshape(480080, 10)

test_data.shape

data2d_test=test_data.reshape(120020, 10)

data_2d.shape

bilstm_output = model.predict(test_data)

bilstm_output.shape

updated_array = np.where(bilstm_output <= 0.5, 0, 1).reshape(-1)

# Print the updated array
print(updated_array)

updated_array.shape

data_2d.shape,data['Label'].shape

from sklearn.ensemble import RandomForestClassifier

# Create a Random Forest classifier using the BiLSTM outputs as features
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(data_2d,data['Label'].values)

rf_predictions = rf.predict(data2d_test)
accuracy_rf = np.mean(rf_predictions == td['Label'])
print("Accuracy of Random Forest:", accuracy_rf)

rf_predictions.shape

from sklearn.metrics import classification_report

# For Random Forest
print("Classification Report for Random Forest:")
print(classification_report(td['Label'], rf_predictions))

from sklearn.metrics import confusion_matrix

# For Random Forest
confusion_rf = confusion_matrix(td['Label'], rf_predictions)
print("Confusion Matrix for Random Forest:")
print(confusion_rf)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier

# Define the models
knn_classifier = KNeighborsClassifier()
gaussian_nb_classifier = GaussianNB()
random_forest_classifier = RandomForestClassifier()
decision_tree_classifier = DecisionTreeClassifier()
logistic_regression_classifier = LogisticRegression()
ada_boost_classifier = AdaBoostClassifier()
gradient_boosting_classifier = GradientBoostingClassifier()
xgb_classifier = XGBClassifier()

from sklearn.metrics import classification_report, confusion_matrix
# Define a dictionary to store results
results = {}

# Iterate through each classifier
classifiers = {
    'KNeighborsClassifier': knn_classifier,
    'GaussianNB': gaussian_nb_classifier,
    'RandomForestClassifier': random_forest_classifier,
    'DecisionTreeClassifier': decision_tree_classifier,
    'LogisticRegression': logistic_regression_classifier,
    'AdaBoostClassifier': ada_boost_classifier,
    'GradientBoostingClassifier': gradient_boosting_classifier,
    'XGBClassifier': xgb_classifier,
}

for classifier_name, classifier in classifiers.items():
    # Train the classifier
    classifier.fit(data_2d, data['Label'].values)

    # Make predictions
    predictions = classifier.predict(data2d_test)

    # Calculate accuracy
    accuracy = np.mean(predictions == td['Label'])

    # Print the accuracy
    print(f"Accuracy of {classifier_name}: {accuracy}")

    # Calculate and print the classification report
    classification_rep = classification_report(td['Label'], predictions)
    print(f"Classification Report for {classifier_name}:\n{classification_rep}")

    # Calculate and print the confusion matrix
    confusion_mat = confusion_matrix(td['Label'], predictions)
    print(f"Confusion Matrix for {classifier_name}:\n{confusion_mat}")
    print("\n")

    # Store the results in the dictionary
    results[classifier_name] = {
        'Accuracy': accuracy,
        'Classification Report': classification_rep,
        'Confusion Matrix': confusion_mat
    }

"""# ENSEMBLE"""

predictions1 = knn_classifier.predict(data2d_test)
predictions2 = random_forest_classifier.predict(data2d_test)

"""2116 600
1745 115596

p55 r0.78
"""

# Add the arrays element-wise
sum_array = 0.89*predictions1 + 0.71*predictions2 + 1*updated_array

# Calculate the average
avg = sum_array/1.16

result = np.where(avg <= 0.5, 0, 1)
# Print the updated array
print(result)

result.shape

classification_rep = classification_report(td['Label'], result)
print(f"Classification Report for \n{classification_rep}")

    # Calculate and print the confusion matrix
confusion_mat = confusion_matrix(td['Label'], result)
print(f"Confusion Matrix :\n{confusion_mat}")
print("\n")

"""BILSTM CLASSIFICATION REPORT"""

classification_rep = classification_report(td['Label'], updated_array)
print(f"Classification Report for \n{classification_rep}")

    # Calculate and print the confusion matrix
confusion_mat = confusion_matrix(td['Label'], updated_array)
print(f"Confusion Matrix :\n{confusion_mat}")
print("\n")

"""#ATTACK CLASSIFICATION"""

X_train = pd.read_csv('/content/drive/MyDrive/LSTM_project/FINAL FINAL/new_train_data.csv')
X_test = pd.read_csv('/content/drive/MyDrive/LSTM_project/FINAL FINAL/new_test_data.csv')

X_test.head()

print(X_train.shape,X_test.shape)

df_train = X_train[X_train['Label']==1]
df_test = X_test[X_test['predictions']==1]

print(df_train.shape,df_test.shape)

df_train.columns

df_test.columns

df_train.drop(columns=['Unnamed: 0','IPV4_SRC_ADDR','IPV4_DST_ADDR','Label'],inplace=True)
df_test.drop(columns=['Unnamed: 0','IPV4_SRC_ADDR','IPV4_DST_ADDR','predictions'],inplace=True)

df_train.columns

df_test.columns

df_train['out-in_pkts']=df_train.OUT_PKTS-df_train.IN_PKTS
df_train['out-in_bytes']=df_train.OUT_BYTES-df_train.IN_BYTES

df_test['out-in_pkts']=df_test.OUT_PKTS-df_test.IN_PKTS
df_test['out-in_bytes']=df_test.OUT_BYTES-df_test.IN_BYTES

df_train.drop(columns=['OUT_PKTS','out-in_pkts'],axis=1,inplace=True)
df_test.drop(columns=['OUT_PKTS','out-in_pkts'],axis=1,inplace=True)

df_train.columns

df_train['Attack'].unique()

df_test['Attack'].unique()

df_test = df_test.drop(df_test[df_test['Attack'] == 'Benign'].index)
print(df_test.shape)

df_test['Attack'].value_counts()

# Label Encoding the target

from sklearn.preprocessing import LabelEncoder

le=LabelEncoder()
le.fit(df_train['Attack'])
df_train['Attack_type'] = le.transform(df_train['Attack'])
df_test['Attack_type'] = le.transform(df_test['Attack'])

le.classes_

df_train = df_train.drop('Attack',axis=1)
df_test = df_test.drop('Attack',axis=1)

df_train.columns

print(df_train.shape,df_test.shape)

"""### FEATURE SELECTION"""

X_train_m2= df_train.drop('Attack_type',axis=1)
y_train_m2= df_train['Attack_type']
print(X_train_m2.shape,y_train_m2.shape)

X_test_m2=df_test.drop('Attack_type',axis=1)
y_test_m2=df_test['Attack_type']
print(X_test_m2.shape,y_test_m2.shape)

X_train_m2.info()

X_test_m2.info()

X_train_m2['FLOW_DURATION_MILLISECONDS']*=0.001
X_test_m2['FLOW_DURATION_MILLISECONDS']*=0.001

print(X_train_m2.shape,X_test_m2.shape)

X_train_m2.head()

from sklearn.preprocessing import MinMaxScaler
mms=MinMaxScaler(feature_range=(0,1))
X_train_scaled_m2 = mms.fit_transform(X_train_m2)
X_test_scaled_m2 = mms.transform(X_test_m2)
print(X_train_scaled_m2.shape,X_test_scaled_m2.shape)

y_train_m2.value_counts()

y_test_m2.value_counts()

"""# MODEL BUILDING

## KNN CLASSIFIER
"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold

knn = KNeighborsClassifier()
k_range = list(range(5,11))
param_grid = {
    'n_neighbors': k_range,
    'metric':['euclidean'],#'manhatten','minkowski'
    'algorithm' : ['auto', 'kd_tree',],# 'ball_tree','brute'
    'weights' : ['uniform'],#'distance'
}
# defining parameter range

cv_method = RepeatedStratifiedKFold(n_splits=5,  n_repeats=1)
scorer = make_scorer(f1_score, average='macro')
grid = GridSearchCV(knn, param_grid, cv=cv_method, scoring=scorer, return_train_score=False,verbose=10)
# fitting the model for grid search
grid_search_knn=grid.fit(X_train_scaled_m2,y_train_m2)

print(grid_search_knn.best_params_)

from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
knn = KNeighborsClassifier(algorithm = 'auto', metric = 'euclidean',n_neighbors = 100, weights = 'uniform')
knn.fit(X_train_scaled_m2,y_train_m2)
y_pred_knn_m2= knn.predict(X_test_scaled_m2)
mean_acc = metrics.accuracy_score(y_test_m2, y_pred_knn_m2)

# Get the hyperparameters
hyperparameters = knn.get_params()

# Print the hyperparameters
print("Hyperparameters:")
for param, value in hyperparameters.items():
    print(f"{param}: {value}")

from sklearn.metrics import classification_report
print(classification_report(y_test_m2, y_pred_knn_m2)) #k = 100

# Confusion Matrix
from sklearn.metrics import confusion_matrix
print("Confusion Matrix:\n")
print(confusion_matrix(y_test_m2,y_pred_knn_m2)) #k= 100

from sklearn.metrics import classification_report
print(classification_report(y_test_m2, y_pred_knn_m2)) #k = 200

# Confusion Matrix
from sklearn.metrics import confusion_matrix
print("Confusion Matrix:\n")
print(confusion_matrix(y_test_m2,y_pred_knn_m2)) #k= 200

"""## Other Classification Algorithms"""

from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier

# Define the models
gradient_boosting_classifier = GradientBoostingClassifier()
gaussian_nb_classifier = GaussianNB()
mlp_classifier= MLPClassifier()
lda_classifier = LinearDiscriminantAnalysis()
qda_classfier = QuadraticDiscriminantAnalysis()

from sklearn.metrics import classification_report, confusion_matrix
# Define a dictionary to store results
results = {}

# Iterate through each classifier
classifiers = {
    'GradientBoostingClassifier': gradient_boosting_classifier,
    'GaussianNB': gaussian_nb_classifier,
    'MLPClassifier': mlp_classifier,
    'LinearDiscriminantAnalysis': lda_classifier,
    'QuadraticDiscriminantAnalysis': qda_classfier
}

for classifier_name, classifier in classifiers.items():
    # Train the classifier
    classifier.fit(X_train_scaled_m2,y_train_m2)

    # Make predictions
    predictions = classifier.predict(X_test_scaled_m2)

    # Calculate accuracy
    accuracy = metrics.accuracy_score(y_test_m2, predictions)

    # Print the accuracy
    print(f"Accuracy of {classifier_name}: {accuracy}")

    # Calculate and print the classification report
    classification_rep = classification_report(y_test_m2, predictions)
    print(f"Classification Report for {classifier_name}:\n{classification_rep}")

    # Calculate and print the confusion matrix
    confusion_mat = confusion_matrix(y_test_m2, predictions)
    print(f"Confusion Matrix for {classifier_name}:\n{confusion_mat}")
    print("\n")

    # Store the results in the dictionary
    results[classifier_name] = {
        'Accuracy': accuracy,
        'Classification Report': classification_rep,
        'Confusion Matrix': confusion_mat
    }

"""## GRADIENT BOOSTING CLASSIFIER"""

from sklearn.ensemble import GradientBoostingClassifier
gbc = GradientBoostingClassifier()
gbc.fit(X_train_scaled_m2,y_train_m2)

# Get the hyperparameters
hyperparameters = gbc.get_params()

# Print the hyperparameters
print("Hyperparameters:")
for param, value in hyperparameters.items():
    print(f"{param}: {value}")

y_pred_gbc_m2 = gbc.predict(X_test_scaled_m2)

# Calculate and print the classification report
from sklearn.metrics import classification_report
classification_rep = classification_report(y_test_m2, y_pred_gbc_m2)
print(classification_rep)

# Calculate and print the confusion matrix
from sklearn.metrics import confusion_matrix
confusion_mat = confusion_matrix(y_test_m2, y_pred_gbc_m2)
print(confusion_mat)

"""## MLP CLASSIFIER"""

from sklearn.neural_network import MLPClassifier
mlp= MLPClassifier()
mlp.fit(X_train_scaled_m2,y_train_m2)

# Get the hyperparameters
hyperparameters = mlp.get_params()

# Print the hyperparameters
print("Hyperparameters:")
for param, value in hyperparameters.items():
    print(f"{param}: {value}")

y_pred_mlp_m2 = mlp.predict(X_test_scaled_m2)

classification_rep = classification_report(y_test_m2, y_pred_mlp_m2)
print(classification_rep)

confusion_mat = confusion_matrix(y_test_m2, y_pred_mlp_m2)
print(confusion_mat)

"""## QDA CLASSIFIER"""

from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
qda = QuadraticDiscriminantAnalysis()
qda.fit(X_train_scaled_m2,y_train_m2)

# Get the hyperparameters
hyperparameters = qda.get_params()

# Print the hyperparameters
print("Hyperparameters:")
for param, value in hyperparameters.items():
    print(f"{param}: {value}")

y_pred_qda_m2 = qda.predict(X_test_scaled_m2)

classification_rep = classification_report(y_test_m2, y_pred_qda_m2)
print(classification_rep)

confusion_mat = confusion_matrix(y_test_m2, y_pred_qda_m2)
print(confusion_mat)

"""## ENSEMBLING"""

y_pred_knn_m2_proba = knn.predict_proba(X_test_scaled_m2)
y_pred_gbc_m2_proba = gbc.predict_proba(X_test_scaled_m2)
y_pred_mlp_m2_proba = mlp.predict_proba(X_test_scaled_m2)
y_pred_qda_m2_proba = qda.predict_proba(X_test_scaled_m2)

y_pred_ensemble_m2 = ((y_pred_knn_m2_proba + y_pred_gbc_m2_proba + y_pred_mlp_m2_proba+ y_pred_qda_m2_proba)/4).argmax(axis=1)

classification_rep = classification_report(y_test_m2, y_pred_ensemble_m2)
print(classification_rep)

confusion_mat = confusion_matrix(y_test_m2, y_pred_ensemble_m2)
print(confusion_mat)

"""### ENSEMBLE NEW (KNN + GBC)"""

y_pred_knn_m2_proba = knn.predict_proba(X_test_scaled_m2)
y_pred_gbc_m2_proba = gbc.predict_proba(X_test_scaled_m2)

y_pred_ensemble_m2_new = ((y_pred_knn_m2_proba + y_pred_gbc_m2_proba)/2).argmax(axis=1)

classification_rep = classification_report(y_test_m2, y_pred_ensemble_m2_new)
print(classification_rep)

confusion_mat = confusion_matrix(y_test_m2, y_pred_ensemble_m2_new)
print(confusion_mat)