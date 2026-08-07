"""
inspect_volume.py

Purpose: open a medical image file and print out what is inside it.
We use this to sanity-check any new data before trusting it.

How to run (from the petct-interactive folder):
    python tools/inspect_volume.py ../autoPETV/test/images
"""

import glob    # helps us find all files matching a pattern, e.g. "*.nii.gz"
import sys     # lets us read arguments the user typed after the script name

import numpy as np      # library for working with number arrays
import nibabel as nib   # library that knows how to read NIfTI medical images


class VolumeInspector:
    """Loads one 3D medical image and answers simple questions about it."""

    def __init__(self, file_path):
        # Store the file path so the other methods can refer to it later.
        self.file_path = file_path

        # nib.load() opens the file and reads only the small header part.
        # It does NOT read all the pixel values yet, so this stays fast.
        self.image = nib.load(file_path)

        # Now we actually pull the pixel values into memory as a number array.
        # This is the slow step, because the volume can be hundreds of megabytes.
        self.voxels = np.asanyarray(self.image.dataobj)

    def get_shape(self):
        """How many voxels the volume has along each of its three axes."""
        return self.image.shape

    def get_spacing(self):
        """How many millimetres one single voxel covers along each axis."""
        # The scanner wrote this into the file header when the scan was made.
        return self.image.header.get_zooms()

    def get_value_range(self):
        """The smallest and the largest measured value in the whole volume."""
        smallest_value = float(self.voxels.min())
        largest_value = float(self.voxels.max())
        return smallest_value, largest_value

    def get_physical_size_mm(self):
        """The real-world size of the scanned box, in millimetres."""
        # Number of voxels multiplied by the size of one voxel = real distance.
        physical_sizes = []
        for voxel_count, mm_per_voxel in zip(self.get_shape(), self.get_spacing()):
            physical_sizes.append(round(voxel_count * mm_per_voxel, 1))
        return physical_sizes

    def print_report(self):
        """Print everything we know about this volume in a readable block."""
        # Show only the file name, not the whole long path.
        file_name = self.file_path.split("/")[-1]
        smallest_value, largest_value = self.get_value_range()

        print(file_name)
        print("  shape (voxels)   :", self.get_shape())
        print("  spacing (mm)     :", self.get_spacing())
        print("  real size (mm)   :", self.get_physical_size_mm())
        print("  value range      :", round(smallest_value, 2), "to", round(largest_value, 2))
        print()


def main():
    # sys.argv is the list of words typed on the command line.
    # Position 0 is the script name, position 1 is the folder we want to look at.
    if len(sys.argv) < 2:
        print("Please give me a folder, for example:")
        print("    python tools/inspect_volume.py ../autoPETV/test/images")
        return

    folder_path = sys.argv[1]

    # Build a search pattern and collect every NIfTI file inside that folder.
    # sorted() keeps the order stable so runs are reproducible.
    search_pattern = folder_path + "/*.nii.gz"
    found_files = sorted(glob.glob(search_pattern))

    # Fail loudly instead of silently printing nothing.
    if len(found_files) == 0:
        print("No .nii.gz files found in:", folder_path)
        return

    # Inspect each file one at a time.
    for file_path in found_files:
        inspector = VolumeInspector(file_path)
        inspector.print_report()


# This line means: only run main() when the file is executed directly,
# not when some other file imports it.
if __name__ == "__main__":
    main()