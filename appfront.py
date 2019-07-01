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
	
	#Llamo a la funcion que analiza el archivo usando sklearn
	top_porcentajes = mlanalisis(doc)
	
	line_chart = pygal.Bar()
	line_chart.title = 'Analisis de riesgo en archivo'
	for i in range(len(resul)):
		line_chart.add(resul[i][0],resul[i][4])
	graph_data=line_chart.render()
	#graph_data=line_chart.render_table(style=True)
	
	lines_chart = pygal.Bar()
	lines_chart.title = 'Browser usage evolution (in %)'
	lines_chart.x_labels = map(str, range(2002, 2013))
	lines_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
	lines_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
	lines_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
	lines_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
	#lines_chart.value_formatter = lambda x: '%.2f%%' % x if x is not None else '0'
	
	graph_table=lines_chart.render_table(style=True)
	
	return render_template('analisis.html',resul=resul,nombrearchivo=nombrearchivo,graph_table=graph_table, graph_data=graph_data,resultadodetalle=resultadodetalle,top_porcentajes=top_porcentajes)
		
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

