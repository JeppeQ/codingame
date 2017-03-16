from __future__ import division
import pickle
import numpy as np
from gamesim import *

from keras.models import Sequential, model_from_json
from keras.layers import Dense, Activation, Dropout, Convolution2D
from keras.optimizers import SGD, Nadam

#DATA
X_train = pickle.load(open('training_x', 'rb'))
Y_train = pickle.load(open('training_y', 'rb'))
X_train1 = pickle.load(open('training1_x', 'rb'))
Y_train1 = pickle.load(open('training1_y', 'rb'))
X_train2 = pickle.load(open('training2_x', 'rb'))
Y_train2 = pickle.load(open('training2_y', 'rb'))

X_train += X_train1+X_train2
Y_train += Y_train1+Y_train2

#Hyper parameters
H = 35 #hidden neurons

sgd = SGD(lr=0.01)
model = Sequential()
model.add(Dense(output_dim=H, input_dim=8, activation='sigmoid', bias=None))
model.add(Dense(H, activation='tanh', bias=None))
model.add(Dense(1, activation='sigmoid', bias=None))
model.compile(loss="binary_crossentropy", optimizer=sgd)

model.fit(np.array(X_train), np.array(Y_train), nb_epoch=800, verbose=2)


# p1 = RandomPlayer(1)
# p2 = RandomPlayer(2)
# g = game(p1, p2)
# states = list()
# for i in range(1000):
#     states += g.save_states()

p1 = Player_v1(1, model)
p2 = Player_v2(2, model)
g = game(p1, p2)
print (g.run_games())


