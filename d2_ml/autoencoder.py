from keras.layers import Input, Dense
from keras.models import Model
import numpy as np

toy_data = np.random.rand(10000, 450) * 1000

print toy_data

information_per_hero = 50  # this can be changed along the development
encoding_dim = 9  # There is a total of 9 heroes
total_dim = information_per_hero * encoding_dim
input_v = (Input(shape=(total_dim,)))

encoded_representation = Dense(encoding_dim, activation='relu')(input_v)
decoded_representation = Dense(total_dim, activation='sigmoid')(encoded_representation)

autoencoder = Model(input=input_v, output=decoded_representation)
encoder = Model(input=input_v, output=encoded_representation)

encoded_input = Input(shape=(encoding_dim,))

decoder_layer = autoencoder.layers[-1]

decoder = Model(input=encoded_input, output=decoder_layer(encoded_input))

autoencoder.compile(optimizer='adadelta', loss='hinge')

autoencoder.fit(toy_data, toy_data, nb_epoch=50, shuffle=True, validation_split=0.2, batch_size=100)


print autoencoder.predict(np.ones(shape=(1, 450)) * 10)
print autoencoder.predict(np.ones(shape=(1, 450)))
rand = np.random.rand(1, 450) * 10
print "randomly generated: "
print rand
print autoencoder.predict(rand)
