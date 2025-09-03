# Task 1.4: CV Data Management

## Objective
Implement CV data management functionality that reads, parses, and validates CV information from local files in the `data/cv/` directory. This CV data will serve as the base profile information for matching against job opportunities, replacing the need for API-based CV submission. The system will prepare for intelligent job-CV matching and motivation letter generation.

## Overview
This task establishes the foundation for CV-based job matching by creating a robust CV data management system. The CV information will be stored locally and parsed into structured data that can be effectively matched against job requirements from the existing `data/jobs/` directory.

## Configuration Enhancement

### Enhanced config.yaml Structure
```yaml
# Existing configuration sections remain unchanged...

# CV data configuration
cv:
  data_directory: "data/cv"
  supported_formats: ["pdf", "markdown", "docx"]  # Support multiple formats
  primary_file: "cv1"  # File without extension, will search for supported formats
  cache_ttl: 3600  # Cache CV data for 1 hour
  pdf_extraction:
    method: "pypdf"  # or "pdfplumber" for better text extraction
    fallback_to_ocr: false  # Future: OCR for scanned PDFs
  required_sections:
    - "personal_information"
    - "experience"
    - "skills"
  optional_sections:
    - "education"
    - "certifications"
    - "languages"
    - "introduction"

# Job matching configuration
matching:
  algorithm: "weighted_scoring"  # Future: ML-based, rule-based
  weights:
    skills: 0.4
    experience: 0.3
    education: 0.2
    location: 0.1
  minimum_match_score: 0.6  # Threshold for job recommendations
  max_recommendations: 10
```

## Tasks Breakdown

### 1.4.1 CV Data Structure Design
- [x] Analyze existing CV format (PDF + Markdown extraction)
- [x] Create CV data models based on real CV structure
- [x] Design parser for Dutch CV format and terminology
- [ ] Implement support for multiple file formats (PDF, Markdown, DOCX)
- [x] Create CV template based on actual cv1.md structure

### 1.4.2 CV Data Storage and Format Support
- [ ] Support multiple CV file formats (PDF primary, Markdown secondary)
- [ ] Implement PDF text extraction with pypdf/pdfplumber
- [ ] Create fallback mechanisms (PDF → Markdown → Manual)
- [ ] Set up CV file organization with version detection
- [ ] Document actual CV data format based on cv1.md

### 1.4.3 CV Parsing Service for Real Data
- [ ] Implement Dutch CV text parsing (cv1.md format)
- [ ] Parse professional experience with Dutch date formats
- [ ] Extract skills, certifications, and education sections
- [ ] Handle complex experience descriptions and responsibilities
- [ ] Add validation for actual CV structure patterns

### 1.4.4 CV Management API
- [ ] Create CV CRUD endpoints
- [ ] Implement CV data caching
- [ ] Add CV validation endpoints
- [ ] Create CV export/import functionality
- [ ] Implement CV search and filtering

### 1.4.5 Job-CV Matching Foundation
- [ ] Design matching algorithm interface
- [ ] Implement basic skill matching
- [ ] Create experience level comparison
- [ ] Add location and availability matching
- [ ] Develop scoring and ranking system

### 1.4.6 Integration with Existing Systems
- [ ] Integrate with existing health check system
- [ ] Update configuration management
- [ ] Enhance logging for CV operations
- [ ] Extend testing framework for CV functionality
- [ ] Update API documentation

### 1.4.7 Testing and Validation
- [ ] Create CV parsing unit tests
- [ ] Implement API endpoint tests
- [ ] Add CV validation test cases
- [ ] Create performance benchmarks
- [ ] Test error handling scenarios

## Deliverables
1. CV data management service
2. CV parsing and validation system
3. CV management API endpoints
4. Basic job-CV matching foundation
5. Comprehensive test suite
6. CV data format documentation
7. Integration with existing FastAPI application

## Acceptance Criteria
- [ ] CV data can be read and parsed from `data/cv/` directory
- [ ] CV information is properly validated and structured
- [ ] API endpoints for CV management are functional
- [ ] Basic job-CV matching produces relevant scores
- [ ] All CV operations are covered by tests
- [ ] Health checks include CV system validation
- [ ] Configuration supports CV-related settings

