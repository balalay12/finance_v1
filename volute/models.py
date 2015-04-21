# -*- coding: utf-8 -*-

from django.db import models

class GetCategory(models.Manager):
    def cost_category(self):
        return self.filter(operation_type=2)

    def aern_category(self):
        return self.filter(operation_type=2)

class Category(models.Model):
    name = models.CharField(max_length=100)
    operation_type = models.IntegerField(max_length=1)
    objects = models.Manager()
    get_category = GetCategory()

    def __unicode__(self):
        return self.name

class GetMany(models.Manager):
    def earn_for_month(self, id, month):
        return self.filter(users=id, sum__gt=0, date__month=month)

    def cost_for_month(self, id, month):
        return self.filter(users=id, sum__lt=0, date__month=month)

class Many(models.Model):
    users = models.ManyToManyField('auth.User', related_name='+')
    sum = models.FloatField(verbose_name=u'Сумма')
    date = models.DateField(verbose_name=u'Дата')
    comment = models.CharField(max_length=100, verbose_name=u'Описание')
    category = models.ForeignKey(Category, verbose_name=u'Категория')
    objects = models.Manager()
    get_many = GetMany()

    def __unicode__(self):
        return u'%s %s %s %s' % (self.sum, self.date,  self.comment, self.category_id)

class Ostatok(models.Model):
    user = models.ForeignKey('auth.User')
    date = models.DateField()
    sum = models.FloatField()