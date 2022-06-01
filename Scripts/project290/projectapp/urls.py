from django.urls import path
from . import views

urlpatterns=[
path('land',views.first),
path('fieldsForm',views.fieldForm),
path('fieldsSubmit',views.fieldsSubmit),
path('xlfile',views.excelpage),
path('xcelRead',views.Decodexl),
path('onDat',views.onDatPage),
path('cropEntryPage',views.cropEntryPage),
path('reqpage',views.ReqPage),
path('fieldsEntryPage',views.fieldsEntryPage),
path('',views.landpage),
path('getxl',views.dloadxl),
]