## Dependencies
- Task 1.1 (Project Setup) completed ✅
- Task 1.2 (Azure Integration) completed ✅
- Task 1.3 (Core FastAPI Application) completed ✅
- Existing job data management from `data/jobs/` ✅

## Estimated Time
**3-4 days**

## Key Packages
```toml
[project.dependencies]
# Existing dependencies remain...
python-docx = "^1.1.0"         # For DOCX support
pypdf = "^5.4.0"               # Primary PDF text extraction
pdfplumber = "^0.11.0"         # Advanced PDF parsing (fallback)
fuzzywuzzy = "^0.18.0"         # For fuzzy string matching in Dutch text
python-levenshtein = "^0.25.0" # Performance for fuzzy matching
nltk = "^3.9.0"                # Natural language processing (Dutch support)
spacy = "^3.8.0"               # Advanced NLP with Dutch models
scikit-learn = "^1.6.0"        # Machine learning for matching
python-dateutil = "^2.9.0"     # Parse Dutch date formats
regex = "^2024.0.0"            # Advanced regex for Dutch text patterns
```

## Files to Create/Modify

### New Files
```
data/
└── cv/
    ├── cv1.pdf                # Primary CV file (PDF format)
    ├── cv1.md                 # Extracted/converted markdown version
    └── README.md              # CV data format documentation

src/job_agent/
├── models/
│   ├── cv.py                  # CV data models (based on cv1.md structure)
│   └── matching.py            # Job-CV matching models
├── services/
│   ├── cv_service.py          # Multi-format CV data management
│   ├── pdf_extractor.py       # PDF text extraction service
│   └── matching_service.py    # Job-CV matching service
└── api/v1/
    ├── cv.py                  # CV management endpoints
    └── matching.py            # Matching endpoints

tests/
├── unit/
│   ├── test_cv_service.py     # CV service tests
│   ├── test_pdf_extraction.py # PDF parsing tests
│   ├── test_cv_parsing.py     # CV parsing tests (Dutch format)
│   └── test_matching_service.py # Matching service tests
├── integration/
│   └── test_cv_api.py         # CV API integration tests
└── fixtures/
    ├── cv1.md                 # Real CV test data
    └── sample_job.md          # Test job for matching
```

### Files to Modify
```
src/job_agent/
├── core/
│   ├── config.py              # Add CV and matching settings
│   └── health.py              # Add CV system health checks
├── api/
│   └── deps.py                # Add CV service dependencies
└── main.py                    # Update startup to include CV services

config.yaml                    # Add CV and matching configuration
```

## CV Data Models (Based on Actual cv1.md Structure)

### Real CV Data Structure Analysis
Based on the provided cv1.md, the Dutch CV format includes:
- **Header**: Name, Current Role, Location
- **Introduction**: Professional summary paragraph
- **Skills**: Simple bullet-point list of technical capabilities
- **Experience History**: Chronological work experience with periods
- **Education**: Degrees, certifications, and training
- **Languages**: Language proficiency
- **Detailed Experience**: Rich descriptions for each role with responsibilities and technologies

