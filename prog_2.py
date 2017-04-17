"""
Esercizio Programmazione
pyton3 prog_2.py --url <url_csv_file> | --file <csv_file> [--output <file_out>]
                [--unique][--max <max_key>][--host | --common]
"""
import argparse
import collections
import pprint
import socket
import ssl
import requests

resolver_cache = {}
def get_host_name(ip_addr):
    """
    Funzione per il recupero dell'hostname associato all'indirizzo IP
    """
    if ip_addr not in resolver_cache:
        try:
            hostname = socket.gethostbyaddr(ip_addr)[0]
            resolver_cache[ip_addr] = "{} ({})".format(ip_addr, hostname)
        except socket.herror:
            resolver_cache[ip_addr] = "{} (N/A)".format(ip_addr)

    return resolver_cache[ip_addr]

def get_comm_name(ip_addr):
    """
    Funzione per recuperare il CN dal certificato SSL (se presente)
    """
    if ip_addr not in resolver_cache:
        try:
            hostname = socket.gethostbyaddr(ip_addr)[0]
            cert = ssl.get_server_certificate((hostname, 443))
            cert = ssl.PEM_cert_to_DER_cert(cert)
            begin = cert.rfind(b'\x06\x03\x55\x04\x03') + 7
            end = begin + cert[begin:].find(b'0')
            comm_name = cert[begin:end].decode()
            resolver_cache[ip_addr] = "{} ({})".format(ip_addr, comm_name)
        except (socket.herror, TimeoutError):
            resolver_cache[ip_addr] = "{} (N/A)".format(ip_addr)

    return resolver_cache[ip_addr]

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
    parser.add_argument('--unique', action="store_true",
                        help='remove duplicate IPs')
    parser.add_argument('--max', '-m', dest='maxKey', type=int,
                        help='limit the execution up to N IPs', default=0)

    group_input = parser.add_mutually_exclusive_group()
    group_input.add_argument('--url', '-u', dest='targetSite',
                             help='target url containing netflow file')
    group_input.add_argument('--file', '-f', dest='inputFile',
                             help='target url containing netflow file')

    group_res = parser.add_mutually_exclusive_group()
    group_res.add_argument("--host", action="store_true",
                           help='resolve hostnames')
    group_res.add_argument("--common", action="store_true",
                           help='retrive common names from SSL certificate')

    try:
        parsed = parser.parse_args()
    except argparse.ArgumentError:
        return

    #recupero del file
    if parsed.targetSite is not None:
        parsed.targetSite = parsed.targetSite.lower()
        if not parsed.targetSite.startswith("http://"):
            parsed.targetSite = "http://" + parsed.targetSite
        try:
            netflow_file = requests.get(parsed.targetSite, timeout=10).content
        except:
            print("unable to reach required site, please check --url option")
            return
    #lettura del file
    elif parsed.inputFile is not None:
        try:
            with open(parsed.inputFile, "rb") as in_file:
                netflow_file = in_file.read()
        except (FileNotFoundError, PermissionError):
            print("unable to read input file, check --file option")
            return

    else:
        print("please provide url via --url option or input file via --file")
        return

    dict_report = collections.defaultdict(list)
    netflow_list = netflow_file.split(b'\n')

    #controllo degli header
    if not check_header(netflow_list[0].decode()):
        print("netflow file has wrong header line, aborting.")
        return

    #composizione del dizionario
    for netflow_line in netflow_list[1:]:
        if parsed.maxKey > 0 and len(dict_report.keys()) >= parsed.maxKey:
            break

        try:
            ip_src, ip_dst, *rem = netflow_line.decode().split('|')
            res_key, res_val = ip_src, ip_dst
            if parsed.host:
                res_key, res_val = get_host_name(ip_src), get_host_name(ip_dst)
            elif parsed.common:
                res_key, res_val = get_comm_name(ip_src), get_comm_name(ip_dst)

            if parsed.unique and res_val not in dict_report[res_key]:
                dict_report[res_key].append(res_val)

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
        print("unable to write output file")


if __name__ == '__main__':
    main()
