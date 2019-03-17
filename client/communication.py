import pika

class Publisher():
	def publish(_self, text):
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue='translator', durable=True)

		channel.basic_publish(exchange='',
		                      routing_key='translator',
		                      body=text)

		connection.close()