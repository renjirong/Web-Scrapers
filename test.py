import multiprocessing
from re import A

ret = ["hello"]

lock = multiprocessing.Lock()

def worker(n, return_dict):
    return_dict[n] = [1,[1,3,4],{"red":3}]
    



if __name__ == '__main__':
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    p1 = multiprocessing.Process(target=worker, args=(1, return_dict))
    p2 = multiprocessing.Process(target=worker, args=(2, return_dict))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(return_dict.values())  # Prints {"foo": True}