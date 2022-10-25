import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from classifiers import NMC
from data_loaders import CDataLoaderMNIST
from data_perturb import CDataPerturbRandom, CDataPerturbGaussian
from sklearn.model_selection import train_test_split


def test_acc(yts, y_pred):
    return np.mean(yts == y_pred)


def plot_digits(image, shape=(28, 28)):
    plt.imshow(np.reshape(image, newshape=shape), cmap='gray')


def plot_ten_digits(x, y=None):
    plt.figure(figsize=(10, 5))

    for i in range(10):
        plt.subplot(2, 5, i + 1)
        plot_digits(x[i, :])

        if y is not None:
            plt.title('Label: ' + str(y[i]))


def classify_perturb_data(clf, x, y, data_peturb, perturb_parms, parm_name):
    acc_values = np.zeros(perturb_parms.size)

    for i, val in enumerate(perturb_parms):
        # set perturbation param, perturb data, classify it, compute acc
        if hasattr(data_peturb, parm_name):
            setattr(data_peturb, parm_name, val)
        else:
            raise ValueError("Wrong parameter name!")

        xp = data_peturb.perturb_dataset(x)
        y_pred = clf.predict(xp)
        acc_values[i] = test_acc(y, y_pred)

    return acc_values


data_loader = CDataLoaderMNIST()
x, y = data_loader.load_data()

plt.figure()
plot_ten_digits(x, y)
plt.show()

data_perturb1 = CDataPerturbRandom(K=100)
data_perturb2 = CDataPerturbGaussian(sigma=0.5)
xp1 = data_perturb1.perturb_dataset(x)
xp2 = data_perturb2.perturb_dataset(x)

plt.figure()
plot_ten_digits(xp1, y)
plt.show()

plt.figure()
plot_ten_digits(xp2, y)
plt.show()

xtr, xts, ytr, yts = train_test_split(x, y, train_size=0.6)

clf = NMC()
clf.fit(xtr, ytr)
ypred = clf.predict(xts)
acc = test_acc(yts, ypred)
print("Initial accuracy:", acc * 100, "%")

sigma_values = np.array([0, 0.1, 0.2, 0.5, 1.0])
acc_gaussian = classify_perturb_data(
    clf, xts, yts, data_perturb2, sigma_values, "sigma")

k_values = np.array([0, 10, 20, 50, 100, 200])
acc_uniform = classify_perturb_data(
    clf, xts, yts, data_perturb1, k_values, "K")

print("Initial acc:", acc_gaussian[0], acc_uniform[0])

plt.figure()
plt.subplot(1, 2, 1)
plt.plot(k_values, acc_uniform)
plt.xlabel("K")
plt.subplot(1, 2, 2)
plt.plot(sigma_values, acc_gaussian)
plt.xlabel(r"$\sigma$")
plt.show()


plt.figure()
plt.plot(k_values, acc_uniform, 'b', label="uniform")
plt.plot(sigma_values*100, acc_gaussian, 'r', label="normal")
plt.title('Test accuracy')
plt.xlabel(r'Perturbation size (K or $\sigma$*100)')
plt.legend()
plt.savefig('../figs/error_perturbed.pdf')
plt.show()
