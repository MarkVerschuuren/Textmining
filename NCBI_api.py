#make request to NCBI for the gene, chemical and organism indices for the corresponding PMED ID
import simplejson as json
import requests
from Bio import Entrez
from Bio import Medline
import re


def search(query):
    Entrez.email = 'timvandekerkhof@hotmail.com'
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax='10000',
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    idlist = results["IdList"]
    return idlist

def ncbi_gene(results):

    termDictonary = {}
    print(len(results))

    for ids in range(0,len(results),500):

        try:
            custom_url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/bioconcept/{}/JSON".format(results[ids])
            r = requests.get(custom_url)

            json_obj = r.json()
            termDictonary[results[ids]] = {"genes" : [], "Chemicals": [], "Species": []}

            geness, speciess, chemicalss, ab = parse_json(json_obj,termDictonary, results[ids])
        except json.JSONDecodeError:
            print("woeps")




    return geness, speciess, chemicalss, ab

def parse_json(json_obj, termDictonary, pubmedID):
    ab = json_obj['text']
    genes = []
    species = []
    chemicals = []

    for denot in json_obj['denotations']:
        if denot['obj'].split(":")[0] == 'Gene':
            if ab[denot['span']['begin']:denot['span']['end']].upper() not in genes:
                genes.append(ab[denot['span']['begin']:denot['span']['end']].upper())
        if denot['obj'].split(":")[0] == "Species":
            specie = getOrganism(ab[denot['span']['begin']:denot['span']['end']])
            if specie not in species:
                species.append(specie)
        if denot['obj'].split(":")[0] == "Chemical":
            if ab[denot['span']['begin']:denot['span']['end']] not in chemicals:
                if re.match("(?!anthocyanins?)",ab[denot['span']['begin']:denot['span']['end']].lower()) and re.match("(?!flavonoids?)",ab[denot['span']['begin']:denot['span']['end']].lower()):

                    chemicals.append(ab[denot['span']['begin']:denot['span']['end']])

    termDictonary[pubmedID].update({"genes" : genes})
    termDictonary[pubmedID].update({"Chemicals": chemicals})
    termDictonary[pubmedID].update({"Species": species})

    print(termDictonary)




    return genes, species, chemicals, ab
def getOrganism(specie):
    file = open("Organismes.txt", "r")
    file = file.readlines()
    for line in range(61,len(file)):
        if "C=" in file[line]:
            lin = file[line].replace(" ","").lower()
            pattern = "c="+specie+"$"
            if re.search(pattern, lin):
                specie = file[line-1].split("=")[1].split(" ")[0]

    return specie







def main():

    results = search('Anthocyanin')

    genes, species, chemicals ,ab = ncbi_gene(results)


main()

# 4 onde