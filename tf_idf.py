from math import log
from collections import Counter 
import json 


class Article:

	def __init__(self, articleID, name):
		self.articleID = articleID   # int
		self.name = name   # full url of article
		self.keywords_list = []   # list of Keyword objects contained within this article 
		self.length_of_article = 500   # 500 is a placeholder value
		self.keywords_count_dict = Counter()   # e.g. {keyword.nodeID: 2} 
									    	   # number of times each keyword appears in article
		self.keywords_tf_dict = {}   # e.g. {keyword.nodeID: 0.00667}
		self.tf_idf_scores = {}   # tf-idf score of each keyword wrt this article 

	def build_keywords_tf_dict(self):
		# TF(t) = (Number of times term t appears in a document) 
		#          / (Total number of terms in the document)
		keywords_tf_dict = {}
		for key,value in self.keywords_count_dict.items():
			keywords_tf_dict[key] = float(value)
			# keywords_tf_dict[key] = float(value / self.length_of_article)
		return keywords_tf_dict

	def compute_tf_idf_scores(self):
		# for key,value in self.keywords_tf_dict.items():
		for i in range(len(self.keywords_list)):
			# if self.keywords_list[i].nodeID == key:
			self.tf_idf_scores[self.keywords_list[i].nodeID] = float(self.keywords_tf_dict[self.keywords_list[i].nodeID] * self.keywords_list[i].idf_score)


class Keyword:

	def __init__(self, nodeID, chinese_encoding, global_num_articles):
		self.nodeID = nodeID   # int
		self.chinese_encoding = chinese_encoding 
		self.translation = "blah"
		self.articles_list = []   # list of Article objects that contain this keyword
		self.global_num_articles = global_num_articles   # total num of articles
		self.idf_score = 0

	def compute_idf_for_each_keyword(self):
		# IDF(t) = log_e(Total number of documents 
		#                 / Number of documents with term t in it)
		return log( float(self.global_num_articles / (len(self.articles_list) + 1) ))


