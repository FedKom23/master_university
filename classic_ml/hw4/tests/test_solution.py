import timeit
from collections import defaultdict

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from hw4.solution import GBCustomClassifier


@pytest.mark.parametrize('params', [{
    'max_depth': 7,
    'n_estimators': 7,
    'learning_rate': 0.7,
    'min_samples_split': 7,
    'criterion': 'friedman_mse',
}])
def test_arguments(params: dict):
    obj = GBCustomClassifier(**params)
    for key, value in params.items():
        assert obj.__getattribute__(key) == value


def test_metrics():
    accuracy_values = defaultdict(list)

    rocauc_values = defaultdict(list)
    timings = defaultdict(list)

    for i in range(50):

        seed = i
        X, y = make_classification(
            n_samples=1000,
            random_state=seed,
            n_classes=3,
            n_informative=6
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=seed)

        params = {
            'max_depth': i % 6 + 1,
            'n_estimators': i + 1,
            'learning_rate': 0.1 + (i % 10) * 0.05,
            'min_samples_split': 2 + i % 20,
            'criterion': 'friedman_mse',
        }

        classes_for_test = {
            'custom': GBCustomClassifier,
            'sklearn': GradientBoostingClassifier,
        }

        for model_name, ModelClass in classes_for_test.items():
            start = timeit.default_timer()

            model = ModelClass(**params)
            model.fit(X_train, y_train)
            y_pred_scores = model.predict_proba(X_test)
            assert y_pred_scores.sum(axis=1).mean() == 1.0
            y_pred = model.predict(X_test)
            rocauc_values[model_name].append(roc_auc_score(
                y_test, y_pred_scores, multi_class='ovo'))
            accuracy_values[model_name].append(
                accuracy_score(y_test, y_pred))

            stop = timeit.default_timer()
            execution_time = stop - start
            timings[model_name].append(execution_time)

    tol = 0.03
    assert np.mean(accuracy_values['custom']) + \
        tol > np.mean(accuracy_values['sklearn'])
    assert np.mean(rocauc_values['custom']) + \
        tol > np.mean(rocauc_values['sklearn'])
