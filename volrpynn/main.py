import json
import sys
import numpy as np
import volrpynn as v

class Main():
    """A runtime class that accepts a model and exposes a 'train' method
       to train that model with a given optimiser, given data via std in"""

    def __init__(self, model, parameter_file=None):
        self.model = model
        if parameter_file:
            self._load_parameter_file(parameter_file)

    def _load_parameter_file(self, file_name):
        parameters = np.load(file_name)
        for index in range(len(self.model.layers) - 1):
            layer = self.model.layers[index]
            weights, biases = parameters[:2]
            layer.biases = biases
            layer.set_weights(weights.T)
            # Continue with next element in tuple
            parameters = parameters[2:]

    def _normalise_data(self, data):
        """Normalises the data according to a linear model for spiking neuron
        activation, where f(x) = 3.225x - 1.613"""
        # Normalise the data to [1;10]
        data /= data.max()
        data *= 20
        data += 5
        # Scale the data linearly
        return (data + 1.61295370014) / 3.22500557

    def _normalise_model_weights(self):
        input_layer_size = self.model.node_input.size
        input_data = np.ones((input_layer_size)) * 25
        self.model.normalise_weights(input_data)

    def train(self, optimiser, xs=None, ys=None, split=0.8):
        """Trains and tests the model loaded in this class with the given
        optimiser, input data, expected output data and testing/training
        split

        Args:
        optimiser -- The optimisation algorithm that trains the model
        xs -- The input data, will later be normalised
        ys -- Expected categorical output labels
        split -- Testing/training split. Defaults to 0.8 (80%)

        Returns:
        A Report of the training and testing run
        """
        if not isinstance(xs, np.ndarray) or not isinstance(ys, np.ndarray):
            if len(sys.argv) < 3:
                raise Exception("Training input and training labels expected via std in")
            xs_text, ys_text = (sys.argv[1], sys.argv[2])
            xs = self._normalise_data(np.array(json.loads(xs_text)))
            ys = np.array(json.loads(ys_text))

        # Normalise model weights
        self._normalise_model_weights()

        split = int(len(xs) * split)
        x_train = xs[:split]
        y_train = ys[:split]
        x_test = xs[split:]
        y_test = ys[split:]
        assert len(x_train) > 0 and len(x_test) > 0, "Must have at least 5 data points"
        _, errors = optimiser.train(self.model, x_train, y_train, v.SoftmaxCrossEntropy())
        report = optimiser.test(self.model, x_test, y_test, v.ErrorCostCategorical())
        reportDict = report.toDict()
        reportDict['train_errors'] = errors # Include training errors
        # Return a JSON version of the report to stdout
        print(json.dumps(reportDict))