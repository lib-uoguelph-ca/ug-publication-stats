from wos import WosClient
import wos.utils
import secrets

# with WosClient(secrets.WOS_USER, secrets.WOS_PASS) as client:
#     print(wos.utils.query(client, 'OG="University of Guelph"'))

def get_dois():
    """
    Get a list of UG DOIs from the Web of Science API.
    :return: a list of DOIs
    """

    # We're just stubbing this out for now, because WOS hasn't approved my developer application yet.
    dois = ["10.1016/j.foodchem.2018.12.028",
            "10.1016/j.tourman.2018.10.025",
            "10.1016/j.cej.2018.11.013",
            "10.1016/j.foodqual.2018.10.010",
            "10.1016/j.foodhyd.2018.09.003",
            "10.1016/j.foodchem.2018.09.023",
            "10.1016/j.foodchem.2018.09.010",
            "10.1111/fwb.13220",
            "10.1007/s11146-017-9623-2",
            "10.1111/1744-7917.12488",
            "10.1111/jac.12289",
            "10.1016/j.aquaculture.2018.09.025",
            "10.1016/j.biortech.2018.11.004]"]

    return dois

def get_dois_from_xlsx(file):
    import pandas as pd

    data = pd.read_excel(file)
    data.dropna(subset=['DI'], inplace=True)
    return data['DI']
