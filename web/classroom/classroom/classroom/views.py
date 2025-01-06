import json
import os
from wsgiref.util import FileWrapper
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.core import exceptions
from django.http import HttpResponse, Http404
from django.conf import settings
from django.db.models import F
from . import models

class RequireLoginMixin(object):
    login_url = reverse_lazy('students:login')

    def handle_no_permission(self):
        return redirect(self.login_url)

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('is_login', None) != True:
            return self.handle_no_permission()
        return super(RequireLoginMixin, self).dispatch(request, *args, **kwargs)

class JsonResponseMixin(object):

    def _jsondata(self, msg, status_code=200):
        return JsonResponse({'message': msg}, status=status_code)

class LoginView(JsonResponseMixin, generic.TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        stu = models.Student.objects.filter(**data).first()
        if not stu or stu.passkey != data['passkey']:
            return self._jsondata('', 403)
        else:
            request.session['is_login'] = True
            return self._jsondata('', 200)

class LogoutView(RequireLoginMixin, JsonResponseMixin, generic.RedirectView):
    url = reverse_lazy('students:login')

    def get(self, request, *args, **kwargs):
        request.session.flush()
        return super(LogoutView, self).get(request, *args, **kwargs)

class IndexView(RequireLoginMixin, JsonResponseMixin, generic.TemplateView):
    template_name = 'index.html'

    def post(self, request, *args, **kwargs):
        ret = []
        for group in models.Group.objects.all():
            ret.append(dict(name=group.name, information=group.information, created_time=group.created_time, members=list(group.student_set.values('name', 'id').all())))

        return self._jsondata(ret, status_code=200)

class StaticFilesView(generic.View):
    content_type = 'text/plain'

    def get(self, request, *args, **kwargs):
        filename = self.kwargs['path']
        filename = os.path.join(settings.BASE_DIR, 'students', 'static', filename)
        name, ext = os.path.splitext(filename)
        if ext in ('.py', '.conf', '.sqlite3', '.yml'):
            raise exceptions.PermissionDenied('Permission deny')
            try:
                return HttpResponse(FileWrapper(open(filename, 'rb'), 8192), content_type=self.content_type)
            except BaseException as e:
                raise Http404('Static file not found')
