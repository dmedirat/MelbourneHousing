# -*- coding: utf-8 -*-
"""ML_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yqrO89A8MGizMeZFWiPcKkLdxrF-22eS

## **Import Libraries**
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.model_selection import KFold
from sklearn.svm import SVR
import warnings
warnings.filterwarnings('ignore')

# Checking if connected to GPU
"""import tensorflow as tf
device_name = tf.test.gpu_device_name()
if tf.test.is_gpu_available:
  print('Found GPU at: {}'.format(device_name))
else:
  raise SystemError('GPU device not found')
  """

"""## **Fetching Data**"""

data = pd.read_excel('output8.xlsx')
data1 = pd.read_csv('Melbourne_housing_FULL.csv')

"""## **Data Exploration**"""

data.shape

data.columns

# Check Data Types
data.info()

# Check Numeric Values
data.describe().transpose()
## This shows that Postal code is being taken as a numeric value, but it should be categorical.

"""## **Handling missing values**"""

#Look for missing/null values
data.isnull().sum()

"""### **Price**"""

# Remove any rows which have price as null because that is our target value.
data = data.dropna(axis=0, subset=['Price'])
data = data.reset_index()

"""### **Longitude and Lattitude**"""

# if we couldnt find the Longtitude and Lattitude using the geopy API, then put the median.
data['Lattitude']= data['Lattitude'].fillna(data['Lattitude'].median())
data['Longtitude']= data['Longtitude'].fillna(data['Longtitude'].median())

"""###**PostCode**"""

# we can use geooy to find post code
geolocator = Nominatim(user_agent="Melbourne Housing Prediction")
location = geolocator.geocode("Brian St Fawkner Lot")
if location is not None:
  print(location.address)

data['Postcode']= data['Postcode'].fillna(3060)

"""### **Others**"""

# Replacing data with median
data['YearBuilt']= data['YearBuilt'].fillna(data['YearBuilt'].median())

# Replacing data with mean
# only 1 row has missing distance, can replace with mean value.
data['Distance']= data['Distance'].fillna(data['Distance'].mean())

# Replacing 
data['Bathroom']= data['Bathroom'].fillna(data['Bathroom'].mean())
data['Car']= data['Car'].fillna(data['Car'].mean())
data['Landsize']= data['Landsize'].fillna(data['Landsize'].mean()) 
data['BuildingArea']= data['BuildingArea'].fillna(data['BuildingArea'].mean())

#Look for missing/null values
data.isnull().sum()

# Replacing categorical data with mode
data['CouncilArea']= data['CouncilArea'].fillna(data['CouncilArea'].mode()[0])
data['Regionname']= data['Regionname'].fillna(data['Regionname'].mode()[0])
data['Propertycount']= data['Propertycount'].fillna(data['Propertycount'].mode()[0])

"""### **Bedroom2**"""

sns.lmplot(data= data, x='Bedroom2', y='Rooms')

# remove bedroom2, it is same as room. 
data= data.drop(['Bedroom2'], axis=1)

data['Bathroom'] = pd.to_numeric(data['Bathroom']).round(0).astype(int)
data['Car'] = pd.to_numeric(data['Car']).round(0).astype(int)

data.shape

"""## **Outlier Detection and Removal**

### Building Area
"""

sns.boxplot(data = data, y = 'BuildingArea')

data['BuildingArea'].loc[data.BuildingArea<1].count()

data.loc[data.BuildingArea<1].head()

#use the unary operator ~ to delete the rows
data = data[~(data['BuildingArea'] < 1)]  
#check the deletion
data['BuildingArea'].loc[data.BuildingArea<1].count()

data.loc[data.BuildingArea>40000].transpose()

#use the unary operator ~ to delete the rows
data = data[~(data.BuildingArea>40000)]  
#check the deletion
data['BuildingArea'].loc[data.BuildingArea>40000].count()

"""### **LandSize**"""

sns.boxplot(data = data, y = 'Landsize')

data['Landsize'].loc[data.Landsize<1].count()

#use the unary operator ~ to delete the rows
data = data[~(data['Landsize'] < 1)]  
#check the deletion
data['Landsize'].loc[data.Landsize<1].count()

"""### **Bathroom**"""

data['Bathroom'].value_counts()

data.loc[data.Bathroom>7].head(10)

"""### **YearBuilt**"""

data['YearBuilt'].loc[data.YearBuilt>2019]

#replace 2106 with 2016
data['YearBuilt'].replace([2106], [2016], inplace=True)

data['YearBuilt'].loc[data.YearBuilt<1200]

data.loc[12754]

data.shape

"""## **Feature Engineering**

### **Get Age from YearBuilt**
"""

