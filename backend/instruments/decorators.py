from functools import wraps


def cors(allow_origin: str):
    def decorator(func):
        @wraps(func)
        def inner_func(*args, **kwargs):
            response = func(*args, **kwargs)
            response.headers["Access-Control-Allow-Origin"] = allow_origin
            return response

        return inner_func

    return decorator
