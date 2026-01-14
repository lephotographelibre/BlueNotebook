# From Grok
# https://github.com/jdepoix/youtube-transcript-api
#

# Installer spacy et les modèles de langue
# pip install spacy
# python -m spacy download fr_core_news_sm
# python -m spacy download en_core_web_sm
# -------------> Resultats pas flagrands sur cete exemple --------------------------------
# --------- Solution pas retenue -----------------------------------

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import Formatter
import spacy
import re


class ParagraphFormatter(Formatter):
    def __init__(self, language="en"):
        """
        Initialise le formateur avec un modèle de langue Spacy.
        :param language: Code de langue ("fr" ou "en")
        """
        self.nlp = spacy.load(
            "fr_core_news_sm" if language == "fr" else "en_core_web_sm"
        )

    def format_transcript(self, transcript, pause_threshold=1.0, language="en"):
        """
        Formate le transcript en paragraphes en utilisant Spacy pour la détection des phrases.
        :param transcript: Liste de snippets du transcript
        :param pause_threshold: Seuil de pause (en secondes) pour séparer les paragraphes
        :param language: Langue pour l'analyse ("fr" ou "en")
        :return: Texte formaté en paragraphes
        """
        paragraphs = []
        current_paragraph = []
        previous_end_time = 0
        current_text = []

        # Concaténer les snippets pour analyse par Spacy
        for snippet in transcript:
            text = snippet.text.strip()
            start_time = snippet.start
            duration = snippet.duration
            end_time = start_time + duration

            # Ignorer les snippets vides ou contenant des annotations comme [Music]
            if not text or re.match(r"^\[.*\]$", text):
                continue

            current_text.append(text)
            pause = start_time - previous_end_time if current_paragraph else 0

            # Analyser le texte accumulé avec Spacy
            doc = self.nlp(" ".join(current_text))

            # Vérifier si le dernier snippet termine une phrase
            sentences = list(doc.sents)
            is_sentence_end = len(sentences) > 0 and sentences[
                -1
            ].text.strip().endswith((".", "!", "?"))

            # Créer un nouveau paragraphe si pause significative ou fin de phrase
            if pause > pause_threshold or (is_sentence_end and current_paragraph):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                    current_text = [text]  # Réinitialiser avec le texte courant
                else:
                    current_paragraph.append(text)
            else:
                current_paragraph.append(text)

            previous_end_time = end_time

        # Ajouter le dernier paragraphe s'il existe
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        # Joindre les paragraphes avec des sauts de ligne doubles
        return "\n\n".join(paragraphs)


# Exemple d'utilisation
video_id = "Z208NMP7_-0"

# Récupérer le transcript
ytt_api = YouTubeTranscriptApi()
try:
    fetched_transcript = ytt_api.fetch(
        video_id, languages=["fr", "en"], preserve_formatting=True
    )
except Exception as e:
    print(f"Erreur lors de la récupération du transcript : {e}")
    exit(1)

# Déterminer la langue du transcript (par exemple, prendre la première langue disponible)
transcript_list = ytt_api.list(video_id)
language = next(iter(transcript_list)).language_code[:2]  # Extrait "fr" ou "en"

# Formater en paragraphes avec Spacy
formatter = ParagraphFormatter(language=language)
formatted_transcript = formatter.format_transcript(
    fetched_transcript, pause_threshold=1.5, language=language
)

# Afficher le résultat
print(formatted_transcript)
