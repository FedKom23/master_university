import numpy as np

from sklearn.tree import DecisionTreeRegressor


class GBCustomClassifier:
    def __init__(
        self,
        max_depth=3,
        learning_rate=0.1,
        n_estimators=100,
        min_samples_split=2,
        criterion='friedman_mse',
    ):
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.min_samples_split = min_samples_split
        self.criterion = criterion

    def fit(self, X, y):
        self.classes = np.unique(y)
        self.kolvo = len(self.classes)
        self.trees = [[] for _ in range(self.kolvo)]
        for idx, label in enumerate(self.classes):
            y_label = (y == label).astype(int)
            y_pred = np.zeros(y.shape)
            for i in range(self.n_estimators):
                delta = y_label - y_pred
                tree = DecisionTreeRegressor(
                    max_depth=self.max_depth,
                    criterion=self.criterion,
                    min_samples_split=self.min_samples_split,
                )
                tree.fit(X, delta)
                self.trees[idx].append(tree)
                y_pred += self.learning_rate * tree.predict(X)

    def predict(self, X):
        proba = self.predict_proba(X)
        return self.classes[np.argmax(proba, axis=1)]

    def predict_proba(self, X):
        scores = np.zeros((X.shape[0], self.kolvo))
        for idx in range(self.kolvo):
            for tree in self.trees[idx]:
                scores[:, idx] += self.learning_rate * tree.predict(X)
        exp_scores = np.exp(scores - np.max(scores, axis=1, keepdims=True))
        return exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
