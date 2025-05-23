import numpy as np
import matplotlib.pyplot as plt
import axis


def shift_axis_after_index(data, index, shift_value, axis):
    """
    Przesuwa wybraną oś (x, y lub z) o zadaną wartość od danego indeksu w dół.

    Parametry:
    - data: DataFrame z kolumnami: x, y, z (czyli 0, 1, 2)
    - index: indeks wiersza, po którym dane mają być przesunięte (czyli od index+1)
    - shift_value: liczba, o którą przesunąć (np. -2)
    - axis: 'x', 'y' lub 'z' (wskazuje kolumnę do modyfikacji)

    Zwraca:
    - Nowy DataFrame z naniesionym przesunięciem (oryginalny nie jest modyfikowany)
    """
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if axis not in axis_map:
        raise ValueError("Oś musi być jedną z: 'x', 'y', 'z'")

    col = axis_map[axis]
    data_copy = data.copy()
    data_copy.loc[index:, col] += shift_value
    return data_copy


def check_points(data, diff):
    for i in range(len(data) - 1):
        x = np.diff(data[axis.Axis.X.value])
        y = np.diff(data[axis.Axis.Y.value])
        z = np.diff(data[axis.Axis.Z.value])

        data = edge_points(data, diff, i, x, y, z)
    return data


def edge_points(data, diff, i, x, y, z):
    if x[i] > diff or x[i] < -diff:
        data = shift_axis_after_index(data, i + 1, 0.05 - x[i], 'x')
    if y[i] > diff or y[i] < -diff:
        data = shift_axis_after_index(data, i + 1, 0.05 - y[i], 'y')
    if z[i] > diff or z[i] < -diff:
        data = shift_axis_after_index(data, i + 1, 0.05 - z[i], 'z')
    return data


def licz_pochodne(df):
    """
    Zwraca pochodne (różnice pozycji) w postaci DataFrame.
    """
    d = df.diff()  # różnice między kolejnymi wierszami
    d.iloc[0] = 0  # pierwsza różnica nie istnieje (bo nie ma poprzedniego punktu)
    return d


def wykryj_nieciaglosci(df_diff, prog=1.0):
    """
    Wykrywa indeksy, gdzie długość pochodnej przekracza próg.
    """
    magnitude = np.sqrt(
        df_diff[axis.Axis.X.value] ** 2 + df_diff[axis.Axis.Y.value] ** 2 + df_diff[axis.Axis.Z.value] ** 2)
    nieciaglosci = magnitude[magnitude > prog].index.tolist()
    return nieciaglosci


def rysuj(df, nieciaglosci):
    """
    Wykres 3D trajektorii z zaznaczeniem nieciągłości.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(df[axis.Axis.X.value], df[axis.Axis.Y.value], df[axis.Axis.Z.value], label='Trajektoria')

    for i in nieciaglosci:
        ax.scatter(df.loc[i, axis.Axis.X.value], df.loc[i, axis.Axis.Y.value], df.loc[i, axis.Axis.Z.value],
                   color='red', s=60, label='Nieciągłość' if i == nieciaglosci[0] else "")

    ax.set_title('Ruch telefonu (z ARCore) + analiza pochodnych')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.show()


def korekta(nieciaglosci, df):
    for i in nieciaglosci:
        # obliczamy wektor skoku (pochodna w tym punkcie)
        dx = df.loc[i, axis.Axis.X.value] - df.loc[i - 1, axis.Axis.X.value]
        dy = df.loc[i, axis.Axis.Y.value] - df.loc[i - 1, axis.Axis.Y.value]
        dz = df.loc[i, axis.Axis.Z.value] - df.loc[i - 1, axis.Axis.Z.value]

        # przesuwamy wszystkie kolejne punkty, żeby usunąć skok
        df.loc[i:, axis.Axis.X.value] -= dx
        df.loc[i:, axis.Axis.Y.value] -= dy
        df.loc[i:, axis.Axis.Z.value] -= dz
    return df
