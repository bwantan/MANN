import tensorflow as tf
import pandas as pd
import numpy as np
from LSTMCell import *
import helper

length = 5
bitDepth = 3

def makeLSTM(x, mask):  
    lstmCell = LSTMCell("lstm", bitDepth+1, 12, 12)
    output = []

    for i in range(0,x.get_shape()[1]):
        print("Building step: "+str(i+1))
        input = tf.squeeze(tf.slice(x, [0,i,0], [-1,1,-1]),[1])
        O = lstmCell.buildTimeLayerBatch(input, bool(i==0))
        
        if(mask[i]==1):
            with tf.variable_scope("lstm"):
                O = helper.mapBatch("outputMap", O, bitDepth)
                print(O.get_shape())
                output.append(tf.expand_dims(O, 0))

    return tf.concat(output, axis=0)

x = tf.placeholder(tf.float32, shape=(None, length * 2, bitDepth+1))
_y = tf.placeholder(tf.float32, shape=(None, length, bitDepth))

#mask = np.concatenate((np.zeros((length*2)), np.array([0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1])), axis=0)
mask = np.concatenate((np.zeros((length)), np.ones((length))), axis=0)
y = makeLSTM(x, mask)

crossEntropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=_y, logits=y)
trainStep = tf.train.AdamOptimizer().minimize(crossEntropy)

p = tf.round(tf.sigmoid(y))
accuracy = tf.reduce_mean(tf.cast(tf.equal(_y,p), tf.float32))

helper.printStats(tf.trainable_variables())

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(10000):
        #X,Y = helper.getNewxyBatch(length, bitDepth,100)
        #trainStep.run(feed_dict={x: X, _y: Y})

        #for j in range(1000):
        X,Y = helper.getNewxyBatch(length, bitDepth, 1000)
        trainStep.run(feed_dict={x: X, _y: Y})

        sum = 0.0
        #for j in range(100):
        X,Y = helper.getNewxyBatch(length, bitDepth, 100)
        sum += sess.run(accuracy, feed_dict={x: X, _y: Y})

        print("Training batch: " + str(i+1) + " | AVG accuracy: " + str(sum/100))