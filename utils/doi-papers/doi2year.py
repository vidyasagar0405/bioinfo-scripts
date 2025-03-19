#!/usr/bin/env python3
import pandas as pd
import requests
import sys


def get_year_from_doi(doi):
    """
    Given a DOI, query the CrossRef API and return the publication year.
    If the request fails or the data is missing, return None.
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error on a bad status code
        data = response.json()
        # Extract the year from the 'issued' field; CrossRef returns a list of date parts.
        year = data['message']['issued']['date-parts'][0][0]
        print(f"{doi}: {year}")
        return year
    except Exception as e:
        print(f"Error retrieving year for DOI {doi}: {e}")
        return None


def main():

    input = sys.argv[1]

    # Load the TSV file into a DataFrame.
    df = pd.read_csv(input, sep='\t')

    # Apply the function to each DOI in the DataFrame and create a new column 'year'
    df['year'] = df['doi'].apply(get_year_from_doi)

    # Optionally, write the DataFrame with the new column back to a TSV file.
    df.to_csv(f'{input[:-4]}_with_year.tsv', sep='\t', index=False)

    print(f"Processing complete. The output file '{input[:-4]}_with_year.tsv' has been created.")

if __name__ == "__main__":
    main()
