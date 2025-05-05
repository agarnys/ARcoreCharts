import os
import re
import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum


class Axis(Enum):
    X = 0
    Y = 1
    Z = 2

# ====== USTAWIENIE ZAKRESÓW DYNAMICZNIE (z marginesem procentowym) ======
# Możesz zmieniać ten procent np. 10% (0.1), 20% (0.2), itd.
margin_ratio = 0.1  # 10% marginesu

def get_dynamic_range(data):
    """Zwraca min i max z dodanym marginesem procentowym."""
    data_min = data.min()
    data_max = data.max()
    range_span = data_max - data_min
    margin = range_span * margin_ratio
    return data_min - margin, data_max + margin

# ====== USTAWIENIA ŚCIEŻEK ======
base_folder = "files"
data_prefix = "dane"
checkpoints_prefix = "checkpoint"
data_suffix = ".csv"

# ====== SZUKANIE FOLDERÓW dataset-YYYY-MM-DD_HH-MM-SS ======
available_folders = sorted(
    [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f)) and f.startswith("dataset-")]
)

if not available_folders:
    print("Brak folderów z danymi w katalogu 'files/'.")
    exit(1)

print("Dostępne foldery z danymi:")
for idx, folder in enumerate(available_folders):
    print(f"{idx}: {folder}")

selected_idx = int(input("Wybierz numer folderu z listy: "))
selected_folder = available_folders[selected_idx]

# ====== WYODRĘBNIENIE ZNACZNIKA CZASU Z NAZWY ======
match = re.match(r"dataset-(.+)", selected_folder)
if not match:
    print("Niepoprawna nazwa folderu.")
    exit(1)

timestamp = match.group(1)

# ====== KONSTRUKCJA ŚCIEŻEK DO PLIKÓW ======
folder_path = os.path.join(base_folder, selected_folder)
fileName1 = os.path.join(folder_path, f"{data_prefix}-{timestamp}{data_suffix}")
fileName2 = os.path.join(folder_path, f"{checkpoints_prefix}-{timestamp}{data_suffix}")

print(f"\nŁadowanie plików:\n - {fileName1}\n - {fileName2}")

# ====== WCZYTYWANIE DANYCH ======
allValues = pd.read_csv(fileName1, header=None)
checkpointsData = pd.read_csv(fileName2, header=None)

# ====== USTAWIENIE ZAKRESÓW ======
combined_x = pd.concat([allValues[Axis.X.value], checkpointsData[Axis.X.value]])
combined_y = pd.concat([allValues[Axis.Y.value], checkpointsData[Axis.Y.value]])
combined_z = pd.concat([allValues[Axis.Z.value], checkpointsData[Axis.Z.value]])

axis_x_min, axis_x_max = get_dynamic_range(combined_x)
axis_y_min, axis_y_max = get_dynamic_range(combined_y)
axis_z_min, axis_z_max = get_dynamic_range(combined_z)

# ====== WYKRES 3D Plotly ======
# Z is switched with Y to better clarity
trace = go.Scatter3d(
    x=allValues[Axis.X.value], y=allValues[Axis.Z.value], z=allValues[Axis.Y.value],
    mode='markers',
    marker=dict(size=5, color='blue', opacity=0.8),
    name='Values'
)

checkpoints = go.Scatter3d(
    x=checkpointsData[Axis.X.value], y=checkpointsData[Axis.Z.value], z=checkpointsData[Axis.Y.value],
    mode='markers',
    marker=dict(size=5, color='red', opacity=0.8),
    name='Checkpoints'
)

layout = go.Layout(
    title='Map',
    scene=dict(
        xaxis_title='X(prawo lewo)',
        yaxis_title='Z(przód tył)',
        zaxis_title='Y(góra dół)',
        xaxis=dict(range=[axis_x_min, axis_x_max]),
        yaxis=dict(range=[axis_z_min, axis_z_max]),
        zaxis=dict(range=[axis_y_min, axis_y_max]),
    )
)

fig = go.Figure(data=[trace, checkpoints], layout=layout)
fig.show()

# ====== WYKRESY 2D Matplotlib ======
# XY
plt.scatter(allValues[Axis.X.value], allValues[Axis.Y.value])
plt.scatter(checkpointsData[Axis.X.value], checkpointsData[Axis.Y.value])
plt.xlabel("X")
plt.ylabel("Y")
plt.xlim([axis_x_min, axis_x_max])
plt.ylim([axis_y_min, axis_y_max])
plt.show()

# XZ
plt.scatter(allValues[Axis.X.value], allValues[Axis.Z.value])
plt.scatter(checkpointsData[Axis.X.value], checkpointsData[Axis.Z.value])
plt.xlabel("X")
plt.ylabel("Z")
plt.xlim([axis_x_min, axis_x_max])
plt.ylim([axis_z_min, axis_z_max])
plt.show()

# ZY
plt.scatter(allValues[Axis.Z.value], allValues[Axis.Y.value])
plt.scatter(checkpointsData[Axis.Z.value], checkpointsData[Axis.Y.value])
plt.xlabel("Z")
plt.ylabel("Y")
plt.xlim([axis_z_min, axis_z_max])
plt.ylim([axis_y_min, axis_y_max])
plt.show()
