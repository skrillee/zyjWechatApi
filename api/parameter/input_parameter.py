#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/06/23
# @Author  : yanzhe(skrillee)
# @FileName: input_parameter.py
# @Software: Pycharm
from datetime import datetime, timedelta, date
import pypinyin
from collections import defaultdict


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


def time_set():

    # "end_last_year_datetime" and "yesterday_datetime" Should not be used as a return parameter
    end_last_year_datetime = datetime(datetime.now().year, 1, 1) - timedelta(days=1)
    yesterday_datetime = datetime.now()-timedelta(days=1)

    one_day = timedelta(days=1)
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
    this_year_today = date.today().strftime("%Y-%m-%d")
    beginning_this_year = str(
        datetime.now().year) + '-' + '1-1'
    beginning_last_year = str(
        datetime.now().year - 1) + '-' + '1-1'
    end_last_year = str(
        end_last_year_datetime.year) + '-' + str(
        end_last_year_datetime.month) + '-' + str(
        end_last_year_datetime.day)
    last_week = (date.today() + timedelta(days=-7)).strftime("%Y-%m-%d")
    time_dict = {
        'one_day': one_day,
        'yesterday': yesterday,
        'this_year_today': this_year_today,
        'beginning_this_year': beginning_this_year,
        'beginning_last_year': beginning_last_year,
        'end_last_year': end_last_year,
        'last_week': last_week
    }
    return time_dict


def request_get_this_year_freight(odoo_obj):
    time_set_dict = time_set()
    this_year_today = time_set_dict['this_year_today']
    beginning_this_year = time_set_dict['beginning_this_year']
    freight_this_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', this_year_today), ('date_invoice', '>=', beginning_this_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_this_year:
        freight_this_year[0]['start_date'] = beginning_this_year
        freight_this_year[0]['end_date'] = this_year_today
    return freight_this_year


def request_get_last_week_freight(odoo_obj):
    time_set_dict = time_set()
    last_week = time_set_dict['last_week']
    this_year_today = time_set_dict['this_year_today']
    freight_ids = odoo_obj.env['fixed.freight_bill'].search(
        ['&',
         ('date_invoice', '>=', last_week),
         ('date_invoice', '<=', this_year_today)
         ]
    )
    freight_last_week = []
    total_number_of_agent = 0
    for freight_id in freight_ids:
        browse_data = odoo_obj.env['fixed.freight_bill'].browse(freight_id).read()[0]
        partner_id = browse_data['partner_id']

        amount_total = browse_data['amount_total']
        date_invoice = browse_data['date_invoice']
        partner_name = partner_id[-1]
        total_number_of_agent += amount_total
        freight_detail = {
            'amount_total': amount_total,
            'partner_name': partner_name,
            'date_invoice': date_invoice,
        }
        freight_last_week.append(freight_detail)
    freight_last_week[0]['start_time'] = last_week
    freight_last_week[0]['end_time'] = this_year_today
    freight_last_week[0]['total_number_of_agent'] = total_number_of_agent
    return freight_last_week


def reverse_list_add_amount_position(parameter):
    n = len(parameter)
    asc_order = 0
    desc_order = n+1
    for i in range(n // 2):
        asc_order += 1
        desc_order -= 1
        parameter[i]['order'] = desc_order
        parameter[n - i - 1]['order'] = asc_order
        parameter[i], parameter[n - i - 1] = parameter[n - i - 1], parameter[i]
    return parameter


def request_get_this_year_freight_by_partner(odoo_obj):
    time_set_dict = time_set()
    this_year_today = time_set_dict['this_year_today']
    beginning_this_year = time_set_dict['beginning_this_year']
    freight_this_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', this_year_today), ('date_invoice', '>=', beginning_this_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['partner_id'],
        orderby='amount_total'
    )
    freight_this_year = reverse_list_add_amount_position(freight_this_year)

    if freight_this_year:
        freight_this_year[0]['start_date'] = beginning_this_year
        freight_this_year[0]['end_date'] = this_year_today
        freight_this_year[0]['total_number_of_agent'] = len(freight_this_year)
    return freight_this_year


def request_get_last_year_freight(odoo_obj):
    time_set_dict = time_set()
    end_last_year = time_set_dict['end_last_year']
    beginning_last_year = time_set_dict['beginning_last_year']
    freight_last_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', end_last_year), ('date_invoice', '>=', beginning_last_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_last_year:
        freight_last_year[0]['start_date'] = beginning_last_year
        freight_last_year[0]['end_date'] = end_last_year
    return freight_last_year


