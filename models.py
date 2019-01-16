from tensorflow import keras
from log_utils import get_logger
LOGGER = get_logger("models")

def get_model(name,vocab_size,embedding_matrix,input_length, classify_type):
    if  name=="zzw_cnn":
        return zzw_cnn(vocab_size,embedding_matrix,input_length, classify_type)
    elif name=="zzw_lstm":
        return zzw_lstm(vocab_size,embedding_matrix,input_length, classify_type)
    else:
        LOGGER.error("no such model: {}".format(name))
        assert(0)


def final_active_func(classify_type):
    if classify_type == 4:
        return 'sigmoid'
    elif classify_type == 16:
        return 'softmax'

def zzw_cnn(vocab_size,embedding_matrix,input_length, classify_type):
    model = keras.Sequential()
    e = keras.layers.Embedding(vocab_size, 50, weights=[embedding_matrix], input_length=input_length, trainable=False)
    model.add(e)
    model.add(keras.layers.Conv1D(128, 5, padding='valid', activation='relu', strides=1))
    model.add(keras.layers.MaxPool1D(5))
    model.add(keras.layers.Conv1D(128, 5, padding='valid', activation='relu', strides=1))
    model.add(keras.layers.MaxPool1D(5))
    model.add(keras.layers.Conv1D(128, 5, padding='valid', activation='relu', strides=1))
    model.add(keras.layers.MaxPool1D(35))
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(128, activation='relu'))
    model.add(keras.layers.Dense(classify_type, activation=final_active_func(classify_type)))
    return model

def zzw_lstm(vocab_size,embedding_matrix,input_length, classify_type):
    model = keras.Sequential()
    e = keras.layers.Embedding(vocab_size, 50, weights=[embedding_matrix], input_length=input_length, trainable=False,
                                     batch_input_shape=(32, input_length, 50))
    model.add(e)
    model.add(keras.layers.CuDNNLSTM(50, return_sequences=True, stateful=True))
    model.add(keras.layers.CuDNNLSTM(50, return_sequences=True, stateful=True))
    model.add(keras.layers.CuDNNLSTM(50, return_sequences=False, stateful=True))
    model.add(keras.layers.Dense(classify_type, activation=final_active_func(classify_type)))
    return model

