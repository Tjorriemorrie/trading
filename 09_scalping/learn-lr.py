import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from pprint import pprint

X = np.array([
    [1, 3, 5],
    [1, 2, 3],
    [2, 5, 7],
    [2, 3, 6],
])
#pprint(sample)
print '\nX Shape'
print X.shape

# Split the data into training/testing sets
X_train = X[:2]
X_test = X[-2:]
print '\nX_train'
pprint(X_train)
print '\nX_test'
pprint(X_test)

# Split the targets into training/testing sets
Y = np.array([
    [3, 5, 8],
    [3, 6, 9],
    [1, 2, 5],
    [2, 4, 8],
])
print '\nY Shape'
print Y.shape
Y_train = Y[:-2]
Y_test = Y[-2:]
print '\nY_train'
pprint(Y_train)
print '\nY_test'
pprint(Y_test)

# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(X_train, Y_train)

# The coefficients
print('Coefficients: \n', regr.coef_)
# The mean square error
print("Residual sum of squares: %.2f"
      % np.mean((regr.predict(X_test) - Y_test) ** 2))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % regr.score(X_test, Y_test))

# Plot outputs
plt.scatter(X_test, Y_test,  color='black')
plt.plot(X_test, regr.predict(X_test), color='blue',
         linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()