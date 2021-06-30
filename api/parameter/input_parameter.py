#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/06/23
# @Author  : yanzhe(skrillee)
# @FileName: input_parameter.py
# @Software: Pycharm
from datetime import datetime, timedelta


def request_get_username_value(request_data) -> str or None:
    """
    Args:
        request_data (QueryDict): Include token and date_invoice and username
    Returns:
        username(str): return username or None
    """
    for item in request_data:
        if item == 'username':
            username = request_data['username']
            return username
        else:
            pass


def request_get_other_value(request_data) -> dict or None:
    """
    Args:
        request_data (QueryDict): Include token and date_invoice and username
    Returns:
        parameter_other_dict(dict): return date_invoice and username or None
    """
    parameter_other_dict = {}
    for item in request_data:
        if item != 'username' and item != 'token':
            parameter_other_dict.update({'key': item, 'value': request_data[item]})
            return parameter_other_dict
        else:
            pass


def on_ids_models_search_result(parameter) -> list:
    """
    Args:
        parameter (dict): Include ids , model , search_field , odoo_obj , username
    Returns:
        browse_data_list(list): All of a person's freights within a specified date
        browse_value_list(list): Amount of all orders
    """
    browse_data_list = []
    ids = parameter['ids']
    model = parameter['model']
    model = parameter['odoo_obj'].env[model]
    for name in ids:
        browse_data = model.browse(name).read()
        browse_data_list.append(browse_data)
    return browse_data_list


def on_ids_freight_bill_search_result_detail(odoo_obj, freight_line_ids) -> list:
    """
    Args:
        freight_line_ids (list): freight_line_ids
        odoo_obj(object): odoo object
    Returns:
        result_data(dict): freight_bill_ids -> freight_line_line
    """
    freight_line_detail = []
    if freight_line_ids:
        for freight_line in freight_line_ids:
            browse_data = odoo_obj.env['fixed.freight_bill.line'].browse(freight_line).read()
            freight_line_detail.append(browse_data)
    return freight_line_detail


# "end_last_year_datetime" and "yesterday_datetime" Should not be used as a return parameter
end_last_year_datetime = datetime(datetime.now().year, 1, 1) - timedelta(days=1)
yesterday_datetime = datetime.now()-timedelta(days=1)


one_day = timedelta(days=1)
yesterday = str(
    yesterday_datetime.year) + '-' + str(
    yesterday_datetime.month) + '-' + str(
    yesterday_datetime.day)
this_year_today = str(
    datetime.now().year) + '-' + str(
    datetime.now().month) + '-' + str(
    datetime.now().day)
beginning_this_year = str(
    datetime.now().year) + '-' + '1-1'
beginning_last_year = str(
    datetime.now().year - 1) + '-' + '1-1'
end_last_year = str(
    end_last_year_datetime.year) + '-' + str(
    end_last_year_datetime.month) + '-' + str(
    end_last_year_datetime.day)


def request_get_this_year_freight(odoo_obj):
    freight_this_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', this_year_today), ('date_invoice', '>=', beginning_this_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_this_year:
        freight_this_year[0]['start_date'] = beginning_this_year
        freight_this_year[0]['end_date'] = this_year_today
    return freight_this_year


def request_get_this_year_freight_by_partner(odoo_obj):
    freight_this_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', this_year_today), ('date_invoice', '>=', beginning_this_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['partner_id'],
        orderby='amount_total'
    )
    freight_this_year.reverse()
    if freight_this_year:
        freight_this_year[0]['start_date'] = beginning_this_year
        freight_this_year[0]['end_date'] = this_year_today
    return freight_this_year


def request_get_last_year_freight(odoo_obj):
    freight_last_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', end_last_year), ('date_invoice', '>=', beginning_last_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_last_year:
        freight_last_year[0]['start_date'] = beginning_last_year
        freight_last_year[0]['end_date'] = end_last_year
    return freight_last_year


def request_get_last_year_freight_by_partner(odoo_obj):
    freight_last_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', end_last_year), ('date_invoice', '>=', beginning_last_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['partner_id'],
        orderby='amount_total'
    )
    if freight_last_year:
        freight_last_year[0]['start_date'] = beginning_last_year
        freight_last_year[0]['end_date'] = end_last_year
    return freight_last_year


def request_today_freight(odoo_obj):
    freight_today = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '=', this_year_today)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_today:
        freight_today[0]['start_date'] = this_year_today
        freight_today[0]['end_date'] = this_year_today
    return freight_today


def request_yesterday_freight(odoo_obj):
    freight_yesterday = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '=', yesterday)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_yesterday:
        freight_yesterday[0]['start_date'] = yesterday
        freight_yesterday[0]['end_date'] = yesterday
    return freight_yesterday


def on_partner_id_search_partner_name(odoo_obj, partner_id):
    browse_data = odoo_obj.env['res.partner'].browse(partner_id).read()[0]
    partner_name = browse_data['name']
    return partner_name


def request_freight_detail(request_data, odoo_obj):
    freight_ids = odoo_obj.env['fixed.freight_bill'].search(
        ['&',
         ('date_invoice', '>=', request_data['start_date']),
         ('date_invoice', '<=', request_data['end_date'])
         ]
    )
    freight_detail_list = []
    for freight_id in freight_ids:
        browse_data = odoo_obj.env['fixed.freight_bill'].browse(freight_id).read()[0]
        partner_id = browse_data['partner_id']

        amount_total = browse_data['amount_total']
        date_invoice = browse_data['date_invoice']
        partner_name = partner_id[-1]

        freight_detail = {
            'amount_total': amount_total,
            'partner_name': partner_name,
            'date_invoice': date_invoice,
            'freight_line_ids': browse_data['freight_line_ids']
        }
        freight_detail_list.append(freight_detail)
    return freight_detail_list

