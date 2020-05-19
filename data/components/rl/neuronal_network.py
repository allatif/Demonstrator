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

        self._nn_neurons = []
        self._connections = []
        self._layer_sizes = []
        self._W = []

        max_weights = []
        counter = 0
        for variable in model.weights:
            if variable.name.split('/')[1].split(':')[0] != 'bias':
                self._W.append(variable)
                max_weights.append(float(tf.reduce_max(tf.math.abs(variable))))
                s_list = list(variable.shape)
                self._layer_sizes += s_list if counter == 0 else s_list[1:]
                counter += 1

        self._max_w = max(max_weights)

    def build(self):
        layers = len(self._layer_sizes)
        max_dense = max(self._layer_sizes)

        neuron_radius = self._radiusfitter(max_dense)

        layer_distance = 8*neuron_radius
        if neuron_radius == 1:
            layer_distance = 16*neuron_radius
        layer_void = 4*neuron_radius

        screen_center_x = pg_init.SCREEN_SIZE[0]//2
        screen_center_y = pg_init.SCREEN_SIZE[1]//2
        nn_width = (layers*2*neuron_radius
                    + (layers-1)*(layer_distance-2*neuron_radius))
        nn_height = (max_dense*2*neuron_radius
                     + (max_dense-1)*(layer_void-2*neuron_radius))
        input_layer_center_x = screen_center_x - nn_width//2 + neuron_radius
        max_layer_top_center_y = screen_center_y - nn_height//2 + neuron_radius

        # Set pos and color of neurons
        for layer_num, layer_size in enumerate(self._layer_sizes):
            neuron_pos_x = input_layer_center_x + layer_num*layer_distance
            neuron_color = colors.LBLUE
            if layer_num == 0:
                neuron_color = colors.GREEN
            elif layer_num == len(self._layer_sizes)-1:
                neuron_color = colors.LRED

            neurons = []
            self._nn_neurons.append(neurons)

            diff_layer_size = max_dense - layer_size
            layer_margin_top = (max_layer_top_center_y
                                + diff_layer_size*layer_void//2)
            for num in range(layer_size):
                neuron_pos_y = layer_margin_top + num*layer_void
                neurons.append(Neuron((neuron_pos_x, neuron_pos_y),
                                      neuron_radius, neuron_color))

        # Set pos of connection lines between layers
        for lay_n, w in enumerate(self._W):
            for row_n, row in enumerate(w.numpy()):
                for n, value in enumerate(row):
                    self._connections.append(
                        Connection(abs(value)/self._max_w,
                                   self._nn_neurons[lay_n][row_n].get_center(),
                                   self._nn_neurons[lay_n+1][n].get_center())
                    )

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
