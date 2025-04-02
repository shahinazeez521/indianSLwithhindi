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
from indicnlp.tokenize import indic_tokenize
from gtts import gTTS
import os
from django.conf import settings

# Hindi to animation filename mapping
HINDI_ANIMATION_MAP = {
    "नमस्ते": "hello",
    "मेरा":"my",
    "नाम": "name",
    "हाँ": "yes",
    "नहीं": "no",
    "धन्यवाद": "thank you",
    "कृपया": "please",
    "माफ़कीजिए": "sorry",
    "मदद": "help",
    "प्यार": "love",
    "मित्र": "friend",
    "माता": "mother",
    "पिता": "father",
    "पानी": "water",
    "भोजन": "food",
    "खुश": "happy",
    "दुखी": "sad",
    "गुस्सा": "angry",
    "सोना": "sleep",
    "खाना": "eat",
    "पीना": "drink",
    "रुको": "stop",
    "जाओ": "go",
    "आओ": "come",
    "बैठो": "sit",
    "खड़े हो": "stand",
    "चलो": "walk",
    "दौड़ो": "run",
    "पढ़ो": "read",
    "लिखो": "write",
    "क्यों": "why",
    "क्या": "what",
    "कहाँ": "where",
    "कौन": "who",
    "कैसे": "how",
     "बाद": "after",
    "फिर से": "again",
    "के खिलाफ": "against",
    "उम्र": "age",
    "सभी": "all",
    "अकेला": "alone",
    "भी": "also",
    "और": "and",
    "पूछना": "ask",
    "पर": "at",
    "सुंदर": "beautiful",
    "पहले": "before",
    "सर्वश्रेष्ठ": "best",
    "बेहतर": "better",
    "व्यस्त": "busy",
    "लेकिन": "but",
    "अलविदा": "bye",
    "सकता है": "can",
    "बदलाव": "change",
    "कॉलेज": "college",
    "आओ": "come",
    "कंप्यूटर": "computer",
    "दिन": "day",
    "दूरी": "distance",
    "मत करो": "do not",
    "खाना": "eat",
    "इंजीनियर": "engineer",
    "लड़ाई": "fight",
    "समाप्त": "finish",
    "से": "from",
    "अच्छा": "good",
    "हाथ": "hand",
    "खुश": "happy",
    "उसकी": "her",
    "यहाँ": "here",
    "घर": "home",
    "भाषा": "language",
    "हँसना": "laugh",
    "तुम": "you",
    "तुम्हारा": "your",
    "दुनिया": "world",
    "क्या": "what",
    "कब": "when",
    "कहाँ": "where",
    "कौन सा": "which",
    "कौन": "who",
    "क्यों": "why",
    "करेंगे": "will",
    "के साथ": "with",
    "बिना": "without",
    "काम": "work",
    "अ": "a",
    "आ": "a a",
    "इ": "i",
    "ई": "i i",
    "उ": "u",
    "ऊ": "u u",
    "ए": "e",
    "ऐ": "a i",
    "ओ": "o",
    "औ": "a u",
    "अं": "a n",
    "अः": "a h",
   "क": "k a",
    "ख": "k h a",
    "ग": "g a",
    "घ": "g h a",
    "ङ": "n g a",
    "च": "c h a",
    "छ": "c h h a",
    "ज": "j a",
    "झ": "j h a",
    "ञ": "n y a",
    "ट": "t a",
    "ठ": "t h a",
    "ड": "d a",
    "ढ": "d h a",
    "ण": "n a",

    "त": "ta",
    "थ": "t h a",
    "द": "d a",
    "ध": "d h a",
    "न": "n a",
    "प": "p a",
    "फ": "fa",
    "ब": "b a",
    "भ": "b h a",
    "म": "m a",
    "य": "y a",
    "र": "r a",
    "ल": "l a",
    "व": "v a",   
    "श":"s h a",
    "ष": "s h a",
    "स": "s a",
    "ह": "h a",
    "शब्द": "words",
    "दुनिया": "world",
    "एक्स-रे": "X-ray",
    "वाई": "Y",
    "तुम": "you",
    "आपका": "your",
    "खुद": "yourself"
}

def home_view(request):
    return render(request, 'home.html')

@login_required(login_url="login")
def animation_view(request):
    if request.method == 'POST':
        text = request.POST.get('sen')
        language = request.POST.get('language', 'en')  # Default to English

        # Tokenize based on language
        if language == "hi":  # Hindi
            words = indic_tokenize.trivial_tokenize(text, lang="hi")
            tagged = [(w, 'NN') for w in words]  # Simplified POS tagging for Hindi
        else:  # English
            text = text.lower()
            words = word_tokenize(text)
            tagged = nltk.pos_tag(words)

        # Tense detection (English only, Hindi will skip this for simplicity)
        tense = {}
        if language == "en":
            tense["future"] = len([word for word in tagged if word[1] == "MD"])
            tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
            tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
            tense["present_continuous"] = len([word for word in tagged if word[1] == "VBG"])
        else:
            tense = {"present": 1}  # Default for Hindi

        # Stopwords (English only)
        stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've", 'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have', 'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])

        # Lemmatization (English only, Hindi skips this)
        lr = WordNetLemmatizer()
        filtered_text = []
        if language == "en":
            for w, p in zip(words, tagged):
                if w not in stop_words:
                    if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']:
                        filtered_text.append(lr.lemmatize(w, pos='v'))
                    elif p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']:
                        filtered_text.append(lr.lemmatize(w, pos='a'))
                    else:
                        filtered_text.append(lr.lemmatize(w))
        else:
            filtered_text = words  # Hindi skips lemmatization

        # Tense adjustment (English only)
        words = filtered_text
        temp = []
        if language == "en":
            for w in words:
                if w == 'I':
                    temp.append('Me')
                else:
                    temp.append(w)
            words = temp
            probable_tense = max(tense, key=tense.get)

            if probable_tense == "past" and tense["past"] >= 1:
                temp = ["Before"]
                temp = temp + words
                words = temp
            elif probable_tense == "future" and tense["future"] >= 1:
                if "Will" not in words:
                    temp = ["Will"]
                    temp = temp + words
                    words = temp
            elif probable_tense == "present" and tense["present_continuous"] >= 1:
                temp = ["Now"]
                temp = temp + words
                words = temp

        # Map Hindi words to animation filenames
        if language == "hi":
            words = [HINDI_ANIMATION_MAP.get(w, w) for w in words]

        # Check for animation files and split if not found
        filtered_text = []
        for w in words:
            path = w + ".mp4"
            f = finders.find(path)
            if not f:
                for c in w:
                    filtered_text.append(c)
            else:
                filtered_text.append(w)
        words = filtered_text

        # Generate TTS for Hindi
        audio_file = None
        if language == "hi":
            tts = gTTS(text=text, lang="hi", slow=False)
            audio_file = "output.mp3"
            tts.save(os.path.join(settings.MEDIA_ROOT, audio_file))
            audio_file = f"/media/{audio_file}"

        return render(request, 'animation.html', {
            'words': words,
            'text': text,
            'audio': audio_file,
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