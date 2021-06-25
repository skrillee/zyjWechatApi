import json
import odoorpc
import urllib.error
from odoorpc.error import RPCError
from django.shortcuts import render
from rest_framework.views import APIView
from django.shortcuts import HttpResponse
from api.utils.jwt_auth import create_token
from api.parameter.input_parameter import *
from django.views.decorators.csrf import csrf_exempt
from api.extensions.auth import JwtQueryParamsAuthentication
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
        token = create_token({'id': res_partner_id, 'name': username})
        response_data = {'code': 1001, 'data': token}
        return HttpResponse(json.dumps(response_data))


class ProSearchFreightUsernamePricesView(LoginView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        odoo_obj = odoorpc.ODOO.load(request.user['name'])

        if 'sale.order' in odoo_obj.env:
            request_data = request.query_params
            request_username_value = request_get_username_value(request_data)
            parameter_other_dict = request_get_other_value(request_data)
            freight_ids = []
            if request_username_value and parameter_other_dict is None:
                odoo_obj.read()

            # Pass in the ID of the username and return the freight_ids
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
                'odoo_obj': odoo_obj,
            }
            # return all the freight that belong to someone
            search_freight_bill_data = on_ids_models_search_result(parameter)
            search_freight_bill_data_detail = []

            # Pass in the ID of the freight_line_id and return the detail of data
            for freight in search_freight_bill_data:
                freight_line_ids = freight[0]['freight_line_ids']
                if freight_line_ids:
                    freight_line_detail = on_ids_freight_bill_search_result_detail(odoo_obj, freight_line_ids)
                    freight[0]['freight_line_detail'] = freight_line_detail
                search_freight_bill_data_detail.append(freight)
            return HttpResponse(json.dumps(search_freight_bill_data_detail), content_type="application/json")


class ProStatisticsFreightView(LoginView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        odoo_obj = odoorpc.ODOO.load(request.user['name'])
        odoo_obj.env['fixed.freight_bill'].search(args)
        request_data = request.query_params
        result_freight = {}
        if 'this_year_freight' in request_data and 'date_month' in request_data:
            this_year_freight = request_get_this_year_freight(odoo_obj)
            result_freight = this_year_freight
        if 'this_year_freight' in request_data and 'partner_id' in request_data:
            this_year_freight_by_partner = request_get_this_year_freight_by_partner(odoo_obj)
            this_year_freight_by_partner.reverse()
            result_freight = this_year_freight_by_partner
        if 'last_year_freight' in request_data and 'date_month' in request_data:
            last_year_freight = request_get_last_year_freight(odoo_obj)
            result_freight = last_year_freight
        if 'last_year_freight' in request_data and 'partner_id' in request_data:
            last_year_freight_by_partner = request_get_last_year_freight_by_partner(odoo_obj)
            last_year_freight_by_partner.reverse()
            result_freight = last_year_freight_by_partner
        if 'today_freight' in request_data:
            today_freight = request_today_freight(odoo_obj)
            result_freight = today_freight
        if 'yesterday_freight' in request_data:
            yesterday_freight = request_yesterday_freight(odoo_obj)
            result_freight = yesterday_freight
        return HttpResponse(json.dumps(result_freight), content_type="application/json")


# def listing(request):
#     contact_list = Contacts.objects.all()
#     paginator = Paginator(contact_list, 25)  # Show 25 contacts per page
#
#     page = request.GET.get('page')
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         contacts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         contacts = paginator.page(paginator.num_pages)
#
#     return render(request, 'list.html', {'contacts': contacts})


class ProStatisticsFreightDetailView(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        odoo_obj = odoorpc.ODOO.load(request.user['name'])
        odoo_obj.env['fixed.freight_bill'].search(args)
        request_data = request.query_params
        if 'start_date' and 'end_date' in request_data:
            freight_detail_list = request_freight_detail(request_data, odoo_obj)
            search_freight_bill_data_detail = []
            for freight in freight_detail_list:
                if freight:
                    freight_line_ids = freight['freight_line_ids']
                    freight_line_detail = on_ids_freight_bill_search_result_detail(odoo_obj, freight_line_ids)
                    freight['freight_line_detail'] = freight_line_detail
                search_freight_bill_data_detail.append(freight)
            paginator = Paginator(search_freight_bill_data_detail, 20, 9)
            page = request_data['page']
            try:
                contacts = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)
            return HttpResponse(json.dumps(contacts.object_list), content_type="application/json")


