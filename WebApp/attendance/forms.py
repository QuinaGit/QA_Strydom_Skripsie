from django import forms

class UploadAttendanceFileForm(forms.Form):
    file = forms.FileField()

class UploadClasslistFileForm(forms.Form):
    file = forms.FileField()