import numpy as np
import time
from brain import SimpleBrain
import matplotlib.pyplot as plt

def run_fast_training():
    print("=== Fast Neural Network Runner ===")
    print("Task: Learning a non-linear pattern (Sine Wave with Noise)")
    
    # Generate data
    X = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)
    y = np.sin(X) + np.random.normal(0, 0.1, X.shape)
    
    # Normalize data for sigmoid
    X_norm = X / (2 * np.pi)
    y_norm = (y + 1.5) / 3.0  # Map [-1.5, 1.5] to [0, 1]
    
    # Initialize Brain
    brain = SimpleBrain(input_size=1, hidden_size=10, output_size=1)
    
    start_time = time.time()
    print("Training...")
    brain.train(X_norm, y_norm, epochs=50000, learning_rate=0.1)
    end_time = time.time()
    
    print(f"\nTraining completed in {end_time - start_time:.2f} seconds.")
    
    # Predict
    predictions = brain.forward(X_norm)
    
    # Denormalize for plotting
    y_pred = predictions * 3.0 - 1.5
    
    # Plot results
    plt.figure(figsize=(10, 5))
    plt.scatter(X, y, color='gray', alpha=0.5, label='Noisy Data')
    plt.plot(X, np.sin(X), color='blue', label='True Sine')
    plt.plot(X, y_pred, color='red', linewidth=2, label='NN Prediction')
    plt.title("Neural Network Learning a Sine Wave")
    plt.legend()
    
    plot_path = "C:\\Users\\sao\\Documents\\calculator\\nn_result.png"
    plt.savefig(plot_path)
    print(f"Result plot saved to: {plot_path}")
    plt.show()

if __name__ == "__main__":
    run_fast_training()
