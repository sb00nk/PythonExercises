"""
Esercizio Programmazione
pyton3 prog_1.py --url <url_netflov_csv_file>
"""
import argparse
import collections
import pprint
import requests

def check_header(header):
    """
    Funzione per il controllo della riga d'intestazione del file csv
    """
    count, valid_head = 0, set(["IPV4_SRC_ADDR", "IPV4_DST_ADDR"])
    for head in header.split('|'):
        if head in valid_head:
            count += 1
            if count == len(valid_head):
                return True
    return False

def main():
    """
    Funzione main, la sola ed unica
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', dest='reportFile',
                        help='output file for analysis',
                        default='netflow_analysis_output')
    parser.add_argument('--url', '-u', dest='targetSite',
                        help='target url containing netflow file', default=None)

    try:
        parsed = parser.parse_args()
    except argparse.ArgumentError:
        return

    if parsed.targetSite is None:
        print("please provide url via --url option")
        return

    parsed.targetSite = parsed.targetSite.lower()
    if not parsed.targetSite.startswith("http://"):
        parsed.targetSite = "http://" + parsed.targetSite
    try:
        netflow_file = requests.get(parsed.targetSite, timeout=10).content
    except:
        print("unable to reach required site, please check --url option")
        return

    dict_report = collections.defaultdict(list)
    netflow_list = netflow_file.split(b'\n')

    #controllo degli header
    if not check_header(netflow_list[0].decode()):
        print("netflow file has wrong header line, aborting.")
        return

    #composizione del dizionario
    for netflow_line in netflow_list[1:]:
        try:
            ip_src, ip_dst, *rem = netflow_line.decode().split('|')
            dict_report[ip_src].append(ip_dst)
        except ValueError:
            continue

    #stampa dell'esito
    printer = pprint.PrettyPrinter(width=150, compact=True)
    printer.pprint(dict_report)
    try:
        with open(parsed.reportFile, 'w') as out_file:
            printer = pprint.PrettyPrinter(stream=out_file, compact=True)
            printer.pprint(dict_report)
    except PermissionError:
        print("unable to write into output file")


if __name__ == '__main__':
    main()
