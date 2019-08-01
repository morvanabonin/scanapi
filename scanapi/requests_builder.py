#!/usr/bin/env python3
import requests
import yaml

from scanapi.variable_parser import (
    populate_dict,
    populate_str,
    save_response,
    save_variable,
)


class RequestsBuilder:
    def __init__(self, file_path):
        self.file_path = file_path
        with open(file_path, "r") as stream:
            try:
                self.api = yaml.safe_load(stream)["api"]
            except yaml.YAMLError as exc:
                print(exc)

    def all_responses(self):
        responses = []
        url = populate_str(self.api["base_url"])
        headers = self.merge_headers({}, self.api)
        params = self.merge_params({},self.api)
        self.merge_custom_vars(self.api)

        return self.parse_endpoints(responses, self.api["endpoints"], headers, url, params)

    def parse_endpoints(self, responses, endpoints, headers, url, params, namespace=""):
        for endpoint in endpoints:
            headers = self.merge_headers(headers, endpoint)
            url = self.merge_url_path(url, endpoint)
            namespace = self.merge_namespace(namespace, endpoint)
            params = self.merge_params(params, endpoint)
            self.merge_custom_vars(endpoint)

            for request in endpoint["requests"]:
                request_headers = self.merge_headers(headers, request)
                request_url = self.merge_url_path(url, request)
                request_params = self.merge_params(params, request)
                request_body = self.merge_body({}, request)

                if request["method"].lower() == "get":
                    response = self.get_request(request_url, request_headers, request_params)
                    response_id = "{}_{}".format(namespace, request["name"])
                    save_response(response_id, response)
                    responses.append(response)
                
                if request["method"].lower() == "post":
                    response = self.post_request(request_url, request_headers, request_body)
                    response_id = "{}_{}".format(namespace, request["name"])
                    save_response(response_id, response)
                    responses.append(response)

                self.merge_custom_vars(request)

            if "endpoints" in endpoint:
                return self.parse_endpoints(
                    responses, endpoint["endpoints"], headers, url, namespace
                )

        return responses

    def merge_headers(self, headers, node):
        if "headers" not in node:
            return headers

        return {**headers, **populate_dict(node["headers"])}

    def merge_custom_vars(self, node):
        if "vars" not in node:
            return

        for var_name, var_value in node["vars"].items():
            save_variable(var_name, var_value)

    def merge_url_path(self, path, node):
        if "path" not in node:
            return path

        populated_node_path = populate_str(node["path"])
        return "/".join(s.strip("/") for s in [path, populated_node_path])

    def merge_namespace(self, namespace, node):
        if "namespace" not in node:
            return namespace

        populated_node_namespace = populate_str(node["namespace"])

        if not namespace:
            return populated_node_namespace

        return "{}_{}".format(namespace, populated_node_namespace)

    def merge_params(self, params, node):
        if "params" not in node:
            return params

        return {**params, **populate_dict(node["params"])}

    def merge_body(self, body, node):
        if "body" not in node:
            return body

        return {**body, **populate_dict(node["body"])}

    def get_request(self, url, headers, params):
        return requests.get(url, headers=headers, params=params)

    def post_request(self, url, headers, body):
        return requests.post(url, json=body, headers=headers)