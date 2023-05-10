#!/usr/bin/env python
# -*- coding: utf-8 -*-


# def clean_url(url: str) -> str:
#     url = url.replace("https://", "").replace("http://", "")
#     if url.endswith("/"):
#         url = url[:-1]

#     return url

def clean_url(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "")
    index = url.find("/")
    if index != -1:
        url = url[:index]
    return url
