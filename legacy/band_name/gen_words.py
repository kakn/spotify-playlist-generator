import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import words
from tqdm import tqdm

nltk.download('wordnet')
nltk.download('words')


def generate_evocative_words(seed_words, max_length=10):
    """Generate a list of evocative words based on seed words."""
    potential_words = set()

    # for word in tqdm(seed_words, desc="Generating words"):
    for word in seed_words:
        # Synonyms
        for syn in wn.synsets(word):
            for lemma in syn.lemma_names():
                potential_words.add(lemma.replace("_", " "))

            # Hypernyms
            for hypernym in syn.hypernyms():
                for lemma in hypernym.lemma_names():
                    potential_words.add(lemma.replace("_", " "))

            # Hyponyms
            for hyponym in syn.hyponyms():
                for lemma in hyponym.lemma_names():
                    potential_words.add(lemma.replace("_", " "))

    # Filter based on word length and if it's an actual English word
    english_words = set(words.words())
    filtered_words = {word for word in potential_words if word in english_words and len(word) <= max_length}

    return list(filtered_words)

def iter_evocative_words(seed_words, max_length=10, iterations=100):
    """Run generate_evocative_words 'iterations' times, using the output of each as input for the next."""
    all_words = set(seed_words)
    for _ in tqdm(range(iterations), desc="Iterating generations"):
        evocative_words = generate_evocative_words(list(all_words), max_length)
        all_words.update(evocative_words)
    return set(list(all_words))

def read_seed_words(filename='band_name/data/generated_words.txt'):
    """Read seed words from a file."""
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]


def write_words_to_file(words, filename='band_name/data/generated_words.txt'):
    """Write words to a specified file."""
    with open(filename, 'w') as file:
        for word in tqdm(sorted(words), desc="Writing words"):
            file.write(word + '\n')

def main():
    # Read, generate and write words
    seed_words = read_seed_words()
    # evocative_words = generate_evocative_words(seed_words)
    # all_words = set(seed_words + evocative_words)
    
    # Filtering the words to only contain those with the letter 'z'
    # z_filtered_words = {word for word in all_words if 'z' in word.lower()}
    iterated_evocative_words = iter_evocative_words(seed_words)
    er_filtered_words = {word for word in iterated_evocative_words if word[-2:].lower() == 'er'}
    
    write_words_to_file(er_filtered_words, 'band_name/data/er_generated_words.txt')

    print(f"\n{len(er_filtered_words)} words written to er_generated_words.txt!")

if __name__ == "__main__":
    main()
