"""
Esercizio 2: il gioco di Mario (topcoders)
python3 23_03_es2.py [-s <sequenza_arbitraria> | -n <numero_carte>]
"""
import argparse
import random
from collections import Counter

VALIDTOKENS = list('0123456789+')
PLUSTOKEN = '+'

def generate_sequence(num_token):
    """
    Genera una nuova sequenza come stringa, dove ogni elemento ha la stessa
        probabilità di essere inserito
    """
    return ''.join([token for n in range(num_token)
                    for token in random.choice(VALIDTOKENS)])

def check_sequence(game_seq):
    """
    Scorre la lista (presa in input) e verifica che contenga solo elementi ammessi
    """
    for letter in game_seq:
        if letter not in VALIDTOKENS:
            return False
    return True

def penalty_count(game_seq):
    """
    Calcola la penalità associata alla lista passata in ingresso secondo le
        regole specificate nella traccia
    """
    counter, penalty = 0, 0
    for token in game_seq:
        if token == PLUSTOKEN:
            counter += 1
        else:
            num_token = int(token)
            penalty += abs(num_token - counter)
    return str(penalty)

def order_sequence(game_seq):
    """
    Esegue l'ordinamento della sequenza di gioco
    """
    count = Counter(game_seq)
    order_string = ''
    for token in '0123456789':
        order_string += token * count[token]
        order_string += PLUSTOKEN * min(count[PLUSTOKEN], 1)
        count[PLUSTOKEN] -= min(count[PLUSTOKEN], 1)
    order_string += PLUSTOKEN * count[PLUSTOKEN]
    return order_string

def main():
    """
    Funzione principale, stabilisce gli argomenti e controlla gli input
    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--seq', dest='sequence', help='Input sequence',
                       default='')
    group.add_argument('-n', '--num', dest='numtoken', type=int,
                       help='Number of tokens for random sequence', default=10)

    try:
        parsed = parser.parse_args()
    except:
        return

    game_seq = ''
    if len(parsed.sequence) < 1:
        game_seq = generate_sequence(parsed.numtoken)
    elif not check_sequence(parsed.sequence):
        print("Input sequence is not valid")
        return
    else:
        game_seq = parsed.sequence

    print("Original sequence\t" + game_seq)
    print("Original penalty\t" + penalty_count(game_seq))

    order_seq = order_sequence(game_seq)
    print("Ordered sequence\t" + order_seq)
    print("Ordered penalty \t" + penalty_count(order_seq))

if __name__ == '__main__':
    main()
