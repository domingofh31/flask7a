from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import pusher

import mysql.connector
import datetime
import pytz

app = Flask(__name__)

class ControladorTemperaturaHumedad:
    def notificarActualizacionTemperaturaHumedad(self):
        pusher_client = pusher.Pusher(
            app_id="1714541",
            key="fd5645cc1fbe3479bba7",
            secret="5fcf6e39324c08027f21",
            cluster="us2",
            ssl=True
        )
    
        pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", {})

    def buscar(self):
        con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
        )

        # if not con.is_connected():
            # con.reconnect()
    
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
        SELECT Id_Log, Temperatura, Humedad, DATE_FORMAT(Fecha_Hora, '%d/%m/%Y') AS Fecha, DATE_FORMAT(Fecha_Hora, '%H:%i:%s') AS Hora FROM sensor_log
        ORDER BY Id_Log DESC
        LIMIT 10 OFFSET 0
        """)
        registros = cursor.fetchall()
    
        con.close()

        return make_response(jsonify(registros))

    
    def guardar(self, id, temperatura, humedad):
        con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
        )

        # if not con.is_connected():
            # con.reconnect()
    
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
            fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))

            sql = """
            INSERT INTO sensor_log (Temperatura, Humedad, Fecha_Hora)
                            VALUES (%s,          %s,      %s)
            """
            val =                  (temperatura, humedad, fechahora)
        
        cursor.execute(sql, val)
        con.commit()
        con.close()
    
        self.notificarActualizacionTemperaturaHumedad()
    
        return make_response(jsonify({}))

    def editar():
        print("Editar")
    
    def eliminar():
        print("Eliminar")

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/buscar")
def buscar():
    controlador = ControladorTemperaturaHumedad()
    return controlador.buscar()

@app.route("/guardar", methods=["POST"])
def guardar():
    id          = request.form["id"]
    temperatura = request.form["temperatura"]
    humedad     = request.form["humedad"]
    
    controlador = ControladorTemperaturaHumedad()
    return controlador.guardar(id, temperatura, humedad)

@app.route("/editar", methods=["GET"])
def editar():
    if not con.is_connected():
        con.reconnect()

    id = request.args["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Log, Temperatura, Humedad FROM sensor_log
    WHERE Id_Log = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/eliminar", methods=["POST"])
def eliminar():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM sensor_log
    WHERE Id_Log = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))
