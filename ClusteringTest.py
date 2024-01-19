import numpy as np
import csv
import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

inputFile = "Sandbox_file.csv"
def loadData(fileName):
    data = []
    with open(fileName, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader, None)

        for row in csv_reader:
            nativeText = row[10]
            translatedText = row[11]

            if translatedText == "-":
                data.append(nativeText)
            else:
                data.append(translatedText)

    return data

def doClusters(data):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(data)

    num_clusters = 8
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(tfidf_matrix)

    nearestDataPoints = pairwise_distances_argmin_min(kmeans.cluster_centers_, tfidf_matrix)[0]

    for cluster_num, data_index in enumerate(nearestDataPoints):
        print("Cluster " + str(cluster_num) + ":" )
        print(data[data_index])

    return kmeans.labels_

def writeNewCSVFile(clusterLabels,inputFileName):
    clusterLabels += 1
    outputFileName = "Clustered_" + inputFileName 
    frame = pandas.read_csv(inputFileName)
    frame['Cluster'] = clusterLabels
    frame.to_csv(outputFileName, index=False)

  
writeNewCSVFile(doClusters(loadData(inputFile)), inputFile)

        