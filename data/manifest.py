"""
manifest.py

Purpose: build the frozen dev-40 list — the 40 studies we will measure on.

Rules we follow:
  - Only studies the shipped model has NEVER seen (fold-0 validation list).
  - FDG : 10 positive + 10 empty
  - PSMA: 18 positive + 2 empty
  - Positives spread over small / medium / large tumor size.
  - One study per patient only.
  - Fixed random seed, so the same 40 come out every time.

How to run (from the petct-interactive folder):
    python3 data/manifest.py /data/PSMA-FDG-PET-CT-Lesions_v2 burden_census.csv
"""

import csv       # read and write simple table files
import hashlib   # make a fingerprint of the final file
import json      # read the splits file
import random    # random picking (with a fixed seed)
import sys       # read command line arguments


class ManifestBuilder:
    """Builds the frozen dev-40 list from the census and the split file."""

    def __init__(self, dataset_folder, census_csv_path):
        # Remember where things are.
        self.dataset_folder = dataset_folder
        self.census_csv_path = census_csv_path

        # Fixed seed: makes the random choice repeatable for everyone.
        random.seed(42)

    def load_unseen_case_ids(self):
        """Read the split file and return the case IDs the model never saw."""
        split_path = self.dataset_folder + "/splits_final.json"
        with open(split_path) as f:
            splits = json.load(f)

        # Fold 0 is the checkpoint the organizers shipped.
        # Its "val" list = the cases that model was never trained on.
        unseen = set(splits[0]["val"])
        return unseen

    def load_census_rows(self, unseen_case_ids):
        """Read the census CSV, keep only rows that are in the unseen list."""
        rows = []
        with open(self.census_csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["case_id"] in unseen_case_ids:
                    # Convert the text values into proper types.
                    row["burden_voxels"] = int(row["burden_voxels"])
                    row["empty"] = (row["empty"] == "True")
                    rows.append(row)
        return rows

    def keep_one_study_per_patient(self, rows):
        """If a patient has several studies, keep only one (randomly chosen)."""
        # Group all rows by patient ID.
        by_patient = {}
        for row in rows:
            patient = row["patient_id"]
            if patient not in by_patient:
                by_patient[patient] = []
            by_patient[patient].append(row)

        # For each patient, pick exactly one study.
        chosen = []
        for patient in sorted(by_patient.keys()):     # sorted = stable order
            studies = by_patient[patient]
            chosen.append(random.choice(studies))
        return chosen

    def split_into_size_groups(self, positive_rows):
        """Sort positives by tumor size and cut them into three equal groups."""
        # Sort from smallest tumor to largest.
        ordered = sorted(positive_rows, key=lambda r: r["burden_voxels"])

        # Cut into three parts: small, medium, large.
        third = len(ordered) // 3
        small = ordered[:third]
        medium = ordered[third:2 * third]
        large = ordered[2 * third:]
        return small, medium, large

    def pick_positives(self, positive_rows, how_many):
        """Pick positives spread evenly over the three size groups."""
        small, medium, large = self.split_into_size_groups(positive_rows)

        # Decide how many from each group (e.g. 10 -> 3, 3, 4).
        per_group = how_many // 3
        remainder = how_many - (per_group * 3)

        picked = []
        picked = picked + random.sample(small, per_group)
        picked = picked + random.sample(medium, per_group)
        picked = picked + random.sample(large, per_group + remainder)
        return picked

    def build_dev40(self, rows):
        """Build the final 40-case list, following our frozen rules."""
        # Keep only one study per patient first.
        rows = self.keep_one_study_per_patient(rows)

        # How many we want from each group.
        wanted = {
            ("fdg", "positive"): 10,
            ("fdg", "empty"): 10,
            ("psma", "positive"): 18,
            ("psma", "empty"): 2,
        }

        selected = []
        for tracer in ["fdg", "psma"]:
            # Split this tracer's rows into positive and empty.
            positives = [r for r in rows if r["tracer"] == tracer and not r["empty"]]
            empties = [r for r in rows if r["tracer"] == tracer and r["empty"]]

            # Pick the positives with size spreading.
            n_pos = wanted[(tracer, "positive")]
            selected = selected + self.pick_positives(positives, n_pos)

            # Pick the empties plainly (they have no size to spread over).
            n_empty = wanted[(tracer, "empty")]
            selected = selected + random.sample(empties, n_empty)

        return selected

    def write_manifest(self, selected_rows, output_path):
        """Write the chosen cases to a CSV file, sorted for stability."""
        # Sort by case_id so the file content never changes order.
        ordered = sorted(selected_rows, key=lambda r: r["case_id"])

        with open(output_path, "w") as f:
            f.write("case_id,tracer,patient_id,empty,burden_voxels\n")
            for row in ordered:
                f.write("{},{},{},{},{}\n".format(
                    row["case_id"], row["tracer"], row["patient_id"],
                    row["empty"], row["burden_voxels"]))

        print("Wrote", len(ordered), "cases to", output_path)

    def fingerprint(self, file_path):
        """Make a SHA-256 fingerprint, so we can prove the file never changed."""
        with open(file_path, "rb") as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 data/manifest.py <dataset_folder> <census_csv>")
        return

    dataset_folder = sys.argv[1]
    census_csv = sys.argv[2]

    builder = ManifestBuilder(dataset_folder, census_csv)

    # Step 1: which cases did the model never see?
    unseen = builder.load_unseen_case_ids()
    print("Unseen cases available:", len(unseen))

    # Step 2: get their census rows.
    rows = builder.load_census_rows(unseen)
    print("Census rows matched   :", len(rows))

    # Step 3: choose our 40.
    selected = builder.build_dev40(rows)

    # Step 4: save and fingerprint.
    output_path = "data/dev40_manifest.csv"
    builder.write_manifest(selected, output_path)
    print("SHA-256:", builder.fingerprint(output_path))


if __name__ == "__main__":
    main()