# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 10:03:02 2019

@author: el_in
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 08 11:50:37 2017
version 1.2

@author: Cgrs scripts
"""


import sys
import os
import os.path
import codigo.funciones_sismicas2_optimized as fc
import json
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import tkintermapview

class SismoAdvancedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vista Previa de Sismo Avanzada")
        self.root.geometry("1000x600")

        # Load data
        self.paths = open(os.path.join('utiles', "paths.txt")).readlines()
        self.path_poligonos = 'provinciascsv'
        self.path_ciudades = os.path.join('utiles', 'localidades_2mundo.dat')
        self.hyp_path = self.paths[0][:-1]
        self.fpath = open(os.path.join(self.hyp_path))
        self.ciudades = fc.get_ciudades(self.path_ciudades)
        self.formato = fc.formatear_hyp(self.fpath, self.path_poligonos, self.ciudades, False, 1)

        self.sentido_var = tk.BooleanVar(value=False)
        self.send_sini_var = tk.BooleanVar(value=True)
        self.send_all_var = tk.BooleanVar(value=False)

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for data and controls
        left_frame = tk.Frame(main_frame, width=333)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        left_frame.pack_propagate(False) # Prevent frame from resizing to fit content

        # Right frame for map
        right_frame = tk.Frame(main_frame, width=667)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False) # Prevent frame from resizing to fit content

        # Data display
        self.create_data_display(left_frame)

        # Map display
        self.create_map_display(right_frame)

        # Buttons
        self.create_buttons(left_frame)

    def create_data_display(self, parent):
        data_frame = tk.LabelFrame(parent, text="Datos del Sismo")
        data_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(data_frame, columns=("Dato", "Valor"), show="headings")
        self.tree.heading("Dato", text="Dato")
        self.tree.heading("Valor", text="Valor")
        self.tree.column("Dato", width=100, minwidth=100, stretch=tk.NO)
        self.tree.column("Valor", width=500, minwidth=500, stretch=tk.YES)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.update_data_display()

    def update_data_display(self):
        self.tree.delete(*self.tree.get_children())

        # Configure tags for coloring
        self.tree.tag_configure("normal_mag", foreground="blue") # Example color for normal mag
        self.tree.tag_configure("red_mag", foreground="red")

        display_keys = ['id', 'analista', 'fecha', 'hora', 'lat', 'lon', 'depth', 'rms', 'magL', 'magW', 'magC', 'mag', 'comentario', 'sentido']

        for key in display_keys:
            value = self.formato.get(key, "N/A")
            if key == 'mag' and self.sentido_var.get():
                self.tree.insert("", "end", values=(key.capitalize(), value), tags=("red_mag",))
            elif key == 'sentido':
                self.tree.insert("", "end", values=(key.capitalize(), self.sentido_var.get()))
            else:
                self.tree.insert("", "end", values=(key.capitalize(), value))

    def create_map_display(self, parent):
        map_widget = tkintermapview.TkinterMapView(parent, width=500, height=500, corner_radius=0, relief=tk.RIDGE, borderwidth=2)
        map_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        lat = float(self.formato['lat'])
        lon = float(self.formato['lon'])

        map_widget.set_position(lat, lon)
        map_widget.set_marker(lat, lon, text="Ubicación del sismo")
        map_widget.set_zoom(10)

    def create_buttons(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        # Magnitude selection (Radiobuttons)
        mag_radio_frame = tk.Frame(button_frame)
        mag_radio_frame.pack(fill=tk.X, pady=5)
        self.mag_var = tk.IntVar(value=self.formato.get('tipo_magni', 1))
        tk.Radiobutton(mag_radio_frame, text="Mag Coda", variable=self.mag_var, value=1, command=self.update_magnitude).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mag_radio_frame, text="Mag Local", variable=self.mag_var, value=2, command=self.update_magnitude).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mag_radio_frame, text="Mag MW", variable=self.mag_var, value=3, command=self.update_magnitude).pack(side=tk.LEFT, padx=5)

        # Email options (Checkbuttons)
        email_check_frame = tk.Frame(button_frame)
        email_check_frame.pack(fill=tk.X, pady=5)
        tk.Checkbutton(email_check_frame, text="Sismo Sentido", variable=self.sentido_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(email_check_frame, text="Enviar a SINI", variable=self.send_sini_var).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(email_check_frame, text="Enviar a Todos", variable=self.send_all_var).pack(side=tk.LEFT, padx=5)

        # Action buttons
        action_button_frame = tk.Frame(button_frame)
        action_button_frame.pack(fill=tk.X, pady=5)
        tk.Button(action_button_frame, text="Enviar", command=self.send).pack(side=tk.RIGHT, padx=5)
        tk.Button(action_button_frame, text="Cancelar", command=self.root.destroy).pack(side=tk.RIGHT)

    def update_magnitude(self):
        self.formato['tipo_magni'] = self.mag_var.get()
        if self.mag_var.get() == 1:
            self.formato['mag'] = self.formato['magC']
        elif self.mag_var.get() == 2:
            self.formato['mag'] = self.formato['magL']
        elif self.mag_var.get() == 3:
            self.formato['mag'] = self.formato['magW']
        self.update_data_display()

    def send(self):
        sentido = self.sentido_var.get()
        send_sini = self.send_sini_var.get()
        send_all = self.send_all_var.get()
        crear_hyper(self.formato, sentido, self.paths, send_sini, send_all)
        self.root.destroy()

def crear_hyper(formato,sentido,paths,send_sini,send_all):
    fc.insertar_comentario(paths,formato,sentido)
    fc.guardar_datos(paths,formato)

    if(send_sini):
        archivos_sini=open('utiles\contactos-sini.txt','r').readlines()
        archivos_sini=open(paths[8][:-1],'r').readlines()
        contactos_sini = [n[:-1] for n in archivos_sini]# if n not in contactos_sini]
        contactos_sini[-1]=archivos_sini[-1]
        fc.enviarEmail(contactos_sini,formato,sentido,paths)

    if(send_all):
        # archivos_contactos=open('utiles\contactos.txt','r').readlines()
        archivos_contactos=open(paths[9][:-1],'r').readlines()
        contactos = [n[:-1] for n in archivos_contactos]# if n not in contactos]
        contactos[-1]=archivos_contactos[-1]
        fc.enviarEmail(contactos,formato,sentido,paths,'html')

if __name__ == "__main__":
    root = tk.Tk()
    app = SismoAdvancedApp(root)
    root.mainloop()
