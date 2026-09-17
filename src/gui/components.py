import tkinter as tk
from tkinter import ttk


def crear_label(parent, texto):
    return ttk.Label(
        parent,
        text=texto
    )


def crear_entry(parent, variable, width=50):
    return ttk.Entry(
        parent,
        textvariable=variable,
        width=width
    )


def crear_boton(parent, texto, comando, width=15):
    return ttk.Button(
        parent,
        text=texto,
        command=comando,
        width=width
    )


def crear_frame(parent):
    return ttk.Frame(parent)


def crear_label_frame(parent, texto):
    return ttk.LabelFrame(
        parent,
        text=texto
    )


def crear_progressbar(parent, maximum=100):
    return ttk.Progressbar(
        parent,
        orient="horizontal",
        mode="determinate",
        maximum=maximum
    )


def crear_treeview(parent, columnas):
    tree = ttk.Treeview(
        parent,
        columns=columnas,
        show="headings"
    )

    for columna in columnas:
        tree.heading(
            columna,
            text=columna
        )

    return tree


def crear_listbox(parent, height=10):
    return tk.Listbox(
        parent,
        height=height
    )