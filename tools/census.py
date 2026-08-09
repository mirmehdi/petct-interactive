"""
census.py

Purpose: walk the dataset folder and answer three questions:
  1. How many studies (scans) per tracer?
  2. How many unique PATIENTS per tracer?  (leakage prevention groundwork)
  3. How many studies have an EMPTY label (no tumor)?  (stratification groundwork)

How to run (on the machine where the data lives):
    python tools/census.py /data/PSMA-FDG-PET-CT-Lesions_v2
"""

import glob     # find files by pattern
import os       # work with file paths
import sys      # read command-line arguments

import numpy as np       # number arrays
import nibabel as nib    # read NIfTI medical images


class FilenameParser:
    """Knows how to cut one dataset filename into (tracer, patient, study)."""

    def parse(self, file_path):
        """Take a full path, return (tracer, patient_id, study_label)."""
        # Keep only the file name, e.g. "psma_3959d1c381a5bcd6_2015-11-12_0001.nii.gz"
        file_name = os.path.basename(file_path)

        # Cut the channel suffix and extension off the end, if present.
        # "_0000.nii.gz" -> ""   (we only need the patient/study part)
        for suffix in ["_0000.nii.gz", "_0001.nii.gz", ".nii.gz"]:
            if file_name.endswith(suffix):
                file_name = file_name[: -len(suffix)]
                break

        # Split on underscore. Rule we froze together:
        # piece 0 = tracer, piece 1 = patient ID, everything after = study label.
        pieces = file_name.split("_")
        tracer = pieces[0]                    # "fdg" or "psma"
        patient_id = pieces[1]                # e.g. "fe705ea1cc"
        study_label = "_".join(pieces[2:])    # the rest, kept as-is (messy is OK)

        return tracer, patient_id, study_label


class DatasetCensus:
    """Walks the dataset and produces the counting report."""

    def __init__(self, dataset_folder):
        # Folder that contains imagesTr/ and labelsTr/
        self.dataset_folder = dataset_folder
        self.parser = FilenameParser()

    def collect_studies(self):
        """Find every CT file (one per study) and parse its name."""
        # Every study has exactly one _0000 (CT) file -> perfect study counter.
        pattern = os.path.join(self.dataset_folder, "imagesTr", "*_0000.nii.gz")
        ct_files = sorted(glob.glob(pattern))

        studies = []
        for ct_path in ct_files:
            tracer, patient_id, study_label = self.parser.parse(ct_path)
            studies.append(
                {"tracer": tracer, "patient": patient_id, "study": study_label}
            )
        return studies

    def count_patients_and_studies(self, studies):
        """Report studies and unique patients, per tracer."""
        for tracer in ["fdg", "psma"]:
            # Keep only this tracer's studies.
            tracer_studies = [s for s in studies if s["tracer"] == tracer]

            # Your 'unique' idea: a set keeps each patient ID only once.
            unique_patients = set(s["patient"] for s in tracer_studies)

            print(tracer.upper())
            print("  studies         :", len(tracer_studies))
            print("  unique patients :", len(unique_patients))

            # How many patients have MORE than one study? (the leakage risk group)
            patients_seen = {}
            for s in tracer_studies:
                patients_seen[s["patient"]] = patients_seen.get(s["patient"], 0) + 1
            multi_study = sum(1 for count in patients_seen.values() if count > 1)
            print("  patients with >1 study :", multi_study)
            print()

    def count_empty_labels(self):
        """Open every label file and check: does it contain any tumor voxel?"""
        pattern = os.path.join(self.dataset_folder, "labelsTr", "*.nii.gz")
        label_files = sorted(glob.glob(pattern))

        # Counters per tracer: total labels and empty (tumor-free) labels.
        totals = {"fdg": 0, "psma": 0}
        empties = {"fdg": 0, "psma": 0}

        for i, label_path in enumerate(label_files):
            tracer, patient_id, study_label = self.parser.parse(label_path)

            # Load the mask and ask: is the sum of all voxels zero?
            # (sum == 0 means: not a single tumor voxel anywhere)
            mask = np.asanyarray(nib.load(label_path).dataobj)
            is_empty = bool(mask.sum() == 0)

            totals[tracer] = totals[tracer] + 1
            if is_empty:
                empties[tracer] = empties[tracer] + 1

            # Progress heartbeat every 100 files, so we know it is alive.
            if (i + 1) % 100 == 0:
                print("  ...checked", i + 1, "of", len(label_files), "labels")

        print()
        for tracer in ["fdg", "psma"]:
            share = 100.0 * empties[tracer] / max(totals[tracer], 1)
            print(tracer.upper())
            print("  labels checked :", totals[tracer])
            print("  empty (no tumor):", empties[tracer],
                  "({:.1f} % of this tracer)".format(share))
            print()


def main():
    if len(sys.argv) < 2:
        print("Please give the dataset folder, for example:")
        print("  python tools/census.py /data/PSMA-FDG-PET-CT-Lesions_v2")
        return

    census = DatasetCensus(sys.argv[1])

    print("=== Part 1: studies and patients ===")
    studies = census.collect_studies()
    census.count_patients_and_studies(studies)

    print("=== Part 2: empty-label census (takes some minutes) ===")
    census.count_empty_labels()


if __name__ == "__main__":
    main()