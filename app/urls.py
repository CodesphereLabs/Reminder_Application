
from django.contrib import admin
from django.urls import path
from app.views import home , login , signup , add_todo , signout , delete_todo, change_todo, load_todo_details, update_todo


urlpatterns = [
   path('' , home , name='home' ),
   path('load_todo_details/<int:id>/', load_todo_details, name='load_todo_details'),
   path('login/' ,login  , name='login'),
#    path('signup/' , signup ),
   path('signup/', signup, name='signup'),
   path('add_todo/' , add_todo, name='add_todo' ),
   path('delete-todo/<int:id>' , delete_todo ),
   path('change-status/<int:id>/<str:status>' , change_todo ),
   path('logout/' , signout ),
   path('update_todo/<int:id>/', update_todo, name='update_todo'),
]
