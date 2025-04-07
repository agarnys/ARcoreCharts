import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum

class Axis(Enum):
    X = 0
    Y = 1
    Z = 2

number = input("wpisz numer pliku")

fileName1 = "files/dane" + number + ".csv"
fileName2 = "files/checkpoint" + number + ".csv"

allValues = pd.read_csv(fileName1, header=None)
checkpointsData = pd.read_csv(fileName2, header=None)

trace = go.Scatter3d(
    x=allValues[0], y=allValues[1], z=allValues[2],
    mode='markers',
    marker=dict(size=5, color='blue', opacity=0.8),
    name='Values'
)

checkpoints = go.Scatter3d(
    x=checkpointsData[0], y=checkpointsData[1], z=checkpointsData[2],
    mode='markers',
    marker=dict(size=5, color='red', opacity=0.8),
    name='Checkpoints'
)

layout = go.Layout(
    title='Map',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    )
)

fig = go.Figure(data=[trace, checkpoints], layout=layout)
fig.show()
# X=-0.22008243, Y=-0.10234111, Z=0.33484104
plt.scatter(allValues[Axis.X.value], allValues[Axis.Y.value])
plt.scatter(checkpointsData[Axis.X.value], checkpointsData[Axis.Y.value])
plt.xlabel("X")
plt.ylabel("Y")
plt.show()

plt.scatter(allValues[Axis.X.value], allValues[Axis.Z.value])
plt.scatter(checkpointsData[Axis.X.value], checkpointsData[Axis.Z.value])
plt.xlabel("X")
plt.ylabel("Z")
plt.show()

plt.scatter(allValues[Axis.Y.value], allValues[Axis.Z.value])
plt.scatter(checkpointsData[Axis.Y.value], checkpointsData[Axis.Z.value])
plt.xlabel("Y")
plt.ylabel("Z")
plt.show()
