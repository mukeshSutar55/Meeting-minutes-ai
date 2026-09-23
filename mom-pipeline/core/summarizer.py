import json
import re
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

    def _clean_json_string(self, text: str) -> str:
        """Removes Markdown code blocks or wrapping quotes to ensure clean JSON parsing."""
        text = text.strip()
        # Remove ```json ... ``` code fence if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\n?```$", "", text)
        return text.strip()

    def generate_mom(self, aligned_transcript: list[dict]) -> dict:
        """
        Generates structured Minutes of Meeting using Groq LLM while dynamically 
        extracting real participant names from dialogue cues.
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
            "You are an executive assistant processing meeting transcripts "
            "(including English, Hindi, and Odia). Output the final result strictly as a valid JSON object.\n\n"
            "TASK 1: Speaker Name Detection & Mapping\n"
            "- Scan transcript text for introductions, greetings, and name cues.\n"
            "- Map generic IDs (e.g., 'Person 1') to real names (e.g., 'Samir'). If unnamed, retain original ID.\n\n"
            "TASK 2: Minutes of Meeting (MoM) Extraction\n"
            "- Provide summary, key_discussion_points, decisions_made, and action_items.\n"
            "- Use resolved real names across all summary fields.\n"
            "- Action items must contain: 'task', 'assigned_to', and 'deadline' ('TBD' if unstated).\n"
            "- Translate Hindi/Odia segments into professional English.\n"
            "- Do NOT hallucinate or assume facts outside the transcript.\n\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "speaker_map": {"Person 1": "Samir"},\n'
            '  "minutes_of_meeting": {\n'
            '    "summary": "Executive summary...",\n'
            '    "key_discussion_points": ["Point 1"],\n'
            '    "decisions_made": ["Decision 1"],\n'
            '    "action_items": [{"task": "Task", "assigned_to": "Samir", "deadline": "TBD"}]\n'
            '  }\n'
            "}"
        )

        user_prompt = f"Extract the MoM from this transcript into valid JSON format:\n\n{formatted_transcript}"

        logger.info(f"Generating MoM and resolving speaker names via Groq API ({settings.GROQ_LLM_MODEL})...")

        raw_content = ""
        try:
            # Primary Call: Strict JSON Object Mode
            response = self.client.chat.completions.create(
                model=settings.GROQ_LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw_content = response.choices[0].message.content
            cleaned_json = self._clean_json_string(raw_content)
            mom_result = json.loads(cleaned_json)

            logger.info("MoM generation completed successfully.")
            return mom_result

        except Exception as e:
            logger.warning(f"Strict JSON mode failed ({str(e)}). Retrying without response_format constraint...")
            
            try:
                # Fallback Call: Relaxed mode for complex multilingual transcripts
                fallback_response = self.client.chat.completions.create(
                    model=settings.GROQ_LLM_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                raw_content = fallback_response.choices[0].message.content
                cleaned_json = self._clean_json_string(raw_content)
                
                # Regex extract JSON object if markdown wrapper was generated
                match = re.search(r"\{.*\}", cleaned_json, re.DOTALL)
                if match:
                    cleaned_json = match.group(0)

                mom_result = json.loads(cleaned_json)
                logger.info("Fallback MoM generation succeeded.")
                return mom_result

            except Exception as fallback_error:
                logger.error(f"MoM generation failed completely: {str(fallback_error)}")
                return {
                    "speaker_map": {},
                    "minutes_of_meeting": {
                        "summary": "Failed to parse generated summary into structured JSON.",
                        "key_discussion_points": [],
                        "decisions_made": [],
                        "action_items": []
                    }
                }