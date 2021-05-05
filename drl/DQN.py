import numpy as np
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, InputLayer
from tensorflow.keras.optimizers import Adam

from collections import deque

## Adapted from https://towardsdatascience.com/reinforcement-learning-w-keras-openai-dqns-1eed3a5338c
## Please refer to this web-page to understand the model as this model has been modified for the current work.


class DQN:
    def __init__(self):
        # self.env     = env
        self.action_dim=2
        self.state_space_dim=1
        self.memory  = deque(maxlen=200)
        
        self.gamma = 0.85
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.98
        self.learning_rate = 0.1
        self.tau = .125

        self.model        = self.create_model()
        self.target_model = self.create_model()

    def create_model(self):
        model   = Sequential()
        # model.add(InputLayer(input_shape=[self.state_space_dim,1]))
        model.add(Dense(32, input_dim=self.state_space_dim, activation="relu"))
        model.add(Dense(16, activation="relu"))
        model.add(Dense(2))
        model.compile(loss="mean_squared_error",
            optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return np.random.choice([0,1])
        return np.argmax(self.model.predict(state))

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 16
        if len(self.memory) < batch_size: 
            return

        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            state, action, reward, new_state, done = sample
            target = self.target_model.predict(state)
            if done:
                target[0][action] = reward
            else:
                Q_future = np.amax(self.target_model.predict(new_state))
                target[0][action] = reward + Q_future * self.gamma
            self.model.fit(state, target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)