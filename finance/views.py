# -*- coding: utf-8 -*-

import datetime
from django.db.models import Sum
from django.contrib import auth
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import RedirectView
from volute.models import Many
from volute.models import Category
import forms
from django.core.mail import send_mail, BadHeaderError
from settings import EMAIL_HOST_USER
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class LoggedInMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/login/')
        return super(LoggedInMixin, self).dispatch(request, *args, **kwargs)

class LogIn(FormView):
    template_name = 'login.html'
    form_class = forms.LoginForm
    success_url = '/main/'

    def form_valid(self, form):
        if form.get_user():
            auth.login(self.request, form.get_user())
            return super(LogIn, self).form_valid(form)

class LogOut(RedirectView):
    url = '/login/'

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return super(LogOut, self).get(request, *args, **kwargs)

class Reg(FormView):
    template_name = 'reg.html'
    form_class = forms.RegForm
    success_url = '/login/'

    def form_valid(self, form):
        form.save()
        return super(Reg, self).form_valid(form)

class OperationsList(LoggedInMixin, object):
    model = Many
    earn = False
    cost = False
    title = ''
    summa = {}
    form = ''

    def get_queryset(self):
        qs = Many.objects.filter(users=self.request.user.id).order_by('-date')
        return qs

    def get_context_data(self, **kwargs):
        context = super(OperationsList, self).get_context_data(**kwargs)
        context['user_username'] = self.request.user.username
        context['e'] = self.earn
        context['c'] = self.cost
        context['title'] = self.title
        context['category'] = get_category()
        if self.summa: context['summa'] = check_none(self.summa['sum__sum'])
        return context

class Main(OperationsList, ListView):
    template_name = 'main.html'
    costs_list = {}
    earnings_list = {}
    costs_sum = ''
    earns_sum = ''
    cat_sum = {}
    sum_cat_cost = {}

    def get_queryset(self):
        self.costs_list = super(Main, self).get_queryset().filter(sum__lt=0, date__month=get_month())
        self.earnings_list = super(Main, self).get_queryset().filter(sum__gt=0, date__month=get_month())
        for cat in get_category():
            s = super(Main, self).get_queryset().filter(sum__lt=0, category_id=cat.id, date__month=get_month()).aggregate(Sum('sum'))
            self.cat_sum[cat.id] = int(check_none( s['sum__sum']))
        for cat_cost in get_costs_category():
            s = super(Main, self).get_queryset().filter(sum__lt=0, category_id=cat_cost.id, date__month=get_month()).aggregate(Sum('sum'))
            self.sum_cat_cost[cat_cost.id] = int(check_none(s['sum__sum']))

    def get_context_data(self, **kwargs):
        self.costs_sum = self.costs_list.aggregate(Sum('sum'))
        self.earns_sum = self.earnings_list.aggregate(Sum('sum'))
        context = super(Main, self).get_context_data(**kwargs)
        context['costs_list'] = self.costs_list
        context['earnings_list'] = self.earnings_list
        context['costs_sum'] = int(check_none(self.costs_sum['sum__sum']))
        context['earns_sum'] = int(check_none(self.earns_sum['sum__sum']))
        context['cat'] = get_category()
        context['cat_sum'] = self.cat_sum
        context['sum_cat_cost'] = self.sum_cat_cost
        context['current_balance'] = 0
        context['user_username'] = self.request.user.username
        return context

class EarningsList(OperationsList, ListView):
    template_name = 'operation.html'
    context_object_name = 'earnings_list'
    earn = True
    title = u'Доходы'

    def get_queryset(self):
        self.summa = super(EarningsList, self).get_queryset().filter(sum__gt=0, date__month=get_month()).aggregate(Sum('sum'))
        earnings_list = super(EarningsList, self).get_queryset().filter(sum__gt=0, date__month=get_month())
        paginator = Paginator(earnings_list, 2)
        page = self.request.GET.get('page')
        try:
            earnings_list = paginator.page(page)
        except PageNotAnInteger:
            earnings_list = paginator.page(1)
        except EmptyPage:
            earnings_list = paginator.page(paginator.num_pages)
        return earnings_list
        #return super(EarningsList, self).get_queryset().filter(sum__gt=0, date__month=get_month())

class CostsList(OperationsList, ListView):
    template_name = 'operation.html'
    context_object_name = 'costs_list'
    cost = True
    title = u'Расходы'

    def get_queryset(self):
        self.summa = super(CostsList, self).get_queryset().filter(sum__lt=0, date__month=get_month()).aggregate(Sum('sum'))
        costs_list = super(CostsList, self).get_queryset().filter(sum__lt=0, date__month=get_month())
        paginator = Paginator(costs_list, 2)
        page = self.request.GET.get('page')
        try:
            costs_list = paginator.page(page)
        except PageNotAnInteger:
            costs_list = paginator.page(1)
        except EmptyPage:
            costs_list = paginator.page(paginator.num_pages)
        return costs_list
        # return super(CostsList, self).get_queryset().filter(sum__lt=0, date__month=get_month())

