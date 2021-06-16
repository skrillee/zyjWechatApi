import urllib.error
from rest_framework.views import APIView
from rest_framework.response import Response
import odoorpc
import json
import time
import datetime
from odoorpc.error import RPCError


class LoginView(APIView):

    def __init__(self):
        super().__init__()
        self.ip = '47.92.85.245'
        self.port = '3366'
        self.username = '1979736774@qq.com'
        self.password = 'odooodoo'
        self.dbname = 'odoo'

    def __call__(self):
        odoo = self.odoo_instance()
        self.odoo_login(odoo)
        return odoo

    def odoo_instance(self):
        try:
            odoo = odoorpc.ODOO(self.ip, port=self.port)
        except urllib.error.URLError as URLError:
            return None
        return odoo

    def odoo_login(self, odoo):
        odoo.login(self.dbname, self.username, self.password)


class FreightBill(LoginView):

    def __init__(self):
        super().__init__()
        login = LoginView()
        odoo_login = login()
        self.odoo = odoo_login

    @staticmethod
    def request_extract_parameters(self, request_data):
        parameter_dict = {}
        parameter_username_dict = {}
        for item in request_data:
            if item == 'username':
                username = request_data['username']
                parameter_username_dict.update({'username': username})
            else:
                parameter_dict.update({item: request_data[item]})
        return [parameter_dict, parameter_username_dict]

    def get(self, request):
        if 'sale.order' in self.odoo.env:
            name_db = self.odoo.env['fixed.freight_bill']
            request_data = request._request.GET
            parameter_dict = self.request_extract_parameters(request_data)[0]
            parameter_user_dict = self.request_extract_parameters(request_data)[1]
            request_username = parameter_user_dict.get('username', None)
            parameter_dict_key = list(parameter_dict.keys())[0]
            parameter_dict_value = parameter_dict[parameter_dict_key]
            if request_username:
                name_id = self.odoo.env['res.partner'].search([('name', '=', request_username)])
                if name_id:
                    freight_ids = self.odoo.env['fixed.freight_bill'].search(
                        ['&', (parameter_dict_key, 'like', parameter_dict_value), ('partner_id', '=', name_id[0])])
            else:
                freight_ids = self.odoo.env['fixed.freight_bill'].search(
                    [(parameter_dict_key, 'like', parameter_dict_value)])
            browse_value = []
            if isinstance(freight_ids, list):
                for name in freight_ids:
                    browse_data = name_db.browse(name).read()
                    browse_value.append({browse_data[0]['partner_id'][1]: browse_data[0]['amount_total_signed']})
            res_data = {}
            for data in browse_value:
                for dict_data_key, dict_data_value in data.items():
                    if dict_data_key in res_data.keys():
                        new_value = res_data[dict_data_key] + dict_data_value
                        res_data.update({dict_data_key: new_value})
                    else:
                        res_data.update({dict_data_key: dict_data_value})
            # 将res_data序列化为json对象，并返回
        else:
            res_data = {}
        print(res_data)
        return Response(json.dumps(res_data), content_type="application/json")