# Adding age
data['Age'] = 2019 - data['YearBuilt']

"""### **Get season from Date**"""

data['Date_new'] = pd.to_datetime(data['Date'])

# calculate day of year
data['doy'] = data['Date_new'].dt.dayofyear
# Create year
data['Year'] = data['Date_new'].dt.year

#to divide by season it's better to use the day of the year instead of the months
autumn = range(70, 150)
winter = range(150, 240)
spring = range(240, 330)
# summer = everything else

daje = []
for i in data['doy']:
    if i in spring:
        season = 'spring'
    elif i in winter:
        season = 'winter'
    elif i in autumn:
        season = 'autumn'
    else:
        season = 'summer'
    daje.append(season)   

#add the resulting column to the dataframe (after transforming it as a Series)
data['season']= pd.Series(daje)

"""### **Feature Selection**"""

# correlation matrix
corrmat = data.corr()
f, ax = plt.subplots(figsize=(13, 8))
sns.set(font_scale=1)
sns.heatmap(corrmat,annot=True, square=True, fmt='.2f', vmax=.8);

"""### **Drop useless columns**"""

## We have Longitude and Latitude, which are nothing but Suburb and Address converted to numeric. 
# So We can drop Suburb and Address.
# We have fetched age from YearBuilt, so that is also not required now.
data =data.drop(columns=['Suburb', 'Address', 'Date','Method','SellerG','CouncilArea','Postcode','YearBuilt',
                         'Date_new','doy'])

"""### **Type to Dummy**"""

dummy = pd.get_dummies(data['Type'])
data = pd.concat([data, dummy], axis=1)

dummy = pd.get_dummies(data['Regionname'])
data = pd.concat([data, dummy], axis=1)


dummy = pd.get_dummies(data['season'])
data = pd.concat([data, dummy], axis=1)

data =data.drop(columns=['Type', 'Regionname', 'season'])

# dropping price here because it is target value
# dropping Lattitude and Longtitude because they have negative values and SelectKBest does not allow negative values.
X = data[data.columns.drop(['Price','Lattitude', 'Longtitude'])]
Y = data['Price']

selector = SelectKBest(chi2, k=10)
selector.fit(X, Y)
X_new = selector.transform(X)
print(X.columns[selector.get_support(indices=True)]) #top 3 columns

# %config InlineBackend.figure_format = 'svg'
#Plot the SalePrice of each instance
sns.distplot(data['Price'])

#skewness and kurtosis
print("Skewness: %f" % data['Price'].skew())
print("Kurtosis: %f" % data['Price'].kurt())

data.plot(kind="scatter", x="Longtitude", y="Lattitude", alpha=0.4,
c=data.Price, cmap=plt.get_cmap("jet"), label= 'Price by location', figsize=(10,7)) 
plt.ylabel("Latitude", fontsize=14)

plt.legend(fontsize=14)

"""## **Min max scaling**"""

features = ['Rooms',  'Distance', 'Bathroom', 'Car', 'Landsize',
       'BuildingArea', 'Lattitude', 'Longtitude', 'Propertycount', 'Age',
       'Year', 'h', 't', 'u', 'Eastern Metropolitan', 'Eastern Victoria',
       'Northern Metropolitan', 'Northern Victoria',
       'South-Eastern Metropolitan', 'Southern Metropolitan',
       'Western Metropolitan', 'Western Victoria', 'autumn', 'spring', 'summer',
       'winter','Price']

normalized_data = data[features]

# Normalization using Min-Max Scaler
scaler = MinMaxScaler()
scaler.fit(normalized_data)
normalized_data = pd.DataFrame(scaler.transform(normalized_data), index=normalized_data.index, columns = normalized_data.columns)

normalized_data.to_excel("processedData.xlsx")

X = normalized_data[normalized_data.columns.drop(['Price'])]
y = normalized_data['Price']

X.describe().transpose()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

"""## **Utility functions**"""

def metrices(y_test, y_predicted, model, X_test):
  # calculate the spearman's correlation between two variables
  from numpy.random import rand
  from numpy.random import seed
  from scipy.stats import spearmanr
  # seed random number generator
  seed(1)
  
  # calculate spearman's correlation
  coef, p = spearmanr(y_test, y_predicted)
  
  print("Mean Absolute Error:", mean_absolute_error(y_test, y_predicted))
  print('Mean Square Error:', mean_squared_error(y_test, y_predicted))
  print('Root Mean Square Error:', np.sqrt(mean_squared_error(y_test, y_predicted)))
  """ RuntimeWarning: Degrees of freedom <= 0 for slice
  occurs when you use the wrong shape, e.g.:
  """
  print('Pearson Correlation coefficient:',np.corrcoef(y_test.T, y_predicted.T)[0, 1])
  print('Spearmans correlation coefficient:',  coef)
  print('Model R^2 score:', model.score(X_test, y_test))

