from tkinter import messagebox


def mostrar_error(titulo, mensaje):
    return messagebox.showerror(
        titulo,
        mensaje
    )


def mostrar_advertencia(titulo, mensaje):
    return messagebox.showwarning(
        titulo,
        mensaje
    )


def mostrar_info(titulo, mensaje):
    return messagebox.showinfo(
        titulo,
        mensaje
    )


def confirmar(titulo, mensaje):
    return messagebox.askyesno(
        titulo,
        mensaje
    )