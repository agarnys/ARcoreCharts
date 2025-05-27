import numpy as np
import matplotlib.pyplot as plt
import axis
import plotly.graph_objs as go


def shift_axis_after_index(data, index, shift_value, axis_name):
    """
    Przesuwa wybraną oś (x, y lub z) o zadaną wartość od danego indeksu w dół.

    Parametry:
    - data: DataFrame z kolumnami: x, y, z (czyli 0, 1, 2)
    - index: indeks wiersza, po którym dane mają być przesunięte (czyli od index+1)
    - shift_value: liczba, o którą przesunąć (np. -2)
    - axis_name: 'x', 'y' lub 'z' (wskazuje kolumnę do modyfikacji)

    Zwraca:
    - Nowy DataFrame z naniesionym przesunięciem (oryginalny nie jest modyfikowany)
    """
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if axis_name not in axis_map:
        raise ValueError("Oś musi być jedną z: 'x', 'y', 'z'")

    col = axis_map[axis_name]
    data_copy = data.copy()
    data_copy.loc[index:, col] += shift_value
    return data_copy


def edge_points(data, diff, i, dx, dy, dz):
    """
    Sprawdza pochodne w punkcie i i w razie przekroczenia progu koryguje kolejne punkty.
    """
    if abs(dx[i]) > diff:
        data = shift_axis_after_index(data, i + 1, 0.05 - dx[i], 'x')
    if abs(dy[i]) > diff:
        data = shift_axis_after_index(data, i + 1, 0.05 - dy[i], 'y')
    if abs(dz[i]) > diff:
        data = shift_axis_after_index(data, i + 1, 0.05 - dz[i], 'z')
    return data


def check_points(data, diff):
    """
    Iteracyjnie sprawdza wszystkie różnice między punktami i koryguje te,
    które przekraczają dopuszczalny próg.
    """
    for i in range(len(data) - 1):
        dx = np.diff(data[axis.Axis.X.value])
        dy = np.diff(data[axis.Axis.Y.value])
        dz = np.diff(data[axis.Axis.Z.value])
        data = edge_points(data, diff, i, dx, dy, dz)
    return data


def licz_pochodne(df):
    """
    Zwraca pochodne (różnice pozycji) w postaci DataFrame.
    """
    d = df.diff()
    d.iloc[0] = 0
    return d


def wykryj_nieciaglosci(df_diff, prog=1.0):
    """
    Wykrywa indeksy punktów, w których długość wektora pochodnej przekracza próg.

    Zwraca:
    - Listę indeksów, gdzie pochodna przekracza zadany próg.
    """
    magnitude = calculate_magnitude(df_diff)
    return np.where(magnitude > prog)[0].tolist()


def calculate_magnitude(df_diff):
    magnitude = np.linalg.norm(df_diff[[axis.Axis.X.value, axis.Axis.Y.value, axis.Axis.Z.value]].values, axis=1)
    return magnitude


def korekta(nieciaglosci, df):
    """
    Koryguje dane usuwając nagłe skoki poprzez przesunięcie kolejnych punktów tak,
    aby wyrównać trajektorię (ciągłość ścieżki).
    """
    for i in nieciaglosci:
        dx = df.loc[i, axis.Axis.X.value] - df.loc[i - 1, axis.Axis.X.value]
        dy = df.loc[i, axis.Axis.Y.value] - df.loc[i - 1, axis.Axis.Y.value]
        dz = df.loc[i, axis.Axis.Z.value] - df.loc[i - 1, axis.Axis.Z.value]

        df.loc[i:, axis.Axis.X.value] -= dx
        df.loc[i:, axis.Axis.Y.value] -= dy
        df.loc[i:, axis.Axis.Z.value] -= dz
    return df


def rysuj(df, nieciaglosci):
    """
    Tworzy interaktywny wykres 3D trajektorii z zaznaczeniem punktów nieciągłości.
    """

    trace_trajektoria = go.Scatter3d(
        x=df[axis.Axis.X.value],
        y=df[axis.Axis.Z.value],
        z=df[axis.Axis.Y.value],
        mode='lines+markers',
        marker=dict(size=3, color='blue', opacity=0.8),
        line=dict(color='blue'),
        name='Trajektoria'
    )

    trace_nieciaglosci = go.Scatter3d(
        x=df.loc[nieciaglosci, axis.Axis.X.value],
        y=df.loc[nieciaglosci, axis.Axis.Z.value],
        z=df.loc[nieciaglosci, axis.Axis.Y.value],
        mode='markers',
        marker=dict(size=6, color='red', opacity=1.0),
        name='Nieciągłość'
    )

    fig = go.Figure(data=[trace_trajektoria, trace_nieciaglosci])
    fig.update_layout(
        title='Ruch telefonu (z ARCore) + analiza pochodnych',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Z',
            zaxis_title='Y'
        ),
        legend=dict(x=0, y=1)
    )
    fig.show()


# Funkcja pomocnicza do rysowania
def rysuj_wykres_dX(df_diff, kolumna, kolor, label, threshold, timestamp):
    plt.figure(figsize=(16, 6))
    indexes = np.arange(len(df_diff))
    if kolumna == 'none':
        delta = df_diff
    else:
        delta = df_diff[kolumna].values
    plt.plot(indexes, delta, color=kolor, label=label)
    plt.axhline(0, color='gray', linestyle='--')

    for i, val in enumerate(delta):
        if abs(val) > threshold:
            plt.text(i, val, f"{i}-{i + 1}", color='purple', fontsize=9, ha='center')

    plt.title(f"Pochodne {label} - {timestamp}")
    plt.xlabel("Indeks")
    plt.ylabel(f"{label}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.margins(x=0.05, y=0.1)
    plt.show()
