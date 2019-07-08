from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer

#Función para entrenar el modelo
def train(classifier, X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)#, random_state=33)
    classifier.fit(X_train, y_train)
    print ("Accuracy: %s" % classifier.score(X_test, y_test))
    return classifier

#Función que realizar la predicción en base al documento recibido y retorna los porcentajes de categorias
def mlanalisis(doc):
	
	#Crea el objeto en base al set de datos 20 news group
	news = fetch_20newsgroups(subset='all')

	#Matriz auxiliar para los resultados de las categorias.
	porcentajes = []
	#Matriz donde se retornan los 3 porcentajes de coincidencias más altos.
	top_porcentajes = []

	trial1 = Pipeline([
		('vectorizer', TfidfVectorizer()),
		('classifier', MultinomialNB()),
	])

	#Transformación del texto para que puedar ser analizado por el modelo
	doc=[doc]
	
	#Se entrena en el modelo
	print("TRAIN\n")
	X_train, X_test, y_train, y_test = train_test_split(news.data, news.target, test_size=0.2)
	print("FIT\n")
	trial1.fit(X_train, y_train)
	#Imprime el resultado del entrenamiento para medir el modelo.
	print("SCORE DEL MODELO: ",trial1.score(X_test, y_test))
	
	# Se hace la predicción del documento recibido
	sample_prediction_proba = trial1.predict_proba(doc)
	sample_prediction = trial1.predict(doc)
	
	# Se crea la matriz auxiliar de la predicción en base a las categorias.
	for porcentaje in range(0,19):
		porcentajes.append([news.target_names[porcentaje],round(sample_prediction_proba[0][porcentaje]*100,1)])
		
	# Se ordena la tabla.
	porcentajes=sorted(porcentajes, key=lambda item: item[1], reverse=True)
		
	print("TABLA DE PORCENTAJES")
	
	# Se crea la tabla con solo las 3 categorias con más poercentajes.	
	for porcentaje in range(0,3):
		print(porcentajes[porcentaje])
		top_porcentajes.append(porcentajes[porcentaje])
	
	return top_porcentajes
