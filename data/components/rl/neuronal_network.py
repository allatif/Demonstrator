import os

import tensorflow as tf
from tensorflow import keras

from ... import pg_init
from ... components import colors


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class ANN:

    def __init__(self, model_name):
        path = 'data\\components\\rl\\models\\' + model_name
        model = keras.models.load_model(path, compile=False)

        self._layer_sizes = []
        self._W = []
        self._max_W = []

        counter = 0
        for variable in model.weights:
            if variable.name.split('/')[1].split(':')[0] != 'bias':
                self._W.append(variable)
                self._max_W.append(float(tf.reduce_max(tf.math.abs(variable))))
                s_list = list(variable.shape)
                self._layer_sizes += s_list if counter == 0 else s_list[1:]
                counter += 1

        self._nn_neurons = []
        self._connections = []

        self._init_img_settings()

        self._image = None
        self.built = False

    def _init_img_settings(self):
        layers = len(self._layer_sizes)
        max_dense = max(self._layer_sizes)
        neuron_r = self._radiusfitter(max_dense)

        self._settings = {
            'neuron radius': neuron_r,
            'layer distance': 16*neuron_r if neuron_r == 1 else 8*neuron_r,
            'layer void': 4*neuron_r,
            'image margin': 25,
            'max dense': max_dense
        }

        # Calculate screen centered AAN image rect
        screen_center_x = pg_init.SCREEN_SIZE[0]//2
        screen_center_y = pg_init.SCREEN_SIZE[1]//2
        dist = self._settings['layer distance']
        void = self._settings['layer void']
        width = (layers*2*neuron_r + (layers-1)*(dist-2*neuron_r))
        height = (max_dense*2*neuron_r + (max_dense-1)*(void-2*neuron_r))

        left = screen_center_x - width//2
        top = screen_center_y - height//2

        img_margin = self._settings['image margin']
        img_left = left - img_margin
        img_top = top - img_margin
        img_width = width + 2*img_margin
        img_height = height + 2*img_margin

        self._image_rect = (img_left, img_top, img_width, img_height)

    def build(self):
        neuron_r = self._settings['neuron radius']
        dist = self._settings['layer distance']
        void = self._settings['layer void']
        margin = self._settings['image margin']
        max_dense = self._settings['max dense']

        # Coords on self._image_rect
        input_layer_center_x = margin + neuron_r
        max_layer_top_center_y = margin + neuron_r

        # Set pos and color of neurons
        for layer_num, layer_size in enumerate(self._layer_sizes):
            neuron_pos_x = input_layer_center_x + layer_num*dist
            neuron_color = colors.LBLUE
            if layer_num == 0:
                neuron_color = colors.GREEN
            elif layer_num == len(self._layer_sizes)-1:
                neuron_color = colors.LRED

            neurons = []
            self._nn_neurons.append(neurons)

            diff_layer_size = max_dense - layer_size
            layer_margin_top = (max_layer_top_center_y
                                + diff_layer_size*void//2)
            for num in range(layer_size):
                neuron_pos_y = layer_margin_top + num*void
                neurons.append(Neuron((neuron_pos_x, neuron_pos_y),
                                      neuron_r, neuron_color))

        # Set pos of connection lines between layers
        for lay_n, (w, max_w) in enumerate(zip(self._W, self._max_W)):
            for row_n, row in enumerate(w.numpy()):
                for n, value in enumerate(row):
                    self._connections.append(
                        Connection(abs(value)/max_w,
                                   self._nn_neurons[lay_n][row_n].get_center(),
                                   self._nn_neurons[lay_n+1][n].get_center())
                    )
        self.built = True

    def save_image(self, surface):
        self._image = surface

    @staticmethod
    def _radiusfitter(dense):
        if dense <= 8:
            return 15
        elif dense > 8 and dense <= 12:
            return 11
        elif dense > 12 and dense <= 18:
            return 7
        elif dense > 18 and dense <= 30:
            return 4
        return 1

    @staticmethod
    def flatten_nn(nn_neurons):
        return [neuron for sublist in nn_neurons for neuron in sublist]

    @property
    def neurons(self):
        return self.flatten_nn(self._nn_neurons)

    @property
    def connections(self):
        return self._connections

    @property
    def settings(self):
        return self._settings

    @property
    def image(self):
        return self._image

    @property
    def image_rect(self):
        return self._image_rect


class Neuron:

    def __init__(self, center, radius, color):
        self._c_x, self._c_y = center
        self._r = radius
        self._color = color

    def get_center(self):
        return self._c_x, self._c_y

    @property
    def r(self):
        return self._r

    @property
    def color(self):
        return self._color


class Connection:

    def __init__(self, rel_value, start, end):
        self._rel_value = rel_value
        self._start = start
        self._end = end
        self._color = self._get_color_from_relvalue()

    def _get_color_from_relvalue(self):
        max = colors.WHITE[0]
        rbg_intensity = int(round((1-self._rel_value) * max))
        return (rbg_intensity, rbg_intensity, rbg_intensity)

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def color(self):
        return self._color
