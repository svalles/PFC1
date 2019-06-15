import spacy
import tika
from spacy.matcher import Matcher
from spacy.lang.es import Spanish
from tika import parser
from tika import detector
from tika import language

#Cadena de patrones tupla (nombre,patron,impacto)
patrones = [
		("URL",[{'LIKE_URL': True}],1),
		("EMAIL",[{'LIKE_EMAIL': True}],2),
		("IP",[{"TEXT": {"REGEX": "^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$"}}],5),
		("DNI",[{"TEXT": {"REGEX": "^\d{1,3}[.]\d{1,3}[.]\d{1,3}$"}}],10),
		("SHAREFOLDER",[{"TEXT": {"REGEX": "\\[^\\]+$"}}],10),
		("TELEFONO",[{"SHAPE": "dddd"},{"ORTH": "-"},{"SHAPE": "dddd"}],3),
		("CUIL",[{"SHAPE": "dd"},{"ORTH": "-"},{"SHAPE": "dddddddd"},{"ORTH": "-"},{"SHAPE": "d"}],9),
		]

#Lista de busqueda de NLP: nombre,hash, impacto
#(el hash es cero porque no es necesario para la busqueda por name entity.
busqueda = [
		("PER",0,3),
		#("ORG",0,2),
		]


def fileanalisis(f_in_tika):

	global patrones
	global busqueda
	
	#Tabla donde quedan los resultados finales
	# Tiene el formato: Nombre,hash,impacto,cant.ocurrencias,impacto
	resultados=[]
	
	#################################
	#Parseo de archivo con Tika
	#################################
	tika.initVM()
	parsed = parser.from_file(f_in_tika)

	#imprimo todo el documento completo
	#print(parsed["content"])

	#Entrenamiento de 10MB para Spacy el procesador de lenguaje natural NLP
	nlp = spacy.load("es_core_news_sm")
	#Entrenamiento de 70 MB
	#nlp = spacy.load("es_core_news_md")
	
	# Cargo en la tabla resultados los elementos de "patrones". Convierto los nombres a hash
	# El impacto queda en cero ya que luego será calculado.
	for name,patron,impacto in patrones:
		resultados.append([name,nlp.vocab.strings[name],impacto,0,0])
	
	# Cargo en la tabla resultados los elementos de "busqueda"
	# El impacto queda en cero ya que luego será calculado.
	for name,hash,impacto in busqueda:
		resultados.append([name,hash,impacto,0,0])
	
	print("RESUL",resultados,"\n")
	print ("\nCantidad de tipo de elementos a buscar=",len(resultados),"\n")
	
	###############################
	#Procesamiento usando Spacy de la cadena de caracteres entregada por Tika
	#################################
	doc = nlp(parsed["content"])
	
	# Creo el objeto con todos los match 
	matcher_obj = Matcher(nlp.vocab) 
	
	##################################################
	# Busqueda por expresiones Regulares
	###################################################
	#agrego todos los patrones a buscar	al objeto para que Spacy pueda buscar expresiones regulares.
	for nombre,pat,impacto in patrones:
		matcher_obj.add(nombre,None,pat)
		
	#Me fijo cuantos patrones se cargaron
	print("Cantidad de entradas con patrones", len(matcher_obj))

	#Hago la busqueda
	#Guardo en la lista "Coincidencias" todos los match de las expresiones regulares, el formato de la lista es hash,start,end (en el documento)
	coincidencias=matcher_obj(doc)

	#Saco el listado de matcheos
	#print("Listado de los hallazgos") por expresiones regulares
	for match_id, start, end in coincidencias:
		print('Match encontrado:', doc[start:end].text)
	
	#Recorro la lista de objetos encontrados y matcheo con la tabla de resultados usando el hash como id. Por cada hallazgo aumento en 1 el campor cant_ocurrencias
	for var in range(len(coincidencias)):
		hash = coincidencias[var][0]
		for index in range(len(resultados)):
			if hash == resultados[index][1]:
				resultados[index][3]+=1

	##################################################
	# Busqueda por NLP de Spacy, usando name entitys
	###################################################
	# Entidades a buscar con nombre,hash (todos 0), impacto

	#Lista de entidades econtradas
	entidades = []
	
	#Imprimo las entidades encontradas según lo especificado en búsqueda y agrego los hallazgos a "Entidades"
	for ent in doc.ents:
		for index in range(len(busqueda)):
			if ent.label_ == busqueda[index][0]:
				print(ent.text, ent.label_)
				entidades.append([ent.label_,ent.text])
	

	#Vuelvo a recorrer todas las entidades econtradas y por cada hallazgo sumo 1 a la tabla de resultados
	for ente in range(len(entidades)):
		tipo = entidades[ente][0]
		for index in range(len(resultados)):
			if tipo == resultados[index][0]:
				resultados[index][3]+=1

		
	#################################################################################			
	#Calculo el IOC por medio de la formula IOC=Impacto * cantidad de ocurrencias			
	#################################################################################
	for resul in range(len(resultados)):
		resultados[resul][4]=resultados[resul][2]*resultados[resul][3]

	#Ordeno la lista por la columna peso y la vuelvo a imprimir
	resultados=sorted(resultados, key=lambda item: item[4], reverse=True)
	
	#Imprimo los resultados finales estadisticos
	print("\nTABLA DE RESULTADOS\n")
	print("\nTIPO - IMPACTO - CANTIDAD - RIESGO\n")
	for linea in range(len(resultados)):
		print (resultados[linea][0],resultados[linea][2],resultados[linea][3],resultados[linea][4])
	print("\n")
		
	#Me fijo la cantidad de hallazgos
	print('Total de matcheos en el documento:', len(resultados))
	return