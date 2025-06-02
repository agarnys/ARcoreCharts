import os
import re

import pandas as pd
import plotly.graph_objs as go

import algorithm
import axis

margin_ratio = 0.1


def get_dynamic_range(data):
    data_min = data.min()
    data_max = data.max()
    range_span = data_max - data_min
    margin = range_span * margin_ratio
    return data_min - margin, data_max + margin


# === ŚCIEŻKI ===
base_folder = "files"
data_prefix = "data"
checkpoints_prefix = "checkpoints"
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

# === DANE OD UŻYTKOWNIKA ===
invert_z = input("Czy chcesz zamienić zwrot osi Z (przód ↔ tył) dla lepszej orientacji wykresu? (t/n) ")
repair = input("Czy chcesz poprawić pomiary względem odstających punktów? (t/n) ")
axis_size = input("Czy skala ma być taka sama dla wszystkich osi? (t/n) ")

if invert_z.lower() in ("tak", "t"):
    # === ODWRÓĆ OŚ Z ===
    allValues[axis.Axis.Z.value] *= -1
    checkpointsData[axis.Axis.Z.value] *= -1

if repair.lower() in ("tak", "t"):
    # === KOREKTA DANYCH ===
    # Popraw dane główne
    deltas_all = algorithm.compute_position_deltas(allValues)
    discontinuities_all = algorithm.detect_position_discontinuities(deltas_all, threshold=0.1)
    allValues = algorithm.correct_discontinuities(discontinuities_all, allValues)
    algorithm.plot_trajectory_with_discontinuities(allValues, discontinuities_all, timestamp)

    # # Popraw checkpointy
    # deltas_cp = algorithm.compute_position_deltas(checkpointsData)
    # discontinuities_cp = algorithm.detect_position_discontinuities(deltas_cp, threshold=0.1)
    # checkpointsData = algorithm.correct_discontinuities(discontinuities_cp, checkpointsData)
    # algorithm.plot_trajectory_with_discontinuities(checkpointsData, discontinuities_cp)

# ====== USTAWIENIE ZAKRESÓW ======
combined_x = pd.concat([allValues[axis.Axis.X.value], checkpointsData[axis.Axis.X.value]])
combined_y = pd.concat([allValues[axis.Axis.Y.value], checkpointsData[axis.Axis.Y.value]])
combined_z = pd.concat([allValues[axis.Axis.Z.value], checkpointsData[axis.Axis.Z.value]])

axis_x_min, axis_x_max = get_dynamic_range(combined_x)
axis_y_min, axis_y_max = get_dynamic_range(combined_y)
axis_z_min, axis_z_max = get_dynamic_range(combined_z)

if axis_size.lower() in ("tak", "t"):
    # === ZAKRES OSI ===
    common_min = min(axis_x_min, axis_y_min, axis_z_min)
    common_max = max(axis_x_max, axis_y_max, axis_z_max)

    axis_x_min = axis_y_min = axis_z_min = common_min
    axis_x_max = axis_y_max = axis_z_max = common_max

# ====== WYKRES 3D Plotly ======
# Z is switched with Y to better clarity

allValues_texts = [
    f"Value {i + 1}X: {x:.2f}<br>Y: {y:.2f}<br>Z: {z:.2f}"
    for i, (x, y, z) in enumerate(zip(
        allValues[axis.Axis.X.value],
        allValues[axis.Axis.Y.value],
        allValues[axis.Axis.Z.value]
    ))
]

checkpoints_texts = [
    f"Checkpoint {i + 1}<br>X: {x:.2f}<br>Y: {y:.2f}<br>Z: {z:.2f}"
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
    line=dict(color='blue'),
    text=allValues_texts,
    hoverinfo='text'
)

if repair.lower() not in ("tak", "t"):
    checkpoints = go.Scatter3d(
        x=checkpointsData[axis.Axis.X.value], y=checkpointsData[axis.Axis.Z.value],
        z=checkpointsData[axis.Axis.Y.value],
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

if repair.lower() not in ("tak", "t"):
    fig = go.Figure(data=[trace, checkpoints], layout=layout)
else:
    fig = go.Figure(data=[trace], layout=layout)

fig.show()

# ====== WYKRESY 2D Matplotlib ======

algorithm.plot_2d_projections_with_checkpoints(
    all_values=allValues,
    checkpoints_data=checkpointsData,
    axis_limits={
        axis.Axis.X.value: (axis_x_min, axis_x_max),
        axis.Axis.Y.value: (axis_y_min, axis_y_max),
        axis.Axis.Z.value: (axis_z_min, axis_z_max),
    },
    timestamp=timestamp,
    repair=repair
)

# Oblicz różnice (pochodne)
pochodne = algorithm.compute_position_deltas(allValues)

# Próg dla oznaczenia odstających punktów
threshold = 0.1

# Rysowanie wykresów
algorithm.plot_derivative_changes(pochodne, axis.Axis.X.value, 'blue', 'ΔX', threshold, timestamp)
algorithm.plot_derivative_changes(pochodne, axis.Axis.Y.value, 'green', 'ΔY', threshold, timestamp)
algorithm.plot_derivative_changes(pochodne, axis.Axis.Z.value, 'orange', 'ΔZ', threshold, timestamp)
algorithm.plot_derivative_changes(algorithm.compute_derivative_magnitude(pochodne), 'none', 'red', '|ΔV|', threshold,
                                  timestamp)
