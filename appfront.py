#Importación de las librerias que requiere la aplicación
import os
from flask import Flask , render_template, request,flash, redirect
from flask_bootstrap import Bootstrap
import urllib.request
from werkzeug.utils import secure_filename
from appback import fileanalisis
from appback import patrones
from appback import busqueda
from appml import mlanalisis
import pygal

#Crea la instacia para el framework Flask
app = Flask(__name__)
#Creación de clave para el manejo de sesiones en Flask. No es utilizado en este aplicativo pero es necesario para que funcione.
app.secret_key = 'algun_secreto'
# Inicializa el framework Bootstrap
bootstrap = Bootstrap(app)

#Archivo local donde se guardan los nombres de servicios y sus claves secretas asociadas
UPLOAD_FOLDER = 'D:/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf'])
rutaarchivo = ''
nombrearchivo = ''
resul = []
prueba = [5, 1.2, 'DevCode', 5, 2]

#Routeo de páginas para Flask
#Pagina de inicio donde presenta las opciones de registrar o probar
@app.route('/')
def index():
	expresiones = []
	entidadesnlp = []
	for i in range(len(patrones)):
		expresiones.append(patrones[i][0])
	
	for i in range(len(busqueda)):
		entidadesnlp.append(busqueda[i][0])
		
	return render_template('index.html',expresiones=expresiones,entidadesnlp=entidadesnlp)

   
@app.route('/', methods=['POST'])
def upload_file():
	global rutaarchivo
	global nombrearchivo
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No se seleccionó ningún archivo')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			rutaarchivo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			nombrearchivo = filename
			flash('Archivo subido satisfactoriamente.')
			return redirect('/')
		else:
			flash('Solo se permiten archivos PDF')
			return redirect(request.url)

	
#Pagina para registrar un nuevo servicio y guardar en la base de datos
@app.route('/analisis', methods=['GET'])
def analisis():
	#flash('Analizando Archivo', 'danger')
	global nombrearchivo
	resul,resultadodetalle,doc=fileanalisis(rutaarchivo)
	
	#doc = [str (item) for item in doc]
	top_porcentajes = mlanalisis(doc)
	
	line_chart = pygal.Bar()
	line_chart.title = 'Analisis de riesgo en archivo'
	for i in range(len(resul)):
		line_chart.add(resul[i][0],resul[i][4])
	graph_data=line_chart.render()
	return render_template('analisis.html',resul=resul,nombrearchivo=nombrearchivo,graph_data=graph_data,resultadodetalle=resultadodetalle,top_porcentajes=top_porcentajes)
		
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

