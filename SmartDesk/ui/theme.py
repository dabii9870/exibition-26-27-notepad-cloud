"""Shared theme styling for Tk widgets."""

import tkinter as tk


_DARK_TO_LIGHT_BACKGROUNDS = {
    "#0B1020": "#F8FAFC",
    "#050816": "#F1F5F9",
    "#111827": "#FFFFFF",
    "#0F172A": "#FFFFFF",
    "#172033": "#F1F5F9",
    "#1E293B": "#E2E8F0",
    "#334155": "#CBD5E1",
    "#475569": "#CBD5E1",
}
_LIGHT_TO_DARK_BACKGROUNDS = {
    "#F8FAFC": "#0B1020",
    "#F1F5F9": "#050816",
    "#FFFFFF": "#111827",
    "#E2E8F0": "#1E293B",
    "#CBD5E1": "#334155",
}
_DARK_TO_LIGHT_TEXT = {
    "#CBD5E1": "#334155",
    "#94A3B8": "#64748B",
    "#E5E7EB": "#1E293B",
    "#E2E8F0": "#1E293B",
    "#D1D5DB": "#334155",
}
_LIGHT_TO_DARK_TEXT = {
    "#0F172A": "white",
    "#334155": "#CBD5E1",
    "#64748B": "#94A3B8",
    "#1E293B": "#E5E7EB",
}
_COLOR_OPTIONS = (
    "background",
    "foreground",
    "activebackground",
    "activeforeground",
    "disabledforeground",
    "selectcolor",
    "highlightbackground",
    "highlightcolor",
    "insertbackground",
    "selectbackground",
)
_BACKGROUND_OPTIONS = (
    "background",
    "activebackground",
    "selectcolor",
    "highlightbackground",
    "selectbackground",
)


def apply_widget_theme(widget, theme, source_theme="dark"):
    if theme not in ("dark", "light"):
        raise ValueError(f"Unsupported theme: {theme}")
    if source_theme not in ("dark", "light"):
        raise ValueError(f"Unsupported source theme: {source_theme}")
    if theme == source_theme:
        return

    if theme == "light":
        backgrounds = _DARK_TO_LIGHT_BACKGROUNDS
        text_colors = _DARK_TO_LIGHT_TEXT
    else:
        backgrounds = _LIGHT_TO_DARK_BACKGROUNDS
        text_colors = _LIGHT_TO_DARK_TEXT

    color_options = widget.keys()
    original_background = (
        widget.cget("background")
        if "background" in color_options
        else None
    )

    for option in _COLOR_OPTIONS:
        if option not in color_options:
            continue

        color = widget.cget(option)
        if not isinstance(color, str):
            continue

        mapped_color = backgrounds.get(color.upper())
        if option in _BACKGROUND_OPTIONS and mapped_color:
            widget.configure(**{option: mapped_color})
            continue

        mapped_color = text_colors.get(color.upper())
        if mapped_color is None and color.lower() == "white" and theme == "light":
            if isinstance(original_background, str) and original_background.upper() in backgrounds:
                mapped_color = "#0F172A"
        if mapped_color:
            widget.configure(**{option: mapped_color})

    for child in widget.winfo_children():
        apply_widget_theme(child, theme, source_theme)

    menu_name = widget.cget("menu") if "menu" in color_options else None
    if menu_name:
        try:
            menu = widget.nametowidget(menu_name)
        except tk.TclError:
            return
        apply_widget_theme(menu, theme, source_theme)
