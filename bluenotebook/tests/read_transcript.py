# From doc: https://github.com/jdepoix/youtube-transcript-api
# Test Video: https://www.youtube.com/watch?v=S2TUommS3O0 --> ID = "S2TUommS3O0"
# 2nd Yann Le Cun https://www.youtube.com/watch?v=Z208NMP7_-0 --> ID = "Z208NMP7_-0"
#
# Pre-requisite:
#   pip install youtube-transcript-api


from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from youtube_transcript_api.formatters import PrettyPrintFormatter


video_id = "Z208NMP7_-0"

ytt_api = YouTubeTranscriptApi()
# fetched_transcript = ytt_api.fetch("S2TUommS3O0")
# fetched_transcript = ytt_api.fetch("S2TUommS3O0", languages=["fr", "en"])
print(f"-- Start -- ")
fetched_transcript = ytt_api.fetch(
    video_id, languages=["fr", "en"], preserve_formatting=True
)

""# is iterable
for snippet in fetched_transcript:
    print(snippet.text)
print(f"-- End -- ")

# indexable
last_snippet = fetched_transcript[-1]
print(f"last_snippet = {last_snippet}")""


# provides a length
print(f"-- Count -- ")
snippet_count = len(fetched_transcript)
print(f"snippet_count = {snippet_count}")


print(f"-- List available transcripts -- ")
transcript_list = ytt_api.list(video_id)
print(transcript_list)
print(f"-- End List available transcripts -- ")

print(f"-- PrettyPrintFormatter -- ")
fetched_transcript = ytt_api.fetch(
    video_id, languages=["fr", "en"], preserve_formatting=True
)
formatter = PrettyPrintFormatter()
formatted_transcript = formatter.format_transcript(fetched_transcript)
print(formatted_transcript)
print(f"-- End PrettyPrintFormatter -- ")
