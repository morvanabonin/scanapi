from scanapi.tools.curl import convert_httpx_request_to_curl
from jinja2 import Environment, FileSystemLoader, PackageLoader


def render(template_path, context, is_external=False):
    """ Controller function that handles the Jinga2 rending of the template"""
    loader = _loader(is_external)
    env = Environment(loader=loader)
    env.filters["to_curl"] = convert_httpx_request_to_curl
    env.filters["dir"] = dir
    chosen_template = env.get_template(template_path)

    return chosen_template.render(**context)


def _loader(is_external):
    """ Private function that either returns Jinga2 FileSystemLoader or the PackageLoader. """
    if is_external:
        return FileSystemLoader(searchpath="./")

    return PackageLoader("scanapi", "templates")
