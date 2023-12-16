import csv

def read_and_sort_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # skip the header row
        next(reader)
        # sort the data by the third index (converted to int) in descending order
        sorted_data = sorted(reader, key=lambda row: int(row[2]), reverse=True)
        return sorted_data

def main():
    file_path = 'potential_playlists.csv'
    sorted_data = read_and_sort_csv(file_path)
    avoid = ['official', 'lyrics', 'video', 'audio', 'directed']
    counter = 0
    for item in sorted_data:
        c = 0
        for item2 in avoid:
            if item2 in item[0].lower():
                c += 1
        if c != 0:
            counter += 1
        # else:
            # print(item[0], item[2])
        print(item)
    print(counter)
main()