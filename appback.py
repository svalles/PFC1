import spacy
import tika
from spacy.matcher import Matcher
#from spacy.lang.es import Spanish
from tika import parser
from tika import detector
from tika import language

#Cadena de patrones tupla (nombre,patron,impacto)
patrones = [
		("URL",[{'LIKE_URL': True}],1),
		("EMAIL",[{'LIKE_EMAIL': True}],2),
		("IP",[{"TEXT": {"REGEX": "^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$"}}],5),
		("DNI",[{"TEXT": {"REGEX": "^\d{1,2}[.]\d{3}[.]\d{3}$"}}],50),
		("SHAREFOLDER",[{"TEXT": {"REGEX": "\\[^\\]+$"}}],10),
		("PHONE",[{"TEXT": {"REGEX": "^(1?)(-| ?)(\()?([0-9]{3})(\)|-| |\)-|\) )?([0-9]{3})(-| )?([0-9]{4}|[0-9]{4})$"}}],10),
		("CUIL",[{"SHAPE": "dd"},{"ORTH": "-"},{"SHAPE": "dddddddd"},{"ORTH": "-"},{"SHAPE": "d"}],9),
		("CREDITCARD",[{"TEXT": {"REGEX": "^((4\d{3})|(5[1-5]\d{2})|(6011))-?\d{4}-?\d{4}-?\d{4}|3[4,7]\d{13}$"}}],50)
		]

#Lista de busqueda_pln de NLP: nombre,hash, impacto
#(el hash es cero porque no es necesario para la busqueda_pln por name entity.
busqueda_pln = [
		("PERSON",0,3),
		("MONEY",0,3),
		#("PRODUCT",0,3)
		]

#Función para remover elementos duplicados de una lista
def removeDuplicates(listofElements):
    
    # Crea una lista vacia para guardar elementos únicos
    uniqueList = []
    
    # Itera sobre la lista original por cada elemento
	# Agrega a la lista destino solo los elementos nuevos 
    for elem in listofElements:
        if elem not in uniqueList:
            uniqueList.append(elem)
    
    # Retorna la lista de elementos únicos        
    return uniqueList

def fileanalisis(f_in_tika):

	global patrones
	global busqueda_pln
	
	# Tabla resultados
	# Guarda un resumen de la sumatoria de hallazgos por cada tipo econtrado
	# Tiene el formato: Nombre,hash,impacto,cant.ocurrencias,impacto
	resultados=[]
	
	# Tabla resultadodetalle
	# Guarda el detalle de cada item encontrado.
	# Tiene el formato: Tipo,dato
	resultadodetalle=[]
	
	#################################
	#Parseo de archivo con Tika
	#################################
	tika.initVM()
	parsed = parser.from_file(f_in_tika)

	#Se extrae el contenido del archivo parseado. La otra opción es extraer los metadatos del archivo
	doctika=parsed["content"]
		
	#Entrenamiento de Spacy el procesador de lenguaje natural NLP
	nlp = spacy.load('en_core_web_sm')
	# En el caso de querer probar con idioma español se debe usar la proxima linea.
	# nlp = spacy.load('es_core_new_sm')
	
	
	# Carga en la tabla resultados los elementos de "patrones". Convierto los nombres a hash
	# El impacto queda en cero ya que luego será calculado.
	for name,patron,impacto in patrones:
		resultados.append([name,nlp.vocab.strings[name],impacto,0,0])
	
	# Carga en la tabla resultados los elementos de "busqueda_pln"
	# El impacto queda en cero ya que luego será calculado.
	for name,hash,impacto in busqueda_pln:
		resultados.append([name,hash,impacto,0,0])
	
	print("\nNombre de archivo a analizar",f_in_tika)
	
	#########################################################################
	#Procesamiento usando Spacy de la cadena de caracteres entregada por Tika
	#########################################################################
	doc = nlp(parsed["content"])
	
	# Crea el objeto con todos los match 
	matcher_obj = Matcher(nlp.vocab) 
	
	#########################################################
	# busqueda_pln por expresiones Regulares (lista patrones)
	#########################################################
	#agrego todos los patrones a buscar	al objeto para que Spacy pueda buscar expresiones regulares.
	for nombre,pat,impacto in patrones:
		matcher_obj.add(nombre,None,pat)
		
	#Se realiza la busqueda
	#Guarda en la lista "Coincidencias" todos los match de las expresiones regulares.
	#El formato de la lista es hash,start,end (en el documento)
	coincidencias=matcher_obj(doc)

	#Recorre la lista de objetos encontrados y matcheo con la tabla de resultados usando el hash como id.
	#Por cada hallazgo aumenta en 1 el campo cant_ocurrencias
	for var in range(len(coincidencias)):
		hash = coincidencias[var][0]
		for index in range(len(resultados)):
			if hash == resultados[index][1]:
				#print(resultados[index][0],doc[coincidencias[var][1]:coincidencias[var][2]].text)
				resultadodetalle.append([resultados[index][0],doc[coincidencias[var][1]:coincidencias[var][2]].text])
				resultados[index][3]+=1
	
	#Quita Duplicados	
	resultadodetalle=removeDuplicates(resultadodetalle)
		
	######################################################################
	# busqueda_pln por NLP de Spacy, usando Named Entity Recognition (NER)
	######################################################################
	# Entidades a buscar con nombre,hash (todos en 0), impacto

	#Lista de entidades econtradas
	entidades = []
	
	#Imprime las entidades encontradas según lo especificado en búsqueda y agrego los hallazgos a "Entidades"
	for ent in doc.ents:
		for index in range(len(busqueda_pln)):
			if ent.label_ == busqueda_pln[index][0]:
				entidades.append([ent.label_,ent.text])
				resultadodetalle.append([ent.label_,ent.text])
	
	#Quita Duplicados
	entidades=removeDuplicates(entidades)
	
	print("\nEntidades\n")
	print(entidades)
	
	#Imprime los resultados en detalle ordenados por tipo de evento
	print("\nHallazgos en detalle")
	resultadodetalle=sorted(resultadodetalle, key=lambda item: item[0], reverse=False)
	for nombre,detalle in resultadodetalle:
		print(nombre,detalle)
	
	#Vuelve a recorrer todas las entidades econtradas y por cada hallazgo suma 1 a la tabla de resultados
	for ente in range(len(entidades)):
		tipo = entidades[ente][0]
		for index in range(len(resultados)):
			if tipo == resultados[index][0]:
				resultados[index][3]+=1

		
	#################################################################################			
	#Calculo el riesgo del archivo por medio de la formula Riesgo=Impacto * cantidad de ocurrencias			
	#################################################################################
	for resul in range(len(resultados)):
		resultados[resul][4]=resultados[resul][2]*resultados[resul][3]

	#Ordena la lista por la columna peso y la vuelve a imprimir
	resultados=sorted(resultados, key=lambda item: item[4], reverse=True)
	
	riesgoarchivo=0
	
	#Imprime los resultados finales estadisticos
	print("\nTABLA DE RESULTADOS\n")
	print("\nTIPO - IMPACTO - CANTIDAD - RIESGO\n")
	for linea in range(len(resultados)):
		print (resultados[linea][0],resultados[linea][2],resultados[linea][3],resultados[linea][4])
		riesgoarchivo += resultados[linea][4]
	print("\nRiesgo de archivo:",riesgoarchivo)
		
	#Chequea la cantidad de hallazgos
	print('Total de matcheos en el documento:', len(resultados))
	return riesgoarchivo,resultados,resultadodetalle,doctika