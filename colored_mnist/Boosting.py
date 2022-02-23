# Load libraries
from statistics import stdev
from sklearn.ensemble import AdaBoostClassifier
from sklearn.svm import SVC
from sklearn import datasets as ds
#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
import argparse
import numpy as np
import torch
from torchvision import datasets
from torch import nn, optim, autograd
import matplotlib.pyplot as plt
import statistics as stat

# Load MNIST, make train/val splits, and shuffle train set examples

mnist = datasets.MNIST('~/datasets/mnist', train=True, download=True)
mnist_train = (mnist.data[:50000], mnist.targets[:50000])
mnist_val = (mnist.data[50000:], mnist.targets[50000:])

rng_state = np.random.get_state()
np.random.shuffle(mnist_train[0].numpy())
np.random.set_state(rng_state)
np.random.shuffle(mnist_train[1].numpy())

f = open('boosting_color.txt', 'a')
# Build environments

def make_environment(images, labels, e):
  def torch_bernoulli(p, size):
    return (torch.rand(size) < p).float()
  def torch_xor(a, b):
    return (a-b).abs() # Assumes both inputs are either 0 or 1
  # 2x subsample for computational convenience
  images = images.reshape((-1, 28, 28))[:, ::2, ::2]
  # Assign a binary label based on the digit; flip label with probability 0.25
  labels = (labels < 5).float()
  labels = torch_xor(labels, torch_bernoulli(0.25, len(labels)))
  # Assign a color based on the label; flip the color with probability e
  colors = torch_xor(labels, torch_bernoulli(e, len(labels)))
  # Apply the color to the image by zeroing out the other color channel
  images = torch.stack([images, images], dim=1)
  images[torch.tensor(range(len(images))), (1-colors).long(), :, :] *= 0
  return {
    'images': (images.float() / 255.).cpu(),
    'labels': labels[:, None].cpu()
  }

def make_environment_gray(images, labels, e):
  def torch_bernoulli(p, size):
    return (torch.rand(size) < p).float()
  def torch_xor(a, b):
    return (a-b).abs() # Assumes both inputs are either 0 or 1
  # 2x subsample for computational convenience
  images = images.reshape((-1, 28, 28))[:, ::2, ::2]
  # Assign a binary label based on the digit; flip label with probability 0.25
  labels = (labels < 5).float()
  labels = torch_xor(labels, torch_bernoulli(0.25, len(labels)))
  return {
    'images': (images.float() / 255.).cpu(),
    'labels': labels[:, None].cpu()
  }
acc =[]
for i in range(10):
  envs = [
    make_environment(mnist_train[0][::2], mnist_train[1][::2], 0.1),
    make_environment(mnist_train[0][1::2], mnist_train[1][1::2], 0.2),
    make_environment(mnist_val[0], mnist_val[1], 0.9)
  ]

  X_train = torch.cat((envs[0]['images'], envs[1]['images']), 0)
  y_train = torch.cat((envs[0]['labels'], envs[1]['labels']), 0)
  X_train = X_train.reshape(50000,2*14*14)

  X_test = envs[2]['images']
  y_test = envs[2]['labels']
  X_test = X_test.reshape(10000,2*14*14)

  # Create adaboost classifer object
  abc = AdaBoostClassifier(n_estimators=50,learning_rate=1)
  # Train Adaboost Classifer
  model = abc.fit(X_train, y_train.reshape(-1,))
  #Predict the response for test dataset
  y_pred = model.predict_proba(X_test)
  # Model Accuracy, how often is the classifier correct?
  acc.append(metrics.accuracy_score(y_test, y_pred))
f.write(str(acc) +' ' +str(stat.mean(acc))+' '+str(stat.stdev(acc))+ '\n')
f.close()

