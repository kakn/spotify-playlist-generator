import csv
import json

# Function to update the CSV with the best available thumbnails
def update_csv(csv_filename, json_filename, updated_csv_filename):
    # Load JSON data
    with open(json_filename, 'r') as json_file:
        json_data = json.load(json_file)

    # Create a mapping of title to the best available thumbnail URL
    thumbnail_mapping = {}
    for title, details in json_data.items():
        for detail in details:
            snippet = detail['snippet']
            thumbnails = snippet.get('thumbnails', {})
            for quality in ['maxres', 'standard', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    thumbnail_mapping[title] = thumbnails[quality]['url']
                    break

    # Read the CSV file
    with open(csv_filename, 'r', encoding='utf-8') as csv_file:
        csv_data = list(csv.reader(csv_file))

    # Update the thumbnail URLs
    for row in csv_data:  
        title = row[0]  # Assuming the title is in the first column
        if title in thumbnail_mapping:
            row[-1] = thumbnail_mapping[title]  # Update last column

    # Write the updated data back to a new CSV file
    with open(updated_csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

# Call the function with the file names
update_csv('data/new_final_playlist_candidates.csv', 'data/youtube_videos.json', 'data/updated_candidates.csv')