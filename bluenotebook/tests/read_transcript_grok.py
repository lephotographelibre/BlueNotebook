from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import Formatter
import re


class ParagraphFormatter(Formatter):
    def format_transcript(self, transcript, pause_threshold=1.0):
        """
        Formate le transcript en paragraphes en fonction des pauses et du contenu.
        :param transcript: Liste de snippets du transcript
        :param pause_threshold: Seuil de pause (en secondes) pour séparer les paragraphes
        :return: Texte formaté en paragraphes
        """
        paragraphs = []
        current_paragraph = []
        previous_end_time = 0

        for snippet in transcript:
            text = (
                snippet.text.strip()
            )  # Utiliser snippet.text au lieu de snippet["text"]
            start_time = (
                snippet.start
            )  # Utiliser snippet.start au lieu de snippet["start"]
            duration = (
                snippet.duration
            )  # Utiliser snippet.duration au lieu de snippet["duration"]
            end_time = start_time + duration

            # Ignorer les snippets vides ou contenant des annotations comme [Music]
            if not text or re.match(r"^\[.*\]$", text):
                continue

            # Calculer la pause entre ce snippet et le précédent
            pause = start_time - previous_end_time if current_paragraph else 0

            # Si pause significative ou fin de phrase, créer un nouveau paragraphe
            is_sentence_end = text.endswith((".", "!", "?"))
            if pause > pause_threshold or (is_sentence_end and current_paragraph):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []

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

# Disponibilité du transcript : Vérifiez que la vidéo (Z208NMP7_-0) a un transcript disponible dans les langues spécifiées (fr, en).

transcript_list = ytt_api.list(video_id)
for transcript in transcript_list:
    print(transcript.language, transcript.language_code)

try:
    fetched_transcript = ytt_api.fetch(
        video_id, languages=["fr", "en"], preserve_formatting=True
    )
except Exception as e:
    print(f"Erreur lors de la récupération du transcript : {e}")
    exit(1)

# Formater en paragraphes
formatter = ParagraphFormatter()
formatted_transcript = formatter.format_transcript(
    fetched_transcript, pause_threshold=1.5
)

# Afficher le résultat
print(formatted_transcript)
