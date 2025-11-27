from typing import Optional

from pydantic import BaseModel, Field


class ScoreCategory(BaseModel):
    """Score category (education or experience) with detailed analysis"""

    positive_factors: Optional[str] = Field(default=None)
    negative_factors: Optional[str] = Field(default=None)
    potential_improvements: Optional[str] = Field(default=None)
    reasoning: Optional[str] = Field(default=None)
    final_score: Optional[float] = Field(default=None, ge=0.0, le=10.0)


class CandidateScores(BaseModel):
    """Candidate scores with education and experience evaluation"""

    valid: bool = Field()
    education: ScoreCategory = Field(description="Education score analysis and evaluation")
    experience: ScoreCategory = Field(description="Experience score analysis and evaluation")
