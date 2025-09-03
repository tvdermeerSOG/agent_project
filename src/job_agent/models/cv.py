"""CV data models based on Dutch CV format from cv1.md."""

import re
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class PersonalInfo(BaseModel):
    """Basic personal information from CV header."""

    name: str = Field(..., description="Full name (e.g., 'Thomas van der Meer')")
    current_role: str = Field(
        ..., description="Current job title (e.g., 'Generative AI specialist')"
    )
    location: str = Field(..., description="City/location (e.g., 'AMERSFOORT,NL')")


class Experience(BaseModel):
    """Work experience entry with Dutch date format."""

    period: str = Field(
        ..., description="Dutch format like '01/2025 – 06/2025' or '11/2023 – 03/2025'"
    )
    company: str = Field(..., description="Company/organization name")
    role: str | None = Field(None, description="Job role if specified")

    # Computed fields for date parsing
    start_date: date | None = Field(None, description="Parsed start date")
    end_date: date | None = Field(None, description="Parsed end date")
    is_current: bool = Field(False, description="Whether this is a current position")

    @field_validator("period")
    @classmethod
    def validate_dutch_period(cls, v: str) -> str:
        """Validate and parse Dutch date format."""
        # Expected formats:
        # "01/2025 – 06/2025" or "11/2023 – 03/2025"
        # "01/2025 – heden" (heden = current)
        date_range_pattern = r"\d{2}/\d{4}\s*[–-]\s*\d{2}/\d{4}"
        current_pattern = r"\d{2}/\d{4}\s*[–-]\s*(heden|current)"

        if not (re.match(date_range_pattern, v) or re.match(current_pattern, v, re.IGNORECASE)):
            raise ValueError(f"Invalid Dutch date format: {v}. Expected MM/YYYY – MM/YYYY or MM/YYYY – heden")

        return v

    def parse_dates(self) -> None:
        """Parse the period string into start_date, end_date, and is_current."""
        if not self.period:
            return

        # Split on dash/en-dash
        parts = re.split(r"\s*[–-]\s*", self.period)
        if len(parts) != 2:
            return

        start_part, end_part = parts

        # Parse start date
        if re.match(r"\d{2}/\d{4}", start_part):
            month, year = start_part.split("/")
            self.start_date = date(int(year), int(month), 1)

        # Parse end date
        if end_part.lower() in ["heden", "current"]:
            self.is_current = True
            self.end_date = None
        elif re.match(r"\d{2}/\d{4}", end_part):
            month, year = end_part.split("/")
            self.end_date = date(int(year), int(month), 1)


class Education(BaseModel):
    """Education and certification entry."""

    name: str = Field(..., description="Degree, certification, or course name")
    institution: str | None = Field(None, description="Educational institution")
    level: str | None = Field(None, description="Education level (WO, HBO, etc.)")
    description: str | None = Field(None, description="Detailed description")
    is_certification: bool = Field(False, description="Whether this is a certification vs degree")


class Skill(BaseModel):
    """Technical or soft skill with support for Dutch/English terminology."""

    name: str = Field(..., description="Skill name (Dutch or English)")
    category: str | None = Field(None, description="Skill category (technical, soft, language)")

    # Dutch-English skill mappings for common terms
    DUTCH_TRANSLATIONS: dict[str, list[str]] = {
        "Kunstmatige intelligentie": ["AI", "Artificial Intelligence", "Machine Learning"],
        "Natuurlijke taalverwerking": ["NLP", "Natural Language Processing"],
        "Natuurlijke Taal Analyse": ["NLA", "Text Analysis", "Text Mining"],
        "AI governance": ["AI Ethics", "Responsible AI", "AI Compliance"],
        "CICD": ["CI/CD", "DevOps", "Continuous Integration", "Continuous Deployment"],
    }

    def get_english_equivalents(self) -> list[str]:
        """Get English equivalents for Dutch skill names."""
        return self.DUTCH_TRANSLATIONS.get(self.name, [self.name])


class Language(BaseModel):
    """Language proficiency."""

    name: str = Field(..., description="Language name (e.g., 'Nederlands', 'Engels')")
    level: str | None = Field(None, description="Proficiency level (Native, Fluent, etc.)")


