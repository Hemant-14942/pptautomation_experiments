"""Helpers for swapping shapes on a slide's shape tree."""

from __future__ import annotations

from lxml import etree


def replace_shape(sp_tree: etree._Element, orig_el: etree._Element, clone_el: etree._Element) -> None:
    if orig_el.getparent() is not None:
        sp_tree.remove(orig_el)
    sp_tree.append(clone_el)
