# Task 1.2: Azure Integration Setup

## Objective
Configure Azure services integration, specifically Azure OpenAI service connection with managed identity authentication.

## Tasks Breakdown

### 1.2.1 Azure CLI Authentication Setup
- [ ] Verify Azure CLI installation
- [ ] Run `az login` to authenticate
- [ ] Verify access to 'Sogeti AI Team' subscription
- [ ] Set default subscription if needed
- [ ] Test CLI access to target resource group 'generic-rag'

### 1.2.2 Azure OpenAI Service Configuration
- [ ] Verify access to 'rag-cog' OpenAI service instance
- [ ] Document service endpoints and model deployments
- [ ] Identify available models (GPT-4, GPT-3.5-turbo, etc.)
- [ ] Test basic connectivity to the service
- [ ] Document API version and capabilities

### 1.2.3 Managed Identity Implementation
- [ ] Research Azure managed identity best practices
- [ ] Implement Azure credential chain for local development
- [ ] Configure DefaultAzureCredential for production
- [ ] Set up environment-specific authentication
- [ ] Test managed identity token acquisition

### 1.2.4 Azure SDK Integration
- [ ] Install required Azure packages:
  - `azure-identity`
  - `azure-ai-openai`
  - `azure-core`
- [ ] Create Azure service client wrapper
- [ ] Implement error handling for Azure service calls
- [ ] Add retry logic and circuit breaker patterns
- [ ] Configure logging for Azure operations

### 1.2.5 Configuration Management
- [ ] Create Azure-specific configuration classes
- [ ] Set up environment variable management
- [ ] Implement secure credential storage
- [ ] Create configuration validation
- [ ] Add environment-specific overrides

## Deliverables
1. Working Azure CLI authentication
2. Functional Azure OpenAI service connection
3. Proper managed identity implementation
4. Azure SDK integration wrapper
5. Secure configuration management

## Acceptance Criteria
- [ ] Can successfully authenticate to Azure
- [ ] Can connect to 'rag-cog' OpenAI service
- [ ] Managed identity works in both local and production environments
- [ ] Azure SDK calls work with proper error handling
- [ ] Configuration is secure and environment-aware

## Dependencies
- Task 1.1 (Project Setup) completed
- Azure subscription access
- Proper permissions to 'generic-rag' resource group
- Azure CLI installed

## Estimated Time
**2-3 days**

## Security Considerations
- Never commit Azure credentials to version control
- Use managed identity in production
- Implement proper token caching
- Add audit logging for Azure service calls
- Follow Azure security best practices

## Files to Create/Modify
```
src/job_agent/
├── services/
│   ├── __init__.py
│   ├── azure_client.py
│   └── openai_service.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── auth.py
└── utils/
    ├── __init__.py
    └── azure_utils.py

tests/
├── unit/
│   ├── test_azure_client.py
│   └── test_config.py
└── integration/
    └── test_azure_integration.py
```

## Configuration Example
```python
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://rag-cog.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_RESOURCE_GROUP = "generic-rag"
AZURE_SUBSCRIPTION = "Sogeti AI Team"
```

## Testing Strategy
- Unit tests for configuration classes
- Integration tests for Azure service connectivity
- Mock Azure services for local testing
- End-to-end tests for authentication flow
- Performance tests for service calls

## Troubleshooting Checklist
- [ ] Azure CLI authenticated and configured
- [ ] Correct subscription selected
- [ ] Proper permissions to OpenAI service
- [ ] Network connectivity to Azure services
- [ ] Environment variables properly set
- [ ] Managed identity configured correctly
