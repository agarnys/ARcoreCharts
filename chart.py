import os
import re

import numpy as np
import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
import axis

import algorithm



margin_ratio = 0.1

def get_dynamic_range(data):
    data_min = data.min()
    data_max = data.max()
    range_span = data_max - data_min
    margin = range_span * margin_ratio
    return data_min - margin, data_max + margin

# === ŚCIEŻKI ===
base_folder = "files"
data_prefix = "dane"
checkpoints_prefix = "checkpoint"
data_suffix = ".csv"

# === WZORZEC: dowolna nazwa kończąca się na datę ===
folder_pattern = re.compile(r'^(.*)(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$')

# === ZNAJDŹ PASUJĄCE FOLDERY ===
available_datasets = []

for folder in sorted(os.listdir(base_folder)):
    full_path = os.path.join(base_folder, folder)
    if not os.path.isdir(full_path):
        continue

    match = folder_pattern.match(folder)
    if not match:
        continue

    timestamp = match.group(2)
    file1 = os.path.join(full_path, f"{data_prefix}-{timestamp}{data_suffix}")
    file2 = os.path.join(full_path, f"{checkpoints_prefix}-{timestamp}{data_suffix}")

    if os.path.isfile(file1) and os.path.isfile(file2):
        available_datasets.append((folder, timestamp, file1, file2))

if not available_datasets:
    print("Brak folderów zawierających poprawne dane.")
    exit(1)

# === WYBÓR ===
print("Znalezione foldery z poprawnymi danymi:")
for idx, (folder, timestamp, _, _) in enumerate(available_datasets):
    print(f"{idx}: {folder[:-20]} | data: {timestamp}")

selected_idx = int(input("Wybierz numer folderu: "))
selected_folder, timestamp, fileName1, fileName2 = available_datasets[selected_idx]

# === ODCZYT DANYCH ===
print(f"\nWczytywanie danych z:\n- {fileName1}\n- {fileName2}")
allValues = pd.read_csv(fileName1, header=None)
checkpointsData = pd.read_csv(fileName2, header=None)

mode = input("Czy chcesz poprawić pomiary wględem odstających punktów? (t/n)")

if mode.lower() in ("tak", "t"):
    allValues = algorithm.check_points(allValues, 0.1)
else:
    pochodne = algorithm.licz_pochodne(allValues)
    nieciaglosci = algorithm.wykryj_nieciaglosci(pochodne, prog=1.0)
    allValues = algorithm.korekta(nieciaglosci, allValues)
    algorithm.rysuj(allValues, nieciaglosci)

#TODO zób 2 możliwości żeby osie były wszędzie takie same względem największej, lub tak jak teraz jest

# ====== USTAWIENIE ZAKRESÓW ======
combined_x = pd.concat([allValues[axis.Axis.X.value], checkpointsData[axis.Axis.X.value]])
combined_y = pd.concat([allValues[axis.Axis.Y.value], checkpointsData[axis.Axis.Y.value]])
combined_z = pd.concat([allValues[axis.Axis.Z.value], checkpointsData[axis.Axis.Z.value]])

axis_x_min, axis_x_max = get_dynamic_range(combined_x)
axis_y_min, axis_y_max = get_dynamic_range(combined_y)
axis_z_min, axis_z_max = get_dynamic_range(combined_z)

# ====== WYKRES 3D Plotly ======
# Z is switched with Y to better clarity

# allValues_texts = [f"Punkt {i}" for i in range(len(allValues))]
# checkpoints_texts = [f"Checkpoint {i}" for i in range(len(checkpointsData))]

allValues_texts = [
    f"X: {x:.2f}<br>Y: {y:.2f}<br>Z: {z:.2f}"
    for i, (x, y, z) in enumerate(zip(
        allValues[axis.Axis.X.value],
        allValues[axis.Axis.Y.value],
        allValues[axis.Axis.Z.value]
    ))
]

checkpoints_texts = [
    f"Checkpoint {i+1}<br>X: {x:.2f}<br>Y: {y:.2f}<br>Z: {z:.2f}"
    for i, (x, y, z) in enumerate(zip(
        checkpointsData[axis.Axis.X.value],
        checkpointsData[axis.Axis.Y.value],
        checkpointsData[axis.Axis.Z.value]
    ))
]


trace = go.Scatter3d(
    x=allValues[axis.Axis.X.value], y=allValues[axis.Axis.Z.value], z=allValues[axis.Axis.Y.value],
    mode='markers',
    marker=dict(size=4, color='blue', opacity=0.8),
    name='Values',
    text=allValues_texts,
    hoverinfo='text'
)

checkpoints = go.Scatter3d(
    x=checkpointsData[axis.Axis.X.value], y=checkpointsData[axis.Axis.Z.value], z=checkpointsData[axis.Axis.Y.value],
    mode='markers',
    marker=dict(size=5, color='red', opacity=0.8),
    name='Checkpoints',
    text=checkpoints_texts,
    hoverinfo='text'
)

