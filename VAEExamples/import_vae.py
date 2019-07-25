#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:01:37 2019

@author: ajshah
"""

from variational_autoencoder import *
import keras
import numpy as np

def import_model(model:keras.engine.training.Model, weights_file):
    model = model.load_weights(weights_file)
    return model

def show_tile(n,images):
    sel_images = images[0:n*n]
    for i in range(n*n):
        plt.subplot(n,n,i+1)
        plt.imshow(images[i], cmap='gray')
        plt.axis('off')
        plt.box('on')
        
        
if __name__ == '__main__':
    
    vae = import_model(vae, 'vae_mlp_mnist.h5')
    
    #Sample 100 latent variables
    latents = np.random.multivariate_normal(np.zeros((latent_dim,)), np.eye(latent_dim), (1000,))
    flat_images = decoder.predict(latents)
    images = flat_images.reshape((flat_images.shape[0], image_size, image_size))
    