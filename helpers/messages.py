def init_confirm():
    return "Everything's set up now! Send me a request like \"Get me a cheeseburger!\""


def order_confirm(item, restaurant, cost, delivery_time):
    return ("How does a " + item + " from " + restaurant + " Sound? That would cost $" + cost +
            ", and should be delivered in " + delivery_time + " minutes.")
