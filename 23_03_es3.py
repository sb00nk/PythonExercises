"""
Esercizio 3: parser per la proxy list di Hide my Ass
python3 23_03_es3.py
"""
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

def parse_proxy_links(proxy_table, params):
    """
    Ripulisce la tabella e recupera i dati dalle righe
    """
    proxy_links = []

    #identifico le colonne dei parametri da catturare
    cells = proxy_table.findChildren('th')
    valid_index = [k for k, cell in enumerate(cells) if cell.string in params]

    rows = proxy_table.find('tbody').findChildren('tr')
    for row in rows:

        #identifico i tag che non vanno mostrati in output
        regex_disp_none = re.compile("\.(.+)\{display\:none\}")
        hide_style = regex_disp_none.findall(str(row.findChild("style")))
        #pulisco il contenuto della pagina in modo da tenere solo le parti utili
        rem = [x.extract() for x in row.find_all(['span', 'div'],
                                                 {'class' : hide_style})]
        rem = [x.extract() for x in row.find_all(['span', 'div'],
                                                 {'style' : 'display:none'})]
        rem = [x.extract() for x in row.find_all('style')]

        #esamino le celle della tabella e recupero i dati
        cells = row.findChildren('td')
        proxy_string = ''.join([elem.replace(" ", "") for k in valid_index
                                for elem in cells[k].find_all(text=True,
                                                              recursive=True)])
        proxy_links.append(re.sub('\s+', ',', proxy_string.lstrip())+'\n')

    return proxy_links

def main():
    """
    Funzione principale, si occupa di scorrere le pagine e scrivere il file CSV
    """
    webpage = urlopen("http://proxylist.hidemyass.com/").read()
    soup = BeautifulSoup(webpage, 'html.parser')
    #recupero l'elenco delle pagine successive
    page_list = [page.string for page in soup.find_all(href=re.compile("\/\d+$"),
                                                       class_=None)]
    page_list.append('0')

    with open('proxylist.csv', 'w') as file_out:
        for page_url in page_list:
            proxy_table = soup.findChild(id="listable")
            proxy_list = parse_proxy_links(proxy_table,
                                           ("IP Address", "Port", "Country"))
            file_out.writelines(proxy_list)
            #passo alla pagina successiva
            next_page = urlopen("http://proxylist.hidemyass.com/" + page_url)
            soup = BeautifulSoup(next_page.read(), 'html.parser')


if __name__ == '__main__':
    main()
