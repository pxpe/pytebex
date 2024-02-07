import requests
import favicon
import json
from typing import Literal, Optional
import random


class TebexError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class TebexPayment():
    def __init__(self,note : str, package_options : dict, package_id : int, packages : list, price: int, ign : str):
        self.note = note
        self.package_options = package_options
        self.package_id = package_id
        self.packages = packages
        self.price = price
        self.ign = ign
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class TebexGiftcard():
    def __init__(self, expires_at : str = '2050-12-31', note : str = '', amount : int = '0'):
        self.expires_at = expires_at
        self.note = note
        self.amount = amount

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class TebexCoupon():
    def __init__(self, code : str, effective_on : Literal['package','category','cart'], packages : list, categories : list, discount_type : Literal['value','percentage'], discount_amount : int,discount_percentage : int,redeem_unlimited : bool = True, expire_never : bool = True, expire_limit : str = '2050-12-31',expire_date : str = '2050-12-31', start_date : str = '2021-01-01', basket_type : Literal['single','suscription','both'] = 'single', minimum : int = 0, discount_application_method : Literal[0,1,2] = 2, username : str = "", note : str = ""):
        self.code = code if code else self.__random_coupon()
        self.effective_on = effective_on
        self.packages = packages
        self.categories = categories
        self.discount_type = discount_type
        self.discount_amount = discount_amount
        self.discount_percentage = discount_percentage
        self.redeem_unlimited = redeem_unlimited
        self.expire_never = expire_never
        self.expire_limit = expire_limit
        self.expire_date = expire_date
        self.start_date = start_date
        self.basket_type = basket_type
        self.minimum = minimum
        self.note = note
        self.discount_application_method = discount_application_method
        self.username = username



    def __random_coupon(self, length : int = 10):
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(length))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    

