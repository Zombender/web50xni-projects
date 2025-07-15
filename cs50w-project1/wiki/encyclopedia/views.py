from django.contrib.messages.api import success
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from markdown import markdown
from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

class TitleView(TemplateView):
    template_name = "encyclopedia/entry.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs['entry']
        entry = util.get_entry_marksafe(title)
        if entry is None:
            raise Http404('Entrada no encontrada')
        content = entry
        context['title'] = title
        context['entry'] = content
        return context

class SearchView(TemplateView):
    template_name = "encyclopedia/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        results = []
        if query:
            results = [entry for entry in util.list_entries() if query.lower() in entry.lower()]
        context['query'] = query
        context['results'] = results
        return context

class CreateEntry(TemplateView):
    template_name = 'encyclopedia/create_entry.html'

    def post(self, request, *args, **kwargs):
        title = request.POST.get('t')
        content = request.POST.get('c')

        if util.check_existent_entry(title):
            messages.error(request, "Entry already exists")
            return self.render_to_response({
                'title': title,
                'content': content,
            })

        util.save_entry(title, content)
        messages.success(request, "Entry added succesfully")
        return redirect('entry-point', entry=title)

class EditEntry(TemplateView):
    template_name = 'encyclopedia/edit_entry.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs['entry']
        entry = util.get_entry_marksafe(title)
        if entry is None:
            raise Http404('Entrada no encontrada')
        content = entry
        context['title'] = title
        context['entry'] = content
        return context

    def post(self, request, *args, **kwargs):
        title = self.kwargs.get('entry')
        content = request.POST.get('c')
        if content.strip() == '':
            messages.error(request, "Entry content can't be empty")
            return self.render_to_response({
                'title': title,
                'content': content,
            })
        util.save_entry(title,content)
        messages.success(request, 'Entry edited succesfully')
        return redirect('entry-point', entry=title)

class RandomEntry(TemplateView):
    template_name = "encyclopedia/entry.html"
    def get(self, request, *args, **kwargs):
        entry = util.get_random_entry() #Manages IndexError
        if entry is None:
            raise Http404('There are not entries!')
        return redirect('entry-point', entry=entry)