### Pydantic Models for Dutch CV Format
```python
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import re

class PersonalInfo(BaseModel):
    """Basic personal information from CV header."""
    name: str = Field(..., description="Full name (e.g., 'Thomas van der Meer')")
    current_role: str = Field(..., description="Current job title (e.g., 'Generative AI specialist')")
    location: str = Field(..., description="City/location (e.g., 'AMERSFOORT,NL')")

class Experience(BaseModel):
    """Work experience entry with Dutch date format."""
    period: str = Field(..., description="Dutch format like '01/2025 – 06/2025'")
    company: str = Field(..., description="Company/organization name")
    role: Optional[str] = None  # Some entries have detailed role info

    # Calculated fields
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False

    @validator('period')
    def parse_dutch_period(cls, v):
        """Validate and parse Dutch date format."""
        # Expected format: "01/2025 – 06/2025" or "11/2023 – 03/2025"
        if not re.match(r'\d{2}/\d{4}\s*[–-]\s*\d{2}/\d{4}', v):
            if not re.match(r'\d{2}/\d{4}\s*[–-]\s*heden', v.lower()):  # "heden" = current
                raise ValueError(f"Invalid Dutch date format: {v}")
        return v

class Education(BaseModel):
    """Education and certification entry."""
    name: str = Field(..., description="Degree, certification, or course name")
    institution: Optional[str] = None
    level: Optional[str] = None  # WO, HBO, etc.
    description: Optional[str] = None
    is_certification: bool = False

class Skill(BaseModel):
    """Technical or soft skill."""
    name: str = Field(..., description="Skill name")
    category: Optional[str] = None  # "technical", "soft", "language"

class Language(BaseModel):
    """Language proficiency."""
    name: str = Field(..., description="Language name")
    level: Optional[str] = None  # "Native", "Fluent", etc.

class DetailedExperience(BaseModel):
    """Detailed experience description for specific roles."""
    role: str = Field(..., description="Job title")
    company: str = Field(..., description="Company/client name")
    period: str = Field(..., description="Duration in Dutch format")
    description: str = Field(..., description="Role description and responsibilities")
    skills_used: List[str] = Field(default_factory=list, description="Technologies/skills mentioned")

class CV(BaseModel):
    """Complete CV model based on cv1.md structure."""

    # Basic information
    personal_info: PersonalInfo
    introduction: str = Field(..., description="Professional summary/introduction paragraph")

    # Skills and capabilities
    skills: List[Skill] = Field(default_factory=list)

    # Experience overview
    experience_history: List[Experience] = Field(default_factory=list, description="Chronological work history")

    # Education and certifications
    education: List[Education] = Field(default_factory=list)
    certificates: List[Education] = Field(default_factory=list)

    # Languages
    languages: List[Language] = Field(default_factory=list)

    # Detailed experience descriptions
    detailed_experiences: List[DetailedExperience] = Field(default_factory=list)

    # Metadata
    source_file: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)
    last_updated: Optional[datetime] = None

    # Derived/computed fields
    total_experience_years: Optional[int] = None
    key_technologies: List[str] = Field(default_factory=list)
    primary_industries: List[str] = Field(default_factory=list)

    def calculate_experience_years(self) -> int:
        """Calculate total years of experience from experience history."""
        # Implementation would parse date ranges and calculate total
        pass

    def extract_key_technologies(self) -> List[str]:
        """Extract most mentioned technologies across all experiences."""
        # Implementation would analyze detailed_experiences for tech mentions
        pass

class CVSummary(BaseModel):
    """Lightweight CV summary for API responses."""
    name: str
    current_role: str
    location: str
    total_experience_years: Optional[int]
    key_skills: List[str]
    recent_companies: List[str]
    last_updated: datetime

class CVParsingResult(BaseModel):
    """Result of CV parsing operation."""
    success: bool
    cv: Optional[CV] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source_format: str  # "pdf", "markdown", "docx"
    extraction_confidence: float = Field(ge=0.0, le=1.0, default=1.0)
```

## Real CV Data Example (from cv1.md)

### Actual CV Structure
```markdown
# Example based on cv1.md structure:

## Personal Information
- **Name**: Thomas van der Meer
- **Current Role**: Generative AI specialist
- **Location**: AMERSFOORT,NL

## Introduction
Innovatieve en strategische tech lead met een bewezen staat van dienst in het ontwerpen en implementeren van geavanceerde Generatieve AI-oplossingen binnen sterk gereguleerde en complexe omgevingen...

## Skills (Simple List)
- Data science
- Kunstmatige intelligentie
- Natuurlijke Taal Analyse
- Natuurlijke taalverwerking
- RAG
- AI governance
- Azure AI & machine learning
- CICD
- Python

## Professional Experience Timeline
- 01/2025 – 06/2025 Gemeente Amsterdam
- 11/2023 – 03/2025 ABN AMRO Nederland
- 08/2023 – 10/2023 Gemeente Amsterdam
- 11/2022 – 08/2023 Justis
- 02/2022 – 08/2022 Reclassering Nederland

## Education & Certifications
- Amazon Web Services (AWS)
- Artificial Intelligence (AI)/Kennissystemen
- Msc Business Informatics met specialisatie in Data Science
- Microsoft Certified: Azure Fundamentals
- Databricks Certified Generative AI Engineer Associate

## Languages
- Engels
- Nederlands

## Detailed Experience Descriptions
Each role has rich descriptions with:
- Role title and client
- Period and duration
- Detailed responsibilities
- Technologies used
- Achievements and impact
```

