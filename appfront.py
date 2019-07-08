#Importación de las librerias que requiere la aplicación
import os
from flask import Flask , render_template, request,flash, redirect, session
from flask_bootstrap import Bootstrap
import urllib.request
from werkzeug.utils import secure_filename
from appback import fileanalisis
from appback import patrones
from appback import busqueda_pln
from appml import mlanalisis
import pygal
from flask_login import login_required,LoginManager,UserMixin

#Crea la instacia para el framework Flask
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#Creación de clave para el manejo de sesiones en Flask. No es utilizado en este aplicativo pero es necesario para que funcione.
app.secret_key = 'algun_secreto'
# Inicializa el framework Bootstrap
bootstrap = Bootstrap(app)

#Archivo local donde se guardan los nombres de servicios y sus claves secretas asociadas
UPLOAD_FOLDER = 'D:/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf','xls','xlsx','doc'])
rutaarchivo = ''
nombrearchivo = ''
resul = []

@app.route('/login')
def login():
	return render_template('login.html')

#Routeo de páginas para Flask
#Pagina de inicio donde presenta las opciones de registrar o probar
@app.route('/')
def index():
	expresiones = []
	entidadesnlp = []
	
#	if 'email' in session:
#		username = session['email']
#		return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to logout</a></b>"
#	return "You are not logged in <br><a href = '/login'></b>" + "click here to login</b></a>"
	
	
	for i in range(len(patrones)):
		expresiones.append(patrones[i][0])
	
	for i in range(len(busqueda_pln)):
		entidadesnlp.append(busqueda_pln[i][0])
		
	return render_template('index.html',expresiones=expresiones,entidadesnlp=entidadesnlp)

   
@app.route('/', methods=['POST'])
def upload_file():
	global rutaarchivo
	global nombrearchivo
	if request.method == 'POST':
        # Verifica que el request tenga el archivo
		if 'file' not in request.files:
			flash('No fue informado un archivo')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No se seleccionó un archivo',category='warning')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			rutaarchivo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			nombrearchivo = filename
			flash('Archivo subido satisfactoriamente.',category='success')
			return redirect('/')
		else:
			flash('Solo se permiten archivos de tipo: pdf, doc, docx, xls, xlsx',category='danger')
			return redirect(request.url)

	
#Pagina para registrar un nuevo servicio y guardar en la base de datos
@app.route('/analisis', methods=['GET'])
def analisis():
	
	global nombrearchivo
	resul,resultadodetalle,doc=fileanalisis(rutaarchivo)
	
	#Llamo a la funcion que analiza el archivo usando sklearn
	top_porcentajes = mlanalisis(doc)
	
	line_chart = pygal.Bar(height=300)
	line_chart.title = 'Analisis de riesgo en archivo'
	
	for i in range(len(resul)):
		line_chart.add(resul[i][0],resul[i][4])
	
	graph_data=line_chart.render()
	line_chart.render_to_file('../Documents/GitHub/PFC1/static/chart.svg') 
		
	return render_template('analisis.html',resul=resul,nombrearchivo=nombrearchivo, graph_data=graph_data,resultadodetalle=resultadodetalle,top_porcentajes=top_porcentajes)
		
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

