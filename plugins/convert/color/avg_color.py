#!/usr/bin/env python3
""" Average colour adjustment color matching adjustment plugin for faceswap.py converter """

import numpy as np
from ._base import Adjustment


class Color(Adjustment):
    """ Color distribution matching """

    @staticmethod
    def process(old_face, new_face, raw_mask):
        """
        Match the 1st moment of the color distribution from the original facial crop
        by adjusting the distribution in the swapped facial crop.

        Parameters:
        -------
        old_face : Numpy array, shape (height, width, n_channels), float32
            Facial crop of the original subject
        new_face : Numpy array, shape (height, width, n_channels), float32
            Facial crop of the swapped output from the neural network
        raw_mask : Numpy array, shape (height, width, n_channels), float32
            Segmentation mask of the facial crop of the original subject

        Returns:
        -------
        new_face_shifted : Numpy array, shape (height, width, n_channels), float32
            Facial crop of the swapped output with a shifted color distribution
        """
        old_mean = np.average(old_face, axis=(0, 1), weights=raw_mask)
        new_mean = np.average(new_face, axis=(0, 1), weights=raw_mask)
        new_face_shifted = new_face + (old_mean - new_mean)
        return new_face_shifted
