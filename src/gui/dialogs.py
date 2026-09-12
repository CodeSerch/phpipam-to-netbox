from tkinter import messagebox


def mostrar_error(titulo, mensaje):
    messagebox.showerror(
        titulo,
        mensaje
    )


def mostrar_advertencia(titulo, mensaje):
    messagebox.showwarning(
        titulo,
        mensaje
    )


def mostrar_info(titulo, mensaje):
    messagebox.showinfo(
        titulo,
        mensaje
    )


def confirmar(titulo, mensaje):
    return messagebox.askyesno(
        titulo,
        mensaje
    )