from flask import Flask, render_template, request, redirect
import csv
import os
import random

app = Flask(__name__)

ADMIN_PASSWORD = "admin123"  # Puedes cambiarlo

def cargar_amigos():
    with open('amigos.csv', newline='') as f:
        reader = csv.DictReader(f)
        return [row['nombre'] for row in reader]

def cargar_asignaciones():
    asignados = {}
    if os.path.exists('asignaciones.csv'):
        with open('asignaciones.csv', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                asignados[row['nombre']] = row['asignado']
    return asignados

def guardar_asignaciones(asignados):
    with open('asignaciones.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['nombre', 'asignado'])
        writer.writeheader()
        for nombre, asignado in asignados.items():
            writer.writerow({'nombre': nombre, 'asignado': asignado})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        if respuesta == '3':
            return redirect('/sorteo')
        else:
            return render_template('index.html', error="Respuesta incorrecta.")
    return render_template('index.html')

@app.route('/sorteo', methods=['GET', 'POST'])
def sorteo():
    amigos = cargar_amigos()
    asignados = cargar_asignaciones()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        anterior = request.form.get('anterior')

        if nombre in asignados:
            return render_template('resultado.html', resultado=f"Ya te ha tocado: {asignados[nombre]}")

        posibles = [a for a in amigos if a != nombre and a != anterior and a not in asignados.values()]
        if not posibles:
            return render_template('resultado.html', resultado="No hay personas disponibles.")

        random.shuffle(posibles)
        elegido = posibles[0]
        asignados[nombre] = elegido
        guardar_asignaciones(asignados)
        return render_template('resultado.html', resultado=f"Te ha tocado: {elegido}")

    return render_template('sorteo.html', amigos=amigos)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            if os.path.exists('asignaciones.csv'):
                os.remove('asignaciones.csv')
            return render_template('admin.html', mensaje="Asignaciones reiniciadas con éxito.")
        else:
            return render_template('admin.html', error="Contraseña incorrecta.")
    return render_template('admin.html')
