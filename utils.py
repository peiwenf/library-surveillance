#!/usr/bin/env python
# -*- coding: utf-8 -*-


def clean_url(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "")
    # Find the index of the first "/"
    index = url.find("/")
    if index != -1:
        url = url[:index]
#     if url.endswith("/"):
#         url = url[:-1]

    return url
