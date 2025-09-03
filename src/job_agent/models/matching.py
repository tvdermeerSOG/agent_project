"""Job-CV matching models for Dutch market."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    """Individual skill matching result."""

    cv_skill: str = Field(..., description="Skill from CV")
    job_requirement: str = Field(..., description="Required skill from job")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    match_type: str = Field(..., description="Type of match: exact, translated, similar, fuzzy")


class LocationMatch(BaseModel):
    """Location matching result for Dutch geography."""

    cv_location: str = Field(..., description="Location from CV")
    job_location: str = Field(..., description="Job location")
    compatibility_score: float = Field(..., ge=0.0, le=1.0, description="Location compatibility (0-1)")
    distance_km: int | None = Field(None, description="Distance in kilometers")
    same_region: bool = Field(False, description="Whether locations are in same region")
    randstad_compatibility: bool = Field(False, description="Both in Randstad area")


class ExperienceMatch(BaseModel):
    """Experience matching result."""

    relevant_years: int = Field(..., description="Years of relevant experience")
    industry_match: bool = Field(False, description="Has experience in same industry")
    role_similarity: float = Field(..., ge=0.0, le=1.0, description="Role similarity score")
    seniority_match: bool = Field(False, description="Seniority level matches job requirements")


class MatchScore(BaseModel):
    """Comprehensive CV-Job match score."""

    job_id: str
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall match score")

    # Component scores
    skill_score: float = Field(..., ge=0.0, le=1.0, description="Skills matching score")
    experience_score: float = Field(..., ge=0.0, le=1.0, description="Experience matching score")
    industry_score: float = Field(..., ge=0.0, le=1.0, description="Industry/sector matching score")
    location_score: float = Field(..., ge=0.0, le=1.0, description="Location compatibility score")

    # Detailed matching results
    skill_matches: list[SkillMatch] = Field(default_factory=list)
    location_match: LocationMatch | None = None
    experience_match: ExperienceMatch | None = None

    # Dutch market specific fields
    dutch_skill_matches: list[str] = Field(
        default_factory=list, description="Skills matched using Dutch-English translations"
    )
    government_experience_match: bool = Field(
        False, description="Has relevant government/public sector experience"
    )

    # Reasoning and recommendations
    reasoning: list[str] = Field(default_factory=list, description="Reasons for the score")
    recommendations: list[str] = Field(default_factory=list, description="Improvement suggestions")

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in matching accuracy")


class DutchSkillMatcher(BaseModel):
    """Enhanced skill matching for Dutch/English technical terms."""

    # Extended Dutch-English skill translations
    SKILL_TRANSLATIONS: dict[str, list[str]] = {
        "Kunstmatige intelligentie": ["AI", "Artificial Intelligence", "Machine Learning"],
        "Natuurlijke taalverwerking": ["NLP", "Natural Language Processing"],
        "Natuurlijke Taal Analyse": ["NLA", "Text Analysis", "Text Mining"],
        "AI governance": ["AI Ethics", "Responsible AI", "AI Compliance"],
        "CICD": ["CI/CD", "DevOps", "Continuous Integration", "Continuous Deployment"],
        "Data science": ["Data Science", "Data Analysis", "Analytics"],
        "Azure AI & machine learning": ["Azure ML", "Azure AI", "Cloud ML", "Microsoft AI"],
        "Oplossingsarchitectuur": ["Solution Architecture", "Architecture", "System Design"],
        "Python": ["Python", "Python Programming", "Python Development"],
        "RAG": ["Retrieval Augmented Generation", "RAG", "LLM", "Large Language Models"]
    }

    # Industry-specific Dutch terms
    INDUSTRY_TERMS: dict[str, list[str]] = {
        "gemeente": ["municipality", "government", "public sector", "local government"],
        "overheid": ["government", "public administration", "civil service"],
        "sociaal domein": ["social services", "social sector", "welfare"],
        "projectleider": ["project manager", "project lead", "program manager"]
    }

    def normalize_skill(self, skill: str) -> list[str]:
        """Convert Dutch skill to English equivalents for broader matching."""
        normalized = [skill.lower().strip()]

        # Add translations if available
        for dutch_term, english_terms in self.SKILL_TRANSLATIONS.items():
            if dutch_term.lower() in skill.lower():
                normalized.extend([term.lower() for term in english_terms])

        return list(set(normalized))  # Remove duplicates

    def calculate_skill_similarity(self, cv_skill: str, job_requirement: str) -> SkillMatch:
        """Calculate similarity including Dutch-English translations."""
        cv_skill_lower = cv_skill.lower().strip()
        job_req_lower = job_requirement.lower().strip()

        # Exact match
        if cv_skill_lower == job_req_lower:
            return SkillMatch(
                cv_skill=cv_skill,
                job_requirement=job_requirement,
                similarity_score=1.0,
                match_type="exact"
            )

        # Check Dutch translations
        cv_equivalents = self.normalize_skill(cv_skill)
        job_equivalents = self.normalize_skill(job_requirement)

        for cv_eq in cv_equivalents:
            for job_eq in job_equivalents:
                if cv_eq == job_eq:
                    return SkillMatch(
                        cv_skill=cv_skill,
                        job_requirement=job_requirement,
                        similarity_score=0.9,
                        match_type="translated"
                    )

        # Fuzzy matching for similar terms
        # Simple containment check (could be enhanced with edit distance)
        if cv_skill_lower in job_req_lower or job_req_lower in cv_skill_lower:
            return SkillMatch(
                cv_skill=cv_skill,
                job_requirement=job_requirement,
                similarity_score=0.7,
                match_type="similar"
            )

        # Check if any translations are similar
        max_similarity = 0.0
        for cv_eq in cv_equivalents:
            for job_eq in job_equivalents:
                if cv_eq in job_eq or job_eq in cv_eq:
                    max_similarity = max(max_similarity, 0.5)

        return SkillMatch(
            cv_skill=cv_skill,
            job_requirement=job_requirement,
            similarity_score=max_similarity,
            match_type="fuzzy" if max_similarity > 0 else "none"
        )


class DutchLocationMatcher(BaseModel):
    """Location matching for Dutch geography."""

    # Major Dutch cities and regions
    MAJOR_CITIES: dict[str, dict[str, Any]] = {
        "Amsterdam": {"region": "Noord-Holland", "randstad": True},
        "Rotterdam": {"region": "Zuid-Holland", "randstad": True},
        "Utrecht": {"region": "Utrecht", "randstad": True},
        "Den Haag": {"region": "Zuid-Holland", "randstad": True},
        "Amersfoort": {"region": "Utrecht", "randstad": False},
        "Eindhoven": {"region": "Noord-Brabant", "randstad": False},
        "Groningen": {"region": "Groningen", "randstad": False},
        "Tilburg": {"region": "Noord-Brabant", "randstad": False}
    }

    def calculate_location_match(self, cv_location: str, job_location: str) -> LocationMatch:
        """Calculate location compatibility within Dutch geography."""
        cv_clean = cv_location.upper().replace(",NL", "").strip()
        job_clean = job_location.strip()

        # Extract city names
        cv_city = self._extract_city_name(cv_clean)
        job_city = self._extract_city_name(job_clean)

        # Exact city match
        if cv_city == job_city:
            return LocationMatch(
                cv_location=cv_location,
                job_location=job_location,
                compatibility_score=1.0,
                same_region=True,
                randstad_compatibility=self.MAJOR_CITIES.get(cv_city, {}).get("randstad", False)
            )

        # Check region compatibility
        cv_info = self.MAJOR_CITIES.get(cv_city, {})
        job_info = self.MAJOR_CITIES.get(job_city, {})

        same_region = cv_info.get("region") == job_info.get("region")
        both_randstad = cv_info.get("randstad", False) and job_info.get("randstad", False)

        # Calculate compatibility score
        if same_region:
            score = 0.8
        elif both_randstad:
            score = 0.7  # Randstad cities are well connected
        elif cv_info.get("randstad") or job_info.get("randstad"):
            score = 0.5  # One in Randstad
        else:
            score = 0.3  # Different regions

        return LocationMatch(
            cv_location=cv_location,
            job_location=job_location,
            compatibility_score=score,
            same_region=same_region,
            randstad_compatibility=both_randstad
        )

    def _extract_city_name(self, location: str) -> str:
        """Extract city name from location string."""
        # Handle common formats
        location = location.replace("AMERSFOORT", "Amersfoort")
        location = location.replace("AMSTERDAM", "Amsterdam")
        location = location.replace("ROTTERDAM", "Rotterdam")
        location = location.replace("UTRECHT", "Utrecht")

        # Return first known city found
        for city in self.MAJOR_CITIES:
            if city.upper() in location.upper():
                return city

        return location.split(",")[0].strip().title()


class MatchingResult(BaseModel):
    """Complete matching result for a CV against multiple jobs."""

    cv_id: str = Field(..., description="CV identifier")
    cv_summary: str = Field(..., description="Brief CV summary")
    total_jobs_analyzed: int = Field(..., description="Number of jobs analyzed")

    # Top matches
    top_matches: list[MatchScore] = Field(default_factory=list, description="Best job matches")
    all_matches: list[MatchScore] = Field(default_factory=list, description="All job match scores")

    # Analysis summary
    average_match_score: float = Field(0.0, description="Average match score across all jobs")
    best_match_score: float = Field(0.0, description="Highest match score achieved")

    # Dutch market insights
    government_opportunities: int = Field(0, description="Number of government/public sector roles")
    tech_opportunities: int = Field(0, description="Number of tech/AI roles")
    location_flexible_roles: int = Field(0, description="Roles with good location compatibility")

    # Recommendations
    skill_gaps: list[str] = Field(default_factory=list, description="Skills to develop")
    location_recommendations: list[str] = Field(default_factory=list, description="Location suggestions")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)
    analysis_duration_seconds: float = Field(0.0, description="Time taken for analysis")


class MatchingConfiguration(BaseModel):
    """Configuration for CV-Job matching algorithm."""

    # Scoring weights
    skill_weight: float = Field(0.4, ge=0.0, le=1.0, description="Weight for skills matching")
    experience_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for experience matching")
    industry_weight: float = Field(0.2, ge=0.0, le=1.0, description="Weight for industry matching")
    location_weight: float = Field(0.1, ge=0.0, le=1.0, description="Weight for location matching")

    # Thresholds
    minimum_match_score: float = Field(0.6, ge=0.0, le=1.0, description="Minimum score for recommendations")
    skill_similarity_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum skill similarity")

    # Dutch market specific settings
    prioritize_government_experience: bool = Field(True, description="Boost score for government experience")
    randstad_location_bonus: float = Field(0.1, description="Bonus for Randstad location compatibility")
    dutch_skill_translation_bonus: float = Field(0.05, description="Bonus for Dutch skill translations")

    # Result limits
    max_top_matches: int = Field(10, description="Maximum number of top matches to return")
    include_low_matches: bool = Field(False, description="Include matches below threshold")
