"""Unit tests for CV data models."""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from job_agent.models.cv import (
    CV,
    CVParsingResult,
    CVSummary,
    DetailedExperience,
    Education,
    Experience,
    Language,
    PersonalInfo,
    Skill,
)


class TestPersonalInfo:
    """Test PersonalInfo model."""

    def test_personal_info_initialization(self):
        """Test PersonalInfo can be initialized with valid data."""
        info = PersonalInfo(
            name="Thomas van der Meer",
            current_role="Generative AI specialist",
            location="AMERSFOORT,NL"
        )
        
        assert info.name == "Thomas van der Meer"
        assert info.current_role == "Generative AI specialist"
        assert info.location == "AMERSFOORT,NL"

    def test_personal_info_required_fields(self):
        """Test that required fields raise validation error when missing."""
        with pytest.raises(ValidationError) as exc_info:
            PersonalInfo(name="Test")  # Missing required fields
        
        errors = exc_info.value.errors()
        missing_fields = {error["loc"][0] for error in errors}
        assert "current_role" in missing_fields
        assert "location" in missing_fields


class TestExperience:
    """Test Experience model."""

    def test_experience_valid_date_range(self):
        """Test Experience with valid Dutch date range."""
        exp = Experience(
            period="01/2025 – 06/2025",
            company="Gemeente Amsterdam"
        )
        
        assert exp.period == "01/2025 – 06/2025"
        assert exp.company == "Gemeente Amsterdam"
        assert exp.role is None  # Optional field

    def test_experience_current_position(self):
        """Test Experience with current position format."""
        exp = Experience(
            period="01/2025 – heden",
            company="ABN AMRO Nederland",
            role="Gen AI engineer"
        )
        
        assert exp.period == "01/2025 – heden"
        assert exp.role == "Gen AI engineer"

    def test_experience_invalid_date_format(self):
        """Test that invalid date format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Experience(
                period="January 2025 - June 2025",  # Invalid format
                company="Test Company"
            )
        
        error = exc_info.value.errors()[0]
        assert "Invalid Dutch date format" in str(error["ctx"])

    def test_experience_date_parsing(self):
        """Test date parsing functionality."""
        exp = Experience(
            period="01/2025 – 06/2025",
            company="Test Company"
        )
        
        exp.parse_dates()
        
        assert exp.start_date == date(2025, 1, 1)
        assert exp.end_date == date(2025, 6, 1)
        assert exp.is_current is False

    def test_experience_current_position_parsing(self):
        """Test parsing of current position."""
        exp = Experience(
            period="01/2025 – heden",
            company="Current Company"
        )
        
        exp.parse_dates()
        
        assert exp.start_date == date(2025, 1, 1)
        assert exp.end_date is None
        assert exp.is_current is True


class TestSkill:
    """Test Skill model."""

    def test_skill_initialization(self):
        """Test Skill model initialization."""
        skill = Skill(name="Python", category="technical")
        
        assert skill.name == "Python"
        assert skill.category == "technical"

    def test_skill_dutch_translations(self):
        """Test Dutch skill translation functionality."""
        skill = Skill(name="Kunstmatige intelligentie")
        equivalents = skill.get_english_equivalents()
        
        assert "AI" in equivalents
        assert "Artificial Intelligence" in equivalents
        assert "Machine Learning" in equivalents

    def test_skill_english_passthrough(self):
        """Test that English skills pass through unchanged."""
        skill = Skill(name="Python")
        equivalents = skill.get_english_equivalents()
        
        assert equivalents == ["Python"]


class TestEducation:
    """Test Education model."""

    def test_education_degree(self):
        """Test Education model for degree."""
        edu = Education(
            name="Msc Business Informatics",
            institution="Universiteit Utrecht",
            level="WO",
            description="Master's degree in Business Informatics with Data Science specialization"
        )
        
        assert edu.name == "Msc Business Informatics"
        assert edu.institution == "Universiteit Utrecht"
        assert edu.level == "WO"
        assert edu.is_certification is False

    def test_education_certification(self):
        """Test Education model for certification."""
        cert = Education(
            name="Microsoft Certified: Azure Fundamentals",
            is_certification=True
        )
        
        assert cert.name == "Microsoft Certified: Azure Fundamentals"
        assert cert.is_certification is True
        assert cert.institution is None


class TestLanguage:
    """Test Language model."""

    def test_language_initialization(self):
        """Test Language model initialization."""
        lang = Language(name="Nederlands", level="Native")
        
        assert lang.name == "Nederlands"
        assert lang.level == "Native"

    def test_language_minimal(self):
        """Test Language with minimal required fields."""
        lang = Language(name="Engels")
        
        assert lang.name == "Engels"
        assert lang.level is None


class TestDetailedExperience:
    """Test DetailedExperience model."""

    def test_detailed_experience_initialization(self):
        """Test DetailedExperience model initialization."""
        exp = DetailedExperience(
            role="Tech Lead Gen AI",
            company="Gemeente Amsterdam",
            period="Januari 2025 – Juni 2025",
            description="Technology and implementation lead for Gen AI application",
            skills_used=["Python", "Azure AI", "RAG"]
        )
        
        assert exp.role == "Tech Lead Gen AI"
        assert exp.company == "Gemeente Amsterdam"
        assert "Python" in exp.skills_used
        assert len(exp.skills_used) == 3

    def test_detailed_experience_empty_skills(self):
        """Test DetailedExperience with empty skills list."""
        exp = DetailedExperience(
            role="Data Scientist",
            company="Test Company",
            period="01/2023 – 12/2023",
            description="Data analysis and modeling"
        )
        
        assert exp.skills_used == []


class TestCV:
    """Test complete CV model."""

    def test_cv_minimal_initialization(self):
        """Test CV with minimal required fields."""
        personal_info = PersonalInfo(
            name="Test Person",
            current_role="Developer",
            location="Amsterdam"
        )
        
        cv = CV(
            personal_info=personal_info,
            introduction="Test introduction"
        )
        
        assert cv.personal_info.name == "Test Person"
        assert cv.introduction == "Test introduction"
        assert cv.skills == []
        assert cv.experience_history == []
        assert cv.total_experience_years is not None  # Should be calculated

    def test_cv_full_initialization(self):
        """Test CV with all fields populated."""
        personal_info = PersonalInfo(
            name="Thomas van der Meer",
            current_role="Generative AI specialist",
            location="AMERSFOORT,NL"
        )
        
        skills = [
            Skill(name="Python", category="technical"),
            Skill(name="Kunstmatige intelligentie", category="technical")
        ]
        
        experience = [
            Experience(period="01/2025 – 06/2025", company="Gemeente Amsterdam"),
            Experience(period="11/2023 – 03/2025", company="ABN AMRO Nederland")
        ]
        
        cv = CV(
            personal_info=personal_info,
            introduction="Test professional summary",
            skills=skills,
            experience_history=experience
        )
        
        assert len(cv.skills) == 2
        assert len(cv.experience_history) == 2
        assert cv.total_experience_years >= 0

    def test_cv_experience_calculation(self):
        """Test experience years calculation."""
        personal_info = PersonalInfo(
            name="Test Person",
            current_role="Developer", 
            location="Amsterdam"
        )
        
        # Create experience spanning 2 years
        experience = [
            Experience(period="01/2023 – 12/2023", company="Company A"),
            Experience(period="01/2024 – 12/2024", company="Company B")
        ]
        
        cv = CV(
            personal_info=personal_info,
            introduction="Test",
            experience_history=experience
        )
        
        years = cv.calculate_experience_years()
        assert years >= 1  # Should calculate some experience

    def test_cv_key_technologies_extraction(self):
        """Test key technologies extraction."""
        personal_info = PersonalInfo(
            name="Test Person",
            current_role="Developer",
            location="Amsterdam"
        )
        
        skills = [Skill(name="Python"), Skill(name="Azure")]
        detailed_exp = [
            DetailedExperience(
                role="Developer",
                company="Test",
                period="2023",
                description="Test",
                skills_used=["Python", "Docker"]
            )
        ]
        
        cv = CV(
            personal_info=personal_info,
            introduction="Test",
            skills=skills,
            detailed_experiences=detailed_exp
        )
        
        key_techs = cv.extract_key_technologies()
        assert "Python" in key_techs  # Should appear in both skills and detailed experience


class TestCVSummary:
    """Test CVSummary model."""

    def test_cv_summary_initialization(self):
        """Test CVSummary model initialization."""
        summary = CVSummary(
            name="Thomas van der Meer",
            current_role="Generative AI specialist",
            location="AMERSFOORT,NL",
            total_experience_years=10,
            key_skills=["Python", "AI", "Azure"],
            recent_companies=["Gemeente Amsterdam", "ABN AMRO"],
            last_updated=datetime.now()
        )
        
        assert summary.name == "Thomas van der Meer"
        assert summary.total_experience_years == 10
        assert len(summary.key_skills) == 3
        assert len(summary.recent_companies) == 2


class TestCVParsingResult:
    """Test CVParsingResult model."""

    def test_successful_parsing_result(self):
        """Test successful CV parsing result."""
        personal_info = PersonalInfo(
            name="Test Person",
            current_role="Developer",
            location="Amsterdam"
        )
        
        cv = CV(personal_info=personal_info, introduction="Test")
        
        result = CVParsingResult(
            success=True,
            cv=cv,
            source_format="markdown",
            extraction_confidence=0.95
        )
        
        assert result.success is True
        assert result.cv is not None
        assert result.source_format == "markdown"
        assert result.extraction_confidence == 0.95
        assert result.errors == []

    def test_failed_parsing_result(self):
        """Test failed CV parsing result."""
        result = CVParsingResult(
            success=False,
            errors=["Invalid file format", "Missing required sections"],
            source_format="pdf",
            extraction_confidence=0.1
        )
        
        assert result.success is False
        assert result.cv is None
        assert len(result.errors) == 2
        assert "Invalid file format" in result.errors

    def test_parsing_result_validation(self):
        """Test validation of extraction confidence."""
        with pytest.raises(ValidationError):
            CVParsingResult(
                success=True,
                source_format="pdf",
                extraction_confidence=1.5  # Invalid: > 1.0
            )