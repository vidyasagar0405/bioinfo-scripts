import pandas as pd
import requests
import sys

def get_metadata_from_doi(doi):
    """
    Given a DOI, query the CrossRef API and return a dictionary containing metadata.
    Returns keys: 'year', 'title', 'journal', 'authors', and 'publisher'.
    If data is missing or an error occurs, the corresponding field is set to None.
    """
    url = f"https://api.crossref.org/works/{doi}"
    metadata = {'year': None, 'title': None, 'journal': None, 'authors': None, 'publisher': None}

    try:
        print(f"Processing: {doi}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes.
        data = response.json()['message']

        # Publication year extraction
        if 'issued' in data and 'date-parts' in data['issued']:
            metadata['year'] = data['issued']['date-parts'][0][0]

        # Title: CrossRef returns a list, so take the first element if available.
        if 'title' in data and data['title']:
            metadata['title'] = data['title'][0]

        # Journal or container title.
        if 'container-title' in data and data['container-title']:
            metadata['journal'] = data['container-title'][0]

        # Authors: Create a string with all authors' full names.
        if 'author' in data:
            authors = []
            for author in data['author']:
                # Sometimes the given or family names might be missing.
                name_parts = []
                if 'given' in author:
                    name_parts.append(author['given'])
                if 'family' in author:
                    name_parts.append(author['family'])
                if name_parts:
                    authors.append(" ".join(name_parts))
            metadata['authors'] = ", ".join(authors) if authors else None

        # Publisher information.
        if 'publisher' in data:
            metadata['publisher'] = data['publisher']

    except Exception as e:
        print(f"Error retrieving metadata for DOI {doi}: {e}")

    return metadata


def main():

    input = sys.argv[1]

    # Load the TSV file into a DataFrame.
    df = pd.read_csv(input, sep='\t')

    # Apply the function to each DOI in the DataFrame.
    # We create new columns for each metadata field.
    metadata_df = df['doi'].apply(get_metadata_from_doi).apply(pd.Series)

    # Combine the original DataFrame with the new metadata columns.
    df = pd.concat([df, metadata_df], axis=1)

    # Optionally, write the DataFrame with the new metadata columns back to a TSV file.
    df.to_csv(f'{input[:-4]}_with_metadata.tsv', sep='\t', index=False)

    print(f"Processing complete. The output file '{input[:-4]}_with_metadata.tsv' has been created.")


if __name__ == "__main__":
    main()
