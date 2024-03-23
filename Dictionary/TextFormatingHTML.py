from typing import List


def place_between_tag(content: str, tag: str) -> str:
    return f"<{tag}>{content}</{tag}>"


def div(content: str) -> str:
    return f"<div>{content}</div>"


def bold(content: str) -> str:
    return place_between_tag(content, "b")


def italic(content: str) -> str:
    return place_between_tag(content, "i")


def list_item(content: str) -> str:
    return place_between_tag(content, "li")


def make_unordered_list(contents: List[str]) -> str:
    return place_between_tag("".join(contents), "ul")


def make_ordered_list(contents: List[str]) -> str:
    return place_between_tag("".join(contents), "ol")
