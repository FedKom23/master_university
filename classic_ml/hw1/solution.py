import numpy as np


class LinearRegression:
    def __init__(
            self,
            *,
            penalty="l2",
            alpha=0.0001,
            max_iter=1000,
            tol=0.001,
            random_state=None,
            eta0=0.01,
            early_stopping=False,
            validation_fraction=0.1,
            n_iter_no_change=5,
            shuffle=True,
            batch_size=32
    ):
        self.penalty = penalty
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.eta0 = eta0
        self.early_stopping = early_stopping
        self.validation_fraction = validation_fraction
        self.n_iter_no_change = n_iter_no_change
        self.shuffle = shuffle
        self.batch_size = batch_size

    def get_penalty_grad(self):
        if self.penalty == "l2":
            return 2 * self.alpha * self.coef_
        elif self.penalty == "l1":
            return self.alpha * np.sign(self.coef_)
        else:
            return np.zeros_like(self.coef_)

    def fit(self, x, y):
        if self.random_state is not None:
            np.random.seed(self.random_state)

        val_x, val_y = None, None
        if self.early_stopping:
            if 0 < self.validation_fraction < 1:
                n_val = int(x.shape[0] * self.validation_fraction)
                val_inds = np.random.choice(x.shape[0], size=n_val, replace=False)
                mask = np.zeros(x.shape[0], dtype=bool)
                mask[val_inds] = True
                val_x, val_y = x[mask], y[mask]
                x, y = x[~mask], y[~mask]
            else:
                self.early_stopping = False

        self.coef_ = np.zeros(x.shape[1])
        self.intercept_ = 0
        iter_no_change = 0
        best_loss = np.inf

        for i in range(self.max_iter):
            if self.shuffle:
                inds = np.random.permutation(x.shape[0])
                x, y = x[inds], y[inds]

            for start in range(0, x.shape[0], self.batch_size):
                end = min(start + self.batch_size, x.shape[0])
                X_batch = x[start:end]
                y_batch = y[start:end]

                pred = self.predict(X_batch)
                error = y_batch - pred

                grad_coef = -(2/len(y_batch)) * X_batch.T @ error + self.get_penalty_grad()
                grad_intercept = -(2/len(y_batch)) * np.sum(error)

                self.coef_ -= self.eta0 * grad_coef
                self.intercept_ -= self.eta0 * grad_intercept

            if self.early_stopping:
                current_loss = np.mean((val_y - self.predict(val_x))**2)
                if current_loss < best_loss - self.tol:
                    best_loss = current_loss
                    iter_no_change = 0
                else:
                    iter_no_change += 1

                if iter_no_change >= self.n_iter_no_change:
                    break

    def predict(self, x):
        return x @ self.coef_ + self.intercept_

    @property
    def coef_(self):
        return self._coef

    @property
    def intercept_(self):
        return self._intercept

    @coef_.setter
    def coef_(self, value):
        self._coef = value

    @intercept_.setter
    def intercept_(self, value):
        self._intercept = value
