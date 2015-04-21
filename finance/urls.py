from django.conf.urls import patterns, include, url
from finance import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.Main.as_view()),
    url(r'^main/$', views.Main.as_view(), name='main'),
    url(r'^earnings/$', views.EarningsList.as_view(), name='earnings'),
    url(r'^costs/$', views.CostsList.as_view(), name='costs'),
    url(r'^login/$', views.LogIn.as_view(), name='login'),
    url(r'^logout/$', views.LogOut.as_view(), name='logout'),
    url(r'^reg/$', views.Reg.as_view(), name='reg'),
    url(r'^analitycs/$', views.Analitycs.as_view(), name='analitycs'),
    url(r'^earnings/add_earnings/$', views.AddErn.as_view(), name='add_earn'),
    url(r'^costs/add_cost/$', views.AddCost.as_view(), name='add_cost'),
    url(r'^earnings/period/$', views.EarnPeriods.as_view(), name='earnings_period'),
    url(r'^costs/period/$', views.CostPeriods.as_view(), name='costs_period'),
    url(r'^costs/(?P<pk>\d+)/$', views.UpdCost.as_view(template_name='update.html', success_url='/costs/'), name='upd_cost'),
    url(r'^earnings/(?P<pk>\d+)/$', views.UpdEarn.as_view(template_name='update.html', success_url='/earnings/'), name='upd_earn'),
    url(r'^delete/(?P<pk>\d+)/$', views.Delete.as_view(template_name='delete.html', success_url='/main/'), name='delete'),
    url(r'^contact/$', views.Contact.as_view(template_name='contact.html', success_url='/main/'), name='contact'),
    url(r'^admin/', include(admin.site.urls)),
)
