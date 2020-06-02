import math as m
import matplotlib.pyplot as plt


def rewardf(x, sigma=1, b=None, multi=1):
    if b is None:
        y_max = rewardf(0, sigma, b=0, multi=multi)
        b = 1 - y_max
    return ((m.exp(-(x/sigma)**2/2)) / (sigma*m.sqrt(2*m.pi)))*multi + b


def gen_graph(start, end, sigma=1, b=None, multi=1):
    xs = [x/200 for x in range(start, end+1)]
    ys = [rewardf(x, sigma, b, multi) for x in xs]
    return xs, ys


def main():
    xs, ys = gen_graph(-100, 100, sigma=0.07, multi=0.25)
    plt.plot(xs, ys)
    plt.show()


if __name__ == '__main__':
    main()