def runModel(model):
  model.fit(X_train, y_train)
  y_predicted = model.predict(X_test)

  metrices(y_test, y_predicted, model, X_test)

def findBestParams(model):
  from sklearn.metrics import r2_score, mean_squared_error
  from sklearn.model_selection import  GridSearchCV

  params = {
      'n_estimators': [10, 30, 100, 300, 400],
      'max_depth': [3, 5, 7,10,15,20]
  }
  grid_search = GridSearchCV(model, param_grid=params, cv=3, scoring='neg_mean_squared_error', n_jobs=-1)
  grid_search.fit(X_train, y_train)
  preds = grid_search.predict(X_test)
  # plt.figure()
  # plt.plot(list(params.values())[0],(-1*grid_search.cv_results_['mean_test_score'])**0.5)
  # plt.xlabel('Number of trees')
  # plt.ylabel('3-fold CV RMSE')
  print("Best params found: {}".format(grid_search.best_params_))
  print("RMSE score: {}".format(mean_squared_error(y_test, preds) ** 0.5))

"""## **1. Linear Regression**"""

linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
y_predicted = linear_model.predict(X_test)

metrices(y_test, y_predicted, linear_model, X_test)

"""## **1. Linear Regression-K fold**"""

from sklearn.model_selection import validation_curve

kf = KFold(n_splits=10, random_state=None)
list_training_error = []
list_testing_error1 = []

for train_index, test_index in kf.split(X,y):
  X_train, X_test = X.iloc[train_index], X.iloc[test_index] 
  y_train, y_test = y.iloc[train_index], y.iloc[test_index]
  
  
  model = LinearRegression()
  model.fit(X_train, y_train)
  y_train_data_pred = model.predict(X_train)
  y_test_data_pred = model.predict(X_test) 

  fold_training_error = mean_absolute_error(y_train, y_train_data_pred)        
  fold_testing_error = mean_absolute_error(y_test, y_test_data_pred)
  list_training_error.append(fold_training_error)
  list_testing_error1.append(fold_testing_error)

plt.subplot(1,2,1)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_training_error).ravel())
plt.xlabel('number of fold')
plt.ylabel('training error')
plt.title('Training error across folds')
plt.tight_layout()

plt.subplot(1,2,2)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_testing_error1).ravel())
plt.xlabel('number of fold')
plt.ylabel('testing error')
plt.title('Testing error across folds')
plt.tight_layout()
plt.show()

"""## **2. Decision Tree Regressor**"""

decision_tree_model = DecisionTreeRegressor()
decision_tree_model.fit(X_train, y_train)
y_predicted = decision_tree_model.predict(X_test)

metrices(y_test, y_predicted, decision_tree_model, X_test)

"""## **2. Decision Tree Regressor-K fold**"""

from sklearn.model_selection import validation_curve

kf = KFold(n_splits=10, random_state=None)
list_training_error = []
list_testing_error2 = []

for train_index, test_index in kf.split(X,y):
  X_train, X_test = X.iloc[train_index], X.iloc[test_index] 
  y_train, y_test = y.iloc[train_index], y.iloc[test_index]
  
  
  model = DecisionTreeRegressor()
  model.fit(X_train, y_train)
  y_train_data_pred = model.predict(X_train)
  y_test_data_pred = model.predict(X_test) 

  fold_training_error = mean_absolute_error(y_train, y_train_data_pred)        
  fold_testing_error = mean_absolute_error(y_test, y_test_data_pred)
  list_training_error.append(fold_training_error)
  list_testing_error2.append(fold_testing_error)

plt.subplot(1,2,1)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_training_error).ravel())
plt.xlabel('number of fold')
plt.ylabel('training error')
plt.title('Training error across folds')
plt.tight_layout()

plt.subplot(1,2,2)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_testing_error2).ravel())
plt.xlabel('number of fold')
plt.ylabel('testing error')
plt.title('Testing error across folds')
plt.tight_layout()
plt.show()

"""## **3. Nearest Neighbors**"""

from sklearn import neighbors

n_neighbors = 5

knn = neighbors.KNeighborsRegressor(n_neighbors, weights='distance')
knn.fit(X_train, y_train)
y_predicted = knn.predict(X_test)

metrices(y_test, y_predicted, knn, X_test)

"""## **3. Nearest Neighbors-K fold**"""

from sklearn.model_selection import validation_curve

kf = KFold(n_splits=10, random_state=None)
list_training_error = []
list_testing_error3 = []

