"""
inspect_label.py

Purpose: open a segmentation mask (the "answer sheet") and report
which class codes it contains and how many voxels belong to each.

How to run (from the petct-interactive folder):
    python tools/inspect_label.py ../autoPETV/test/labels/psma_ffcaa75377465b37_2018-03-04.nii.gz
"""

import sys      # to read the file path the user typed on the command line

import numpy as np       # number arrays
import nibabel as nib    # reads NIfTI medical images


class LabelInspector:
    """Loads one segmentation mask and reports its class statistics."""

    def __init__(self, file_path):
        # Remember the path for the report.
        self.file_path = file_path

        # Open the file (reads only the small header first — fast).
        self.image = nib.load(file_path)

        # Pull all voxel values into memory as a number array.
        self.voxels = np.asanyarray(self.image.dataobj)

    def get_class_counts(self):
        """Find every distinct value in the mask and count its voxels."""
        # np.unique with return_counts gives two matching lists:
        # the values that occur, and how many times each occurs.
        values, counts = np.unique(self.voxels, return_counts=True)
        return values, counts

    def print_report(self):
        """Print a readable summary of what is inside this mask."""
        file_name = self.file_path.split("/")[-1]
        values, counts = self.get_class_counts()

        # Total number of voxels in the whole volume.
        total_voxels = int(self.voxels.size)

        print(file_name)
        print("  shape        :", self.image.shape)
        print("  data type    :", self.voxels.dtype)
        print("  total voxels :", total_voxels)

        # Show each class code and its share of the volume.
        for value, count in zip(values, counts):
            share = 100.0 * float(count) / float(total_voxels)
            print("  class", int(value), ":", int(count), "voxels",
                  "({:.4f} % of volume)".format(share))


def main():
    # The user must give exactly one thing: the path to a label file.
    if len(sys.argv) < 2:
        print("Please give me a label file, for example:")
        print("  python tools/inspect_label.py ../autoPETV/test/labels/<name>.nii.gz")
        return

    label_path = sys.argv[1]
    inspector = LabelInspector(label_path)
    inspector.print_report()


if __name__ == "__main__":
    main()