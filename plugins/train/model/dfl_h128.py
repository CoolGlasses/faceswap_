#!/usr/bin/env python3
""" DeepFakesLab H128 Model
    Based on https://github.com/iperov/DeepFaceLab
"""

<<<<<<< HEAD
from keras.layers import Dense, Flatten, Input, Reshape
from keras.layers.convolutional import Conv2D
from keras.models import Model as KerasModel

from lib.model.nn_blocks import conv, upscale
from .original import get_config, logger, Model as OriginalModel
=======
from keras.layers import Conv2D, Dense, Flatten, Input, Reshape
from keras.models import Model as KerasModel

from .original import logger, Model as OriginalModel
>>>>>>> 60e0099c4d88a551b33592bf5126ab96bd5dc5ae


class Model(OriginalModel):
    """ Low Memory version of Original Faceswap Model """
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing %s: (args: %s, kwargs: %s",
                     self.__class__.__name__, args, kwargs)
<<<<<<< HEAD
        config = get_config(".".join(self.__module__.split(".")[-2:]))

        kwargs["input_shape"] = (128, 128, 3)
        kwargs["encoder_dim"] = 256 if config["lowmem"] else 512
=======

        kwargs["input_shape"] = (128, 128, 3)
        kwargs["encoder_dim"] = 256 if self.config["lowmem"] else 512
>>>>>>> 60e0099c4d88a551b33592bf5126ab96bd5dc5ae

        super().__init__(*args, **kwargs)
        logger.debug("Initialized %s", self.__class__.__name__)

<<<<<<< HEAD
    def set_training_data(self):
        """ Set the dictionary for training """
        logger.debug("Setting training data")
        training_opts = dict()
        training_opts["mask_type"] = self.config["mask_type"]
        training_opts["preview_images"] = 10
        logger.debug("Set training data: %s", training_opts)
        return training_opts

    def initialize(self):
        """ Initialize DFL H128 model """
        logger.debug("Initializing model")
        mask_shape = self.input_shape[:2] + (1, )
        inp_a = Input(shape=self.input_shape)
        mask_a = Input(shape=mask_shape)
        inp_b = Input(shape=self.input_shape)
        mask_b = Input(shape=mask_shape)

        ae_a = KerasModel(
            [inp_a, mask_a],
            self.networks["decoder_a"].network(self.networks["encoder"].network(inp_a)))
        ae_b = KerasModel(
            [inp_b, mask_b],
            self.networks["decoder_b"].network(self.networks["encoder"].network(inp_b)))

        self.add_predictors(ae_a, ae_b)
        self.masks = [mask_a, mask_b]
        logger.debug("Initialized model")

=======
>>>>>>> 60e0099c4d88a551b33592bf5126ab96bd5dc5ae
    def encoder(self):
        """ DFL H128 Encoder """
        input_ = Input(shape=self.input_shape)
        var_x = input_
<<<<<<< HEAD
        var_x = conv(128)(var_x)
        var_x = conv(256)(var_x)
        var_x = conv(512)(var_x)
        var_x = conv(1024)(var_x)
        var_x = Dense(self.encoder_dim)(Flatten()(var_x))
        var_x = Dense(8 * 8 * self.encoder_dim)(var_x)
        var_x = Reshape((8, 8, self.encoder_dim))(var_x)
        var_x = upscale(self.encoder_dim)(var_x)
=======
        var_x = self.blocks.conv(var_x, 128)
        var_x = self.blocks.conv(var_x, 256)
        var_x = self.blocks.conv(var_x, 512)
        var_x = self.blocks.conv(var_x, 1024)
        var_x = Dense(self.encoder_dim)(Flatten()(var_x))
        var_x = Dense(8 * 8 * self.encoder_dim)(var_x)
        var_x = Reshape((8, 8, self.encoder_dim))(var_x)
        var_x = self.blocks.upscale(var_x, self.encoder_dim)
>>>>>>> 60e0099c4d88a551b33592bf5126ab96bd5dc5ae
        return KerasModel(input_, var_x)

    def decoder(self):
        """ DFL H128 Decoder """
        input_ = Input(shape=(16, 16, self.encoder_dim))
        var = input_
<<<<<<< HEAD
        var = upscale(self.encoder_dim)(var)
        var = upscale(self.encoder_dim // 2)(var)
        var = upscale(self.encoder_dim // 4)(var)

        # Face
        var_x = Conv2D(3, kernel_size=5, padding="same", activation="sigmoid")(var)
        # Mask
        var_y = Conv2D(1, kernel_size=5, padding="same", activation="sigmoid")(var)
        return KerasModel(input_, [var_x, var_y])
=======
        var = self.blocks.upscale(var, self.encoder_dim)
        var = self.blocks.upscale(var, self.encoder_dim // 2)
        var = self.blocks.upscale(var, self.encoder_dim // 4)

        # Face
        var_x = Conv2D(3, kernel_size=5, padding="same", activation="sigmoid")(var)
        outputs = [var_x]
        # Mask
        if self.config.get("mask_type", None):
            var_y = Conv2D(1, kernel_size=5, padding="same", activation="sigmoid")(var)
            outputs.append(var_y)
        return KerasModel(input_, outputs=outputs)
>>>>>>> 60e0099c4d88a551b33592bf5126ab96bd5dc5ae
