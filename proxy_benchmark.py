# This script performs N_REQUESTS to three proxy endpoints and prints statistics.

import requests
import numpy as np
import time

# Base URL for the proxy
BASE_URL = f"http://ec2-52-23-177-186.compute-1.amazonaws.com"
N_REQUESTS = 20

# Dictionary to store statistics for different endpoints
stats = {
    "normal": {
        "responses": [],
        "times": []
    },
    "custom": {
        "responses": [],
        "times": []
    },
    "random": {
        "responses": [],
        "times": []
    }
}

def call_endpoint_http(endpoint_url):
    headers = {"content-type": "application/text"}
    start = time.time()
    r = requests.get(url=endpoint_url, headers=headers)
    return r.status_code, r.text, (time.time() - start)

def print_benchmark_stats(stats):
    def count_occurrences(word, responses):
        return sum([1 for res in responses if word in res])

    for endpoint in ["normal", "custom", "random"]:
        print(f"/{endpoint}:")
        master_occ = count_occurrences('MASTER', stats[endpoint]['responses'])
        slave_1_occ = count_occurrences('SLAVE_1', stats[endpoint]['responses'])
        slave_2_occ = count_occurrences('SLAVE_2', stats[endpoint]['responses'])
        slave_3_occ = count_occurrences('SLAVE_3', stats[endpoint]['responses'])
        total = len(stats[endpoint]['responses'])
        print(f"  TOTAL : {total}\n" +
            f"  Master : {master_occ},\n" +
            f"  Slave #1 : {slave_1_occ},\n" +
            f"  Slave #2 : {slave_2_occ},\n" +
            f"  Slave #3 : {slave_3_occ}\n" +
            "  Average request time on {} requests : {:.4f}ms".format(total, np.average(stats[endpoint]['times'])))

def make_request(endpoint):
    try:
        sc, resp, request_time = call_endpoint_http(f"{BASE_URL}/{endpoint}")
        if sc == 200:
            stats[endpoint]["responses"].append(resp)
            stats[endpoint]["times"].append(request_time)
    except Exception as e:
        print(f"An error occurred while making a request to this endpoint: {endpoint}")
        print(e)

def main():
    for i in range(N_REQUESTS):
        for endpoint in ["normal", "custom", "random"]:
            print(f"Making request #{i} to {endpoint}")
            make_request(endpoint)

    print_benchmark_stats(stats)

if __name__ == '__main__':
    main()
