def get_all_translating_keys(payload, prefix=''):
    for key, value in payload.items():
        if type(value) is dict:
            prefix = f'{prefix}_{key}' if prefix else f'{key}'
            yield from get_all_translating_keys(value, prefix=prefix)
        elif type(value) is str:
            yield f'{prefix}_{key}' if prefix else f'{key}'
        else:
            continue


def populate_with_translating_value(json_payload, translated_payload, tool_name):
    def populate_with_values(payload, prefix=''):
        for key, value in payload.items():
            if type(value) is dict:
                prefix = f'{prefix}_{key}' if prefix else f'{key}'
                populate_with_values(value, prefix=prefix)
            elif type(value) is str:
                payload[key] = translated_payload.get(f'{prefix}_{key}', value)
            else:
                continue
    populate_with_values(json_payload, prefix=tool_name)