class RatingSystem: 

	def __init__(self, articles, keywords, data_lines_list): 
		self.articles = articles   # list of Article objects
		self.keywords = keywords   # list of Keyword objects
		self.data_lines_list = data_lines_list   # list of lists containing data 
												 # index of data_lines_list is articleID 

	def find_keywords_in_articles(self):
		# for each Article, build list of Keyword objects contained within this article
		# also build frequency dictionary for each Article 
		# also build articles_list for each Keyword 
		for i in range(len(self.data_lines_list)):
			for j in range(len(self.data_lines_list[i])):
				if int(self.data_lines_list[i][j]) > 0: 
					self.articles[i].keywords_list.append(self.keywords[j])
					self.articles[i].keywords_count_dict[self.keywords[j].nodeID] += int(self.data_lines_list[i][j])
					self.keywords[j].articles_list.append(self.articles[i])

	def compute_tf_and_idf_scores(self):
		for i in range(len(self.articles)):
			self.articles[i].keywords_tf_dict = self.articles[i].build_keywords_tf_dict()
		for i in range(len(self.keywords)):
			self.keywords[i].idf_score = self.keywords[i].compute_idf_for_each_keyword()
		for i in range(len(self.articles)):
			self.articles[i].compute_tf_idf_scores() 

	def find_translations(self, something):
		return something

	def compute_aggregate_tf_idf_stats(self):
		aggregate_tf_idf = Counter()
		agg_list = []
		for i in range(len(self.articles)):
			for key in self.articles[i].tf_idf_scores.keys():
				aggregate_tf_idf[key] += self.articles[i].tf_idf_scores[key]
		for value in aggregate_tf_idf.values():
			agg_list.append(value)
		agg_list_sorted = sorted(agg_list)
		fake_median1 = agg_list_sorted[len(agg_list_sorted) // 3]
		fake_median2 = agg_list_sorted[(len(agg_list_sorted) // 3) * 2]
		return fake_median1, fake_median2, aggregate_tf_idf

	def generate_json_file_3_parents(self):
		json_3_parents_dict = {"name": "all_nodes", "children": [
								{"name": "prominent", "children": []}, 
								{"name": "average", "children": []}, 
								{"name": "low", "children": []}
								]}
		fake_median1, fake_median2, aggregate_tf_idf = self.compute_aggregate_tf_idf_stats()
		print fake_median1
		print fake_median2
		for key in aggregate_tf_idf.keys():
			markers_str = ""
			for i in range(len(self.keywords[key].articles_list)):
				markers_str += str(self.keywords[key].articles_list[i].articleID) + " "
			markers_str = markers_str.strip()
			json_dict = {"name": self.keywords[key].chinese_encoding, 
						 "value": aggregate_tf_idf[key], 
						 "translation": "blah", 
						 "markers": markers_str,
						 "circleID": ("circle_" + str(key))}
			if aggregate_tf_idf[key] >= fake_median2 and self.keywords[key].idf_score >= 2.5:
				json_3_parents_dict["children"][0]["children"].append(json_dict)
			elif aggregate_tf_idf[key] >= fake_median1 and self.keywords[key].idf_score >= 2.5:
				json_3_parents_dict["children"][1]["children"].append(json_dict)  
			elif self.keywords[key].idf_score >= 2.5:
				json_3_parents_dict["children"][2]["children"].append(json_dict)
		print len(json_3_parents_dict["children"][0]["children"])
		print len(json_3_parents_dict["children"][1]["children"])
		print len(json_3_parents_dict["children"][2]["children"])
		return json_3_parents_dict

	def generate_marker_to_circle_json(self):
		marker_to_circle_dict = {}
		for i in range(len(self.articles)):
			articleID = self.articles[i].articleID
			markerid = str(articleID)
			marker_to_circle_dict[markerid] = []
			for j in range(len(self.articles[i].keywords_list)):
				nodeID = self.articles[i].keywords_list[j].nodeID
				circleid = "circle_" + str(nodeID)
				marker_to_circle_dict[markerid].append(circleid)
		return marker_to_circle_dict



if __name__ == "__main__":

	try:
		frequency_stats = open("../../word_frequency.csv", 'r')
		top40_url = open("../../top40-url-markerid.csv", 'r')
	except IOError:
		print("Can't open input file")
		os.exit(1)

	frequency_stats_list = frequency_stats.readlines()
	top40_url_list = top40_url.readlines()
	frequency_stats.close() 
	top40_url.close() 

	# get urls list and associated markerID
	urls_markers_dict = {}
	for i in range(len(top40_url_list)):
		top40_url_list[i] = top40_url_list[i].strip().split(',')
		urls_markers_dict[top40_url_list[i][0]] = top40_url_list[i][1]
	global_num_articles = len(top40_url_list)

	# build all_keywords_list as list of chinese encodings as strings 
	all_keywords_list = []
	header_line = frequency_stats_list[0].strip().split(',')
	for i in range(1, len(header_line)):
		all_keywords_list.append(header_line[i])

	# build list of Keyword objects 
	keyword_objects_list = [] 
	for i in range(len(all_keywords_list)):
		keyword_objects_list.append(Keyword(i, all_keywords_list[i], global_num_articles))

	# build list of Article objects 
	data_lines_list = []
	article_objects_list = [] 
	filtered_data_lines_list = []
	for i in range(1, len(frequency_stats_list)): 
		data_lines_list.append(frequency_stats_list[i].strip().split(',')) 
		if data_lines_list[-1][0] in urls_markers_dict.keys(): 
			filtered_data_lines_list.append(data_lines_list[-1][1:])
			article_objects_list.append(Article(urls_markers_dict[data_lines_list[-1][0]], data_lines_list[-1][0])) 

	# initialize RatingSystem with lists of Article and Keyword objects, and only data from selected articles
	RS = RatingSystem(article_objects_list, keyword_objects_list, filtered_data_lines_list)
	RS.find_keywords_in_articles() 
	RS.compute_tf_and_idf_scores() 



	# generate json file
	mc = RS.generate_json_file_3_parents()
	out_file = open("json_3_parents.json", "w")
	print >>out_file, json.dumps(mc)
	out_file.close()


	# # count how many unique nodes there are
	# keywords_count = []
	# for i in range(len(RS.articles)):
	# 	for j in range(len(RS.articles[i].keywords_list)):
	# 		if RS.articles[i].keywords_list[j] not in keywords_count:
	# 			keywords_count.append(RS.articles[i].keywords_list[j])
	# print len(keywords_count)


	# # check quality of words 
	# sample_words0 = sorted(RS.articles[0].tf_idf_scores, key=lambda k: RS.articles[0].tf_idf_scores[k], reverse=True)
	# sample_words1 = sorted(RS.articles[1].tf_idf_scores, key=lambda k: RS.articles[1].tf_idf_scores[k], reverse=True)
	# sample_words2 = sorted(RS.articles[2].tf_idf_scores, key=lambda k: RS.articles[2].tf_idf_scores[k], reverse=True)
	# sample_words3 = sorted(RS.articles[3].tf_idf_scores, key=lambda k: RS.articles[3].tf_idf_scores[k], reverse=True)
	# sample_words4 = sorted(RS.articles[4].tf_idf_scores, key=lambda k: RS.articles[4].tf_idf_scores[k], reverse=True)

	# out_file = open("quality_check.txt","w")
	# print >>out_file, RS.articles[0].name
	# for key in sample_words0:
	# 	print >>out_file, RS.keywords[key].chinese_encoding 
	# 	print >>out_file, RS.articles[0].tf_idf_scores[key]

	# print >>out_file, RS.articles[1].name
	# for key in sample_words1:
	# 	print >>out_file, RS.keywords[key].chinese_encoding 
	# 	print >>out_file, RS.articles[1].tf_idf_scores[key]

	# print >>out_file, RS.articles[2].name
	# for key in sample_words2:
	# 	print >>out_file, RS.keywords[key].chinese_encoding 
	# 	print >>out_file, RS.articles[2].tf_idf_scores[key]

	# print >>out_file, RS.articles[3].name
	# for key in sample_words3:
	# 	print >>out_file, RS.keywords[key].chinese_encoding 
	# 	print >>out_file, RS.articles[3].tf_idf_scores[key]

	# print >>out_file, RS.articles[4].name
	# for key in sample_words4:
	# 	print >>out_file, RS.keywords[key].chinese_encoding 
	# 	print >>out_file, RS.articles[4].tf_idf_scores[key]
	# out_file.close()























