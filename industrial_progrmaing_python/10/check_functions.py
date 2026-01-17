import json

import custom_json


def main():
    json_str = '{"gr": 1000, "world": "vf"}'
    json_doc = json.loads(json_str)
    cust_json_doc = custom_json.loads(json_str)
    assert json_doc == cust_json_doc
    cust_json_str = custom_json.dumps(cust_json_doc)
    assert json_str == cust_json_str


if __name__ == "__main__":
    main()