class Tebex:
    BASE_URL = 'https://plugin.tebex.io'

    ENDPOINTS = {
        'information': '/information',
        'queue': '/queue',
                'queue_offline_commands': '/queue/offline-commands',
                'queue_online_commands': '/queue/online-commands/',
        'listing': '/listing',
        'packages': '/packages',
        'payments': '/payments',
        'gift-cards': '/gift-cards',
        'coupons': '/coupons',
        'checkout': '/checkout',
        'community_goals': '/community_goals',
        'bans': '/bans',
        'sales': '/sales',
        'user': '/user/',
        'player': '/player/',
    }
        
    def __init__(self, secret : str):
        self.secret = secret
        self.info = None
        try:
            self.get_information()
        except:
            raise TebexError('Invalid secret key')

    def __get_favicon(self, domain):
        return favicon.get(domain)[0][0]
    
    def __handle_response(self, response : requests.Response):
        if response.status_code != 200:
            return TebexError(response.json()['error_message'])
        return response.json()
    
    # Information

    def get_information(self) -> dict:

        if not self.info:
            raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['information'], headers={"X-Tebex-Secret": self.secret})
            raw_data_json = self.__handle_response(raw_data)

            icon = '?'
            try:
                icon = self.__get_favicon(raw_data_json['account']['domain'])
            except:
                pass

            raw_data_json.update({'favicon': icon})
            self.info = raw_data_json
        
        return self.info
    
    # Command Queue

    def get_due_commands(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['queue'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def get_due_offline_commands(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['queue_offline_commands'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
    
    def get_due_online_commands(self, player_id : str) -> dict:
        if not player_id:
            return TebexError('No player ID to get commands')

        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['queue_online_commands'] + player_id, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
    
    def delete_due_commands(self, command_ids : list):
        if not command_ids:
            return TebexError('No commands to delete')
        
        raw_data = requests.delete(self.BASE_URL + self.ENDPOINTS['queue'], headers={"X-Tebex-Secret": self.secret}, data=json.dumps({'ids': command_ids}))
        if raw_data.status_code != 204:
            return TebexError(raw_data.json()['error_message'])
        return f'{len(command_ids)} commands deleted'
    
    # Listing of categories and packages

    def get_listing(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['listing'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
    

    # Packages

    def get_packages(self, verbose : bool = False) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['packages'], headers={"X-Tebex-Secret": self.secret}, params={'verbose': verbose})
        return self.__handle_response(raw_data)

    
    def get_package(self, package_id : int) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['packages'] + '/' + str(package_id), headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def update_package(self, package_id : int, update_data : dict):
        if not update_data:
            return TebexError('No data to update')
        if not package_id:
            return TebexError('No package ID to update')

        raw_data = requests.put(self.BASE_URL + self.ENDPOINTS['packages'] + '/' + str(package_id), headers={"X-Tebex-Secret": self.secret}, data=json.dumps(update_data))
        
        self.__handle_response(raw_data)
        return 'Package ' + str(package_id) + ' updated'

    # Community Goals

    def get_community_goals(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['community_goals'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    
    def get_community_goal(self, goal_id : int) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['community_goals'] + '/' + str(goal_id), headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)


    # Payments
    def get_payments(self, limit : int = 100) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['payments'], headers={"X-Tebex-Secret": self.secret}, params={'limit': limit})
        return self.__handle_response(raw_data)

    def get_payments_paginated(self, page : int = 1) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['payments'] + '?paged=' + page, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def get_payment(self, transaction_id : str) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['payments'] + '/' + transaction_id, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def create_payment(self, payment_data : TebexPayment ):
        if not payment_data:
            return TebexError('No payment data to create')

        raw_data = requests.post(self.BASE_URL + self.ENDPOINTS['payments'], headers={"X-Tebex-Secret": self.secret}, data=(payment_data.toJSON()))
        if raw_data.status_code != 201:
            return TebexError(raw_data.json()['error_message'])
        return raw_data.json()
    
    def update_payment(self, transaction_id : str, username : str, status : Literal['complete','chargeback','refund'],):
        if not transaction_id:
            return TebexError('No transaction ID to update')
        if not status:
            return TebexError('You have to set an status')
        if not username:
            return TebexError('You have to set an username')

        raw_data = requests.put(self.BASE_URL + self.ENDPOINTS['payments'] + '/' + transaction_id, headers={"X-Tebex-Secret": self.secret}, data={'username': username, 'status': status})
        
        if raw_data.status_code != 204:
            return TebexError(raw_data.json()['error_message'])
        return 'Payment ' + transaction_id + ' updated'

    
    def create_payment_note(self, transaction_id : str, note : str):
        if not transaction_id:
            return TebexError('No transaction ID to add note')
        if not note:
            return TebexError('No note to add')


        raw_data = requests.post(self.BASE_URL + self.ENDPOINTS['payments'] + '/' + transaction_id + '/note', headers={"X-Tebex-Secret": self.secret}, data={'note': note})
        
        if raw_data.status_code != 201:
            return TebexError(raw_data.json()['error_message'])
        return 'Note added to payment ' + transaction_id


    # Checkout URL

    def create_checkout_url(self, package_id : str, username : str) -> dict:
        if not package_id:
            return TebexError('No package ID to create checkout URL')
        if not username:
            return TebexError('No username to create checkout URL')

        raw_data = requests.post(self.BASE_URL + self.ENDPOINTS['checkout'], headers={"X-Tebex-Secret": self.secret}, data={'package_id': package_id, 'username': username})
        if raw_data.status_code != 201:
            return TebexError(raw_data.json()['error_message'])
        return raw_data.json()
    
    # Giftcards
    def get_giftcards(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['gift-cards'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def get_giftcard(self, giftcard_id : str) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['gift-cards'] + '/' + giftcard_id, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def create_giftcard(self, giftcard_data : TebexGiftcard) -> dict:
        if not giftcard_data:
            return TebexError('No giftcard data to create')

        raw_data = requests.post(self.BASE_URL + self.ENDPOINTS['gift-cards'], headers={"X-Tebex-Secret": self.secret}, data=giftcard_data.toJSON())
        if raw_data.status_code != 201:
            return TebexError(raw_data.json()['error_message'])
        return raw_data.json()

    def delete_giftcard(self, giftcard_id : str):
        if not giftcard_id:
            return TebexError('No giftcard ID to delete')

        raw_data = requests.delete(self.BASE_URL + self.ENDPOINTS['gift-cards'] + '/' + giftcard_id, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def update_giftcard(self, giftcard_id : str, amount : int = 0):
        if not giftcard_id:
            return TebexError('No giftcard ID to update')

        raw_data = requests.put(self.BASE_URL + self.ENDPOINTS['gift-cards'] + '/' + giftcard_id, headers={"X-Tebex-Secret": self.secret}, data={'amount': amount})
        
        if raw_data.status_code != 204:
            return TebexError(raw_data.json()['error_message'])
        return 'Giftcard ' + giftcard_id + ' updated with amount ' + str(amount)

    
    # Coupons
    def get_coupons(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['coupons'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    def get_coupon(self, coupon_id : str) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['coupons'] + '/' + coupon_id, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
    
    def create_coupon(self, coupon : TebexCoupon) -> dict:
        if not coupon:
            return TebexError('No coupon data to create')

        raw_data = requests.post(self.BASE_URL + self.ENDPOINTS['coupons'], headers={"X-Tebex-Secret": self.secret}, data=coupon.toJSON())
        if raw_data.status_code != 201:
            return TebexError(raw_data.json()['error_message'])
        return raw_data.json()

    def delete_coupon(self, coupon_id : str):
        if not coupon_id:
            return TebexError('No coupon ID to delete')

        raw_data = requests.delete(self.BASE_URL + self.ENDPOINTS['coupons'] + '/' + coupon_id, headers={"X-Tebex-Secret": self.secret})
        
        if raw_data.status_code != 204:
            return TebexError(raw_data.json()['error_message'])
        return 'Coupon ' + coupon_id + ' deleted'
    
    # Bans
    def get_bans(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['bans'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
    
    def create_ban(self, reason: str, ip: str,user : str):
        if not reason:
            return TebexError('No reason to create ban')
        if not ip:
            return TebexError('No ip to create ban')
        if not user:
            return TebexError('No user to create ban')

        raw_data = requests.post(self.BASE_URL + self.ENDPOINTS['bans'], headers={"X-Tebex-Secret": self.secret}, data={'reason': reason, 'ip': ip, 'user': user})
        if raw_data.status_code != 201:
            return TebexError(raw_data.json()['error_message'])
        return raw_data.json()
    
    # Sales

    def get_sales(self) -> dict:
        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['sales'], headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
    
    # Player Lookup

    def get_player_lookup(self, username : str) -> dict:
        if not username:
            return TebexError('No username to lookup')

        raw_data = requests.get(self.BASE_URL + self.ENDPOINTS['user'] + username, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)

    # Customer Purchases

    def get_customer_purchases(self, player_id : str, package_id : Optional[int]) -> dict:
        if not player_id:
            return TebexError('No player ID to lookup')
        
        url = self.BASE_URL + self.ENDPOINTS['player'] + player_id + '/packages'
        if package_id:
            url += '?package=' + str(package_id)

        raw_data = requests.get(url, headers={"X-Tebex-Secret": self.secret})
        return self.__handle_response(raw_data)
