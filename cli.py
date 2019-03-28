from ABN_TIKKIE import *
import argparse
import json
import sys

if __name__== "__main__":
    parser = argparse.ArgumentParser(description="ABN AMRO TIKKIE API cli")
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='fetch', help='fetch/request: fetch existing requests or create new one')
    parser.add_argument('--amount', nargs='?', const=1, type=int, default=0, help='ammount in cents for payment request')
    parser.add_argument('--description', nargs='?', type=str, help="description for the payment request")
    parser.add_argument('--externalid', nargs='?', type=str, help="id for the payment request for for example invoice numbers")

    mode, amount, description, externalid = parser.parse_args().mode,  parser.parse_args().amount,  parser.parse_args().description,  parser.parse_args().externalid

    access_token = load_access_token()

    if access_token is None:
        sys.exit(-1)

    if mode == 'fetch':
        res = get_payment_requests(access_token)
        if type(res) == dict:
            print(json.dumps(res))
            sys.exit(0)
        else:
            print(json.dumps(res.json()))
            sys.exit(1)
    elif mode == 'request':
        res = create_payment_request(access_token, amount, description, externalid)
        if type(res) == dict:
            print(json.dumps(res))
            sys.exit(0)
        else:
            print(json.dumps(res.json()))
            sys.exit(1)
    else:
        sys.exit(2)