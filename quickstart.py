import torch
import numpy as np
import merlin as ML
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split

X, y = make_circles(n_samples=400)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

min_vals = X_train.min(axis=0, keepdims=True)
max_vals = X_train.max(axis=0, keepdims=True)
X_train = (X_train - min_vals) / np.clip(max_vals - min_vals, a_min=1e-6, a_max=None)
X_test = (X_test - min_vals) / np.clip(max_vals - min_vals, a_min=1e-6, a_max=None)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.long)

quantum_layer = ML.QuantumLayer.simple(input_size=2, output_size=2)

optimizer = torch.optim.Adam(quantum_layer.parameters(), lr=0.01)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(100):
    optimizer.zero_grad()
    logits = quantum_layer(X_train)
    loss = criterion(logits, y_train)
    loss.backward()
    optimizer.step()
    if epoch % 20 == 0 or epoch == 99:
        print(f"epoch {epoch:3d}  train loss {loss.item():.4f}")

with torch.no_grad():
    test_logits = quantum_layer(X_test)
    test_preds = test_logits.argmax(dim=1)
    test_acc = (test_preds == y_test).float().mean().item()
print(f"test accuracy: {test_acc:.4f}")
