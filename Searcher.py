import numpy as np
import csv
import time
import glob
import os

class Searcher:
    def __init__(self, indexPath):  # store the index path
        self.results=dict()
        self.indexPath = indexPath
        with open(self.indexPath) as f:
            # initialize the CSV reader
            SList = csv.reader(f)
            for row in SList:
                # parse out the image ID and features, then compute the
                # chi-squared distance between the features in our index
                # and our query features
                features = [float(x) for x in row[1:]]
                self.results[row[0]] = features
            f.close()

    def search(self, queryFeatures, limit=10):
        # initialize the dictionary of results
        # open the index file for reading
        # initialize the CSV reader

        # loop over rows in the index
        for key,value in self.results.items():
            print(key,value)
            d = self.chi2_distance(value, queryFeatures)

            '''
            now that we have the distance between the two feature
            vectors, we can udpate the results dictionary -- the
            key is the current image ID in the index and the
            value is the distance we just computed, representing
            how 'similar' the image in the index is to our query
            '''
            self.results[key] = d

        # close the reader
        # sort our results, so that the smaller distances (i.e. the
        # more relevant images are at the front of the list)
        results = sorted([(v, k) for (k, v) in self.results.items()])
        # return our (limited) results
        return results

    def chi2_distance(self, histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                          for (a, b) in zip(histA, histB)])

        # return the chi-squared distance
        return d
