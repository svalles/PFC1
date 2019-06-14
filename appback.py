import spacy
import tika
from spacy.matcher import Matcher
from spacy.lang.es import Spanish
from tika import parser
from tika import detector
from tika import language

def fileanalisis(f_in_tika):

	# Parseo de archivo con Tika
	tika.initVM()
	parsed = parser.from_file(f_in_tika)

	#imprimo todo el documento completo
	print(parsed["content"])

	#Entrenamiento de 10MB
	nlp = spacy.load("es_core_news_sm")
	#Entrenamiento de 70 MB
	#nlp = spacy.load("es_core_news_md")

	#Cadena de patrones tupla (nombre,patron,impacto)
	patrones = [
		#("URL",[{'LIKE_URL': True}],1),
		("EMAIL",[{'LIKE_EMAIL': True}],2),
		("IP",[{"TEXT": {"REGEX": "^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$"}}],5),
		("DNI",[{"TEXT": {"REGEX": "^\d{1,3}[.]\d{1,3}[.]\d{1,3}$"}}],10),
		("SHAREFOLDER",[{"TEXT": {"REGEX": "\\[^\\]+$"}}],10),
		("TELEFONO",[{"SHAPE": "dddd"},{"ORTH": "-"},{"SHAPE": "dddd"}],3),
		("CUIL",[{"SHAPE": "dd"},{"ORTH": "-"},{"SHAPE": "dddddddd"},{"ORTH": "-"},{"SHAPE": "d"}],9),
		]

	#Convierto los nombres a hash y armo la tabla de resultados
	resultados = []	
	#print("Patrones",patrones)

	for name,patron,impacto in patrones:
		resultados.append([name,nlp.vocab.strings[name],impacto,0])

	#print("resultados",resultados)
		
	#Procesamiento usando Spacy de la cadena de caracteres entregada por Tika
	doc = nlp(parsed["content"])

	matcher_obj = Matcher(nlp.vocab) 

	#agrego todos los patrones a buscar	
	for nombre,pat,impacto in patrones:
		matcher_obj.add(nombre,None,pat)
		
	#Me fijo cuantos patrones se cargaron
	print("Cantidad de entradas con patrones", len(matcher_obj))

	#Hago la busqueda
	#Coincidencias es hash,start,end (en el documento)
	coincidencias=matcher_obj(doc)

	#Saco el listado de matcheos
	#print("Listado de los hallazgos")
	for match_id, start, end in coincidencias:
		print('Match encontrado:', doc[start:end].text)
		
	#print("\nCoincidencias",coincidencias)

	print ("\nCantidad de tipo de elementos a buscar=",len(resultados),"\n")

	for var in range(len(coincidencias)):
		hash = coincidencias[var][0]
		for index in range(len(resultados)):
			if hash == resultados[index][1]:
				resultados[index][3]+=1


	# Entidades a buscar con nombre,hash (todos 0), impacto

	busqueda = [
		("PER",0,3),
		#("ORG",0,2),
		]

	#cargo tabla de resultados con busqueda de entidades

	for name,hash,impacto in busqueda:
		resultados.append([name,hash,impacto,0])

	#print("\nresultados2",resultados)	
	entidades = []
	#Busqueda de Named Entities

	#Imprimo las entidades encontradas según el patron de búsqueda
	for ent in doc.ents:
		for index in range(len(busqueda)):
			if ent.label_ == busqueda[index][0]:
				print(ent.text, ent.label_)
				entidades.append([ent.label_,ent.text])
			


	for ente in range(len(entidades)):
		tipo = entidades[ente][0]
		for index in range(len(resultados)):
			if tipo == resultados[index][0]:
				resultados[index][3]+=1

			
	#Imprimo los resultados finales estadisticos
	print("\nTABLA DE RESULTADOS\n")
	print("\nTIPO - CANTIDAD - RIESGO\n")
	for linea in range(len(resultados)):
		print (resultados[linea][0],resultados[linea][3],resultados[linea][2]*resultados[linea][3])
	print("\n")

	#Me fijo la cantidad de hallazgos
	print('Total de matcheos en el documento:', len(resultados))
	return