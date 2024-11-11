import csv
import random
from pathlib import Path

# Read rows and cols task inputs
rows = int(Path("/workflow/inputs/rows").read_text())
cols = int(Path("/workflow/inputs/cols").read_text())

# Write random output
with open('/workflow/outputs/random_data', 'w', newline='') as csvfile:
    random_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # produce a header with the right number of columns
    random_writer.writerow([f"col {i}" for i in range(cols)])

    # each row contains cols random values
    for i in range(rows):
        random_writer.writerow([random.randint(1,1000) for _ in range(cols)])
        
        
        #ADDING RANDOM COMMENT 