def request_get_last_year_freight_by_partner(odoo_obj):
    time_set_dict = time_set()
    end_last_year = time_set_dict['end_last_year']
    beginning_last_year = time_set_dict['beginning_last_year']
    freight_last_year = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '<=', end_last_year), ('date_invoice', '>=', beginning_last_year)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['partner_id'],
        orderby='amount_total'
    )
    freight_last_year = reverse_list_add_amount_position(freight_last_year)
    if freight_last_year:
        freight_last_year[0]['start_date'] = beginning_last_year
        freight_last_year[0]['end_date'] = end_last_year
        freight_last_year[0]['total_number_of_agent'] = len(freight_last_year)
    return freight_last_year


def request_today_freight(odoo_obj):
    time_set_dict = time_set()
    this_year_today = time_set_dict['this_year_today']
    freight_today = odoo_obj.env['fixed.freight_bill'].read_group(
        domain=[('date_invoice', '=', this_year_today)],
        fields=['date_invoice', 'amount_total', 'id'],
        groupby=['date_invoice'])
    if freight_today:
        freight_today[0]['start_date'] = this_year_today
        freight_today[0]['end_date'] = this_year_today
    return freight_today


def request_yesterday_freight(odoo_obj):
    time_set_dict = time_set()
    yesterday = time_set_dict['yesterday']
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


def on_search_name_type_search_total(request_data, odoo_obj):
    freight_ids = odoo_obj.env['res.partner'].search(
        [
         ('name', '=', request_data['search_name']),
         ]
    )
    if freight_ids:
        for freight_id in freight_ids:
            freight_someone_total = odoo_obj.env['fixed.freight_bill'].read_group(
                domain=[('partner_id', '=', freight_id)],
                fields=['date_invoice', 'amount_total', 'id'],
                groupby=['date_invoice'])
            freight_someone_total[0]['total_invoice'] = 0
            freight_someone_total[0]['total_freight'] = 0
            for freight_someone_month in freight_someone_total:
                freight_someone_month['name'] = request_data['search_name']
                freight_someone_total[0]['total_invoice'] += freight_someone_month['amount_total']
                freight_someone_total[0]['total_freight'] += freight_someone_month['date_invoice_count']
            return freight_someone_total


def contact_name_to_pinyin(last_name):
    rows = pypinyin.pinyin(last_name, style=pypinyin.NORMAL)
    return ''.join(row[0][0] for row in rows if len(row) > 0)


def on_contact_name_search_by_letter_index(odoo_obj, *args):
    contact_name_order_by_contact_name = []
    contact_name_list = odoo_obj.env['res.partner'].search_read([], ['name'],  offset='', limit='')
    for contact_name in contact_name_list:
        contact_letter_index = contact_name_to_pinyin(contact_name['name'][0])
        contact_name[contact_letter_index] = contact_name['name']
        contact_name_order_by_contact_name.append(contact_name)
    return contact_name_order_by_contact_name


def on_contact_name_search_detail(request_data, odoo_obj, *args):
    request_contact_name = request_data['contact_name']
    if request_contact_name:
        browse_data = odoo_obj.env['res.partner'].search_read(domain=[('name', '=', request_contact_name)],
                                                              fields=['name', 'street', 'mobile', 'create_date'],
                                                              offset='', limit=1)
        return browse_data


def search_all_brand(odoo_obj, *args):
    all_brand = odoo_obj.env['zyj_agent_product.manufacturers'].search_read([], ['manufacturer_of_manufacturer'],
                                                                             offset='', limit='')
    return all_brand


def search_product_according_brand(odoo_obj, request_data):
    request_data_brand = request_data['search_brand']
    search_brand = odoo_obj.env['zyj_agent_product.version'].search_read([
        ('manufacturers_id', '=', request_data_brand)], ['version_name', 'version_date'],
        offset='', limit='')
    return search_brand


def search_model_according_product(odoo_obj, request_data):
    request_data_model = request_data['search_model']
    search_model = odoo_obj.env['zyj_agent_product.model'].search_read([
        ('version_id', '=', request_data_model)], ['model_number_name', 'remark'],
        offset='', limit=''
    )
    return search_model



