# Project Overview: Job Board Polling Application

## Purpose
This application polls job boards for new job openings, evaluates them against user preferences, and automatically generates motivation letters using Azure OpenAI when suitable matches are found.

## Key Features
- **Job Board Polling**: Automated monitoring of job postings
- **Preference Matching**: Intelligent filtering based on user criteria
- **AI-Powered Letter Generation**: Automated motivation letter creation
- **User Notification**: Alert system for potential applications
- **Application Management**: User approval workflow for sending applications

## Technology Stack
- **Backend**: Python with FastAPI
- **AI/ML**: LangChain + Azure OpenAI Service
- **Package Management**: UV
- **Code Quality**: Ruff (linting)
- **Testing**: Pytest
- **Version Control**: Git with pre-commit hooks
- **Cloud**: Azure (Managed Identity authentication)

## Azure Resources
- **OpenAI Service**: 'rag-cog' instance
- **Resource Group**: 'generic-rag'
- **Subscription**: 'Sogeti AI Team'
- **Authentication**: Managed Identity

## Development Workflow
- Feature branches from `dev`
- Pre-commit hooks (ruff + pytest)
- Pull requests to `dev` (NEVER to `main`)
- Frequent commits with clear messages
- GitHub CLI for commits after successful checks

## Success Criteria
1. Successfully polls job boards automatically
2. Accurately matches jobs to user preferences
3. Generates high-quality motivation letters
4. Provides seamless user approval workflow
5. Maintains high code quality and test coverage
