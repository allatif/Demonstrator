import os
import json
import argparse

import matplotlib.pyplot as plt
from data.components import colors


def argparser():
    parser = argparse.ArgumentParser(
        description="############# Plot fron json #############"
    )

    parser.add_argument("-n", "--number", metavar="",
                        help="choose number of file in file list, default: 0 \
                                - check on option -s --show",
                        type=int)

    parser.add_argument("-f", "--filename", metavar="",
                        help="name of the file for data plotting (.json)",
                        type=str)

    parser.add_argument("-x", "--xlabel", metavar="",
                        help="write text for the xlabel, default: 'Iterations'",
                        type=str)

    parser.add_argument("-s", "--show",
                        help="show all jsons in tools\\conserved_plots\\",
                        action="store_true")

    return parser.parse_args()


def load_all_jsons(accept=(".json")):
    jsons = []
    directory = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir(os.path.join(directory, 'tools\\conserved_plots\\')):
        name, ext = os.path.splitext(file)
        if ext.lower() in accept:
            jsons.append(name)
    return jsons


def main():
    args = argparser()
    jsons = load_all_jsons()

    if args.show:
        if len(jsons) == 0:
            print('<empty>')
        else:
            for n, j in enumerate(jsons):
                print(f'[{n}] {j}')

    else:
        if len(jsons) == 0:
            print('<no json to plot>')

        else:
            # check on argparse options
            fnum = 0
            if args.number is not None:
                fnum = args.number

            modelname = jsons[fnum]
            if args.filename is not None:
                modelname = args.filename

            xlabel = 'Iterations'
            if args.xlabel is not None:
                xlabel = args.xlabel

            # Load modelname and rewards from json
            jsonpath = 'tools\\conserved_plots\\' + modelname + '.json'
            total_reward_progress = json.load(open(jsonpath, 'r'))

            # Plot Rewards
            plt.figure(figsize=(12, 8), dpi=80,
                       facecolor=(colors.get_pp(colors.WHITE)))
            plt.plot(total_reward_progress, color=colors.get_pp(colors.TOMATO))
            plt.xlabel(xlabel)
            plt.ylabel('Total rewards')
            plt.grid(True)

            print(f'saving plot as {modelname}.png')
            plt.savefig(f"{modelname}.png")


if __name__ == '__main__':
    main()
