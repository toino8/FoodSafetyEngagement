import threading
import queue
import requests
import json 

def check_proxies_and_generate_valid_list():
    # Queue for threading
    q = queue.Queue()
    valid_proxies = []

    # Load proxies into the queue
    with open('proxy_list.txt', 'r') as f:
        proxies = f.readlines()
        for proxy in proxies:
            q.put(proxy.strip())

    def check_proxies(q, valid_proxies):
        while not q.empty():
            proxy = q.get()
            try:
                res = requests.get('https://x.com/', proxies={'http': proxy, 'https': proxy}, timeout=5)
                if res.status_code == 200:
                    print(f'Valid proxy: {proxy}')
                    valid_proxies.append(proxy)
            except Exception:
                continue
            finally:
                q.task_done()

    # Start threads to check proxies
    threads = []
    for _ in range(10):
        t = threading.Thread(target=check_proxies, args=(q, valid_proxies))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    return valid_proxies

def save_proxies(proxies):
    with open('valid_proxies.txt', 'a') as f:
        for proxy in proxies:
            f.write("%s\n" % proxy)    


def double_check_proxies(proxies, url):
    counter = 0
    print("Avant doublecheck, nous avons", len(proxies), "proxies")
    while counter < len(proxies):
        try:
            res = requests.get(url, proxies={"http": proxies[counter], "https": proxies[counter]}, timeout=5)
            if res.status_code == 200:
                print(f'using the proxy {proxies[counter]} succeeded')
                counter += 1
        except Exception as e:
            print(f'using the proxy {proxies[counter]} failed')
            proxies.pop(counter)

    return proxies



def main():
    # Check and generate valid proxies
    valid_proxies = check_proxies_and_generate_valid_list()
    # Double check the valid proxies
    url = "https://x.com/"
    double_check_proxies(valid_proxies, url)
    print('On a récolté les proxies suivants: ', valid_proxies)
    # Store valid proxies in the file
    save_proxies(valid_proxies)
    

if __name__ == "__main__":
    main()
