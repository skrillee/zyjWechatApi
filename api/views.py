import json
import odoorpc
import urllib.error
from api.parameter.input_parameter import *
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
        self.port = '3366'
        self.dbname = 'odoo'

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
        response_data = {'code': 1001, 'data': token}
        return HttpResponse(json.dumps(response_data))


class ProSearchOrderUsernamePricesView(LoginView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        odoo_obj = odoorpc.ODOO.load(request.user['name'])
        if 'sale.order' in odoo_obj.env:
            request_data = request.query_params
            request_username_value = request_get_username_value(request_data)
            parameter_other_dict = request_get_other_value(request_data)
            freight_ids = []
            if request_username_value:
                name_id = odoo_obj.env['res.partner'].search([('name', '=', request_username_value)])
                if name_id:
                    freight_ids = odoo_obj.env['fixed.freight_bill'].search(
                        ['&', (parameter_other_dict['key'], 'like', parameter_other_dict['value']),
                         ('partner_id', '=', name_id[0])])
                else:
                    freight_ids = odoo_obj.env['fixed.freight_bill'].search(
                        [(parameter_other_dict['key'], 'like', parameter_other_dict['value'])])
            parameter = {
                'ids': freight_ids,
                'model': 'fixed.freight_bill',
                'search_field': 'amount_total_signed',
                'odoo_obj': odoo_obj,
                'username': request_username_value
            }
            search_data, search_value = on_ids_models_search_result(parameter)
            amount_total_signed = on_ids_models_search_result_sum_total(search_value)
            search_data.append([amount_total_signed])
            search_data.append([{'username': request_username_value}])
            return HttpResponse(json.dumps(search_data), content_type="application/json")


class DownloadImg(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        request_data = request.query_params

