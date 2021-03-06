#!/usr/bin/env python

import sys
import networkx as nx
import createGraph
from numpy import array
from scipy.cluster.vq import kmeans, kmeans2, vq
from numpy.random import rand
from pylab import plot, show
import cPickle as pickle
import random

# Cluster into 10 groups
K = 20
MAX_ITERATIONS = 20
OUTPUT_DIR = 'output/'
DATA_DIR = 'data/'
WEIGHTED = False
colors = [
    'or', # Red
    'og', # Green
    'ob', # Blue
    'oy', # Yellow
    'ok', # Black
    'om', # Magenta
    'oc', # Cyan
    'ow', # White
    ]

def writeToFile(communities, weighted):
    with open(OUTPUT_DIR + weighted + "_communities_jaccard_kmeans.txt", 'w+') as f:
        for node in communities:
            f.write(node + ',' + str(communities[node]) + '\n')

def run():

    global K, colors

    papers = pickle.load(open(DATA_DIR + "papers_dict.p", "rb"))
    print "Constructing graph..."
    G = createGraph.loadGraph(weighted=('w' if WEIGHTED else 'uw'))
    print "Completed"
    nodes_list = G.nodes()

    # Pick any K random nodes as the centroids
    centroids = random.sample(nodes_list, K)

    iteration_no = 0

    print "Running K-means..."

    while True:

        # Termination condition
        if iteration_no == MAX_ITERATIONS:
            break
        
        # One cluster for every centroid
        clusters = [[] for no in xrange(0, K)]

        for node in nodes_list:
            idx = 0
            # Cluster index
            c_idx = 0
            max_jacc = 0.0

            # Find closest centroid            
            for c in centroids:
                # Neighbours of node
                n_node = nx.all_neighbors(G, node)
                # Neighbours of centroid
                n_c = nx.all_neighbors(G, c)
                val1 = len(set(n_node).intersection(n_c))
                val2 = len(set(n_node).union(n_c))
                # Calculate Jaccard similarity
                # Include the node and centroid in the union
                jacc = float(val1)/(val2 + 2.0)
                if jacc >= max_jacc:
                    c_idx = idx
                    max_jacc = jacc
                idx += 1
    
            # Append node to the cluster
            clusters[c_idx].append(node)
       
        # Add centroids to respective clusters
        for no in xrange(0, len(centroids)):
            if centroids[no] not in clusters[no]:
                clusters[no].append(centroids[no])
 
        centroids = []

        # Formed our cluster, find new set of centroid points
        for cluster in clusters:
            # Choose the node with most neighbours as new centroid ?
            max_edges = 0
            new_centroid = None
            for node in cluster:
                no_of_edges = len(list(nx.all_neighbors(G, node)))
                if no_of_edges >= max_edges:
                    new_centroid = node
                    max_edges = no_of_edges

            if new_centroid == None:
                # Do this ?
                # Should never happen
                sys.stderr.write("One of the clusters was empty. Please restart\n")
                sys.exit(2)
            else:
                centroids.append(new_centroid)

        iteration_no += 1
        print "Completed Iteration " + str(iteration_no)

    print "K-Means completed."
    print "Storing communities!"
    partition = {}
    cNo = 0
    for cluster in clusters:
        print "Cluster " + str(cNo)
        for node in cluster:
            partition[node] = cNo
        cNo += 1

    writeToFile(partition, weighted=('w' if WEIGHTED else 'uw'))

if __name__ == "__main__":
    run()
