'''Example of VAE on MNIST dataset using MLP

The VAE has a modular design. The encoder, decoder and VAE
are 3 models that share weights. After training the VAE model,
the encoder can be used to  generate latent vectors.
The decoder can be used to generate MNIST digits by sampling the
latent vector from a Gaussian distribution with mean=0 and std=1.

# Reference

[1] Kingma, Diederik P., and Max Welling.
"Auto-encoding variational bayes."
https://arxiv.org/abs/1312.6114
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Lambda, Input, Dense, concatenate
from keras.models import Model, save_model
from keras.datasets import mnist
from keras.losses import mse, binary_crossentropy
from keras.utils import plot_model
from keras import backend as K

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os


# reparameterization trick
# instead of sampling from Q(z|X), sample eps = N(0,I)
# z = z_mean + sqrt(var)*eps
def sampling(args):
    """Reparameterization trick by sampling fr an isotropic unit Gaussian.

    # Arguments:
        args (tensor): mean and log of variance of Q(z|X)

    # Returns:
        z (tensor): sampled latent vector
    """

    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean=0 and std=1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon


def plot_results(models,
                 data,
                 batch_size=128,
                 model_name="vae_mnist"):
    """Plots labels and MNIST digits as function of 2-dim latent vector

    # Arguments:
        models (tuple): encoder and decoder models
        data (tuple): test data and label
        batch_size (int): prediction batch size
        model_name (string): which model is using this function
    """

    encoder, decoder = models
    x_test, y_test = data
    os.makedirs(model_name, exist_ok=True)

    filename = os.path.join(model_name, "vae_mean.png")
    # display a 2D plot of the digit classes in the latent space
    z_mean, _, _ = encoder.predict(x_test,
                                   batch_size=batch_size)
    plt.figure(figsize=(12, 10))
    plt.scatter(z_mean[:, 0], z_mean[:, 1], c=y_test)
    plt.colorbar()
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.savefig(filename)
    plt.show()

    filename = os.path.join(model_name, "digits_over_latent.png")
    # display a 30x30 2D manifold of digits
    n = 30
    digit_size = 28
    figure = np.zeros((digit_size * n, digit_size * n))
    # linearly spaced coordinates corresponding to the 2D plot
    # of digit classes in the latent space
    grid_x = np.linspace(-4, 4, n)
    grid_y = np.linspace(-4, 4, n)[::-1]

    for i, yi in enumerate(grid_y):
        for j, xi in enumerate(grid_x):
            z_sample = np.array([[xi, yi]])
            x_decoded = decoder.predict(z_sample)
            digit = x_decoded[0].reshape(digit_size, digit_size)
            figure[i * digit_size: (i + 1) * digit_size,
                   j * digit_size: (j + 1) * digit_size] = digit

    plt.figure(figsize=(10, 10))
    start_range = digit_size // 2
    end_range = n * digit_size + start_range + 1
    pixel_range = np.arange(start_range, end_range, digit_size)
    sample_range_x = np.round(grid_x, 1)
    sample_range_y = np.round(grid_y, 1)
    plt.xticks(pixel_range, sample_range_x)
    plt.yticks(pixel_range, sample_range_y)
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.imshow(figure, cmap='Greys_r')
    plt.savefig(filename)
    plt.show()


# MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()

image_size = x_train.shape[1]
original_dim = image_size * image_size
x_train = np.reshape(x_train, [-1, original_dim])
x_test = np.reshape(x_test, [-1, original_dim])
x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255
YTrain = pd.DataFrame()
YTrain['label'] = pd.Categorical(y_train, categories = [0,1,2,3,4,5,6,7,8,9])
YTrain = np.array(pd.get_dummies(YTrain))
YTrain = YTrain.astype('float32')


# network parameters
input_shape = (original_dim, )
input2_shape = (YTrain.shape[1],)
intermediate_dim = 512
batch_size = 128
latent_dim = 5
epochs = 50

# VAE model = encoder + decoder
# build encoder model
inputs = Input(shape=input_shape, name='encoder_input')
inputs2 = Input(shape = input2_shape, name = 'condition')
x1 = Dense(intermediate_dim, activation='relu')(inputs)
x2 = Dense(256, activation='relu')(x1)
x3 = concatenate([x2, inputs2])
z_mean = Dense(latent_dim, name='z_mean')(x3)
z_log_var = Dense(latent_dim, name='z_log_var')(x3)

# use reparameterization trick to push the sampling out as input
# note that "output_shape" isn't necessary with the TensorFlow backend
z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

# instantiate encoder model
encoder = Model(inputs=[inputs, inputs2], outputs=[z_mean, z_log_var, z], name='encoder')
encoder.summary()
plot_model(encoder, to_file='cvae_mlp_encoder.png', show_shapes=True)

# build decoder model
latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
final_inputs = concatenate([latent_inputs, inputs2])
x1 = Dense(256, activation = 'relu')(final_inputs)
x2 = Dense(intermediate_dim, activation='relu')(x1)
outputs = Dense(original_dim, activation='sigmoid')(x2)

# instantiate decoder model
decoder = Model(inputs=[latent_inputs, inputs2], outputs=[outputs], name='decoder')
decoder.summary()
plot_model(decoder, to_file='cvae_mlp_decoder.png', show_shapes=True)

# instantiate VAE model
outputs = decoder([encoder([inputs, inputs2])[2], inputs2])
vae = Model([inputs, inputs2], outputs, name='cvae_mlp')

if __name__ == '__main__':
    
    models = (encoder, decoder)
    data = (x_test, y_test)
    VAELoss = 'binary'
    LoadWeights = True
    
    

    # VAE loss = mse_loss or xent_loss + kl_loss
    if VAELoss == 'mse':
        reconstruction_loss = mse(inputs, outputs)
    else:
        reconstruction_loss = binary_crossentropy(inputs,
                                                  outputs)
        
    
    
    reconstruction_loss *= original_dim
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = K.mean(reconstruction_loss + kl_loss)
    vae.add_loss(vae_loss)
    vae.compile(optimizer='adam')
    vae.summary()
    plot_model(vae,
               to_file='cvae_mlp.png',
               show_shapes=True)

    
    if LoadWeights:
        vae.load_weights('cvae_mlp_mnist.h5')
    else:
        # train the autoencoder
        vae.fit([np.array(x_train), np.array(YTrain)],
                epochs=epochs,
                batch_size=batch_size,)
        vae.save_weights('cvae_mlp_mnist.h5')
        
    
    
    digit = 9
    Cond  = np.zeros((1,10))
    Cond[0,digit] = 1
    Cond[0,3] = 1
    
    for i in range(20):
        z_sample = np.array(np.random.normal(size=(1,5)))
        digitvals = decoder.predict([z_sample, Cond])
        digitvals = np.reshape(digitvals, (28,28))
        plt.figure()
        plt.imshow(digitvals)


