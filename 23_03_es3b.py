"""
Esercizio 3b: verifica delle funzionalità dei proxy recuperati col parser
python3 23_03_es3b.py [--file <nome_file_csv_proxy>] [--site <url>] [-g | -t | -c]
"""
import argparse
import datetime
import pathlib
import http.client
import requests

TESTPASS = "WORKING"
TESTFAIL = "NOT WORKING"

def fail_info_message(info):
    """
    Routine per la composizione dei messaggi d'errore specifici
    """
    return "{} ({})".format(TESTFAIL, info)

def normal_test(proxy_string, dest_url, base_cont):
    """
    Test di connessione base attraverso un proxy
    """
    try:
        response = requests.get(dest_url, proxies={"http": proxy_string},
                                timeout=10)
        if response.ok and response.content == base_cont:
            return TESTPASS
        else:
            return fail_info_message(response.status_code)
    except(requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        return fail_info_message("timeout")
    except:
        return TESTFAIL

def tunnel_test(proxy_url, proxy_port, dest_url):
    """
    Test di connessione tramite il metodo CONNECT
    """
    try:
        conn = http.client.HTTPConnection(proxy_url, proxy_port, timeout=10)
        conn.request("CONNECT", dest_url)
        response = conn.getresponse()
        if response.status == 200:
            return TESTPASS
        return TESTFAIL
    except:
        return TESTFAIL

def trace_test(proxy_string, dest_url):
    """
    Test di verifica degli headers con il metodo TRACE
    """
    method_string = ("TRACE / HTTP/1.1\nHost: {}\n\n".format(dest_url))
    try:
        response = requests.request(method=method_string, url=proxy_string,
                                    timeout=10)
        if response.ok:
            trace_mess = response.content.decode('ascii').lower().split(dest_url.lower())
            if len(trace_mess) > 0:
                return "HEADERS ADDED ({})".format(trace_mess[1].strip())
            else:
                return "HEADERS MATCH"
        return fail_info_message(response.status_code)
    except:
        return TESTFAIL

def main():
    """
    Funzione main, definisce gli argomenti e lancia i test
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', dest='proxyFile',
                        help='CSV file cointaning proxies address and ports',
                        default='proxylist.csv')
    parser.add_argument('--site', dest='targetSite',
                        help='Target site to test with proxies',
                        default='https://www.debian.org/social_contract')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-g', dest='getMode', action='store_true',
                       help='Enable Get Mode (DEFAULT)', default=False)
    group.add_argument('-t', dest='tunnelMode', action='store_true',
                       help='Enable Tunnel Mode', default=False)
    group.add_argument('-c', dest='checkMode', action='store_true',
                       help='Enable Check Headers Mode', default=False)

    try:
        parsed = parser.parse_args()
    except:
        return

    #controllo dei parametri immessi
    if not pathlib.Path(parsed.proxyFile).is_file():
        print("--file option needs a valid file")
        return

    base_res_cont = None
    parsed.targetSite = parsed.targetSite.lower()
    if parsed.targetSite.startswith("www"):
        parsed.targetSite = "http://" + parsed.targetSite
    try:
        base_res_cont = requests.get(parsed.targetSite, timeout=10).content
    except:
        print("unable to reach required site, please check --site option")
        return

    #lettura dei proxy da file
    with open(parsed.proxyFile) as proxy_file:
        for proxy_line in proxy_file.readlines():
            url, port, *rem = proxy_line.split(',')
            proxy_string = 'http://{}:{}'.format(url, port)

            time_stamp = str(datetime.datetime.utcnow())
            result_string, proxy_mode = [], 'Get Mode'

            if parsed.tunnelMode:
                proxy_mode = 'Tunnel Mode'
                result_string = tunnel_test(url, port, parsed.targetSite)

            elif parsed.checkMode:
                proxy_mode = 'Check Mode'
                result_string = trace_test(proxy_string, parsed.targetSite[7:])

            #modalità di default
            else:
                result_string = normal_test(proxy_string, parsed.targetSite,
                                            base_res_cont)
            #stampa dell'esito
            print('\t'.join([time_stamp, url, proxy_mode, result_string]))


if __name__ == '__main__':
    main()
