"""Unit tests for CV-Job matching models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from job_agent.models.matching import (
    DutchLocationMatcher,
    DutchSkillMatcher,
    ExperienceMatch,
    LocationMatch,
    MatchingConfiguration,
    MatchingResult,
    MatchScore,
    SkillMatch,
)


class TestSkillMatch:
    """Test SkillMatch model."""

    def test_skill_match_initialization(self):
        """Test SkillMatch model initialization."""
        match = SkillMatch(
            cv_skill="Python",
            job_requirement="Python",
            similarity_score=1.0,
            match_type="exact"
        )
        
        assert match.cv_skill == "Python"
        assert match.job_requirement == "Python"
        assert match.similarity_score == 1.0
        assert match.match_type == "exact"

    def test_skill_match_validation(self):
        """Test SkillMatch validation for similarity score."""
        with pytest.raises(ValidationError):
            SkillMatch(
                cv_skill="Python",
                job_requirement="Python",
                similarity_score=1.5,  # Invalid: > 1.0
                match_type="exact"
            )


class TestLocationMatch:
    """Test LocationMatch model."""

    def test_location_match_initialization(self):
        """Test LocationMatch model initialization."""
        match = LocationMatch(
            cv_location="AMERSFOORT,NL",
            job_location="Amsterdam",
            compatibility_score=0.7,
            distance_km=50,
            same_region=False,
            randstad_compatibility=True
        )
        
        assert match.cv_location == "AMERSFOORT,NL"
        assert match.job_location == "Amsterdam"
        assert match.compatibility_score == 0.7
        assert match.distance_km == 50
        assert match.randstad_compatibility is True

    def test_location_match_validation(self):
        """Test LocationMatch validation."""
        with pytest.raises(ValidationError):
            LocationMatch(
                cv_location="Amsterdam",
                job_location="Rotterdam",
                compatibility_score=1.2  # Invalid: > 1.0
            )


class TestExperienceMatch:
    """Test ExperienceMatch model."""

    def test_experience_match_initialization(self):
        """Test ExperienceMatch model initialization."""
        match = ExperienceMatch(
            relevant_years=5,
            industry_match=True,
            role_similarity=0.8,
            seniority_match=True
        )
        
        assert match.relevant_years == 5
        assert match.industry_match is True
        assert match.role_similarity == 0.8
        assert match.seniority_match is True


class TestMatchScore:
    """Test MatchScore model."""

    def test_match_score_minimal(self):
        """Test MatchScore with minimal required fields."""
        score = MatchScore(
            job_id="job1",
            overall_score=0.75,
            skill_score=0.8,
            experience_score=0.7,
            industry_score=0.6,
            location_score=0.9
        )
        
        assert score.job_id == "job1"
        assert score.overall_score == 0.75
        assert score.calculated_at is not None
        assert score.confidence == 1.0  # Default value

    def test_match_score_with_details(self):
        """Test MatchScore with detailed matching results."""
        skill_matches = [
            SkillMatch(
                cv_skill="Python",
                job_requirement="Python",
                similarity_score=1.0,
                match_type="exact"
            )
        ]
        
        location_match = LocationMatch(
            cv_location="Amsterdam",
            job_location="Amsterdam",
            compatibility_score=1.0
        )
        
        score = MatchScore(
            job_id="job1",
            overall_score=0.85,
            skill_score=0.9,
            experience_score=0.8,
            industry_score=0.7,
            location_score=1.0,
            skill_matches=skill_matches,
            location_match=location_match,
            government_experience_match=True,
            reasoning=["Strong Python skills", "Good location match"],
            recommendations=["Consider improving domain knowledge"]
        )
        
        assert len(score.skill_matches) == 1
        assert score.location_match is not None
        assert score.government_experience_match is True
        assert len(score.reasoning) == 2


class TestDutchSkillMatcher:
    """Test DutchSkillMatcher functionality."""

    def test_skill_matcher_initialization(self):
        """Test DutchSkillMatcher initialization."""
        matcher = DutchSkillMatcher()
        assert "Kunstmatige intelligentie" in matcher.SKILL_TRANSLATIONS
        assert "gemeente" in matcher.INDUSTRY_TERMS

    def test_normalize_dutch_skill(self):
        """Test normalization of Dutch skills."""
        matcher = DutchSkillMatcher()
        normalized = matcher.normalize_skill("Kunstmatige intelligentie")
        
        assert "kunstmatige intelligentie" in normalized
        assert "ai" in normalized
        assert "artificial intelligence" in normalized
        assert "machine learning" in normalized

    def test_normalize_english_skill(self):
        """Test normalization of English skills."""
        matcher = DutchSkillMatcher()
        normalized = matcher.normalize_skill("JavaScript")  # Use a skill that's not in translations
        
        assert "javascript" in normalized
        assert len(normalized) == 1  # No translations for this skill

    def test_exact_skill_match(self):
        """Test exact skill matching."""
        matcher = DutchSkillMatcher()
        match = matcher.calculate_skill_similarity("Python", "Python")
        
        assert match.similarity_score == 1.0
        assert match.match_type == "exact"

    def test_dutch_translation_match(self):
        """Test Dutch-English translation matching."""
        matcher = DutchSkillMatcher()
        match = matcher.calculate_skill_similarity("Kunstmatige intelligentie", "AI")
        
        assert match.similarity_score == 0.9
        assert match.match_type == "translated"

    def test_similar_skill_match(self):
        """Test similar skill matching."""
        matcher = DutchSkillMatcher()
        match = matcher.calculate_skill_similarity("Python Programming", "Python")
        
        # This gets matched as a translation since "Python" is in SKILL_TRANSLATIONS
        assert match.similarity_score == 0.9
        assert match.match_type == "translated"

    def test_containment_skill_match(self):
        """Test containment-based skill matching."""
        matcher = DutchSkillMatcher()
        match = matcher.calculate_skill_similarity("JavaScript Development", "JavaScript")
        
        assert match.similarity_score == 0.7
        assert match.match_type == "similar"

    def test_no_skill_match(self):
        """Test no skill match."""
        matcher = DutchSkillMatcher()
        match = matcher.calculate_skill_similarity("Java", "Python")
        
        assert match.similarity_score == 0.0
        assert match.match_type == "none"


class TestDutchLocationMatcher:
    """Test DutchLocationMatcher functionality."""

    def test_location_matcher_initialization(self):
        """Test DutchLocationMatcher initialization."""
        matcher = DutchLocationMatcher()
        assert "Amsterdam" in matcher.MAJOR_CITIES
        assert matcher.MAJOR_CITIES["Amsterdam"]["randstad"] is True

    def test_exact_city_match(self):
        """Test exact city matching."""
        matcher = DutchLocationMatcher()
        match = matcher.calculate_location_match("Amsterdam", "Amsterdam")
        
        assert match.compatibility_score == 1.0
        assert match.same_region is True
        assert match.randstad_compatibility is True

    def test_randstad_cities_match(self):
        """Test Randstad cities compatibility."""
        matcher = DutchLocationMatcher()
        match = matcher.calculate_location_match("Amsterdam", "Utrecht")
        
        assert match.compatibility_score == 0.7  # Both Randstad
        assert match.randstad_compatibility is True

    def test_same_region_match(self):
        """Test same region matching."""
        matcher = DutchLocationMatcher()
        match = matcher.calculate_location_match("Amsterdam", "Den Haag")
        
        # Both in Zuid-Holland or Noord-Holland regions
        assert match.compatibility_score >= 0.7

    def test_different_regions_match(self):
        """Test different regions matching."""
        matcher = DutchLocationMatcher()
        match = matcher.calculate_location_match("Groningen", "Eindhoven")
        
        assert match.compatibility_score == 0.3  # Different regions
        assert match.randstad_compatibility is False

    def test_amersfoort_location_parsing(self):
        """Test parsing of Amersfoort location from CV format."""
        matcher = DutchLocationMatcher()
        match = matcher.calculate_location_match("AMERSFOORT,NL", "Utrecht")
        
        # Should extract "Amersfoort" and match with Utrecht region
        assert match.compatibility_score > 0.0


class TestMatchingResult:
    """Test MatchingResult model."""

    def test_matching_result_initialization(self):
        """Test MatchingResult initialization."""
        match_scores = [
            MatchScore(
                job_id="job1",
                overall_score=0.8,
                skill_score=0.9,
                experience_score=0.7,
                industry_score=0.8,
                location_score=0.8
            )
        ]
        
        result = MatchingResult(
            cv_id="cv1",
            cv_summary="Test CV",
            total_jobs_analyzed=5,
            top_matches=match_scores,
            all_matches=match_scores,
            average_match_score=0.6,
            best_match_score=0.8
        )
        
        assert result.cv_id == "cv1"
        assert result.total_jobs_analyzed == 5
        assert len(result.top_matches) == 1
        assert result.best_match_score == 0.8

    def test_matching_result_with_insights(self):
        """Test MatchingResult with Dutch market insights."""
        result = MatchingResult(
            cv_id="cv1",
            cv_summary="AI Specialist",
            total_jobs_analyzed=10,
            government_opportunities=3,
            tech_opportunities=7,
            location_flexible_roles=8,
            skill_gaps=["Machine Learning", "DevOps"],
            location_recommendations=["Consider Amsterdam area"]
        )
        
        assert result.government_opportunities == 3
        assert result.tech_opportunities == 7
        assert "Machine Learning" in result.skill_gaps
        assert len(result.location_recommendations) == 1


class TestMatchingConfiguration:
    """Test MatchingConfiguration model."""

    def test_default_configuration(self):
        """Test default matching configuration."""
        config = MatchingConfiguration()
        
        assert config.skill_weight == 0.4
        assert config.experience_weight == 0.3
        assert config.industry_weight == 0.2
        assert config.location_weight == 0.1
        assert config.minimum_match_score == 0.6
        assert config.prioritize_government_experience is True

    def test_custom_configuration(self):
        """Test custom matching configuration."""
        config = MatchingConfiguration(
            skill_weight=0.5,
            experience_weight=0.3,
            industry_weight=0.1,
            location_weight=0.1,
            minimum_match_score=0.7,
            max_top_matches=5
        )
        
        assert config.skill_weight == 0.5
        assert config.minimum_match_score == 0.7
        assert config.max_top_matches == 5

    def test_configuration_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            MatchingConfiguration(
                skill_weight=1.5  # Invalid: > 1.0
            )

    def test_weight_sum_validation(self):
        """Test that weights can sum to 1.0."""
        config = MatchingConfiguration(
            skill_weight=0.25,
            experience_weight=0.25,
            industry_weight=0.25,
            location_weight=0.25
        )
        
        total_weight = (
            config.skill_weight + 
            config.experience_weight + 
            config.industry_weight + 
            config.location_weight
        )
        assert total_weight == 1.0