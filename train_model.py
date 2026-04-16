"""
train_model.py  –  Assignment 6 dummy training script
Simulates a GPU training run for CI/CD demonstration purposes.
"""

import time
import random


def train():
    print("Initialising model...")
    time.sleep(1)

    epochs = 3
    for epoch in range(1, epochs + 1):
        loss = round(random.uniform(0.2, 0.9) - epoch * 0.05, 4)
        acc = round(0.5 + epoch * 0.1 + random.uniform(0, 0.05), 4)
        print(f"Epoch {epoch}/{epochs}  |  loss: {loss}  |  acc: {acc}")
        time.sleep(0.5)

    print("Training finished successfully.")


if __name__ == "__main__":
    train()
raise Exception('GPU memory limit exceeded (Simulated Crash)')
