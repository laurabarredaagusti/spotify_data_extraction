from flask import request

def get_arguments(arg):
    return request.args.get(arg, None)