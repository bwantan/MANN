import tensorflow as tf
import time
import mann
import helper

# Define the MANN
cell = mann.MANNUnit("L1MANN")
cell.addMemory(mann.BasicMemory("M1", 20, 14))
#cell.addController(mann.GRUCell("Controller1", 32))
#cell.addController(mann.LSTMCell("LSTM", 40))
cell.addController(mann.FFCell("FF1", 40))
#cell.addController(mann.FFCell("FF2", 40))
cell.addHead(mann.DNCHead("Head1", 3))
#cell.addHead(mann.NTMHead("Head1"))

#cell = mann.LSTMCell("LSTM", 40)

# Define the test data
# generator = mann.MinPath(7, 10, 4, 8)
# generator = mann.Copy(10,8)
generator = mann.VertexCover(7, 10, 4, 30)

# Define constants
TrainSetSize = 100000
TestSetSize = 10000
BatchSize = 100
TrainSteps = 100

# Define optimizer
#optimizer = tf.train.RMSPropOptimizer(0.001)
optimizer = tf.train.AdamOptimizer()

loadFromFile = None#"2018-05-03 14-09-22 Epoch-350 Loss-168.ckpt"

#### End of configuration ####

# Build the network
x = generator.getInput()
y = cell.build(x, generator.outputMask, generator.outputSize)
_y = generator.getLabel()

# Build optimizer
trainStep, p, accuracy, loss = generator.postBuild(_y, y, optimizer)

# Visualize parameters
helper.printStats(tf.trainable_variables())

# Generate the data
trainData = generator.makeAndSaveDataset(TrainSetSize, "train")
testData = generator.makeAndSaveDataset(TestSetSize, "test")
print("Data ready")

# Print class distribution
print(trainData.C)

# Train network
with tf.Session() as sess:
    if loadFromFile is not None:
        generator.restore(sess, loadFromFile)
    else:
        sess.run(tf.global_variables_initializer())

    # Get accuracy before training
    X, Y = testData.getBatch(BatchSize)
    acc, testLoss = sess.run([accuracy, loss], feed_dict={x: X, _y: Y})
    print("Start:" + "\tacc: " + str(acc) + "\tLoss: " + str(testLoss))

    for i in range(100000):
        # Train 1 epoch
        trainLoss = 0
        start_time = time.time()
        for j in range(TrainSteps):
            X, Y = trainData.getBatch(BatchSize)
            _, l = sess.run([trainStep, loss], feed_dict={x: X, _y: Y})
            trainLoss += l
        duration = time.time() - start_time
        trainLoss = trainLoss / BatchSize

        # Get accuracy
        X, Y = testData.getBatch(BatchSize)
        acc, testLoss, r = sess.run([accuracy, loss, p], feed_dict={x: X, _y: Y})

        generator.process(X, Y, r)

        # Print data
        print("#" + str(i + 1) + "\tacc: " + str(acc) + "\tLoss: " + str(trainLoss) + "-" + str(
            testLoss) + "\tTime: " + "{0:.4f}".format(duration) + "s")

        if i % 50 == 0 and i > 0:
            generator.save(sess, i, int(trainLoss))


