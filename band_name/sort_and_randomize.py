import random


def sort_and_randomize(file_path: str, randomize: bool=True) -> None:
    # Read the file
    with open(file_path, 'r') as file:
        band_names = file.read().splitlines()

    if randomize:
        # Shuffle the list
        random.shuffle(band_names)

    # Sort the list by name length
    sorted_band_names = sorted(band_names, key=len)

    # Replace with the desired output file path
    if randomize:
        output_file_path = 'data/sorted_randomized_candidate_names.txt'
    else:
        output_file_path = 'data/sorted_candidate_names.txt'

    # Write the sorted list to the output file
    with open(output_file_path, 'w') as file:
        file.write("\n".join(sorted_band_names))

def main():
    file_path = "data/candidate_names.txt"
    sort_and_randomize(file_path, randomize=False)
main()