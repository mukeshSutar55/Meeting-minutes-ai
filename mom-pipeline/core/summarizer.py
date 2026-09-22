import json
from groq import Groq
from config.settings import settings
from utils.logger import logger

class GroqMoMSummarizer:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.error("GROQ_API_KEY is missing in environment or config.")
            raise ValueError(
                "GROQ_API_KEY is required for MoM summarization. "
                "Please set GROQ_API_KEY in your .env file or environment variables."
            )
        
        logger.info("Initializing Groq API client for MoM summarization...")
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_mom(self, aligned_transcript: list[dict]) -> dict:
        """
        Generates structured Minutes of Meeting using Groq LLM while dynamically 
        extracting real participant names from dialogue cues.

        Args:
            aligned_transcript (list[dict]): Speaker-aligned chronological transcript.

        Returns:
            dict: JSON containing speaker_map and structured minutes_of_meeting.
        """
        if not aligned_transcript:
            logger.warning("Empty transcript received for summarization.")
            return {
                "speaker_map": {},
                "minutes_of_meeting": {
                    "summary": "No speech content detected in recording.",
                    "key_discussion_points": [],
                    "decisions_made": [],
                    "action_items": []
                }
            }

        # Format transcript into a readable timeline block
        transcript_lines = [
            f"[{seg['start']}s - {seg['end']}s] {seg['speaker']}: {seg['text']}"
            for seg in aligned_transcript
        ]
        formatted_transcript = "\n".join(transcript_lines)

        system_prompt = (
    "You are an expert executive assistant specializing in processing multilingual meeting transcripts "
    "(including English, Hindi, and Odia). Analyze the provided transcript and produce a structured "
    "Minutes of Meeting (MoM) output in English.\n\n"
    "TASK 1: Speaker Name Detection & Mapping\n"
    "- Carefully scan the transcript text for self-introductions, greetings, and direct address cues "
    '(e.g., "Hi, I\'m Samir", "Thanks Will", "This is Mukesh").\n'
    '- Create a mapping dictionary matching generic speaker IDs (e.g., "Person 1", "Person 2") to their real spoken names.\n'
    '- If a person\'s real name is not mentioned anywhere in the transcript, retain their original label (e.g., "Person 1").\n\n'
    "TASK 2: Minutes of Meeting (MoM) Extraction & Document Compliance\n"
    "- Generate Executive Summary, Key Discussion Points, Decisions Made, and Action Items.\n"
    "- Use the RESOLVED real names (e.g., Samir, Will) across all summary sections instead of generic labels.\n"
    "- Decisions Made (where identifiable):\n"
    "  * Extract formal agreements, agreed strategies, choices finalized, or consensus reached by the team.\n"
    "  * If no explicit decisions were made during the meeting, return an empty list [].\n"
    "- Action Items (where identifiable):\n"
    "  * Extract explicit tasks, follow-ups, or commitments assigned to or accepted by individuals.\n"
    "  * Extract assigned names using resolved real names. If assigned to a team or unassigned, state 'Unassigned'.\n"
    "  * Extract deadlines if explicitly stated; otherwise default to 'TBD'.\n"
    "  * If no actionable tasks or commitments were discussed, return an empty list [].\n"
    "- Translation & Tone: Ensure all non-English speech segments (Hindi, Odia) are accurately translated and synthesized into professional executive English.\n"
    "- Factuality & Grounding: Base all summary points strictly on facts present in the transcript. Do NOT hallucinate, extrapolate, or assume outside context.\n"
    "- Completeness: Retain critical technical context, numbers, deadlines, and project milestones discussed during the recording.\n\n"
    "Return a strictly formatted JSON object matching this schema:\n"
    "{\n"
    '  "speaker_map": {\n'
    '     "Person 1": "Samir",\n'
    '     "Person 2": "Will"\n'
    '  },\n'
    '  "minutes_of_meeting": {\n'
    '    "summary": "Concise executive summary of the meeting",\n'
    '    "key_discussion_points": ["Point 1", "Point 2"],\n'
    '    "decisions_made": ["Decision 1", "Decision 2"],\n'
    '    "action_items": [\n'
    '       {\n'
    '         "task": "Task description",\n'
    '         "assigned_to": "Resolved Speaker Name",\n'
    '         "deadline": "Deadline if specified, else TBD"\n'
    '       }\n'
    '    ]\n'
    '  }\n'
    "}\n\n"
    "Ensure the JSON output is strictly valid and contains no markdown formatting outside the JSON response."
)

        logger.info(f"Generating MoM and resolving speaker names via Groq API ({settings.GROQ_LLM_MODEL})...")

        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Meeting Transcript:\n{formatted_transcript}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )

            raw_content = response.choices[0].message.content
            mom_result = json.loads(raw_content)

            logger.info("MoM generation and speaker resolution completed successfully.")
            return mom_result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from LLM: {str(e)}")
            return {
                "speaker_map": {},
                "minutes_of_meeting": {
                    "summary": raw_content if 'raw_content' in locals() else "Summary generation failed.",
                    "key_discussion_points": [],
                    "decisions_made": [],
                    "action_items": []
                }
            }
        except Exception as e:
            logger.error(f"Groq LLM summarization call failed: {str(e)}")
            raise RuntimeError(f"MoM summarization failed: {str(e)}")