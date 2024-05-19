import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
from lvisClass import lvisData

class plotLVIS(lvisData):
    """
    A class that inherits from lvisData and adds a method for plotting waveforms.
    """

    def plotWave(self, index, output_path):
        """
        Plots a single waveform at the specified index and saves it to the given output path.

        Parameters:
        1. 'index' (int): Index of the waveform to plot.
        2. 'output_path' (str): Full path to save the output plot image.
        """
        output_directory = os.path.dirname(output_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        plt.figure()
        plt.plot(self.waves[index], self.z[index])
        plt.xlabel('Waveform Return Amplitude')
        plt.ylabel('Elevation (m)')
        plt.title(f'LVIS Waveform for Index {index}')
        plt.grid(True)
        plt.savefig(output_path)
        plt.close()
        print(f"Waveform plot saved as {output_path}")

def parse_arguments():
    """
    Parses command-line arguments for the script.

    Parameters:
        1. '--input_file' - Will use the default file listed below if user does not specify a desired file to read from.
        2. '--output_file' - Will send the plot to the default folder listed below as 'waveform_plot' unless the user specifies a desired folder/name.
        3. '--waveform_index' Will return the waveform at index 0 unless the user specifies an alternate waveform.
    """
    parser = argparse.ArgumentParser(description="Plot an LVIS waveform.")
    parser.add_argument('--input_file', type=str, default='/geos/netdata/oosa/assignment/lvis/2009/ILVIS1B_AQ2009_1020_R1408_049700.h5', help='Input LVIS file')
    parser.add_argument('--output_file', type=str, default='src/outputs/t1_outputs/waveform_plot.png', help='Output plot file with path')
    parser.add_argument('--waveform_index', type=int, default=0, help='Index of the waveform to plot')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse the command-line arguments
    args = parse_arguments()

    # Create an instance of the plotLVIS class
    lvis = plotLVIS(args.input_file)
    lvis.setElevations()

    # Plot a specific waveform
    lvis.plotWave(args.waveform_index, args.output_file)