## Dutch CV Parsing Challenges and Considerations

### Language and Format Specifics
Based on the cv1.md example, Dutch CVs have unique characteristics:

1. **Dutch Terminology**:
   - "Professionele Ervaring" = Professional Experience
   - "Opleidingen" = Education
   - "Vaardigheden" = Skills
   - "Functie" = Role/Function
   - "Opdrachtgever" = Client/Employer
   - "Periode" = Period

2. **Date Formats**:
   - Dutch format: "01/2025 – 06/2025" (MM/YYYY – MM/YYYY)
   - Current role: "01/2025 – heden" (heden = current/ongoing)
   - Duration calculations need Dutch date parsing

3. **Industry-Specific Terms**:
   - "Gemeente" = Municipality/Government
   - "Generative AI specialist" = Technical AI roles
   - Dutch company names and government organizations

4. **Skill Categories**:
   - Mix of English and Dutch technical terms
   - "Kunstmatige intelligentie" = Artificial Intelligence
   - "Natuurlijke taalverwerking" = Natural Language Processing

### Job Matching Adaptations for Dutch Market

#### Skills Matching Challenges
```python
class DutchSkillMatcher:
    """Enhanced skill matching for Dutch/English technical terms."""

    SKILL_TRANSLATIONS = {
        "Kunstmatige intelligentie": ["AI", "Artificial Intelligence", "Machine Learning"],
        "Natuurlijke taalverwerking": ["NLP", "Natural Language Processing"],
        "Natuurlijke Taal Analyse": ["NLA", "Text Analysis", "Text Mining"],
        "AI governance": ["AI Ethics", "Responsible AI", "AI Compliance"],
        "CICD": ["CI/CD", "DevOps", "Continuous Integration", "Continuous Deployment"]
    }

    def normalize_skill(self, skill: str) -> List[str]:
        """Convert Dutch skill to English equivalents for broader matching."""
        pass

    def calculate_skill_similarity(self, cv_skill: str, job_requirement: str) -> float:
        """Calculate similarity including Dutch-English translations."""
        pass
```

#### Location Matching for Dutch Market
```python
class DutchLocationMatcher:
    """Location matching for Dutch geography."""

    MAJOR_CITIES = {
        "Amsterdam": {"region": "Noord-Holland", "randstad": True},
        "Rotterdam": {"region": "Zuid-Holland", "randstad": True},
        "Utrecht": {"region": "Utrecht", "randstad": True},
        "Den Haag": {"region": "Zuid-Holland", "randstad": True},
        "Amersfoort": {"region": "Utrecht", "randstad": False}
    }

    def calculate_location_match(self, cv_location: str, job_location: str) -> float:
        """Calculate location compatibility within Dutch geography."""
        pass
```

## Job-CV Matching Foundation (Updated for Real Data)

