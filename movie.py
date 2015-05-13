from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import cmudict
from re import match
from operator import itemgetter


key = '463756c73f8fe8baa51ef9e4a87359ba3d34a8f1'

######## Following code lifted from http://www.slumberheart.com/things/flesch_kincaid.py

cmu = cmudict.dict()
def syllable_count(word):
	reduced = reduce(word)
	if (not len(reduced)) or (not reduced in cmu):
		return 0
	return len([x for x in list(''.join(list(cmu[reduced])[-1])) if match(r'\d', x)])

def reduce(word):
	return ''.join([x for x in word.lower() if match(r'\w', x)])

def grade_level(text):
	sentences = nltk.tokenize.sent_tokenize(text)
	totalwords = 0
	totalsyllables = 0
	totalsentences = len(sentences)
	for sentence in sentences:
		words = nltk.tokenize.word_tokenize(sentence)
		words = [reduce(word) for word in words]
		words = [word for word in words if word != '']
		totalwords += len(words)
		syllables = [syllable_count(word) for word in words]
		totalsyllables += sum(syllables)
	totalwords = float(totalwords)
	return ( # Flesh-Kincaid Grade Level formula. Thanks, Wikipedia!
			0.39 * (totalwords / totalsentences)
			+ 11.8 * (totalsyllables / totalwords)
			- 15.59 )

###Rest is mine


def getScores(movie, percentile):
	"""accepts moviename string and returns flesch kinkaid reading level scores"""

	reviews = scrapeMetaCritic(movie)
	read_scores = []

	for review in reviews:
		try:
			text = ''
			link = review['link']
			requrl = 'https://www.readability.com/api/content/v1/parser?url='+link+'&token='+key
			r = requests.get(requrl)
			content = r.json()['content']
			bs = BeautifulSoup(content)
			bs_p = bs.find_all('p')

			for paragraph in bs_p:
				x = nltk.clean_html(str(paragraph))
				if len(x) > 300:
					sent = nltk.sent_tokenize(x)
					for s in sent:
						if len(s) > 50:
							text = text + ' '+ nltk.clean_html(s)
							
					 
			
			
			glevel = grade_level(text)
			#print(text_only)
			read_scores.append(glevel)
			review['glevel'] = glevel
			read_scores.append(glevel)
			print('glevel: ')
			print(glevel)
			print('article: ')
			print(text)
		except:
			print('fail on: '+review['author'])

	num = int(round(len(read_scores)*percentile/100))
	print(num)

	adj_read_scores = sorted(read_scores)[-num:]
	
	top_reviews = []
	top_meta_score = []

	for review in reviews:

		try:
			if review['glevel'] in adj_read_scores:
				top_reviews.append(review)
				metscore = int(review['score'])
				top_meta_score.append(metscore)
				print(review)
		except:
			print('fail on '+review['author'])
	
	high_brow_score = sum(top_meta_score) / len(top_meta_score)
	print(top_meta_score)
	print(high_brow_score)


def scrapeMetaCritic(id):
	"""scrapes spefic metacritic movie and returns review URLs and scores"""

	reviews = []
	url = 'http://www.metacritic.com/movie/'+id+'/critic-reviews'
	page = createBS(url)
	main = page.find('div', {'id':'main'})
	containers = main.find_all('div', {'class': 'review_content'})
	for review in containers:
		try:
			pub_container = review.find('div', {'class': 'source'}).find('a').contents
			auth_container = review.find('div', {'class': 'author'}).find('a').contents
			score_container = review.find('div', {'class': 'movie'}).contents
			link = review.find('li', {'class': 'full_review'}).find('a')['href']
			info = {'author':auth_container[0], 'publication':pub_container[0], 'link':link, 'score':score_container[0]}
			reviews.append(info)

		except:
			pass
		
	return reviews


def createBS(url):
	"""takes URL and returns beautiful soup object"""

	header = {
	'User-Agent': 'Mozilla/5.0'
	}

	raw = requests.get(url, headers=header).text
	return BeautifulSoup(raw)


getScores('wish-i-was-here', 20)

#into-the-abyss
