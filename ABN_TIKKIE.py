import yaml
import requests
import jwt
import base64
import time

## configs
with open('config.yaml', 'r') as stream:
    config = yaml.load(stream)

with open(config['key_private'], 'rb') as stream:
    key_private = stream.read()

## util functions
def encode64(string):
    return base64.urlsafe_b64encode(string.encode()).rstrip(b"=")

## auth flow functions
def prepare_oauth_token_creation():

    header = {
        "typ": "JWT",
        "alg": "RS256",
    }

    payload = {
        "nbf" : int(time.time()) - 1,
        "exp" : int(time.time()) + 120,
        "iss" : "footloose",
        "sub" : config['consumer_key'],
        "aud" : config['abnurl_auth_aud'],
    }

    # signature = api_jws.encode("{}.{}".format(header, payload).encode(), key_private, algorithm='RS256')
    signature = jwt.encode(payload, key_private, algorithm="RS256", headers=header)

    return {
        #"client_assertion" : "{}.{}.{}".format(encode64(json.dumps(header)).decode(), encode64(json.dumps(payload)).decode(), signature.decode()),
        "client_assertion" : signature,
        "client_assertion_type" : "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "grant_type" : "client_credentials",
        "scope" : "tikkie",
    }

def fetch_access_token():
    r = requests.post(config['abnurl_auth'], data=prepare_oauth_token_creation(), headers={"API-Key" : config['consumer_key']})
    if r.status_code == 200:
        with open('access_token.dump', 'w') as stream:
            stream.write(r.json()['access_token'])
        return r.json()['access_token']
    else:
        return r

def load_access_token():
    try:
        with open('access_token.dump', 'r') as stream:
            access_token = stream.read()
    except:
        access_token = None

    headers = {"API-Key": config['consumer_key'], "Authorization": "Bearer {}".format(access_token)}
    r = requests.get(config['abnurl'] + "tikkie", headers=headers)
    if r.status_code != 404: #not found means that the access_token passed
        try:
            if r.json()['errors'][0]['category'] == 'ACCESS_TOKEN_EXPIRED' or \
                    r.json()['errors'][0]['category'] == 'INVALID_ACCESS_TOKEN':
                access_token = fetch_access_token()
            else:
                return None
        except KeyError:
            return None
    return access_token

def set_api_headers(access_token):
    return {"API-Key": config['consumer_key'], "Authorization": "Bearer {}".format(access_token)}

## tikkie API
## platforms
def create_platform(access_token, name, phonenumber):
    headers = set_api_headers(access_token)
    payload = {
        "name" : name,
        "phoneNumber" : phonenumber,
        "platformUsage" : "PAYMENT_REQUEST_FOR_MYSELF"
    }
    r = requests.post(config['abnurl'] + "tikkie/platforms", json=payload, headers=headers)
    if r.status_code == 201: # HTTP Created
        return r.json()
    else:
        return r

def get_platforms(access_token):
    headers = set_api_headers(access_token)
    r = requests.get(config['abnurl'] + "tikkie/platforms", headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        return r

def get_my_platform_token(access_token):
    platforms = get_platforms(access_token)
    for platform in platforms:
        if platform['name'] == config['platform_name']:
            if platform['status'] == 'ACTIVE':
                return True, platform['platformToken']
            else:
                return False, platform['platformToken']
    return None, None


## users
def create_user(access_token, name, phonenumber, iban, label, platform_token=None):
    if platform_token is None:
        platform_token = get_my_platform_token(access_token)[1]
    headers = set_api_headers(access_token)
    payload = {
        "name" : name,
        "phoneNumber" : phonenumber,
        "iban" : iban,
        "bankAccountLabel" : label
    }

    r = requests.post(config['abnurl'] + "tikkie/platforms/{}/users".format(platform_token),
                      json=payload, headers=headers)
    if r.status_code == 201: # HTTP Created
        return r.json()
    else:
        return r

def get_users(access_token, platform_token=None):
    if platform_token is None:
        platform_token = get_my_platform_token(access_token)[1]
    headers = set_api_headers(access_token)

    r = requests.get(config['abnurl'] + "tikkie/platforms/{}/users".format(platform_token), headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        return r

def get_my_user_token(access_token, platform_token=None):
    users = get_users(access_token, platform_token=platform_token)
    for user in users:
        if user['name'] == config['user_name']:
            if user['status'] == 'ACTIVE':
                return True, user['userToken']
            else:
                return False, None
    return None, None

#returns both user token and back account token as these are always needed in pair
def get_my_bank_account_token(access_token, platform_token=None):
    users = get_users(access_token, platform_token=platform_token)
    for user in users:
        if user['name'] == config['user_name']:
            if user['status'] == 'ACTIVE':
                for account in user['bankAccounts']:
                    if account['iban'] == config['user_iban']:
                        return True, user['userToken'], account['bankAccountToken']
                return None, None
            else:
                return False, None
    return None, None


## payment requests
def create_payment_request(access_token, amount, description, id, user_token=None, bank_account_token=None, platform_token=None):
    if platform_token is None:
        platform_token = get_my_platform_token(access_token)[1]

    if user_token is None or bank_account_token is None:
        _, user_token, bank_account_token = get_my_bank_account_token(access_token, platform_token=platform_token)

    headers = set_api_headers(access_token)
    payload = {
        "amountInCents" : amount,
        "currency" : "EUR",
        "description" : description,
        "externalId" : id,
    }

    r = requests.post(config['abnurl'] + "tikkie/platforms/{}/users/{}/bankaccounts/{}/paymentrequests"
                      .format(platform_token, user_token, bank_account_token),
                      json=payload, headers=headers)
    if r.status_code == 201: # HTTP Created
        return r.json()
    else:
        return r

def get_payment_requests(access_token, offset=0, limit=100, platform_token=None, user_token=None):
    if platform_token is None:
        platform_token = get_my_platform_token(access_token)[1]
    if user_token is None:
        user_token = get_my_user_token(access_token, platform_token=platform_token)[1]

    headers = set_api_headers(access_token)

    r = requests.get(config['abnurl'] + "tikkie/platforms/{}/users/{}/paymentrequests?limit={}&offset={}"
                     .format(platform_token, user_token, limit, offset), headers=headers)

    if r.status_code == 200:
        return r.json()
    else:
        return r

