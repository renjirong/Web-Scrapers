import json
import csv




def main():
    with open("lastLinks.json","r") as f:
        data = json.load(f)

    with open("lastLinksJSON.csv", "w") as f:
            writer = csv.writer(f)
            for i in data:
                f.write(f"{i}, {data[i]}\n")
            
if __name__ == "__main__":
    main()
    