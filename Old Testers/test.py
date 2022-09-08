import csv



list  = [["ass","man"], ["house","hold"]]

with open("out.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(list)