for train_index, test_index in kf.split(X,y):
  X_train, X_test = X.iloc[train_index], X.iloc[test_index] 
  y_train, y_test = y.iloc[train_index], y.iloc[test_index]
  
  
  model = neighbors.KNeighborsRegressor(n_neighbors, weights='distance')
  model.fit(X_train, y_train)
  y_train_data_pred = model.predict(X_train)
  y_test_data_pred = model.predict(X_test) 

  fold_training_error = mean_absolute_error(y_train, y_train_data_pred)        
  fold_testing_error = mean_absolute_error(y_test, y_test_data_pred)
  list_training_error.append(fold_training_error)
  list_testing_error3.append(fold_testing_error)

plt.subplot(1,2,1)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_training_error).ravel())
plt.xlabel('number of fold')
plt.ylabel('training error')
plt.title('Training error across folds')
plt.tight_layout()

plt.subplot(1,2,2)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_testing_error3).ravel())
plt.xlabel('number of fold')
plt.ylabel('testing error')
plt.title('Testing error across folds')
plt.tight_layout()
plt.show()

"""## **4. BaggingRegressor**"""

from sklearn.ensemble import BaggingRegressor

bagging_model = BaggingRegressor(DecisionTreeRegressor(random_state=1))
bagging_model.fit(X_train, y_train)
y_predicted = bagging_model.predict(X_test)

metrices(y_test, y_predicted, bagging_model, X_test)

"""## **4. BaggingRegressor-K fold**"""

from sklearn.model_selection import validation_curve

kf = KFold(n_splits=10, random_state=None)
list_training_error = []
list_testing_error4 = []

for train_index, test_index in kf.split(X,y):
  X_train, X_test = X.iloc[train_index], X.iloc[test_index] 
  y_train, y_test = y.iloc[train_index], y.iloc[test_index]
  
  
  model = BaggingRegressor(DecisionTreeRegressor(random_state=1))
  model.fit(X_train, y_train)
  y_train_data_pred = model.predict(X_train)
  y_test_data_pred = model.predict(X_test) 

  fold_training_error = mean_absolute_error(y_train, y_train_data_pred)        
  fold_testing_error = mean_absolute_error(y_test, y_test_data_pred)
  list_training_error.append(fold_training_error)
  list_testing_error4.append(fold_testing_error)

plt.subplot(1,2,1)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_training_error).ravel())
plt.xlabel('number of fold')
plt.ylabel('training error')
plt.title('Training error across folds')
plt.tight_layout()

plt.subplot(1,2,2)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_testing_error4).ravel())
plt.xlabel('number of fold')
plt.ylabel('testing error')
plt.title('Testing error across folds')
plt.tight_layout()
plt.show()

"""## **5. Random Forest Regressor**"""

random_forest_model = RandomForestRegressor()
random_forest_model.fit(X_train, y_train)
y_predicted = random_forest_model.predict(X_test)

metrices(y_test, y_predicted, random_forest_model, X_test)

"""## **5. Random Forest Regressor-K fold**"""

from sklearn.model_selection import validation_curve

kf = KFold(n_splits=10, random_state=None)
list_training_error = []
list_testing_error5 = []

for train_index, test_index in kf.split(X,y):
  X_train, X_test = X.iloc[train_index], X.iloc[test_index] 
  y_train, y_test = y.iloc[train_index], y.iloc[test_index]
  
  
  model = RandomForestRegressor()
  model.fit(X_train, y_train)
  y_train_data_pred = model.predict(X_train)
  y_test_data_pred = model.predict(X_test) 

  fold_training_error = mean_absolute_error(y_train, y_train_data_pred)        
  fold_testing_error = mean_absolute_error(y_test, y_test_data_pred)
  list_training_error.append(fold_training_error)
  list_testing_error5.append(fold_testing_error)

plt.subplot(1,2,1)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_training_error).ravel())
plt.xlabel('number of fold')
plt.ylabel('training error')
plt.title('Training error across folds')
plt.tight_layout()

plt.subplot(1,2,2)
plt.plot(range(1, kf.get_n_splits() + 1), np.array(list_testing_error5).ravel())
plt.xlabel('number of fold')
plt.ylabel('testing error')
plt.title('Testing error across folds')
plt.tight_layout()
plt.show()

"""## **Statistical Testing**"""

from scipy.stats import friedmanchisquare

list_testing_error5
stat, p = friedmanchisquare(list_testing_error1,list_testing_error2,list_testing_error3,list_testing_error4, list_testing_error5)
print('Statistics=%.3f, p=%.3f' % (stat, p))
# interpret
alpha = 0.05
if p > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')