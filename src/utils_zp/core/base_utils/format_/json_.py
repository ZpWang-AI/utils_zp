import json


def json_dumps_force(obj, indent=None, *args, **kwargs):
    def json_encoder(obj):
        try:
            return str(obj)
        except:
            raise TypeError(f'{repr(obj)} is not JSON serializable')
    return json.dumps(obj=obj, indent=indent, ensure_ascii=False, default=json_encoder, *args, **kwargs)
