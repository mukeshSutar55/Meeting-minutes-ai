from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ActionItemSchema(BaseModel):
    task: str = Field(..., description="Description of the action item or task")
    assigned_to: str = Field(default="Unassigned", description="Participant assigned to the task")
    deadline: str = Field(default="TBD", description="Deadline or due date for the task")


class MinutesOfMeetingSchema(BaseModel):
    summary: str = Field(..., description="Executive summary of the meeting")
    key_discussion_points: List[str] = Field(default_factory=list, description="List of key points discussed")
    decisions_made: List[str] = Field(default_factory=list, description="List of decisions agreed upon")
    action_items: List[ActionItemSchema] = Field(default_factory=list, description="Structured action items")


class SpeakerStatSchema(BaseModel):
    total_speaking_time_seconds: float = Field(..., description="Total speaking time in seconds")
    speaking_segments_count: int = Field(..., description="Number of speech turns")
    speaking_percentage: float = Field(..., description="Talk time proportion percentage")


class TranscriptSegmentSchema(BaseModel):
    speaker: str = Field(..., description="Identified speaker label (e.g., Person 1)")
    start: float = Field(..., description="Segment start time in seconds")
    end: float = Field(..., description="Segment end time in seconds")
    text: str = Field(..., description="Transcribed text content")


class MetadataSchema(BaseModel):
    source_file: str = Field(..., description="Original filename")
    primary_language: str = Field(..., description="Detected primary language code")
    total_duration_seconds: float = Field(..., description="Total recording duration in seconds")


class PipelineResponseSchema(BaseModel):
    metadata: MetadataSchema
    speaker_statistics: Dict[str, SpeakerStatSchema]
    minutes_of_meeting: MinutesOfMeetingSchema
    transcript: List[TranscriptSegmentSchema]


from pydantic import BaseModel

class HealthCheckSchema(BaseModel):
    status: str
    device: str
    groq_api_configured: bool
    deepgram_api_configured: bool  