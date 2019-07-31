#!/usr/bin/env python3
""" Default configurations for models """

import logging
import os
import sys

from importlib import import_module

from lib.config import FaceswapConfig
from lib.model.masks import get_available_masks
from lib.utils import full_path_split

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

ADDITIONAL_INFO = ("\nNB: Unless specifically stated, values changed here will only take effect "
                   "when creating a new model.")


class Config(FaceswapConfig):
    """ Config File for Models """
    # pylint: disable=too-many-statements
    def set_defaults(self):
        """ Set the default values for config """
        logger.debug("Setting defaults")
        self.set_globals()
        current_dir = os.path.dirname(__file__)
        for dirpath, _, filenames in os.walk(current_dir):
            default_files = [fname for fname in filenames if fname.endswith("_defaults.py")]
            if not default_files:
                continue
            base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
            import_path = ".".join(full_path_split(dirpath.replace(base_path, ""))[1:])
            plugin_type = import_path.split(".")[-1]
            for filename in default_files:
                self.load_module(filename, import_path, plugin_type)

    def set_globals(self):
        """ 
        Set the global options for training

        Loss Documentation
        MAE https://heartbeat.fritz.ai/5-regression-loss-functions-all-machine
            -learners-should-know-4fb140e9d4b0
        MSE https://heartbeat.fritz.ai/5-regression-loss-functions-all-machine
            -learners-should-know-4fb140e9d4b0
        LogCosh https://heartbeat.fritz.ai/5-regression-loss-functions-all-machine
                -learners-should-know-4fb140e9d4b0
        Smooth L1 https://arxiv.org/pdf/1701.03077.pdf
        L_inf_norm https://medium.com/@montjoile/l0-norm-l1-norm-l2-norm-l-infinity
                   -norm-7a7d18a4f40c
        SSIM http://www.cns.nyu.edu/pub/eero/wang03-reprint.pdf
        GMSD https://arxiv.org/ftp/arxiv/papers/1308/1308.3052.pdf
        """
        logger.debug("Setting global config")
        section = "global"
        self.add_section(title=section,
                         info="Options that apply to all models" + ADDITIONAL_INFO)
        self.add_item(
            section=section, title="icnr_init", datatype=bool, default=False,
            info="\nUse ICNR to tile the default initializer in a repeating pattern. \n"
                 "This strategy is designed for pairing with sub-pixel / pixel shuffler \n"
                 "to reduce the 'checkerboard effect' in image reconstruction. \n"
                 "https://arxiv.org/ftp/arxiv/papers/1707/1707.02937.pdf \n")
        self.add_item(
            section=section, title="conv_aware_init", datatype=bool, default=False,
            info="Use Convolution Aware Initialization for convolutional layers. \n"
                 "This can help eradicate the vanishing and exploding gradient problem \n"
                 "as well as lead to higher accuracy, lower loss and faster convergence. \n"
                 "NB This can use more VRAM when creating a new model so you may want to \n"
                 "lower the batch size for the first run. The batch size can be raised \n"
                 "again when reloading the model. \n"
                 "NB: Building the model will likely take several minutes as the calculations \n"
                 "for this initialization technique are expensive. \n")
        self.add_item(
            section=section, title="subpixel_upscaling", datatype=bool, default=False,
            info="\nUse subpixel upscaling rather than pixel shuffler. These techniques \n"
                 "are both designed to produce better resolving upscaling than other \n"
                 "methods. Each perform the same operations, but using different TF opts.\n"
                 "https://arxiv.org/pdf/1609.05158.pdf \n")
        self.add_item(
            section=section, title="reflect_padding", datatype=bool, default=False,
            info="\nUse reflection padding rather than zero padding with convolutions. \n"
                 "Each convolution must pad the image boundaries to maintain the proper \n"
                 "sizing. More complex padding schemes can reduce artifacts at the \n"
                 "border of the image.\n"
                 "http://www-cs.engr.ccny.cuny.edu/~wolberg/cs470/hw/hw2_pad.txt \n")
        self.add_item(
            section=section, title="penalized_mask_loss", datatype=bool, default=True,
            info="\nImage loss function is weighted by mask presence. For areas of \n"
                 "the image without the facial mask, reconstuction errors will be \n"
                 "ignored while the masked face area is prioritized. May increase \n"
                 "overall quality by focusing attention on the core face area.\n")
        self.add_item(
            section=section, title="image_loss_function", datatype=str,
            default="Mean_Absolute_Error",
            choices=["Mean_Absolute_Error", "Mean_Squared_Error", "LogCosh",
                     "Smooth_L1", "L_inf_norm", "SSIM", "GMSD", "Pixel_Gradient_Difference"],
            info="\nMean_Absolute_Error ---\n"
                 "MAE will guide reconstructions of each pixel towards its median \n"
                 "value in the training dataset. Robust to outliers but as a median, \n"
                 "it can potentially ignore some infrequent image types in the dataset. \n"

                 "\nMean_Squared_Error ---\n"
                 "MSE will guide reconstructions of each pixel towards its average \n"
                 "value in the training dataset. As an avg, it will be suspectible to \n"
                 "outliers and typically produces slightly blurrier results. \n"

                 "\nLogCosh ---\n"
                 "log(cosh(x)) acts similiar to MSE for small errors and to MAE for large \n"
                 "errors. Like MSE, it is very stable and prevents overshoots when errors \n"
                 "are near zero. Like MAE, it is robust to outliers. \n"

                 "\nSmooth_L1 ---\n"
                 "Modification of the MAE loss to correct two of its disadvantages. \n"
                 "This loss has improved stability and better guidance for small errors. \n"

                 "\nL_inf_norm ---\n"
                 "The L_inf norm will reduce the largest individual pixel error in an image. \n"
                 "As each largest error is minimized sequentially, the overall error is \n"
                 "improved. This loss will be extremely focused on outliers. \n"

                 "\nSSIM - Structural Similarity Index Metric ---\n"
                 "SSIM is a perception-based loss that considers changes in texture, \n"
                 "luminance, contrast, and local spatial statistics of an image. \n"
                 "Potentially better textural, and realistic looking images. \n"

                 "\nGMSD - Gradient Magnitude Similarity Deviation ---\n"
                 "GMSD seeks to match the differences between pixel color changes \n"
                 "when moving from pixel to pixel in an image. Corresponding pixels in \n"
                 "two images will have a difference with their neighboring pixels. \n"
                 "The global standard deviation of the pixel to pixel differences for \n"
                 "each image is calculated and the differnece in this metric is minimized. \n"

                 "\nPixel_Gradient_Difference ---\n"
                 "Instead of minimizing the difference between the absolute value of \n"
                 "each pixel in two reference images, compute the pixel to pixel \n"
                 "spatial difference in each image and then minimize that difference \n"
                 "between two images. Allows for large color shifts,but maintains the \n"
                 "structure of the image.\n"
                 )
        self.add_item(section=section, title="mask_type", datatype=str, default="none",
                      choices=get_available_masks(),
                      info="The mask to be used for training:"
                           "\n\t none: Doesn't use any mask."
                           "\n\t components: An improved face hull mask using a facehull of 8 "
                           "facial parts"
                           "\n\t dfl_full: An improved face hull mask using a facehull of 3 "
                           "facial parts"
                           "\n\t extended: Based on components mask. Extends the eyebrow points "
                           "to further up the forehead. May perform badly on difficult angles."
                           "\n\t facehull: Face cutout based on landmarks")
        self.add_item(
            section=section, title="learning_rate", datatype=float, default=5e-5,
            min_max=(1e-6, 1e-4), rounding=6, fixed=False,
            info="Learning rate - how fast your network will learn (how large are \n"
                 "the modifications to the model weights after one batch of training).\n"
                 "Values that are too large might result in model crashes and the \n"
                 "inability of the model to find the best solution.\n"
                 "Values that are too small might be unable to escape from dead-ends \n"
                 "and find the best global minimum.")
        self.add_item(
            section=section, title="coverage", datatype=float, default=68.75,
            min_max=(62.5, 100.0), fixed=True,
            info="How much of the extracted image to train on. Generally the model is optimized"
                "\nto the default value. Sensible values to use are:"
                "\n\t62.5%% spans from eyebrow to eyebrow."
                "\n\t75.0%% spans from temple to temple."
                "\n\t87.5%% spans from ear to ear."
                "\n\t100.0%% is a mugshot.")

    def load_module(self, filename, module_path, plugin_type):
        """ Load the defaults module and add defaults """
        logger.debug("Adding defaults: (filename: %s, module_path: %s, plugin_type: %s",
                     filename, module_path, plugin_type)
        module = os.path.splitext(filename)[0]
        section = ".".join((plugin_type, module.replace("_defaults", "")))
        logger.debug("Importing defaults module: %s.%s", module_path, module)
        mod = import_module("{}.{}".format(module_path, module))
        helptext = mod._HELPTEXT  # pylint:disable=protected-access
        helptext += ADDITIONAL_INFO if module_path.endswith("model") else ""
        self.add_section(title=section, info=helptext)
        for key, val in mod._DEFAULTS.items():  # pylint:disable=protected-access
            self.add_item(section=section, title=key, **val)
        logger.debug("Added defaults: %s", section)
