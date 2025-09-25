import os
import json
import csv
import glob
import re

# Set derivatives path (edit for each dataset)
derivatives = "/data/BIDS_MICs/derivatives/micapipe_v0.2.0"

# Prepare subject and session extraction from folder names
sub_ses_pattern = re.compile(r"sub-([^/]+)")
ses_pattern = re.compile(r"ses-([^/]+)")

# Set output csv file path (edit for each module)
output_csv = "/data/mica1/03_projects/ella/MICs_DWI_metadata.csv"

# Collect rows
rows = []

# Find all subjects in derivatives directory
subjects = sorted(glob.glob(os.path.join(derivatives, "sub-*")))

# Extract metadata
for sub_path in subjects:
    sub_match = sub_ses_pattern.search(sub_path)
    if not sub_match:
        continue
    sub = sub_match.group(1)

    # Find all sessions for this subject
    sessions = sorted(glob.glob(os.path.join(sub_path, "ses-*")))
    for ses_path in sessions:
        ses_match = ses_pattern.search(ses_path)
        if not ses_match:
            continue
        ses = ses_match.group(1)

        # Paths to QC and preproc JSON files (edit for each module)
        qc_json_path = os.path.join(derivatives, f"sub-{sub}", f"ses-{ses}", "QC", f"sub-{sub}_ses-{ses}_module-proc_dwi.json")
        preproc_json_path = os.path.join(derivatives, f"sub-{sub}", f"ses-{ses}", "dwi", f"sub-{sub}_ses-{ses}_desc-preproc_dwi.json")

        # Initialize metadata values
        micapipeVersion = user = workstation = processing = date = regSynth = None

        # Load QC JSON
        if os.path.exists(qc_json_path):
            with open(qc_json_path, "r") as f:
                qc_data = json.load(f)
                micapipeVersion = qc_data.get("micapipeVersion")
                user = qc_data.get("User")
                workstation = qc_data.get("Workstation")
                processing = qc_data.get("Processing")
                date = qc_data.get("Date")
        else:
            print(f"Missing QC JSON: {qc_json_path}")

        # Load preproc JSON
        if os.path.exists(preproc_json_path):
            with open(preproc_json_path, "r") as f:
                preproc_data = json.load(f)
                regSynth = preproc_data.get("regSynth")
        else:
            print(f"Missing preproc JSON: {preproc_json_path}")

        # Append row
        rows.append({
            "subject": sub,
            "session": ses,
            "micapipeVersion": micapipeVersion,
            "user": user,
            "workstation": workstation,
            "processing": processing,
            "regSynth": regSynth,
            "Date": date,
        })

# Write all rows to CSV file
with open(output_csv, "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["subject", "session", "micapipeVersion", "user", "workstation", "processing", "regSynth", "Date"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Metadata CSV written to {output_csv}")