class DetailedExperience(BaseModel):
    """Detailed experience description for specific roles."""

    role: str = Field(..., description="Job title (e.g., 'Tech Lead Gen AI')")
    company: str = Field(..., description="Company/client name")
    period: str = Field(..., description="Duration in Dutch format")
    description: str = Field(..., description="Role description and responsibilities")
    skills_used: list[str] = Field(
        default_factory=list, description="Technologies/skills mentioned in description"
    )

    @field_validator("period")
    @classmethod
    def validate_period_format(cls, v: str) -> str:
        """Validate period format similar to Experience model."""
        # Accept various formats used in detailed experience
        # "Januari 2025 – Juni 2025", "November 2023 – Maart 2025", etc.
        dutch_month_pattern = r"(Januari|Februari|Maart|April|Mei|Juni|Juli|Augustus|September|Oktober|November|December)\s+\d{4}\s*[–-]\s*(Januari|Februari|Maart|April|Mei|Juni|Juli|Augustus|September|Oktober|November|December)\s+\d{4}"
        short_format = r"\d{2}/\d{4}\s*[–-]\s*\d{2}/\d{4}"

        if not (re.match(dutch_month_pattern, v) or re.match(short_format, v)):
            # Be more lenient for detailed experience descriptions
            pass

        return v


class CV(BaseModel):
    """Complete CV model based on cv1.md structure."""

    # Basic information
    personal_info: PersonalInfo
    introduction: str = Field(..., description="Professional summary/introduction paragraph")

    # Skills and capabilities
    skills: list[Skill] = Field(default_factory=list)

    # Experience overview
    experience_history: list[Experience] = Field(
        default_factory=list, description="Chronological work history"
    )

    # Education and certifications
    education: list[Education] = Field(default_factory=list)
    certificates: list[Education] = Field(default_factory=list)

    # Languages
    languages: list[Language] = Field(default_factory=list)

    # Detailed experience descriptions
    detailed_experiences: list[DetailedExperience] = Field(default_factory=list)

    # Metadata
    source_file: str | None = Field(None, description="Source file path")
    extracted_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime | None = Field(None, description="Last update timestamp")

    # Derived/computed fields
    total_experience_years: int | None = Field(None, description="Total years of experience")
    key_technologies: list[str] = Field(
        default_factory=list, description="Most frequently mentioned technologies"
    )
    primary_industries: list[str] = Field(
        default_factory=list, description="Main industry sectors"
    )

    def calculate_experience_years(self) -> int:
        """Calculate total years of experience from experience history."""
        if not self.experience_history:
            return 0

        # Parse dates from experience history
        total_months = 0
        for exp in self.experience_history:
            exp.parse_dates()
            if exp.start_date:
                end_date = exp.end_date or date.today()
                months = (end_date.year - exp.start_date.year) * 12 + (end_date.month - exp.start_date.month)
                total_months += max(0, months)

        return max(0, total_months // 12)

    def extract_key_technologies(self) -> list[str]:
        """Extract most mentioned technologies across all experiences."""
        tech_count: dict[str, int] = {}

        # Count from skills
        for skill in self.skills:
            tech_count[skill.name] = tech_count.get(skill.name, 0) + 1

        # Count from detailed experiences
        for exp in self.detailed_experiences:
            for tech in exp.skills_used:
                tech_count[tech] = tech_count.get(tech, 0) + 1

        # Return top technologies (sorted by frequency)
        sorted_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)
        return [tech for tech, count in sorted_techs[:10]]  # Top 10

    def model_post_init(self, __context: Any) -> None:
        """Calculate derived fields after model initialization."""
        if self.total_experience_years is None:
            self.total_experience_years = self.calculate_experience_years()
        if not self.key_technologies:
            self.key_technologies = self.extract_key_technologies()


class CVSummary(BaseModel):
    """Lightweight CV summary for API responses."""

    name: str
    current_role: str
    location: str
    total_experience_years: int | None
    key_skills: list[str]
    recent_companies: list[str]
    last_updated: datetime


class CVParsingResult(BaseModel):
    """Result of CV parsing operation."""

    success: bool
    cv: CV | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    source_format: str = Field(..., description="Source format: 'pdf', 'markdown', 'docx'")
    extraction_confidence: float = Field(
        1.0, ge=0.0, le=1.0, description="Confidence score for extraction accuracy"
    )
