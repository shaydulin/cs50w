from django.shortcuts import render, redirect

from django import forms
import markdown2
import random

from . import util
from django.urls import reverse



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def article(request, entry):
    entries = util.list_entries()
    for article in entries:
        if entry.lower() == article.lower():
            return render(request, "encyclopedia/article.html", {
                "entry": article,
                "article": markdown2.markdown(util.get_entry(article))
            })
    else:
        return render(request, "encyclopedia/apology.html", {
            "message": 'Page "' + entry + '" does not exist. <a href="' + reverse('new') + '">Create<a> a new page.'
        })

def search(request):
    
    if request.method == "POST":

        query = request.POST.get('q')
        q = query.lower()
        q_len = len(query)
        entries = []

        for entry in util.list_entries():
            if q == entry.lower():
                return redirect(f"wiki/{entry}")
            else:
                for i in range(len(entry)):
                    if entry.lower()[i:i+q_len] == q:
                        entries.append(entry)
                        break

        return render(request, "encyclopedia/search.html", {
            "query": query,
            "entries": entries
        })

    else:
        return render(request, "encyclopedia/search.html", {
            "entries": util.list_entries()
        })


def random_page(request):

    entry = random.choice(util.list_entries())
    return redirect(reverse('article', args=[entry]))


class NewForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Article'}))

def new_page(request):

    if request.method == "POST":
        form = request.POST
        for entry in util.list_entries():
            if form["title"].lower() == entry.lower():
                return render(request, "encyclopedia/apology.html", {
                    "message": 'Page <a href="' + reverse('article', args=[entry]) + '">' + entry +'<a> already exists.'
                })

        form = NewForm(form)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(reverse('article', args=[title]))

        else:
            return render(request, "encyclopedia/edit.html", {
                "title": "Create New Page",
                "action": reverse('new'),
                "form": form,
                "button": "Create"
            })

    return render(request, "encyclopedia/edit.html", {
        "title": "Create New Page",
        "action": reverse('new'),
        "form": NewForm(),
        "button": "Create"
    })


class EditForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Article'}))

def edit_page(request, entry):

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            title = entry
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(reverse('article', args=[entry]))

        else:
            return render(request, "encyclopedia/edit.html", {
                "title": "Create New Page",
                "action": reverse('edit', args=[entry]),
                "form": form,
                "button": "Create"
            })

    
    article = util.get_entry(entry)
    if article:
        form = EditForm({"content": article})
        return render(request, "encyclopedia/edit.html", {
            "title": "Edit: " + entry,
            "action": reverse('edit', args=[entry]),
            "form": form,
            "button": "Save changes"
        })
    else:
        return redirect("/new")
