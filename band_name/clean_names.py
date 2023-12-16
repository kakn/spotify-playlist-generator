def process_and_save_names(input_file, output_file):
    # Read the names from the input file
    with open(input_file, 'r') as f:
        names = f.readlines()

    # Strip whitespace, capitalize, and filter out single-letter names
    processed_names = [name.strip().capitalize() for name in names if len(name.strip()) > 1]

    # Sort names alphabetically
    processed_names.sort()

    # Write processed names to the output file
    with open(output_file, 'w') as f:
        for name in processed_names:
            f.write(name + '\n')


def main():
    input_filename = "band_name/z_available_names.txt"
    output_filename = "band_name/z_candidate_names.txt"
    process_and_save_names(input_filename, output_filename)
    print(f"Processed names have been saved to {output_filename}.")

if __name__ == "__main__":
    main()