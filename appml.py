from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer

def train(classifier, X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)#, random_state=33)
    classifier.fit(X_train, y_train)
    print ("Accuracy: %s" % classifier.score(X_test, y_test))
    return classifier


def mlanalisis(doc):
	news = fetch_20newsgroups(subset='all')

	texto1 = ["I installed a CDROM version on my desktop. The only problem (besides the sticky tape from the CDROM floder sticking to the working side of the disk and creating a nightmare) was the SCSI driver. I have an AMI controller with cache. There is now a driver for it. A while back I installed EPROM upgrades that, I recalled, removed Adaptec emulation and added BTSCSI. AMI assured me that all I had to do was disable 32 bit support in the BIOS and install. It would default to Adaptec, they said. I could change the Config.sys later and renable 32 bit support. WRONG. Install crashed and said that the necessary driver was not on the disk. But, I immediately booted up from another partition (2.1 nstalled) and added the AMI SCSI adapter to the list of adapters in the install config.sys. I then rebooted from the install drive and it took off from where it had been. How hard, IBM, would it be to write a routine in the install process for the unser to enter the name of the unsupported driver and insert a floopy to transfer it to the hard drive? But for that, no major problems. I installed IBM Works out of curiousity and cant get the Word Processor to launch. Chris"]
	texto2 = ["We’re going to get right after it here.  No bells or whistles…In this post we are going to bring you the trends, tendencies, and story of how ALL Power Play goals were scored from the 2017-2018 NHL season.Over the course of the past year, we dove deep into what made power plays successful a season ago…and it TOOK TIME.  We watched every power play goal scored (there were 1561 of them!) and investigated different attributes and scenarios we thought were relevant to creating a successful power play.It was worth it, because the data that came back was extremely insightful into uncovering why certain teams and players were successful on the man advantage.  From both individual and team perspectives…we wanted to know who was scoring the goals, how they were scoring them…and most importantly, why they were scoring them.This is not an exclusively analytics piece…nor is it based on just the seeing eye.  Our intent was to blend the two together and give both a data-based and opinion-based view of how goals are scored on the power play.  We’ll give you the raw numbers, but we’ll also inject our opinions based on what we know and what we saw while watching the games as well."]
	texto3 = ["Dyspepsia is a term which includes a group of symptoms that come from a problem in your upper gut. The gut (gastrointestinal tract) is the tube that starts at the mouth and ends at the anus. The upper gut includes the oesophagus, stomach and duodenum.Various conditions cause dyspepsia. The main symptom is usually pain or discomfort in the upper tummy (abdomen). In addition, other symptoms that may develop include:Bloating.Belching.Quickly feeling full after eating.Feeling sick (nausea).Being sick (vomiting).Symptoms are often related to eating. Doctors used to include heartburn (a burning sensation felt in the lower chest area) and bitter-tasting liquid coming up into the back of the throat (sometimes called 'waterbrash') as symptoms of dyspepsia. However, these are now considered to be features of a condition called gastro-oesophageal reflux disease (GORD) - see below."]
	texto4 = ["Just like the title say, what part of religion, the concept as a whole, do you appreciate? I'm an atheist myself and I don't believe in any faith. Yet I just love the diversity of belief systems and myths out there. How people come up with an explanation of the world and try to understand it. And as an author, there is a wealth of interesting ideas I can draw from and play within my fantasy worlds."]
	texto5 = ["I agree with all that is written above, and will add one more:-It makes those that are gullible and those that reject fact easy to identify. If someone tells me they go to church every Sunday, (or whatever day,) I instantly learn a lot about that person. It also gives me large clues on the folks that raised the person, the community they likely grew up in etc. In short it helps me identify and label people with surprising accuracy.For instance for my work, I deal with disaster response a lot. If I get a lot of: we will pray, god will see us through this etc etc etc I instantly learn a lot how to deal with the client and even gain insight on possible avenues of attack against the client. (Someone that leaves cyber security in the hands of god, instead of talking real steps to secure their business from attack.)"]

	porcentajes = []

	trial1 = Pipeline([
		('vectorizer', TfidfVectorizer()),
		('classifier', MultinomialNB()),
	])

	#print(doc)
	#input("Press Enter to continue...")
	#doc=str(doc)
	#doc=doc.encode('unicode-escape')
	doc=[doc]
	print(doc)
		
	print("TRAIN\n")
	X_train, X_test, y_train, y_test = train_test_split(news.data, news.target, test_size=0.2)

	print("FIT\n")
	trial1.fit(X_train, y_train)

	print("SCORE DEL MODELO: ",trial1.score(X_test, y_test))

	sample_prediction_proba = trial1.predict_proba(doc)
	sample_prediction = trial1.predict(doc)

	#print("\n Prediction Proba=>",sample_prediction_proba)
	print("\n Prediction=>",sample_prediction)
	print('[%s]:\t\t' % (news.target_names[int(sample_prediction)]))

	top_porcentajes = []
	
	for porcentaje in range(0,19):
		porcentajes.append([news.target_names[porcentaje],round(sample_prediction_proba[0][porcentaje]*100,1)])

	porcentajes=sorted(porcentajes, key=lambda item: item[1], reverse=True)
		
	print("TABLA DE PORCENTAJES")
		
	for porcentaje in range(0,3):
		print(porcentajes[porcentaje])
		top_porcentajes.append(porcentajes[porcentaje])
	
	return top_porcentajes
