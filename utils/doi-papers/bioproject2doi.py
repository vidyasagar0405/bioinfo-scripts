#!/usr/bin/env python3
"""
This script takes a BioProject accession (e.g. PRJDB4360),
first converts it to a numeric BioProject ID via esearch,
then fetches the BioProject record and extracts its linked PubMed ID.
Next, it fetches the corresponding PubMed record and parses it
to extract the DOI from the ArticleIdList.

Note: Not every BioProject has a linked publication or DOI.
"""

import sys
import xml.etree.ElementTree as ET
from Bio import Entrez

# Always include your email address (NCBI requires this)
Entrez.email = "vidyasagar0405@gmail.com"

def get_bioproject_numeric_id(bioproject_acc):
    """
    Use esearch to convert a BioProject accession to its numeric ID.
    """
    query = f"{bioproject_acc}[Accession]"
    handle = Entrez.esearch(db="bioproject", term=query)
    record = Entrez.read(handle)
    handle.close()
    if record["IdList"]:
        return record["IdList"][0]
    return None

def fetch_bioproject_xml(numeric_id):
    """
    Fetch the BioProject record in XML format using its numeric ID.
    """
    handle = Entrez.efetch(db="bioproject", id=numeric_id, retmode="xml")
    xml_data = handle.read()
    handle.close()
    return xml_data

def extract_pubmed_id_from_bioproject(xml_data):
    """
    Parse the BioProject XML to extract the PubMed ID.
    In many BioProject records the <Publication> element includes an "id" attribute.
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        sys.exit(f"Error parsing BioProject XML: {e}")

    # The XML structure is: <RecordSet><DocumentSummary uid="...">...
    # Look for a Publication element with an "id" attribute.
    for doc in root.findall(".//DocumentSummary"):
        pub = doc.find(".//Publication")
        if pub is not None:
            pubmed_id = pub.attrib.get("id")
            if pubmed_id:
                return pubmed_id
    return None

def fetch_pubmed_xml(pubmed_id):
    """
    Fetch the PubMed record in XML.
    """
    handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
    xml_data = handle.read()
    handle.close()
    return xml_data

def extract_doi_from_pubmed(xml_data):
    """
    Parse the PubMed XML and search for an ArticleId element with IdType="doi".
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        sys.exit(f"Error parsing PubMed XML: {e}")

    # Traverse PubmedArticleSet -> PubmedArticle -> PubmedData -> ArticleIdList
    for article in root.findall(".//PubmedArticle"):
        pubmed_data = article.find("PubmedData")
        if pubmed_data is None:
            continue
        articleid_list = pubmed_data.find("ArticleIdList")
        if articleid_list is None:
            continue
        for aid in articleid_list.findall("ArticleId"):
            if aid.attrib.get("IdType", "").lower() == "doi" and aid.text:
                return aid.text.strip()
    return None

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python get_doi_from_bioproject.py <BioProject_accession>")

    bioproject_acc = sys.argv[1]
    numeric_id = get_bioproject_numeric_id(bioproject_acc)
    if not numeric_id:
        sys.exit(f"Could not find numeric BioProject ID for accession {bioproject_acc}")
    print(f"Numeric BioProject ID: {numeric_id}")

    bp_xml = fetch_bioproject_xml(numeric_id)
    pubmed_id = extract_pubmed_id_from_bioproject(bp_xml)
    if not pubmed_id:
        sys.exit(f"No linked PubMed ID found in the BioProject record for {bioproject_acc}")
    print(f"Linked PubMed ID: {pubmed_id}")

    pm_xml = fetch_pubmed_xml(pubmed_id)
    doi = extract_doi_from_pubmed(pm_xml)
    if doi:
        print(f"DOI: {doi}")
    else:
        print(f"DOI not found in PubMed record for PubMed ID {pubmed_id}")

if __name__ == "__main__":
    main()
