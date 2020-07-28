# Bayesian Optimization with Gaussian Process
import pandas as pd
import numpy as np
from sklearn import ensemble
from sklearn import metrics
from sklearn import model_selection


from functools import partial
from skopt import space
from skopt import gp_minimize
from hyperopt import hp, fmin, tpe, Trials
from hyperopt.pyll.base import scope

def optimize(params, x, y):
    model = ensemble.RandomForestClassifier(**params)
    kf = model_selection.KFold(n_splits=5)
    accuracies = []
    for idx in kf.split(X=x, y=y):
        train_idx, test_idx = idx[0], idx[1]
        xtrain = x[train_idx]
        ytrain = y[train_idx]

        xtest = x[test_idx]
        ytest = y[test_idx]

        model.fit(xtrain, ytrain)
        preds = model.predict(xtest)
        fold_acc = metrics.accuracy_score(ytest, preds)
        accuracies.append(fold_acc)

    return -1.0 * np.mean(accuracies)
    


if __name__ == "__main__":
    df = pd.read_csv("../input/mobile_train.csv")
    X = df.drop("price_range", axis = 1).values #Features
    y = df.price_range.values

    param_space = {
        "max_depth": scope.int(hp.quniform("max_depth", 3, 15, 1)),
        "n_estimators": scope.int(hp.quniform("n_estimators", 100, 600, 1)),
        "criterion": hp.choice("criterion", ["gini", "entropy"]),
        "max_features": hp.uniform("max_features", 0.01, 1)
    }


    optimization_function = partial(
        optimize,
        x=X,
        y=y
    )

    trials = Trials()

    result = fmin(
        fn=optimization_function,
        space=param_space,
        algo=tpe.suggest,
        max_evals=15,
        trials=trials,
    )

    print(result)