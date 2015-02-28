import re

email_regex = re.compile('@')
zip_code_regex = re.compile('\d{5}')


def validate_email(email):
    return not email_regex.search(email) is None


def validate_zip_code(zip_code):
    return not zip_code_regex.match(zip_code) is None
