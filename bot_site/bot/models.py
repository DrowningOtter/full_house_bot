import os
from time import sleep

from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User

from pika import BlockingConnection, ConnectionParameters, URLParameters
from bot_management.conf import (RABBITMQ_LOGIN, RABBITMQ_PASSWORD,
                                 RABBITMQ_QUEUE_NAME, RABBITMQ_HOST_NAME,
                                 RABBITMQ_CONNECT_RETRIES, DELAY_BETWEEN_RETRIES)

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField()
    house = models.ForeignKey('House', on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{str(self.photo)}"

@receiver(post_save, sender=User)
def create_rabbitmq_queue(sender, instance, created, **kwargs):
    if created:
        for attempt_number in range(1, RABBITMQ_CONNECT_RETRIES + 1):
            try:
                connection = BlockingConnection(URLParameters(f"amqp://{RABBITMQ_LOGIN}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_NAME}/"))
                if connection:
                    print("Successfully connected to RabbitMQ")
                    break
            except Exception as ex:
                sleep(DELAY_BETWEEN_RETRIES)
                print(ex)
                print(f"Failed to connect to RabbitMQ. Retrying...(attempt number {attempt_number})")
        else:
            print("Failed to connect... Exiting")
            return
        channel = connection.channel()
        queue_name = RABBITMQ_QUEUE_NAME + str(instance.id)
        queue = channel.queue_declare(queue_name)
        channel.queue_bind(exchange="amq.direct", queue=queue_name, routing_key=queue_name)
        connection.close()


@receiver(pre_delete, sender=Photo)
def photo_pre_delete(sender, instance, **kwargs):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.FileField()
    question = models.ForeignKey('Question', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.video}"
    

@receiver(pre_delete, sender=Video)
def video_pre_delete(sender, instance, **kwargs):
    if instance.video:
        if os.path.isfile(instance.video.path):
            os.remove(instance.video.path)


class House(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house_number = models.PositiveIntegerField()
    house_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.house_number}. {self.house_name} ({self.address})"
    
    def get_absolute_url(self):
        return reverse('bot:house-detail', args=[str(self.id)])

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_number = models.PositiveIntegerField()
    question_text = models.TextField(max_length=200)
    answer_text = models.TextField(max_length=500)
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.question_text}"
    
    def get_absolute_url(self):
        return reverse('bot:question-detail', args=[str(self.id)])


class Prompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt_name = models.CharField(max_length=100)
    prompt = models.TextField(max_length=1000)
    helper_text = models.CharField(max_length=100)

    def __str__(self):
        return f"(prompt) {self.prompt_name}"
    

class RegisteredUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tg_user_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'tg_user_id')


class AccessInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField("bot's nickname", max_length=50)
