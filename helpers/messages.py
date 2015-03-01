from random import choice

sample_requests = [
    "Get me a cheeseburger!",
    "May I obtain a burrito?",
    "I want a gyro"
]


def init_confirm():
    return "Everything's set up now! Send me a request like \"" + choice(sample_requests) + "\""


def order_confirm(item, restaurant, cost, delivery_time):
    start_strs = [
        "How'd you like a " + item + " from " + restaurant + "?",
        "How does a " + item + " from " + restaurant + " Sound?",
        "I can get you a " + item + " from " + restaurant + ", sound good?",
        "Would you like a " + item + " from " + restaurant + "?",
        "Should I order you a " + item + " from " + restaurant + "?"
    ]
    end_str = " That would cost $" + cost + ", and should be delivered in " + delivery_time + " minutes."
    return choice(start_strs) + end_str


def misunderstood_order():
    return "Sorry, I had trouble understanding that... Try a simpler request, like \"" + choice(sample_requests) + "\""
