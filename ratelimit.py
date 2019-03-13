import requests
from time import sleep
import time


# This function determines if a query was successful or not
def bad_query(time_to_rec, r):

    # This value is to check if the response time is too long. The value could be tweaked or determined by normal
    # response times
    if time_to_rec > 20:

        return True

    elif r.status_code != 200:
        return True

    else:
        return False


# Determines the API rate limit from server output
def learn_rate_limit(url):

    while True:
        input_str = input("Do you want to reconnect the server with exponential backoff (less load for server)?\n"
                          "Choosing no will use continuous retrys (more accurate)?\n"
                          "Y/N: ")

        if input_str == "Y" or input_str == "y":
            exponential = True
            break

        elif input_str == "N" or input_str == "n":
            exponential = False
            break

        else:
            print("Y/N ?")

    # First start making queries with a constant frequency to determine the maximum number of queries in a given
    # time frame

    queries_available_ = 0
    time_frame_beg = time.time()

    while True:
        send_time = time.time()
        r = requests.get(url)
        time_to_rec = time.time() - send_time
        print(r.status_code)

        print(queries_available_)

        if bad_query(time_to_rec, r) is True or queries_available_ >= 500:
            break

        queries_available_ += 1

    # When the maximum number of queries has been reached, the given time frame should be figured out

    print("Max queries determined")
    n = 0

    while True:

        if exponential is True:
            send_time = time.time()
            r = requests.get(url)
            time_to_rec = time.time() - send_time
            print(r.status_code)
            sleep((2**n)-1)
            print("Waiting for: ", (2**n)-1, " seconds")
            if n < 63:
                n += 1

        else:
            send_time = time.time()
            r = requests.get(url)
            time_to_rec = time.time() - send_time
            print(r.status_code)
            sleep(n)
            print("Waiting: ", n, " seconds")
            n = 0.5

        if bad_query(time_to_rec, r) is False:
            break

    time_frame_ = time.time() - time_frame_beg

    print("Max number of queries: ", queries_available_)
    print("Time frame length is: ", time_frame_)

    print("Waiting for ", time_frame_, " seconds")
    sleep(time_frame_)

    return queries_available_, time_frame_


# Provides possibility for user to make requests. Requests are rate limited
def query_loop(url, queries_available_, time_frame_):

    tokens = queries_available_

    requests_list = []

    while True:

        cmd = input("Press enter to make a request or write a command: ")

        if cmd == "exit":
            return

        if cmd == "refresh":
            print("Waiting for 15 seconds")
            sleep(15)  # Program needs to wait for all the old requests to flush out. This time could be tweaked.
            tokens, time_frame_ = learn_rate_limit(url)
            requests_list = []

        if tokens > 0 and cmd == "":
            r = requests.get(url)
            send_time = time.time()
            if r.status_code == 200:
                print("")
                print("Request successful!")
                print(r.status_code)
                print("")

                tokens -= 1
                requests_list.append(send_time)

            else:
                print("")
                print("Request NOT successful!")
                print(r.status_code)
                print("")

        else:
            print("")
            print("Rate limit exceeded! Please wait.")
            print("")

        for i in range(len(requests_list) - 1, -1, -1):
            if time.time() - requests_list[i] > time_frame_ + 2:
                del requests_list[i]
                tokens += 1

        print("")
        print("Tokens available: ", tokens)


def main():

    url = input("Please enter URL and press enter: ")
    queries_available, time_frame = learn_rate_limit(url)
    query_loop(url, queries_available, time_frame)


main()