### Enhanced Matching Algorithm
```python
class DutchCVJobMatcher:
    """Job-CV matching optimized for Dutch market and CV format."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.skill_matcher = DutchSkillMatcher()
        self.location_matcher = DutchLocationMatcher()

    async def calculate_match_score(self, job: Job, cv: CV) -> MatchScore:
        """Calculate comprehensive match score."""

        # Skills matching (40% weight)
        skill_score = self._calculate_skill_match(job, cv)

        # Experience matching (30% weight)
        experience_score = self._calculate_experience_match(job, cv)

        # Industry/sector matching (20% weight)
        industry_score = self._calculate_industry_match(job, cv)

        # Location matching (10% weight)
        location_score = self._calculate_location_match(job, cv)

        # Weighted overall score
        overall_score = (
            skill_score * 0.4 +
            experience_score * 0.3 +
            industry_score * 0.2 +
            location_score * 0.1
        )

        return MatchScore(
            job_id=job.id,
            overall_score=overall_score,
            skill_score=skill_score,
            experience_score=experience_score,
            industry_score=industry_score,
            location_score=location_score,
            reasoning=self._generate_reasoning(job, cv, overall_score),
            recommendations=self._generate_recommendations(job, cv, overall_score)
        )

    def _calculate_skill_match(self, job: Job, cv: CV) -> float:
        """Match CV skills against job requirements."""

        # Extract job skills from Dutch job description
        job_skills = self._extract_job_skills(job.role, job.industry)

        # Get CV skills (mix of Dutch/English terms)
        cv_skills = [skill.name for skill in cv.skills]

        # Add skills from detailed experiences
        for exp in cv.detailed_experiences:
            cv_skills.extend(exp.skills_used)

        # Calculate similarity using Dutch-English mappings
        total_score = 0.0
        matched_skills = 0

        for job_skill in job_skills:
            best_match_score = 0.0
            for cv_skill in cv_skills:
                similarity = self.skill_matcher.calculate_skill_similarity(cv_skill, job_skill)
                best_match_score = max(best_match_score, similarity)

            total_score += best_match_score
            if best_match_score > 0.7:  # Threshold for "good match"
                matched_skills += 1

        if not job_skills:
            return 0.5  # Neutral score if no specific skills required

        return total_score / len(job_skills)

    def _extract_job_skills(self, role: str, industry: str) -> List[str]:
        """Extract required skills from Dutch job description."""

        # Based on job roles seen in data/jobs/*.md
        skill_patterns = {
            "projectleider": ["project management", "stakeholder management", "agile", "scrum"],
            "sociaal domein": ["social services", "government", "public sector"],
            "gemeente": ["municipality", "government", "public administration"],
            "ai specialist": ["artificial intelligence", "machine learning", "python", "azure"]
        }

        extracted_skills = []
        role_lower = role.lower()
        industry_lower = industry.lower()

        for pattern, skills in skill_patterns.items():
            if pattern in role_lower or pattern in industry_lower:
                extracted_skills.extend(skills)

        return list(set(extracted_skills))  # Remove duplicates

class MatchScore(BaseModel):
    """Enhanced match score with Dutch market considerations."""
    job_id: str
    overall_score: float
    skill_score: float
    experience_score: float
    industry_score: float
    location_score: float
    reasoning: List[str]
    recommendations: List[str]

    # Dutch-specific fields
    dutch_skill_matches: List[str] = []
    location_compatibility: str = ""  # "excellent", "good", "fair", "poor"
    government_experience_match: bool = False  # Important for many Dutch roles
```

## Integration with Existing Job Data

### Matching Against data/jobs/*.md Structure
Based on the existing job files, the matching system should consider:

1. **Job Fields from job1.md, job2.md, job3.md**:
   - Klant (Client) → matches CV company experience
   - Locatie (Location) → matches CV location preferences
   - Gevraagde functie (Required function) → matches CV role titles
   - Branche (Industry) → matches CV industry experience
   - Grade indicatie → matches CV seniority level

2. **Dutch Job Market Specifics**:
   - Government roles ("Gemeente", "Overheid") are common
   - Project management roles often specify "Sociaal Domein"
   - Percentage work (90%, 80%) is important in Dutch market
   - Location flexibility within "Randstad" region

### Example Matching Logic
```python
def match_cv_to_dutch_job(cv: CV, job: Job) -> float:
    """Match CV against Dutch job posting format."""

    score = 0.0

    # Experience in similar industry
    if any("gemeente" in exp.company.lower() for exp in cv.detailed_experiences):
        if "gemeente" in job.client.lower():
            score += 0.3  # Strong government experience match

    # Role title similarity
    cv_roles = [exp.role.lower() for exp in cv.detailed_experiences]
    if any("projectleider" in role for role in cv_roles):
        if "projectleider" in job.function.lower():
            score += 0.3  # Direct role match

    # Location compatibility
    if cv.personal_info.location.upper() in ["AMSTERDAM", "ROTTERDAM", "UTRECHT"]:
        if job.location in ["Amsterdam", "Rotterdam", "Utrecht"]:
            score += 0.2  # Randstad location match

    # Industry experience
    government_keywords = ["gemeente", "overheid", "publieke sector"]
    cv_has_gov_exp = any(
        any(keyword in exp.description.lower() for keyword in government_keywords)
        for exp in cv.detailed_experiences
    )
    job_is_gov = any(keyword in job.industry.lower() for keyword in government_keywords)

    if cv_has_gov_exp and job_is_gov:
        score += 0.2  # Government sector match

    return min(score, 1.0)  # Cap at 100%
```

