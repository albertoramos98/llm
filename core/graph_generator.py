import matplotlib.pyplot as plt

def gerar_grafico_exemplo(data):
    fig, ax = plt.subplots()
    ax.plot(data)
    return fig
