import pika

class Publisher():
	def publish(_self, text):
		try:
			credentials = pika.PlainCredentials('guest', 'guest')
			connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
			channel = connection.channel()

			channel.queue_declare(queue='translator', durable=True)

			channel.basic_publish(exchange='',
			                      routing_key='translator',
			                      body=text)
			connection.close()
		except Exception as e:
			print('fail to connect on RabbitMQ server: ' + str(e))
			