## Testing Strategy (Updated for Real CV Data)

### Test Coverage Areas
1. **PDF and Multi-Format Parsing Tests**
   - PDF text extraction accuracy (pypdf vs pdfplumber)
   - Markdown parsing consistency with cv1.md
   - Error handling for corrupted or unsupported files
   - Performance tests with large PDF files
   - Extraction confidence scoring

2. **Dutch CV Parsing Tests**
   - Dutch date format parsing ("01/2025 – 06/2025")
   - Dutch terminology extraction ("Vaardigheden", "Professionele Ervaring")
   - Personal information extraction from cv1.md format
   - Skills parsing with mixed Dutch/English terms
   - Experience history timeline parsing

3. **CV Service Tests**
   - Multi-format file detection and prioritization
   - Caching behavior with TTL
   - CV validation against real data structure
   - Backup and versioning for PDF sources
   - Error recovery and fallback mechanisms

4. **Dutch Job Matching Tests**
   - Skill matching with Dutch-English translations
   - Government sector experience matching
   - Dutch location compatibility (Randstad region)
   - Industry terminology matching
   - Seniority and role level assessment

5. **API Integration Tests**
   - CV endpoints with real cv1.md data
   - File upload handling for multiple formats
   - Match scoring API with actual job data
   - Error responses for invalid CV formats
   - Performance with real-world CV sizes

