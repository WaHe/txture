from __init__ import ordrin_api, User
from fuzzywuzzy import process
from helpers.reformat_phone import reformat_phone
from pprint import pprint


def parse_menu_tree(tree, rest_name, rest_id, result_dict, options_accumulator, name_accumulator, depth=2):
    node_name = tree['name']
    if tree['is_orderable'] == 1:
        dict_key = rest_name + ' ' + name_accumulator + ' ' + node_name
        result_dict[dict_key] = {'rest_id': rest_id,
                                 'rest_name': rest_name,
                                 'name': name_accumulator + ' ' + node_name,
                                 'options': options_accumulator + [tree['id']],
                                 'price': tree['price']
                                 }
    if depth == 0:
        dict_key = rest_name + ' ' + name_accumulator + ' ' + node_name
        result_dict[dict_key] = {'rest_id': rest_id,
                                 'rest_name': rest_name,
                                 'name': name_accumulator + ' ' + node_name,
                                 'options': options_accumulator + [tree['id']],
                                 'remaining_tree': tree
                                 }
    elif 'children' in tree:
        for child in tree['children']:
            parse_menu_tree(child,
                            rest_name,
                            rest_id,
                            result_dict,
                            options_accumulator + [tree['id']],
                            name_accumulator + ' ' + node_name,
                            depth=depth - 1
                            )


def get_fuzzy_matches(match_string, choices, limit):
    matches = process.extract(match_string, choices, limit=limit)
    return [k[0] for k in matches]


def fuzzy_match_strings(choices, strings, limit):
    m = choices.keys()
    str_len = len(strings)
    test_string = ''
    for i, s in enumerate(strings):
        test_string += ' ' + s
        new_limit = limit - (i + 1) * (limit / str_len) + 3
        m = get_fuzzy_matches(test_string, m, new_limit)
    return m




def match_food_item(test_strings, user, address):
    restaurant_list = ordrin_api.delivery_list('ASAP', address.address_line_1, address.city, address.zip_code)

    # Get items from ordrin API
    menu_items = {}
    for restaurant in restaurant_list[:1]:
        print restaurant['na']
        print restaurant['id']
        rest_details = ordrin_api.restaurant_details(str(restaurant['id']))
        pprint(rest_details)
        for menu_item in rest_details['menu']:
            parse_menu_tree(menu_item, restaurant['na'], restaurant['id'], menu_items, [], '')

    # Fuzzy match long list
    found_matches = fuzzy_match_strings(menu_items, test_strings, 30)
    result_key, result_value = found_matches[0], menu_items[found_matches[0]]

    # Fill out the remaining tree and fuzzy match it, if it exists.
    if 'remaining_tree' in result_value:
        rest_id, rest_name = result_value['rest_name'], result_value['rest_id']
        parse_menu_tree(result_value['remaining_tree'],
                        rest_name,
                        rest_id,
                        menu_items,
                        result_value['options'],
                        result_value['name'],
                        depth=-1
                        )
        found_matches = fuzzy_match_strings(menu_items,  test_strings, 10)
    print found_matches[0], menu_items[found_matches[0]]
    final_order = menu_items[found_matches[0]]
    options = final_order['options']
    return {
               'item': options[0],
               'option': ",".join(options[-2::-1]),
               'price': int(float(final_order['price']) * 100),
               'restaurant_id': str(final_order['rest_id'])
    }


def place_order(restaurant_id, food_string, tip, user, address):
    try:
        ordrin_api.order_user(restaurant_id,
                              food_string,
                              tip,
                              user.first_name,
                              user.last_name,
                              user.email,
                              user.password,
                              phone=reformat_phone(user.phone_number),
                              addr=address.address_line_1,
                              addr2=address.address_line_2,
                              city=address.city,
                              state=address.state,
                              zip=address.zip_code,
                              delivery_date='03-02',
                              delivery_time='12:00',
                              card_nick='default')
    except:
        raise
