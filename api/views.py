import json
import odoorpc
import urllib.error
from odoorpc.error import RPCError
from rest_framework.views import APIView
from django.shortcuts import HttpResponse
from api.utils.jwt_auth import create_token
from django.views.decorators.csrf import csrf_exempt
from api.extensions.auth import JwtQueryParamsAuthentication


class LoginView(APIView):

    def __init__(self):
        super().__init__()
        self.ip = '47.92.85.245'
        self.port = '3367'
        self.dbname = 'odootest'

    def __call__(self, odoo, username, password):
        odoo = self.odoo_instance()
        odoo = self.odoo_login(odoo, username, password)
        return odoo

    def odoo_instance(self):
        try:
            odoo = odoorpc.ODOO(self.ip, port=self.port)
            return odoo
        except urllib.error.URLError as URLError:
            return None

    def odoo_login(self, odoo, username, password):
        odoo.login(self.dbname, username, password)
        odoo.save(username)
        return odoo


class ProLoginView(LoginView):

    def __init__(self):
        super().__init__()
        self.login_obj = LoginView()
        self.odoo_obj = self.login_obj.odoo_instance()

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        username = request.data.get('phone')
        password = request.data.get('password')
        res_partner_id = '2021'
        try:
            self.login_obj(self.odoo_obj, username, password)
        except RPCError as loginError:
            return HttpResponse(json.dumps({'code': 1000, 'error': loginError.args[0]}))
        # if 'sale.order' in odoo.env:
        #     res_partner_id = odoo.env['res.partner'].search([('email', '=', username)])
        token = create_token({'id': res_partner_id, 'name': username})
        res_data = {'code': 1001, 'data': token}
        return HttpResponse(json.dumps(res_data))


class ProOrderView(LoginView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    @staticmethod
    def request_extract_parameters(request_data):
        parameter_dict = {}
        parameter_username_dict = {}
        for item in request_data:
            if item == 'username':
                username = request_data['username']
                parameter_username_dict.update({'username': username})
            elif item != 'token':
                parameter_dict.update({item: request_data[item]})
        return [parameter_dict, parameter_username_dict]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        odoo_obj = odoorpc.ODOO.load(request.user['name'])
        if 'sale.order' in odoo_obj.env:
            name_db = odoo_obj.env['fixed.freight_bill']
            request_data = request.query_params
            parameter_dict = self.request_extract_parameters(request_data)[0]
            parameter_user_dict = self.request_extract_parameters(request_data)[1]
            request_username = parameter_user_dict.get('username', None)
            try:
                parameter_dict_key = list(parameter_dict.keys())[0]
                parameter_dict_value = parameter_dict[parameter_dict_key]
            except IndexError as error:
                return error
            freight_ids = []
            if request_username:
                name_id = odoo_obj.env['res.partner'].search([('name', '=', request_username)])
                if name_id:
                    freight_ids = odoo_obj.env['fixed.freight_bill'].search(
                        ['&', (parameter_dict_key, 'like', parameter_dict_value), ('partner_id', '=', name_id[0])])
            else:
                freight_ids = odoo_obj.env['fixed.freight_bill'].search(
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
        return HttpResponse(json.dumps(res_data), content_type="application/json")
