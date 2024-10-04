from flask import Flask

from flask import render_template
from flask import request

import pusher

import mysql.connector
import datetime
import pytz

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

@app.route("/")
def index():
    con.close()

    return render_template("app.html")

# Ejemplo de ruta GET usando templates para mostrar una vista
@app.route("/alumnos")
def alumnos():
    con.close()

    return render_template("alumnos.html")

# Ejemplo de ruta POST para ver cómo se envia la informacion
@app.route("/alumnos/guardar", methods=["POST"])
def alumnosGuardar():
    con.close()
    matricula      = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]

    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

# Código usado en las prácticas
@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("SELECT * FROM sensor_log ORDER BY Id_Log DESC")
    registros = cursor.fetchall()

    con.close()

    return registros

@app.route("/guardar", methods=["POST"])
def guardar():
    if not con.is_connected():
        con.reconnect()

    id          = request.form["id"]
    temperatura = request.form["temperatura"]
    humedad     = request.form["humedad"]
    fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE sensor_log SET
        Temperatura = %s,
        Humedad     = %s
        WHERE Id_Log = %s
        """
        val = (temperatura, humedad, id)
    else:
        sql = """INSERT INTO sensor_log (Temperatura, Humedad, Fecha_Hora)
                                 VALUES (%s,          %s,      %s)"""
        val =                           (temperatura, humedad, fechahora)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusher_client = pusher.Pusher(
        app_id="1714541",
        key="3ce64b716f42fee14c9b",
        secret="dfe422af8d19a7130710",
        cluster="us2",
        ssl=True
    )

    pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", {})

    return jsonify({})
