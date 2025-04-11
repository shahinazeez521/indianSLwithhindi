from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from gtts import gTTS
import os
from django.conf import settings
from googletrans import Translator

def home_view(request):
    return render(request, 'home.html')

@login_required(login_url="login")
def animation_view(request):
    if request.method == 'POST':
        text = request.POST.get('sen')
        language = request.POST.get('language', 'en')  # Default to English
        translated_text = text  # Initialize with original text

        # Translate Hindi to English
        translator = Translator()
        if language == "hi":
            try:
                translated = translator.translate(text, src='hi', dest='en')
                translated_text = translated.text.lower()
            except Exception:
                translated_text = text.lower()
        else:
            translated_text = text.lower()

        # Tokenize the translated text (English)
        words = word_tokenize(translated_text)
        tagged = nltk.pos_tag(words)

        # Tense detection
        tense = {}
        tense["future"] = len([word for word in tagged if word[1] == "MD"])
        tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
        tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
        tense["present_continuous"] = len([word for word in tagged if word[1] == "VBG"])

        # Stopwords
        stop_words = set(["mightn't", "re", "wasn", "wouldn", "be", "has", "that", "does", "shouldn", "do", "you've", "off", "for", "didn't", "m", "ain", "haven", "weren't", "are", "she's", "wasn't", "its", "haven't", "wouldn't", "don", "weren", "s", "you'd", "don't", "doesn", "hadn't", "is", "was", "that'll", "should've", "a", "then", "the", "mustn", "i", "nor", "as", "it's", "needn't", "d", "am", "have", "hasn", "o", "aren't", "you'll", "couldn't", "you're", "mustn't", "didn", "doesn't", "ll", "an", "hadn", "whom", "y", "hasn't", "itself", "couldn", "needn", "shan't", "isn", "been", "such", "shan", "shouldn't", "aren", "being", "were", "did", "ma", "t", "having", "mightn", "ve", "isn't", "won't"])

        # Lemmatization
        lr = WordNetLemmatizer()
        filtered_text = []
        for w, p in zip(words, tagged):
            if w not in stop_words:
                if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']:
                    filtered_text.append(lr.lemmatize(w, pos='v'))
                elif p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']:
                    filtered_text.append(lr.lemmatize(w, pos='a'))
                else:
                    filtered_text.append(lr.lemmatize(w))
        words = filtered_text

        # Tense adjustment
        temp = []
        for w in words:
            if w == 'i':
                temp.append('me')
            else:
                temp.append(w)
        words = temp
        probable_tense = max(tense, key=tense.get)

        if probable_tense == "past" and tense["past"] >= 1:
            temp = ["before"]
            temp = temp + words
            words = temp
        elif probable_tense == "future" and tense["future"] >= 1:
            if "will" not in words:
                temp = ["will"]
                temp = temp + words
                words = temp
        elif probable_tense == "present" and tense["present_continuous"] >= 1:
            temp = ["now"]
            temp = temp + words
            words = temp

        # Check for animation files
        final_words = []
        for w in words:
            path = w + ".mp4"
            f = finders.find(path)
            if not f:
                final_words.extend([c.lower() for c in w if c.isalpha()])
            else:
                final_words.append(w)

        # Generate TTS for Hindi
        audio_file = None
        if language == "hi":
            tts = gTTS(text=text, lang="hi", slow=False)
            audio_file = "output.mp3"
            tts.save(os.path.join(settings.MEDIA_ROOT, audio_file))
            audio_file = f"/media/{audio_file}"

        return render(request, 'animation.html', {
            'words': final_words,
            'text': text,
            'translated_text': translated_text,
            'audio': audio_file,
            'language': language
        })
    else:
        return render(request, 'animation.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('animation')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('animation')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("home")