import os

# import numpy as np

print(" -- Loading TensorFlow -- ")
from tensorflow import keras


DIR = os.path.join('models')
print(DIR)


def get_models():
    """Returns a list of all TensorFlow model *.h5 file names."""

    model_list = []
    for model_file in os.listdir(DIR):
        # Ignore all files that start with underscore
        if model_file[0] is not '_':
            model_list.append(model_file)
    return model_list


model_names = get_models()

for model_name in model_names:
    model = keras.models.load_model(f'{DIR}\\{model_name}', compile=False)
    print(f'{model_name}: {model.input.shape}')
