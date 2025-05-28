import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go

import axis


def compute_position_deltas(df):
    """
    Zwraca dyskretne pochodne (różnice kolejnych pozycji) jako DataFrame.

    Parametry:
    - df: DataFrame zawierający współrzędne pozycji.

    Zwraca:
    - DataFrame z różnicami kolejnych pozycji.
    """
    d = df.diff()
    d.iloc[0] = 0
    return d


def detect_position_discontinuities(df_diff, threshold=1.0):
    """
    Wykrywa indeksy, w których długość wektora pochodnej przekracza zadany próg.

    Parametry:
    - df_diff: DataFrame z pochodnymi pozycji.
    - threshold: próg długości wektora, powyżej którego uznaje się zmianę za nieciągłość.

    Zwraca:
    - Listę indeksów, w których wykryto nieciągłości.
    """
    magnitude = compute_derivative_magnitude(df_diff)
    return np.where(magnitude > threshold)[0].tolist()


def compute_derivative_magnitude(df_diff):
    """
    Oblicza długość (moduł) wektorów pochodnych 3D.

    Parametry:
    - df_diff: DataFrame z pochodnymi współrzędnych (X, Y, Z).

    Zwraca:
    - Wektor długości pochodnych dla każdego punktu.
    """
    magnitude = np.linalg.norm(df_diff[[axis.Axis.X.value, axis.Axis.Y.value, axis.Axis.Z.value]].values, axis=1)
    return magnitude


def correct_discontinuities(discontinuity_indices, df):
    """
    Koryguje trajektorię poprzez usunięcie nagłych skoków w danych
    — przesuwa wszystkie kolejne punkty tak, aby zachować ciągłość ścieżki.

    Parametry:
    - discontinuity_indices: lista indeksów punktów nieciągłości.
    - df: DataFrame z oryginalnymi danymi pozycji.

    Zwraca:
    - Poprawiony DataFrame z wyrównaną trajektorią.
    """
    for i in discontinuity_indices:
        dx = df.loc[i, axis.Axis.X.value] - df.loc[i - 1, axis.Axis.X.value]
        dy = df.loc[i, axis.Axis.Y.value] - df.loc[i - 1, axis.Axis.Y.value]
        dz = df.loc[i, axis.Axis.Z.value] - df.loc[i - 1, axis.Axis.Z.value]

        df.loc[i:, axis.Axis.X.value] -= dx
        df.loc[i:, axis.Axis.Y.value] -= dy
        df.loc[i:, axis.Axis.Z.value] -= dz
    return df


def plot_2d_projections_with_checkpoints(all_values, checkpoints_data, axis_limits, timestamp, repair):
    """
    Rysuje 2D projekcje (XY, XZ, ZY) pozycji wraz z punktami kontrolnymi, jeśli nie włączono trybu naprawy.

    Parametry:
    - all_values: DataFrame z pełną trajektorią (zawiera kolumny X, Y, Z).
    - checkpoints_data: DataFrame z punktami kontrolnymi (X, Y, Z).
    - axis_limits: słownik z granicami osi, np. {
          'x': (xmin, xmax),
          'y': (ymin, ymax),
          'z': (zmin, zmax)
      }
    - timestamp: etykieta czasu do tytułów wykresów.
    - repair: str, jeżeli "tak" lub "t" (niezależnie od wielkości liter), punkty kontrolne nie będą rysowane.
    """
    def _plot_projection(x_axis, y_axis, x_label, y_label):
        plt.title(timestamp)
        plt.scatter(all_values[x_axis], all_values[y_axis], label='Trajektoria', s=10)

        if repair.lower() not in ("tak", "t"):
            plt.scatter(checkpoints_data[x_axis], checkpoints_data[y_axis], color='red', label='Punkty kontrolne', s=20)
            for i, (x, y) in enumerate(zip(checkpoints_data[x_axis], checkpoints_data[y_axis])):
                plt.text(x, y, f"{i + 1}", fontsize=6, color='black')

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xlim(axis_limits[x_axis])
        plt.ylim(axis_limits[y_axis])
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    _plot_projection(axis.Axis.X.value, axis.Axis.Y.value, "X(lewo prawo)", "Y(dół góra)")
    _plot_projection(axis.Axis.X.value, axis.Axis.Z.value, "X(lewo prawo)", "Z(przód tył)")
    _plot_projection(axis.Axis.Z.value, axis.Axis.Y.value, "Z(przód tył)", "Y(dół góra)")


def plot_trajectory_with_discontinuities(df, discontinuity_indices):
    """
    Tworzy interaktywny wykres 3D trajektorii, zaznaczając punkty, w których wykryto nieciągłości.

    Parametry:
    - df: DataFrame z danymi pozycji.
    - discontinuity_indices: lista indeksów punktów nieciągłości.
    """
    trace_trajectory = go.Scatter3d(
        x=df[axis.Axis.X.value],
        y=df[axis.Axis.Z.value],
        z=df[axis.Axis.Y.value],
        mode='lines+markers',
        marker=dict(size=3, color='blue', opacity=0.8),
        line=dict(color='blue'),
        name='Trajektoria'
    )

    trace_discontinuities = go.Scatter3d(
        x=df.loc[discontinuity_indices, axis.Axis.X.value],
        y=df.loc[discontinuity_indices, axis.Axis.Z.value],
        z=df.loc[discontinuity_indices, axis.Axis.Y.value],
        mode='markers',
        marker=dict(size=6, color='red', opacity=1.0),
        name='Nieciągłość'
    )

    fig = go.Figure(data=[trace_trajectory, trace_discontinuities])
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


def plot_derivative_changes(df_diff, column, color, label, threshold, timestamp):
    """
    Rysuje wykres zmian wartości pochodnych w czasie, z zaznaczeniem punktów przekraczających próg.

    Parametry:
    - df_diff: DataFrame z pochodnymi.
    - column: nazwa kolumny (np. 'x', 'y', 'z') lub 'none', jeśli podano wektor ręcznie.
    - color: kolor linii wykresu.
    - label: etykieta osi i legendy.
    - threshold: wartość progowa do zaznaczenia.
    - timestamp: znacznik czasu używany w tytule wykresu.
    """
    plt.figure(figsize=(16, 6))
    indexes = np.arange(len(df_diff))
    if column == 'none':
        delta = df_diff
    else:
        delta = df_diff[column].values
    plt.plot(indexes, delta, color=color, label=label)
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