class Common(LoggedInMixin, object):
    model = Many
    form_class = forms.AddForm
    category_list = {}
    earn = False
    cost = False
    title = ''

    def get_form_kwargs(self):
        kwargs = super(Common, self).get_form_kwargs()
        kwargs['queryset'] = self.category_list
        return kwargs

    def form_valid(self, form):
        data = form.save(commit=False)
        if self.cost and data.sum > 0:
            data.sum *= -1
        instance = form.save(commit=True)
        instance.users.add(self.request.user.id)
        return super(Common, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(Common, self).get_context_data(**kwargs)
        context['user_username'] = self.request.user.username
        context['e'] = self.earn
        context['c'] = self.cost
        context['title'] = self.title
        return context

class AddErn(Common, CreateView):
    template_name = "add.html"
    success_url = "/earnings/"
    category_list = Category.objects.filter(operation_type=1)
    earn = True
    cost = False
    title = u'Ввод доходов'

class AddCost(Common, CreateView):
    template_name = 'add.html'
    success_url = "/costs/"
    category_list = Category.objects.filter(operation_type=2)
    earn = False
    cost = True
    title = u'Ввод расходов'

class UpdCost(Common, UpdateView):
    template_name = 'add.html'
    success_url = "/costs/"
    category_list = Category.objects.filter(operation_type=2)
    cost = True
    title = u'Ввод расходов'

class UpdEarn(Common, UpdateView):
    template_name = "add.html"
    success_url = "/earnings/"
    category_list = Category.objects.filter(operation_type=1)
    earn = True
    title = u'Ввод доходов'

class Delete(DeleteView):
    model = Many

class EarnPeriods(OperationsList, FormView):
    form_class = forms.DateForm
    template_name = 'period.html'
    earn = True

    def post(self, request):
        context = self.get_context_data()
        context['e'] = self.earn
        context['user_username'] = request.user.username
        if context['form'].is_valid():
            date_start = datetime.datetime.strptime(request.POST['date_start'], '%d.%m.%Y').date()
            date_end = datetime.datetime.strptime(request.POST['date_end'], '%d.%m.%Y').date()
            earnings_list = super(EarnPeriods, self).get_queryset().filter(date__range=(date_start, date_end), sum__gt=0)
            summa = earnings_list.aggregate(Sum('sum'))
            context['earnings_list'] = earnings_list
            context['summa'] = check_none(summa['sum__sum'])
        return super(FormView, self).render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(EarnPeriods, self).get_context_data(**kwargs)
        form = self.get_form(self.form_class)
        context['form'] = form
        return context

class CostPeriods(OperationsList, FormView):
    form_class = forms.DateForm
    template_name = 'period.html'
    cost = True

    def post(self, request):
        context = self.get_context_data()
        context['c'] = self.cost
        context['user_username'] = request.user.username
        if context['form'].is_valid():
            date_start = datetime.datetime.strptime(request.POST['date_start'], '%d.%m.%Y').date()
            date_end = datetime.datetime.strptime(request.POST['date_end'], '%d.%m.%Y').date()
            costs_list = super(CostPeriods, self).get_queryset().filter(date__range=(date_start, date_end), sum__lt=0)
            summa = costs_list.aggregate(Sum('sum'))
            context['costs_list'] = costs_list
            context['summa'] = check_none(summa['sum__sum'])
        return super(FormView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CostPeriods, self).get_context_data(**kwargs)
        form = self.get_form(self.form_class)
        context['form'] = form
        return context

class Analitycs(OperationsList, FormView):
    form_class = forms.DateForm
    template_name = 'analitycs.html'
    sum_c = {}

    def post(self, request):
        context = self.get_context_data()
        context['user_username'] = request.user.username
        if context['form'].is_valid():
            date_start = datetime.datetime.strptime(request.POST['date_start'], '%d.%m.%Y').date()
            date_end = datetime.datetime.strptime(request.POST['date_end'], '%d.%m.%Y').date()
            earn = super(Analitycs, self).get_queryset().filter(date__range=(date_start, date_end), sum__gt=0).aggregate(Sum('sum'))
            cost = super(Analitycs, self).get_queryset().filter(date__range=(date_start, date_end), sum__lt=0).aggregate(Sum('sum'))
            context['earn'] = int(check_none(earn['sum__sum']))
            context['cost'] = int(check_none(cost['sum__sum']))
            context['cat'] = get_costs_category()
            for cat in get_costs_category():
                s = super(Analitycs, self).get_queryset().filter(date__range=(date_start, date_end), sum__lt=0, category_id=cat.id).aggregate(Sum('sum'))
                self.sum_c[cat.id] = int(check_none(s['sum__sum']))
            context['sum'] = self.sum_c
        return super(FormView, self).render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(Analitycs, self).get_context_data(**kwargs)
        form = self.get_form(self.form_class)
        context['form'] = form
        return context

class Contact(LoggedInMixin, FormView):
    form_class = forms.EmailForm

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['user_username'] = self.request.user.username
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request):
        context = self.get_context_data()
        context['user_username'] = request.user.username
        if context['form'].is_valid():
            try:
                send_mail(request.POST['subj'], request.POST['text'], request.POST['email'], [EMAIL_HOST_USER])
                print('mail is send')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        return super(FormView, self).render_to_response(context)

########################################################################################################################

def get_category():
    return Category.objects.all()

def get_costs_category():
    return Category.objects.filter(operation_type=2)

def get_earns_category():
    return Category.objects.filter(operation_type=1)

def get_month():
    now_date = datetime.date.today()
    return now_date.month

def check_none(x):
    if x is None:
        x = 0
        return x
    else: return x