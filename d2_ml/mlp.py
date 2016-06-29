import numpy as np
from keras.layers import Input, Dense, Activation
from keras.layers.core import Dropout
from keras.models import Sequential
from keras.optimizers import SGD

features_per_hero = 17  # hero_id, agpm, axpm, awr, awmd, akda, ahd, atd, ahh, alh, adn, item123, item123wr
heroes_per_match = 9
total_features = features_per_hero * heroes_per_match

# loading input data
x_in = np.load("d2_d.npy")
y_in = np.load("d2_dy.npy")
for y in y_in:
    y[np.random.randint(0, 114)] = 1

network = Sequential(
    [
        Dense(512, input_dim=total_features),
        Activation('relu'),
        Dropout(0.2),
        Dense(512),
        Activation('relu'),
        Dropout(0.2),
        Dense(114, activation='softmax')
    ]
)
network.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
network.fit(x_in, y_in, batch_size=10, nb_epoch=500, validation_split=0.2)
