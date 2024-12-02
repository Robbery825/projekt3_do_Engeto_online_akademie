"""
Projekt_3.py: Třetí projekt do Engeto Online Python Akadamie
author: Robert Svorada
email: robert825@seznam.cz
"""

import csv
import sys
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def scrape_parties(url):
    """Načte seznam stran z URL."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    parties = {}
    rows = soup.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 2:
            party_name = cols[1].text.strip()
            hlasy = cols[2].text.strip()
            if party_name:
                parties[party_name] = hlasy

    return parties


def scrape_data_from_main_page(url):
    """Načte seznam obcí z hlavní stránky."""
    # Nepřidáme sem další výpis URL
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    obce = []
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if cells and row.find("a"):
            detail_url = "https://www.volby.cz/pls/ps2017nss/" + row.find("a")["href"]
            kod_obce = cells[0].text.strip()
            nazev_obce = cells[1].text.strip()
            obce.append({"detail_url": detail_url, "kód obce": kod_obce, "název obce": nazev_obce})

    logging.info(f"Nalezeno {len(obce)} obcí.")
    return obce

def scrape_parties(url):
    """Načte seznam stran z URL."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    parties = {}
    rows = soup.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 2:
            party_name = cols[1].text.strip()
            hlasy = cols[2].text.strip()
            if party_name:
                parties[party_name] = hlasy

    return parties

def scrape_data_from_main_page(url):
    """Načte seznam obcí z hlavní stránky."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    obce = []
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if cells and row.find("a"):
            detail_url = "https://www.volby.cz/pls/ps2017nss/" + row.find("a")["href"]
            kod_obce = cells[0].text.strip()
            nazev_obce = cells[1].text.strip()
            obce.append({"detail_url": detail_url, "kód obce": kod_obce, "název obce": nazev_obce})

    logging.info(f"Nalezeno {len(obce)} obcí.")
    return obce


def scrape_data(obce, parties):
    """Načte data o každé obci a přidá počty hlasů pro každou stranu."""
    results = []

    for obec in obce:
        response = requests.get(obec["detail_url"])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        try:
            volici = soup.find("td", headers="sa2").text.strip()
        except AttributeError:
            volici = "0"

        try:
            obalky = soup.find("td", headers="sa3").text.strip()
        except AttributeError:
            obalky = "0"

        try:
            platne_hlasy = soup.find("td", headers="sa6").text.strip()
        except AttributeError:
            platne_hlasy = "0"

        parties_votes = {}
        for party in parties:
            parties_votes[party] = "0"

        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                party_name = cells[1].text.strip()
                votes = cells[2].text.strip()
                if party_name in parties_votes:
                    parties_votes[party_name] = votes

        obec_data = {
            "kód obce": obec["kód obce"],
            "název obce": obec["název obce"],
            "voliči v seznamu": volici,
            "vydané obálky": obalky,
            "platné hlasy": platne_hlasy,
        }

        for party in parties_votes:
            obec_data[party] = parties_votes.get(party, "0")

        results.append(obec_data)

    return results



def save_to_csv(results, parties, vysledky_voleb_hodonin):
    """Uloží výsledky do CSV souboru."""
    logging.info(f"Ukládám data do souboru {vysledky_voleb_hodonin}...")

    with open(vysledky_voleb_hodonin, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")

        header = ["kód obce", "název obce", "voliči v seznamu", "vydané obálky", "platné hlasy"] + list(parties.keys())
        writer.writerow(header)

        for row in results:
            row_data = []
            for col in header:
                if col in row:
                    row_data.append(row[col])
                else:
                    row_data.append("0")
            writer.writerow(row_data)

    logging.info("Data byla uložena do souboru.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Použití: python volby.py URL vysledky_voleb_hodonin")
        sys.exit(1)

    url = sys.argv[1]
    vysledky_voleb_hodonin = sys.argv[2]

    logging.info(f"Začíná webscraping. Stahuji data z URL: {url}")

    # Po výpisu URL už žádné další výpisy URL zde nejsou
    obce = scrape_data_from_main_page(url)

    parties_url = "https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=11&xnumnuts=6205"
    parties = scrape_parties(parties_url)

    results = scrape_data(obce, parties)

    save_to_csv(results, parties, vysledky_voleb_hodonin)

    logging.info(f"Hotovo! Data byla uložena do souboru {vysledky_voleb_hodonin}. Ukončuji webscraping")
