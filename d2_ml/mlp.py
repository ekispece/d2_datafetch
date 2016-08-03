from __future__ import print_function
from collections import Counter

import numpy as np
import pandas
from keras.layers import Dense, Activation
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.core import Dropout
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential
from d2_db import db

database = db.get_database()

heroes_list_collection = database.heroes

heroes_dfid_id_translate = {}

for hero in heroes_list_collection.find():
    heroes_dfid_id_translate[hero['id_df']] = hero['id']


def validate_model(d, n):
    hits = 0
    misses = 0
    for matchno, match in enumerate(d):
        x_val = np.zeros(shape=(1, len(match) - 1), dtype=np.float32)
        x_val[0] = match[0:-1]
        y = match[-1]
        c_out = n.predict(x_val)
        choices = np.argpartition(c_out[0], -rank_size)[-rank_size:]
        if y in choices:
            hits += 1
        else:
            misses += 1
    print("Validation accuracy", float(hits) / (hits + misses))


# features_per_hero = 16  # hero_id, agpm, axpm, awr, akda, ahd, atd, ahh, alh, adn, item123, item123wr
# heroes_per_match = 9
total_features = 226

load_save = False
rank_size = 15

print("Building network")

network = Sequential(
    [
        Dense(2560, input_dim=total_features),
        Dropout(0.25),
        LeakyReLU(alpha=0.4),
        BatchNormalization(epsilon=1e-5, momentum=0.99),
        Dense(2560),
        Dropout(0.2),
        LeakyReLU(alpha=0.3),
        BatchNormalization(epsilon=1e-6),
        Dense(2560),
        Dropout(0.2),
        LeakyReLU(alpha=0.2),
        BatchNormalization(),
        Dense(1000),
        Dropout(0.2),
        LeakyReLU(alpha=0.1),
        BatchNormalization(),
        Dense(1000),
        Dropout(0.2),
        Activation('relu'),
        BatchNormalization(),
        Dense(111),
        Activation('softmax')
    ]
)

print("done")
# print network.summary()

network.compile(optimizer='nadam', loss='kld', metrics=['accuracy'])

if load_save:
    print("loading previously saved network")
    network.load_weights("model_mlp.d2")

print("Loading input info")
data = pandas.read_csv("data.tar.gz", header=None, compression='gzip', error_bad_lines=False).values

print("loaded. Data obj shape:", data.shape)

# If we were to include validation at training time, then, uncoment this code and call for validate_model

# val_data_size = int(data.shape[0] * 0.2)
# data_size = data.shape[0] - val_data_size  # 80/20 validation training split
# val_data = data[data_size: data.shape[0], :]
# data = data[0:data_size, :]

best_val_acc = -1.0
for shuf in range(100):
    print("Shuffling data")
    # loading input data
    np.random.shuffle(data)
    l = data[:, -1]
    j = Counter(l)
    # make sure to set a reasonable max_data value to train the data with
    max_data = 1200
    masks = []

    print("Making sure there's isn't too much data imbalance, max labels for classes set as " + str(max_data))
    print("actual elements for each label: ")
    print(j)
    print("total inputs " + str(l.shape[0]))

    print(("#" * 10) + "\nStarting undersampling")

    for k, v in j.items():
        mask = (data[:, -1] == k)
        if v > max_data:
            x = 0
            while np.count_nonzero(mask) > max_data:
                # Change x + 1 to a bigger number to increase overall performance
                idx = x + 1000
                mask[x:idx] = False
                x = idx
        masks.append(mask)

    for i in range(len(masks) - 1):
        masks[i + 1] = np.ma.mask_or(masks[i], masks[i + 1])

    print("finished")

    dx = data[masks[-1] == 1, :]
    l = dx[:, -1]
    j = Counter(l)
    # print dx
    print("Total inputs after reduction " + str(l.shape[0]))
    print("class balance after undersampling")
    print(j)

    # # undersampling to reduce class imbalance problem
    # for i, label in enumerate(data[:, -1]):
    #     if j[label] > max_data:
    #         np.delete(data, i, 0)
    #         j[label] -= 1
    #
    # print j

    print("Starting optimization")

    information_gain = 5
    this_batch_loss = 10.0
    it = 0

    while information_gain >= 0:
        it += 1
        # np.random.shuffle(dx)
        y_v = dx[:, -1]
        y_in = np.zeros(shape=(y_v.shape[0], 111))

        for ix, val in enumerate(y_v):
            y_in[ix][val] = 1.0

        x_in = dx[:, 0:-1]
        print("Iteration " + str(it))
        hist = network.fit(x_in, y_in, batch_size=32, nb_epoch=1)

        filename = "model_mlp.d2"
        print("Saving model to file " + filename)
        network.save_weights(filename, True)

        # if hist.history["val_loss"][0] < this_batch_loss:
        #     information_gain += 1 if information_gain < 5 else 0
        #     this_batch_loss = hist.history["val_loss"][0]
        # else:
        #     information_gain -= 1
        # print "Info gain : " + str(information_gain)

        print("Validating model generated")