6. **Real Data Integration Tests**
   - End-to-end CV parsing from cv1.pdf
   - Matching against data/jobs/*.md files
   - Dutch market-specific scoring accuracy
   - Cross-format consistency (PDF vs Markdown)
   - Validation against Thomas van der Meer's actual profile

### Test Data Structure
```
tests/
├── fixtures/
│   ├── cv_data/
│   │   ├── cv1.pdf              # Real CV data
│   │   ├── cv1.md               # Extracted version
│   │   ├── invalid_cv.pdf       # Corrupted PDF for error testing
│   │   └── sample_dutch_cv.md   # Additional test CV
│   ├── job_data/
│   │   ├── gemeente_job.md      # Government job sample
│   │   ├── ai_specialist_job.md # Tech job sample
│   │   └── projectleider_job.md # Project manager job
│   └── expected_results/
│       ├── cv1_parsed.json      # Expected parsing result
│       └── cv1_job_matches.json # Expected job match scores
├── unit/
│   ├── test_pdf_extraction.py   # PDF parsing unit tests
│   ├── test_dutch_parsing.py    # Dutch text parsing tests
│   ├── test_skill_matching.py   # Dutch-English skill matching
│   └── test_location_matching.py # Dutch geography tests
└── integration/
    ├── test_real_cv_parsing.py  # Integration with cv1.pdf/md
    └── test_job_matching.py     # Real CV vs real jobs
```

## Health Check Integration (Updated)

### CV System Health Checks with Real Data
```python
async def check_cv_system_health() -> Dict[str, Any]:
    """Check CV system health with real cv1 data."""
    checks = {
        "cv_directory_accessible": False,
        "cv1_pdf_exists": False,
        "cv1_md_exists": False,
        "pdf_extraction_working": False,
        "cv_parsing_successful": False,
        "dutch_skills_extracted": False,
        "matching_service_available": False
    }

    try:
        # Check CV directory access
        cv_dir = Path(settings.cv.data_directory)
        checks["cv_directory_accessible"] = cv_dir.exists() and cv_dir.is_dir()

        # Check for cv1 files
        cv1_pdf = cv_dir / "cv1.pdf"
        cv1_md = cv_dir / "cv1.md"
        checks["cv1_pdf_exists"] = cv1_pdf.exists()
        checks["cv1_md_exists"] = cv1_md.exists()

        if checks["cv1_pdf_exists"] or checks["cv1_md_exists"]:
            # Test CV parsing with real data
            cv_service = get_cv_service()
            result = await cv_service.load_cv()
            checks["cv_parsing_successful"] = result.success

            if result.success and result.cv:
                # Validate Dutch skills extraction
                dutch_skills = ["Kunstmatige intelligentie", "Natuurlijke taalverwerking", "RAG"]
                extracted_skills = [skill.name for skill in result.cv.skills]
                checks["dutch_skills_extracted"] = any(
                    skill in extracted_skills for skill in dutch_skills
                )

                # Test PDF extraction if PDF exists
                if checks["cv1_pdf_exists"] and result.source_format == "pdf":
                    checks["pdf_extraction_working"] = result.extraction_confidence > 0.7

        # Check matching service with real data
        matching_service = get_matching_service()
        checks["matching_service_available"] = matching_service is not None

    except Exception as e:
        logger.error(f"CV health check failed: {e}")

    return checks
```

## Performance Considerations (Updated)

### Optimization Strategies for Real Data
- **PDF Caching**: Cache extracted text from cv1.pdf to avoid re-parsing
- **Multi-Format Fallback**: Prioritize markdown when available for faster loading
- **Dutch Text Processing**: Optimize regex patterns for Dutch terminology
- **Skill Mapping Cache**: Cache Dutch-English skill translations
- **Experience Timeline Caching**: Pre-calculate experience years and timelines
- **Job Matching Optimization**: Pre-compute skill vectors for faster matching
- **File System Monitoring**: Watch cv1.pdf/md for changes to invalidate cache

### Real-World Performance Targets
- **CV Parsing**: <2 seconds for cv1.pdf (5-page document)
- **Job Matching**: <500ms for scoring against 10 jobs
- **Skills Extraction**: <100ms for Dutch text processing
- **Cache Hit Rate**: >90% for repeated CV access
- **Memory Usage**: <50MB for parsed CV data in memory

## Implementation Insights Based on Real Data

### Key Findings from cv1.md Analysis
1. **CV Structure**: Dutch CVs follow a specific pattern with personal info header, introduction, skills list, chronological experience, education, and detailed role descriptions
2. **Mixed Languages**: Technical skills mix Dutch and English terms requiring translation mappings
3. **Date Formats**: Dutch format MM/YYYY with "heden" for current roles needs special parsing
4. **Industry Focus**: Government sector and AI/tech specialization common in Dutch market
5. **Experience Depth**: Detailed role descriptions provide rich context for matching

### Updated Implementation Priorities
1. **Phase 1**: Multi-format CV parsing (PDF primary, Markdown fallback)
2. **Phase 2**: Dutch text processing and terminology handling
3. **Phase 3**: Real job matching against data/jobs/*.md files
4. **Phase 4**: API integration and caching optimization
5. **Phase 5**: Performance tuning and error handling

### Success Metrics
- [ ] Successfully parse cv1.pdf with >95% accuracy
- [ ] Extract all skills from cv1.md with Dutch-English mapping
- [ ] Calculate meaningful match scores against existing job data
- [ ] Handle PDF extraction with graceful fallbacks
- [ ] Process Dutch dates and terminology correctly
- [ ] Maintain <2 second response time for CV parsing
- [ ] Achieve >90% test coverage on real data scenarios

## Conclusion

This updated Task 1.4 specification reflects the actual CV data structure and Dutch market requirements discovered through analysis of the real cv1.pdf and cv1.md files. The implementation will focus on:

1. **Multi-format support** with PDF as primary source and markdown fallback
2. **Dutch language processing** for terminology, dates, and cultural context
3. **Real-world job matching** against the existing job data in data/jobs/
4. **Robust error handling** for PDF extraction and parsing challenges
5. **Performance optimization** for production readiness

The task provides a realistic foundation for implementing a CV data management system that can effectively process Thomas van der Meer's actual CV and match it against Dutch job market opportunities.
