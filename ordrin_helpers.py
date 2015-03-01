from __init__ import ordrin_api, User
from fuzzywuzzy import process, fuzz
from helpers.reformat_phone import reformat_phone
from pprint import pprint


def string_to_dollar_int(s):
    return int(float(s) * 100)


def parse_menu_tree(tree, rest_name, rest_id, result_dict, options_accumulator, name_accumulator, price_accumulator,
                    depth=2):
    node_name = tree['name']
    int_add = 0
    if 'price' in tree:
        int_add = string_to_dollar_int(tree['price'])
    if tree['is_orderable'] == '1':
        dict_key = name_accumulator + ' ' + node_name
        result_dict[dict_key] = {'rest_id': rest_id,
                                 'rest_name': rest_name,
                                 'name': name_accumulator + ' ' + node_name,
                                 'options': [tree['id']] + options_accumulator,
                                 'price': int_add + price_accumulator
                                 }
    if depth == 0:
        dict_key = name_accumulator + ' ' + node_name
        result_dict[dict_key] = {'rest_id': rest_id,
                                 'rest_name': rest_name,
                                 'name': name_accumulator + ' ' + node_name,
                                 'options': [tree['id']] + options_accumulator,
                                 'remaining_tree': tree,
                                 'price': int_add + price_accumulator
                                 }
    elif 'children' in tree:
        for child in tree['children']:
            parse_menu_tree(child,
                            rest_name,
                            rest_id,
                            result_dict,
                            [tree['id']] + options_accumulator,
                            name_accumulator,
                            int_add + price_accumulator,
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


def match_food_item(nouns, preps, address):
    restaurant_list = ordrin_api.delivery_list('ASAP', address.address_line_1, address.city, address.zip_code)

    # Get items from ordrin API
    menu_items = {}
    for restaurant in restaurant_list:
        print restaurant['na']
        print restaurant['id']
        rest_details = ordrin_api.restaurant_details(str(restaurant['id']))
        if len(preps) > 0:
            print preps
            print restaurant['na']
            if fuzz.ratio(" ".join(preps), restaurant['na']) > 70:
                for item in rest_details['menu']:
                    parse_menu_tree(item, restaurant['na'], restaurant['id'], menu_items, [], '', 0)
        else:
            for item in rest_details['menu']:
                parse_menu_tree(item, restaurant['na'], restaurant['id'], menu_items, [], '', 0)

    # Fuzzy match long list
    found_matches = fuzzy_match_strings(menu_items, nouns, 30)
    print found_matches
    result_key, result_value = found_matches[0], menu_items[found_matches[0]]
    # Fill out the remaining tree and fuzzy match it, if it exists.
    if 'remaining_tree' in result_value:
        menu_items = {}
        rest_id, rest_name = result_value['rest_id'], result_value['rest_name']
        pprint(result_value['remaining_tree'])
        pprint(result_value['options'])
        for child in result_value['remaining_tree']['children']:
            parse_menu_tree(child,
                            rest_name,
                            rest_id,
                            menu_items,
                            result_value['options'],
                            result_value['name'],
                            result_value['price'],
                            depth=-1
                            )
        found_matches = fuzzy_match_strings(menu_items, nouns, 10)
    final_order = menu_items[found_matches[0]]
    print final_order
    options = final_order['options']
    return {'name': final_order['name'],
            'item': options[0],
            'options': ",".join(options[1:]),
            'price': final_order['price'],
            'restaurant_id': str(final_order['rest_id']),
            'restaurant_name': final_order['rest_name']
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