layout = go.Layout(
    title=f'Map:{timestamp}',
    scene=dict(
        xaxis_title='X(prawo lewo)',
        yaxis_title='Z(przód tył)',
        zaxis_title='Y(dół góra)',
        xaxis=dict(range=[axis_x_min, axis_x_max]),
        yaxis=dict(range=[axis_z_min, axis_z_max]),
        zaxis=dict(range=[axis_y_min, axis_y_max]),
    )
)

fig = go.Figure(data=[trace, checkpoints], layout=layout)
fig.show()

# ====== WYKRESY 2D Matplotlib ======
# XY
plt.title(timestamp)
plt.scatter(allValues[axis.Axis.X.value], allValues[axis.Axis.Y.value])
plt.scatter(checkpointsData[axis.Axis.X.value], checkpointsData[axis.Axis.Y.value])
plt.xlabel("X(prawo lewo)")
plt.ylabel("Y(dół góra)")
plt.xlim([axis_x_min, axis_x_max])
plt.ylim([axis_y_min, axis_y_max])

for i, (x, y) in enumerate(zip(checkpointsData[axis.Axis.X.value], checkpointsData[axis.Axis.Y.value])):
    plt.text(x, y, f"{i+1}", fontsize=6, color='black')

plt.show()

# XZ
plt.title(timestamp)
plt.scatter(allValues[axis.Axis.X.value], allValues[axis.Axis.Z.value])
plt.scatter(checkpointsData[axis.Axis.X.value], checkpointsData[axis.Axis.Z.value])
plt.xlabel("X(prawo lewo)")
plt.ylabel("Z(przód tył)")
plt.xlim([axis_x_min, axis_x_max])
plt.ylim([axis_z_min, axis_z_max])

for i, (x, y) in enumerate(zip(checkpointsData[axis.Axis.X.value], checkpointsData[axis.Axis.Z.value])):
    plt.text(x, y, f"{i+1}", fontsize=6, color='black')

plt.show()

# ZY
plt.title(timestamp)
plt.scatter(allValues[axis.Axis.Z.value], allValues[axis.Axis.Y.value])
plt.scatter(checkpointsData[axis.Axis.Z.value], checkpointsData[axis.Axis.Y.value])
plt.xlabel("Z(przód tył)")
plt.ylabel("Y(dół góra)")
plt.xlim([axis_z_min, axis_z_max])
plt.ylim([axis_y_min, axis_y_max])

for i, (x, y) in enumerate(zip(checkpointsData[axis.Axis.Z.value], checkpointsData[axis.Axis.Y.value])):
    plt.text(x, y, f"{i+1}", fontsize=6, color='black')

# ====== RÓŻNICE X, Y, Z (delta między kolejnymi punktami) ======
# Zakładam, że masz dane allValues[Axis.X.value], itp.
# Próg dla odstających punktów
threshold = 0.1

# Oblicz różnice
delta_x = np.diff(allValues[axis.Axis.X.value])
delta_y = np.diff(allValues[axis.Axis.Y.value])
delta_z = np.diff(allValues[axis.Axis.Z.value])

# Indeksy dla wykresów
indexes = np.arange(len(delta_x))

# ====== WYKRES ΔX ======
plt.figure(figsize=(16, 6))
plt.plot(indexes, delta_x, linestyle='-', linewidth=1.5, label="ΔX")
plt.axhline(0, color='gray', linestyle='--')

# Adnotacje dla punktów odstających
for i, val in enumerate(delta_x):
    if abs(val) > threshold:
        plt.text(i, val, str(i+1) +"-"+ str(i+2), color='purple', fontsize=9, ha='center')

plt.title(f"Różnice między kolejnymi punktami (ΔX) - {timestamp}")
plt.xlabel("Indeks")
plt.ylabel("ΔX")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.margins(x=0.05, y=0.1)
plt.show()

# ====== WYKRES ΔY ======
plt.figure(figsize=(16, 6))
plt.plot(indexes, delta_y, color='green', label="ΔY")
plt.axhline(0, color='gray', linestyle='--')

# Adnotacje dla punktów odstających
for i, val in enumerate(delta_y):
    if abs(val) > threshold:
        plt.text(i, val, str(i+1) +"-"+ str(i+2), color='purple', fontsize=9, ha='center')

plt.title(f"Różnice między kolejnymi punktami (ΔY) - {timestamp}")
plt.xlabel("Indeks")
plt.ylabel("ΔY")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ====== WYKRES ΔZ ======
plt.figure(figsize=(16, 6))
plt.plot(indexes, delta_z, color='orange', label="ΔZ")
plt.axhline(0, color='gray', linestyle='--')

# Adnotacje dla punktów odstających
for i, val in enumerate(delta_z):
    if abs(val) > threshold:
        plt.text(i, val, str(i+1) +"-"+ str(i+2), color='purple', fontsize=9, ha='center')

plt.title(f"Różnice między kolejnymi punktami (ΔZ) - {timestamp}")
plt.xlabel("Indeks")
plt.ylabel("ΔZ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()




