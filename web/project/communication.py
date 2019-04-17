import pika
from project import app

class Publisher():
	def publish(_self, text):
		try:
			credentials = pika.PlainCredentials(app.config['RABBITMQ_USER'], app.config['RABBITMQ_PASSWORD'])
			connection = pika.BlockingConnection(pika.ConnectionParameters(host=app.config['RABBITMQ_HOST'], credentials=credentials))
			channel = connection.channel()

			channel.queue_declare(queue=app.config['RABBITMQ_QUEUE_NAME'], durable=True)

			channel.basic_publish(exchange='',
			                      routing_key=app.config['RABBITMQ_QUEUE_NAME'],
			                      body=text)
			connection.close()
		except Exception as e:
			print('fail to connect on RabbitMQ server: ' + str(e))
			