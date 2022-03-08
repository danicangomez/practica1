#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: daniel
"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random

N = 100
K = 10
NPROD = 3
NCONS = 3


def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage, index, data, mutex):
    mutex.acquire()
    try:
        storage[index.value] = data
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release()


def get_data(storage, index, mutex):
    mutex.acquire()
    try:
        data = storage[0]
        index.value = index.value - 1
        delay(6)
        for i in range(index.value):
            storage[i] = storage[i + 1]
        storage[index.value] = -1
    finally:
        mutex.release() 
    return data


def index_lower(storage):
    menor = None #Menor valor en todos los procesos
    index = -1 
    for i in range(NPROD):
        if storage[i][0] == -1:  
            continue
        if index == -1: # Si no han sido incializadas las variables se asignan al primer
            index = i # valor encontrado, i = 0 y el primer valor del storage del prod_0
            menor = storage[i][0]
        if storage[i][0] < menor: # Si el valor leido más pequeño que menos revaloramos 
            menor = storage[i][0] # menor y index
            index = i
    return index


def producer(storage_lista, index_lista, empty_lista, non_empty_lista, mutex_lista):  
    for j in range(N): 
        delay(6)
        empty_lista.acquire()
        add_data(storage_lista, index_lista, j, mutex_lista)
        non_empty_lista.release()
        print (f"Productor {current_process().name} almacenado {j}")
    empty_lista.acquire()
    add_data(storage_lista, index_lista, -1, mutex_lista)
    non_empty_lista.release()
    print (f"Productor {current_process().name} terminado")


def consumer(storage_lista, index_lista, empty_lista, non_empty, mutex_lista, lista_ordenada):
    num = 0
    acquire_lista = [False for i in range(NPROD)]
    delay(6)
    for k in range(N*NPROD):
        for j in range(NPROD):
            if not acquire_lista[j]:
                non_empty[j].acquire()
                acquire_lista[j] = True
        i = index_lower(storage_lista)
        acquire_lista[i] = False
        valor_consumido = get_data(storage_lista[i], index_lista[i], mutex_lista[i])
        empty_lista[i].release()
        lista_ordenada[num] = valor_consumido
        num += 1
        delay(6)
        print (f"Consumiendo {valor_consumido} del productor {i}")
        
def main():
    # Elementos de cada productor
    storage_lista = []
    index_lista = []
    non_empty_lista = []
    empty_lista = []
    mutex_lista = []
    prod_lista = []
    lista_ordenada = Array('i', N*NPROD)

    for i in range(NPROD):
        storage2 = Array('i', K)
        for i in range(K):
            storage2[i] = -1
        storage_lista.append(storage2)
        
        index_lista.append(Value('i', 0))
        non_empty_lista.append(Semaphore(0))
        empty_lista.append(BoundedSemaphore(K))
        mutex_lista.append(Lock())

    for i in range(NPROD):
        print(i)
        prod_lista.append(Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage_lista[i], index_lista[i], empty_lista[i], non_empty_lista[i], mutex_lista[i])))

    merge = Process(target=consumer,
                      name=f'cons_{i}',
                      args=(storage_lista, index_lista, empty_lista, non_empty_lista, mutex_lista, lista_ordenada))

    for p in prod_lista:
        p.start()
    merge.start()

    for p in prod_lista:
        p.join()
    merge.join()

    print (lista_ordenada[:])


if __name__ == '__main__':
    main()