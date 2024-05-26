"""
Tim Gormly
05/26/2024

    The program will read through a csv file and transmit the data
    as messages to a queue on the RabbitMQ server.
"""

import pika
import sys
import webbrowser
import csv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# use to control whether or not admin page is offered to user.
# change to true to receive offer
show_offer = False

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    if show_offer:
        ans = input("Would you like to monitor RabbitMQ queues? y or n ")
        print()
        if ans.lower() == "y":
            webbrowser.open_new("http://localhost:15672/#/queues")
            print()

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """

    try:
        logging.info(f"send_message({host=}, {queue_name=}, {message=})")
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))

        # use the connection to create a communication channel
        ch = conn.channel()
        logging.info(f"connection opened: {host=}, {queue_name=}")

        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)

        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)

        # print a message to the console for the user
        logging.info(f" [x] Sent {message}")

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
        
    finally:
        # close the connection to the server
        conn.close()
        logging.info(f"connection closed: {host=}, {queue_name=}")


def load_csv(filepath):
    """
    Iterates through a csv file.  Each row is
    appended to a list that is returned by the
    function

    parameters:
    filepath (str) - meant to be a valid filepath for accessing a csv file
    """
    rows = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row['message'])
    return rows


def transmit_task_list_from_csv(csv_file='./tasks.csv', host='localhost', queue_name='task_queue3'):
    """
    Uses load_csv and send_message to transmit messages to a RabbitMQ
    server from rows in a CSV file.

    Parameters:
    csv_file (str) - this should be a filepath to a valid csv file
    """
    # load csv file into list
    task_list = load_csv(csv_file)

    # iterate over list and send each item as a message to RabbitMQ
    for task in task_list:
        send_message(host, queue_name, task)
        

# If this is the program being run, then execute the code below
if __name__ == "__main__":  

    # ask the user if they'd like to open the RabbitMQ Admin site
    offer_rabbitmq_admin_site()

    # specify file path for data source
    file_path = 'tasks.csv'

    # transmit task list
    transmit_task_list_from_csv(file_path)