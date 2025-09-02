# Task 1.2: Azure OpenAI Integration Setup

## Objective
Configure Azure OpenAI service connection using Pydantic settings from config.yaml and azure-identity for authentication.

## Tasks Breakdown

### 1.2.1 Azure CLI Authentication Setup
- [ ] Verify Azure CLI installation
- [ ] Run `az login` to authenticate
- [ ] Verify access to 'Sogeti AI Team' subscription
- [ ] Set default subscription if needed
- [ ] Test CLI access to target resource group 'generic-rag'

### 1.2.2 Configuration Management
- [ ] Create config.yaml file with Azure OpenAI settings
- [ ] Implement Pydantic settings classes for configuration
- [ ] Set up environment-specific config overrides
- [ ] Add configuration validation
- [ ] Document required configuration fields

### 1.2.3 Azure Identity Integration
- [ ] Install required packages:
  - `azure-identity`
  - `openai`
  - `pydantic-settings`
  - `pyyaml`
- [ ] Implement DefaultAzureCredential for authentication
- [ ] Create Azure OpenAI client with managed identity
- [ ] Test credential acquisition locally

### 1.2.4 OpenAI Service Integration
- [ ] Create OpenAI service wrapper using Azure credentials
- [ ] Implement basic chat completion functionality
- [ ] Add error handling for service calls
- [ ] Configure logging for operations
- [ ] Test connectivity to Azure OpenAI service

## Deliverables
1. Working Azure CLI authentication
2. Functional Azure OpenAI service connection
3. Pydantic settings classes for configuration management
4. config.yaml file with Azure OpenAI settings
5. OpenAI service wrapper with Azure identity authentication

## Acceptance Criteria
- [ ] Can successfully authenticate to Azure using DefaultAzureCredential
- [ ] Can connect to Azure OpenAI service using settings from config.yaml
- [ ] Pydantic settings validate configuration properly
- [ ] OpenAI service calls work with proper error handling
- [ ] Configuration supports environment-specific overrides

## Dependencies
- Task 1.1 (Project Setup) completed
- Azure subscription access
- Proper permissions to 'generic-rag' resource group
- Azure CLI installed

## Estimated Time
**2-3 days**

## Security Considerations
- Never commit Azure credentials to version control
- Use DefaultAzureCredential for authentication
- Store sensitive configuration in environment variables
- Add audit logging for OpenAI service calls
- Follow Azure security best practices

## Files to Create/Modify
```
config.yaml                    # Configuration file with Azure OpenAI settings

src/job_agent/
├── services/
│   ├── __init__.py
│   └── openai_service.py     # OpenAI service wrapper
├── core/
│   ├── __init__.py
│   └── config.py             # Pydantic settings classes
└── utils/
    ├── __init__.py
    └── azure_utils.py        # Azure credential utilities

tests/
├── unit/
│   ├── test_config.py        # Test configuration loading
│   └── test_openai_service.py # Test OpenAI service
└── integration/
    └── test_azure_openai.py  # Integration tests
```

## Configuration Example

### config.yaml
```yaml
azure_openai:
  endpoint: "https://rag-cog.openai.azure.com/"
  api_version: "2024-02-15-preview"
  deployment_name: "gpt-4"  # Model deployment name
  model: "gpt-4"
  max_tokens: 4096
  temperature: 0.7

azure:
  resource_group: "generic-rag"
  subscription: "Sogeti AI Team"
```

### Pydantic Settings Class
```python
from pydantic import BaseSettings
from typing import Optional

class AzureOpenAISettings(BaseSettings):
    endpoint: str
    api_version: str
    deployment_name: str
    model: str
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7

    class Config:
        env_prefix = "AZURE_OPENAI_"

class AzureSettings(BaseSettings):
    resource_group: str
    subscription: str

    class Config:
        env_prefix = "AZURE_"
```

## Testing Strategy
- Unit tests for Pydantic settings classes
- Unit tests for OpenAI service wrapper
- Integration tests for Azure OpenAI connectivity
- Mock Azure credentials for local testing
- End-to-end tests for authentication flow
- Configuration validation tests

## Troubleshooting Checklist
- [ ] Azure CLI authenticated and configured
- [ ] Correct subscription selected
- [ ] Proper permissions to OpenAI service
- [ ] Network connectivity to Azure services
- [ ] config.yaml file exists and is valid
- [ ] Environment variables properly set (if overriding config)
- [ ] DefaultAzureCredential can acquire tokens
