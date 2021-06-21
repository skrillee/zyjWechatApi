

def request_get_username_value(request_data):
    for item in request_data:
        if item == 'username':
            username = request_data['username']
            return username
        else:
            pass


def request_get_other_value(request_data):
    parameter_other_dict = {}
    for item in request_data:
        if item != 'username' and item != 'token':
            parameter_other_dict.update({'key': item, 'value': request_data[item]})
            return parameter_other_dict
        else:
            pass


def on_ids_models_search_result(parameter):
    browse_data_list = []
    browse_value_list = []
    ids = parameter['ids']
    username = parameter['username']
    model = parameter['model']
    search_field = parameter['search_field']
    model = parameter['odoo_obj'].env[model]
    for name in ids:
        browse_data = model.browse(name).read()
        browse_value_list.append({username: browse_data[0][search_field]})
        browse_data_list.append(browse_data)
    return browse_data_list, browse_value_list


def on_ids_models_search_result_sum_total(search_value):
    result_data = {}
    for data in search_value:
        for dict_data_key, dict_data_value in data.items():
            if 'total' in result_data.keys():
                new_value = result_data['total'] + dict_data_value
                result_data.update({'total': new_value})
            else:
                result_data.update({'total': dict_data_value})
    return result_data
    # 将res_data序列化为json对象，并返回

