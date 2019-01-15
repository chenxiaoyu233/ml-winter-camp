import pandas as pd
from sklearn.utils import shuffle
import numpy as np

np.random.seed(1234)
import tensorflow as tf
from tensorflow import keras

tf.set_random_seed(1234)

from log_utils import get_logger
LOGGER = get_logger("end2end")

from models import get_model

MAX_LENGTH = 200
VOCAB_SIZE = 0
MODEL_NAME = ""

import argparse
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", dest="model", type=str, help="Choose Your Model")
    parser.add_argument("--classify", dest="classify", type=int, help="Choose The Classify Method")
    args = parser.parse_args()
    return args

def input_doc():
    global VOCAB_SIZE
    df = pd.read_csv('MBTIv1.csv')
    df = shuffle(df)

    docs = df['posts']
    labels = np.vstack([df['IE'], df['NS'], df['TF'], df['JP']]).transpose()

    t = keras.preprocessing.text.Tokenizer()
    t.fit_on_texts(docs)

    VOCAB_SIZE= len(t.word_index) + 1
    encoded_docs = t.texts_to_sequences(docs)
    padded_docs = keras.preprocessing.sequence.pad_sequences(encoded_docs, maxlen=MAX_LENGTH, padding='post')
    return t,padded_docs,labels

def get_embedding_matrix(t):
    # Input gloVe
    embeddings_index = {}
    f = open('glove.6B.50d.txt', 'r')
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()
    LOGGER.info('Loaded %s word vectors.' % len(embeddings_index))

    embedding_matrix = np.zeros((VOCAB_SIZE, 50))
    for word, i in t.word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
    return embedding_matrix


def data_splitting(docs,labels):
    num_instances = len(docs)
    d1 = int(num_instances * 0.8)
    d2 = int(num_instances * 0.9)

    trainX = docs[:d1]
    trainY = labels[:d1, :]

    valX = docs[d1:d2]
    valY = labels[d1:d2, :]

    testX = docs[d2:]
    testY = labels[d2:, :]
    return trainX, trainY, valX, valY, testX, testY


def testing(model, testX, testY, classify_type):
    LOGGER.info("\n------------------------\n")
    loss, _ = model.evaluate(testX, testY, verbose=1) # 不用它的accuracy
    LOGGER.info("Loss on test set(10%) = {}".format(loss))

    # 计算accuary
    shape = testX.shape
    counter_one_by_one = 0
    counter_total = 0
    X = model.predict(testX).tolist()
    Y = testY.tolist()
    shape = testY.shape
    print("hhh{}".format(shape))

    if classify_type == 4:
        for i in range(shape[0]):
            rowx = []
            rowy = []
            for j in range(shape[1]):
                bx = X[i][j] > 0.5
                by = Y[i][j] > 0.5
                counter_one_by_one += int(bx == by)
                rowx.append(bx)
                rowy.append(by)
            counter_total += int(rowx == rowy)
        LOGGER.info("Accuracy(Total) on test set(10%) = {}".format(float(counter_total)/float(shape[0])))
        LOGGER.info("Accuracy(One by one) on test set(10%) = {}".format((float(counter_one_by_one)/float(shape[0] * 4))))
    elif classify_type == 16:
        for i in range(shape[0]):
            val, whex, whey = -1e20, -1
            for j in range(shape[1]):
                if val < X[j]:
                    val, whex = X[j], j
            val = -1e20
            for j in range(shape[1]):
                if val < Y[j]:
                    val, whey = Y[j], j
            counter_total += int(whex == whey)
        LOGGER.info("Accuracy(Total) on test set(10%) = {}".format(float(counter_total)/float(shape[0])))


if __name__=="__main__":
    args = parse_args()
    MODEL_NAME = args.model

    t,padded_docs,labels = input_doc()
    embedding_matrix = get_embedding_matrix(t)

    trainX,trainY,valX,valY,testX,testY = data_splitting(padded_docs,labels)

    model = get_model(MODEL_NAME, VOCAB_SIZE, embedding_matrix, MAX_LENGTH, arg.classify)
    # model = keras.models.load_model(MODEL_NAME+".h5")
    model.summary(print_fn=LOGGER.info)

    callbacks = [keras.callbacks.EarlyStopping(monitor='val_loss', patience=3),
                 keras.callbacks.ModelCheckpoint(filepath='best_model.h5', monitor='val_loss', save_best_only=True)]
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Training
    LOGGER.info("Begin Training")
    history = model.fit(trainX, trainY, epochs=20, callbacks=callbacks, verbose=1,
                        validation_data=(valX, valY))

    # Testing
    testing(model, testX, testY, args.classify)

    # Save the model
    model.save(MODEL_NAME+".h5")
