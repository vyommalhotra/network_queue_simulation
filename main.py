from packet_queue import PacketQueue
import csv
import math
from random import random

if __name__ == "__main__":

    # #mm1, rho = 0.25 - 0.95
    file = 'mm1.csv'
    headers = ['rho', 'E[N]', 'P_IDLE']

    print("Question 3:")
    print('Format: ' + ', '.join(headers))

    #create queue and specify question number to set the appropriate rho's
    mm1_des = PacketQueue()

    #obtain the results as a list of lists 
    data = mm1_des.perform_des(question_number = 3)

    # write results to a csv
    with open(file, mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        output_writer.writerow(headers)

        for result in data:
            output_writer.writerow(result)

    print('Results written to {}'.format(file))

    #mm1, rho = 1.2
    # don't need to write csv data for this question
    headers = ['rho', 'E[N]', 'P_IDLE']

    print("Question 4:")
    print('Format: ' + ', '.join(headers))

    #create queue and specify question number to set the appropriate rho's
    #obtain the results as a list of lists 
    mm1_des = PacketQueue()
    data = mm1_des.perform_des(question_number = 4)

    #mm1k, rho = 0.5 - 1.5
    file = 'mm1k.csv'
    headers = ['K', 'rho', 'E[N]', 'P_LOSS']

    print("Question 6:")
    print('Format: ' + ', '.join(headers))

    
    #create queue and specify question number to set the appropriate rho's
    #obtain the results as a list of lists 
    #varying k values
    data = []
    for K in [10, 25, 50]:
        mm1k_des = PacketQueue(K)
        data += mm1k_des.perform_des(question_number = 6)

    #write results to csv files
    with open(file, mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        output_writer.writerow(headers)

        for result in data:
            output_writer.writerow(result)

    print('Results written to {}'.format(file))
