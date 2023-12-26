import json
import os

from chainlit.config import BACKEND_ROOT, PACKAGE_ROOT, config


def get_build_dir():
    local_build_dir = os.path.join(PACKAGE_ROOT, "frontend", "dist")
    packaged_build_dir = os.path.join(BACKEND_ROOT, "frontend", "dist")
    if os.path.exists(local_build_dir):
        return local_build_dir
    elif os.path.exists(packaged_build_dir):
        return packaged_build_dir
    else:
        raise FileNotFoundError("Built UI dir not found")


build_dir = get_build_dir()

def get_html_template():
    PLACEHOLDER = "<!-- TAG INJECTION PLACEHOLDER -->"
    JS_PLACEHOLDER = "<!-- JS INJECTION PLACEHOLDER -->"
    CSS_PLACEHOLDER = "<!-- CSS INJECTION PLACEHOLDER -->"

    default_url = "https://ally.ai"
    url = default_url

    tags = f"""<title>{config.ui.name}</title>
    <meta name="description" content="{config.ui.description}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{config.ui.name}">
    <meta property="og:description" content="{config.ui.description}">
    <meta property="og:image" content="https://chainlit-cloud.s3.eu-west-3.amazonaws.com/logo/chainlit_banner.png">
    <meta property="og:url" content="{url}">"""

    js = f"""<script>{f"window.theme = {json.dumps(config.ui.theme.to_dict())}; " if config.ui.theme else ""}</script>"""

    css = None
    if config.ui.custom_css:
        css = (
            f"""<link rel="stylesheet" type="text/css" href="{config.ui.custom_css}">"""
        )

    index_html_file_path = os.path.join(build_dir, "index.html")

    with open(index_html_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        content = content.replace(PLACEHOLDER, tags)
        if js:
            content = content.replace(JS_PLACEHOLDER, js)
        if css:
            content = content.replace(CSS_PLACEHOLDER, css)
        return content