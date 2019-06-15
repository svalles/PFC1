#Importación de las librerias que requiere la aplicación
import os
from flask import Flask , render_template, request,flash, redirect
from flask_bootstrap import Bootstrap
import urllib.request
from werkzeug.utils import secure_filename
from appback import fileanalisis
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
#from bokeh.charts import Bar

#Crea la instacia para el framework Flask
app = Flask(__name__)
#Creación de clave para el manejo de sesiones en Flask. No es utilizado en este aplicativo pero es necesario para que funcione.
app.secret_key = 'algun_secreto'

rutaarchivo = ''
nombrearchivo = ''


# Inicializa el framework Bootstrap
bootstrap = Bootstrap(app)

#Archivo local donde se guardan los nombres de servicios y sus claves secretas asociadas
UPLOAD_FOLDER = 'D:/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf'])

#Definición de clase para los servicios
class servicio(object):
    def __init__(self, nombre, key=None):
        self.nombre = nombre
        self.key = key
        if key is None:
            self.key = base64.b32encode(os.urandom(10)).decode('utf-8')

    def save(self):
        if len(self.nombre) < 1:
            return False

        servicios = pickle.load(open(SERVICE_FILE_NAME, 'rb'))
        if self.nombre in servicios:
            return False
        else:
            servicios[self.nombre] = self.key
            pickle.dump(servicios, open(SERVICE_FILE_NAME, 'wb'))
            return True


    @classmethod
    def get_servicio(cls, nombre):
        servicios = pickle.load(open(SERVICE_FILE_NAME, 'rb'))
        if nombre in servicios:
            return servicio(nombre, servicios[nombre])
        else:
            return None

#Routeo de páginas para Flask
#Pagina de inicio donde presenta las opciones de registrar o probar
@app.route('/')
def index():
	return render_template('index.html')
	
@app.route("/graph")
def hello():
	name = request.args.get("name")
	if name == None:
		name = "Edward"
	return render_template("probar.html", name=name)
    
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
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			rutaarchivo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			nombrearchivo = filename
			flash('Archivo subido satisfactoriamente.')
			return redirect('/')
		else:
			flash('Solo se permite archivos PDF')
			return redirect(request.url)

	
#Pagina para registrar un nuevo servicio y guardar en la base de datos
@app.route('/analisis', methods=['GET'])
def analisis():
	flash('Analizando Archivo', 'danger')
	print(nombrearchivo)
	fileanalisis(rutaarchivo)
	
	return render_template('analisis.html')
		
#Pagina de prueba de código (token) ya generado con anterioridad
@app.route('/probar', methods=['GET', 'POST'])
def probar():
    """Página para probar el TOTP"""
    if request.method == 'POST':
        s = servicio.get_servicio(request.form['nombreservicio'])
        if s is None:
            flash('Servicio no encontrado', 'danger')
            return render_template('probar.html')
        else:
            otpvalue = request.form['otp']
            if s.authenticate(otpvalue):
                flash('¡Código correcto!', 'success')
                return render_template('/probar.html', servicio=s)
            else:
                flash('Código incorrecto', 'danger')
                return render_template('probar.html')
    else:
        return render_template('probar.html')
		
		
@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("result.html",result = result)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/bokeh')
def bokeh():

    # init a basic bar chart:
    # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars
    fig = figure(plot_width=600, plot_height=600)
    fig.vbar(
        x=[1, 2, 3, 4],
        width=0.5,
        bottom=0,
        top=[1.7, 2.2, 4.6, 3.9],
        color='navy'
    )

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'grafico.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)
	
@app.route('/hola')
def hola():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)
