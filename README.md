# ABN AMRO Tikkie API
This repo contains the source code and an example application for the library to talk to ABN AMRO Tikkie API.
This library is used at Footloose for creating payment requests for tickets and merchandise.
It is pretty minimalistic, processing of status etc is done through the tikkie portal. The library can return raw data on this.
On importing the library it will try to read the config and private_key and store them globally in your python process

## Usage
### Preparing
1. create an abn amro developer account
1. register an app with application scope "tikkie" [here](https://developer.abnamro.com/user/me/apps)
1. register a public key with ABN AMRO as explained [here](https://developer.abnamro.com/get-started) under "authentication" -> "Signed JSON Web Token"
1. create a config.yaml file with the following keys:
    1. key_public: path to your (registered!) public key
    1. key_private: paty to your private key
    1. abnurl: the abn api url for your environment, for example "https://api-sandbox.abnamro.com/v1/"
    1. abnurl_auth: the abn oauth endpoint, for example "https://api-sandbox.abnamro.com/v1/oauth/token"
    1. abnurl_auth_aud: the url string that needs to go into the endpoint. for some reason it differs from the actual endpoint url. for example "https://auth-sandbox.abnamro.com/oauth/token"
    1. consumer_key: the consumer key from your registered app
    1. consumer_secret: the consumer secret from your registered app
    1. platform_name: the default platform name you want to use on the tikkie API
    1. user_name: the default user name you want to use on the tikkie API
    1. user_iban: the default iban you want to use on the tikkie API

### Live Usage
The library will try to reuse an existing access_token. This is wrapped in ```load_access_token```. Keys expire after an hour usually. The library will detect this and refetch the key.
This refetching only happens when calling ```load_access_token``` and is not done by the other functions.

Typical usage would be:
1. get access token from ```load_access_token```
1. one time create platform and user with ```create_platform``` and ```create_user```.
Please note that these require you to input the names yourself, they are the only function to not use the defaults from config.yaml
1. use ```create_payment_request``` to create a new request
1. user ```get_payment_requests``` to see the status of payments