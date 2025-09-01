# Project overview

This project is an application that polls a job board on new job openings.
It checks if the job opening is applicable to the user based on their preferences.
If so, the application writes a motivation letter and notifies the user if it want to send out the application.

## Frameworks and technologies used
- Python
- FastAPI
- LangChain
- Azure OpenAI service
- Uv package management

## coding standards and linting
- ruff

## testing
All the code is tested with unit tests using:
- pytest

## git
- pre-commit hooks are used to ensure code quality and consistency before committing changes to the repository.
- This consists out of a ruff linter check and a pytest run.
If the checks succeed, make the commit through the github cli.
Make frequent commits with clear messages.
When a concrete feature is done and tested, make a pull request from the feature branch to dev.
Work on branches from a dev branch and make pull requests to merge into dev. NEVER MERGE INTO MAIN.

## Azure
- Azure OpenAI service is used for generating motivation letters.
Azure openai is used through managed identity, so use the managed identity of the azure resource to access the service. Make sure your run `az login` to authenticate your azure cli.
you are working with the 'rag-cog' openai service instance, located in the 'generic-rag' resource group in the 'Sogeti AI Team' subscription.

## updating the copilot instructions
- The copilot instructions are located in the .github/copilot-instructions.md file.
- To ensure this file is up to date, make additions and changes based on implementations in the project.
