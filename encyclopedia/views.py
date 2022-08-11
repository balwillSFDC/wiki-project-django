from cProfile import label
from attr import attrs
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponseRedirect 
from django.urls import reverse
from django import forms
from markdown import markdown
from django.contrib import messages
import re
import os
import random
from . import util

class CreateOrEditPageForm(forms.Form):
    title = forms.CharField(
        label="Title", 
        min_length=1, 
        max_length=100,
        widget=forms.TextInput({'class': 'form-control', 'placeholder': 'Web Application'})
    )
    content = forms.CharField(
        label="Content", 
        widget=forms.Textarea(attrs={'rows': 5, 'cols':20, 'class': 'form-control', 'placeholder': '#Web Application \n \n A web application is application software that runs in a web browser...'})
    )

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki_page(request, title, edit=None):
    content = util.get_entry(title)
    form = CreateOrEditPageForm(initial={'title': title, 'content': content }) if edit else None
    
    if request.method == 'POST':
        form = CreateOrEditPageForm(request.POST)
    
        # if form is valid, then make updates to file, else return form with errors
        if form.is_valid():
            print(form.cleaned_data['content'])
            with open(rf"entries/{title}.md", "w") as file: 
                file.write(form.cleaned_data['content'])

            # if user makes update to page title, also rename the file. Else, return to wiki page
            if title != form.cleaned_data['title']:
                os.rename(rf'entries/{title}.md', rf"entries/{form.cleaned_data['title']}.md")
                return HttpResponseRedirect(reverse('wiki_page', args=[form.cleaned_data['title']]))
            else: 
                return HttpResponseRedirect(reverse('wiki_page', args=[title]))
        else: 
            return render(request, 'encyclopedia/wiki_page.html', {
                "form": form
            }) 

    else: 
        # If an entry is found, pass the title and content for the entry. Else return a 404 not found error
        if util.get_entry(title) != None: 
            return render(request, "encyclopedia/wiki_page.html", {
                "title": title,
                "content": markdown(content),
                "edit": edit,
                "form": form
            })
        else:
            return HttpResponseRedirect(reverse('error'))

def error(request):
    return render(request, 'encyclopedia/404.html')

def search(request):
    if request.method == 'POST':
        queryStr = request.POST['q']
        entries = [entry for entry in util.list_entries() if re.match(rf".*{queryStr}.*", entry, re.IGNORECASE)] 

        if len(entries) == 1: 
            # if only 1 result, display wiki page
            return HttpResponseRedirect(reverse('wiki_page', args=[entries[0]]))
        elif len(entries) > 1: 
            # else if more than 1 result, display search results
            return render(request, 'encyclopedia/search.html', {
                "entries": entries
            })
        else:
            # else return error 
            return HttpResponseRedirect(reverse('error'))
    else:
        return HttpResponseRedirect(reverse('error'))

def new_page(request):
    if request.method == 'POST': 
        form = CreateOrEditPageForm(request.POST)
        # if form is valid, attempt to create new page. Else return with errors
        if form.is_valid():
            title = form.cleaned_data['title']
            # if page already exists, return to form with error. Else, create page is it does not already exist
            if os.path.isfile(rf'entries/{title}.md'):
                messages.error(request, 'Page already exists')

                return render(request, 'encyclopedia/new_page.html', {
                    "form": form
                 }) 
            else: 
                with open(rf'entries/{title}.md', 'w') as file: 
                    file.write(form.cleaned_data['content'])
                
                messages.success(request, 'Page created successfully!')
                return HttpResponseRedirect(reverse('new_page'))
        else:
            return render(request, 'encyclopedia/new_page.html', {
                "form": form
            }) 
    else:
        return render(request, 'encyclopedia/new_page.html', {
            "form": CreateOrEditPageForm()
        }) 

def random_page(request):
    entries = util.list_entries()
    return HttpResponseRedirect(reverse('wiki_page', args=[entries[random.randrange(0, len(entries))]]))


