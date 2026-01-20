import numpy as np

class SimpleBrain:
    def __init__(self, input_size, hidden_size, output_size):
        # Initialize weights with small random values
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2

    def train(self, X, y, epochs=10000, learning_rate=0.1):
        for epoch in range(epochs):
            # Forward propagation
            output = self.forward(X)

            # Backpropagation
            error = y - output
            d_output = error * self.sigmoid_derivative(output)

            error_hidden = d_output.dot(self.W2.T)
            d_hidden = error_hidden * self.sigmoid_derivative(self.a1)

            # Update weights and biases
            self.W2 += self.a1.T.dot(d_output) * learning_rate
            self.b2 += np.sum(d_output, axis=0, keepdims=True) * learning_rate
            self.W1 += X.T.dot(d_hidden) * learning_rate
            self.b1 += np.sum(d_hidden, axis=0, keepdims=True) * learning_rate

            if epoch % 1000 == 0:
                loss = np.mean(np.square(y - output))
                print(f"Epoch {epoch}, Loss: {loss:.6f}")

if __name__ == "__main__":
    # Test with XOR
    X = np.array([[0,0], [0,1], [1,0], [1,1]])
    y = np.array([[0], [1], [1], [0]])

    brain = SimpleBrain(2, 4, 1)
    print("Training Brain on XOR...")
    brain.train(X, y, epochs=20000, learning_rate=0.5)

    print("\nPredictions:")
    for i in range(len(X)):
        pred = brain.forward(X[i:i+1])
        print(f"Input: {X[i]}, Target: {y[i]}, Prediction: {pred[0][0]:.4f}")
