/**
 * GitHub Projects v2 GraphQL Helper Functions
 * 
 * These functions handle all GraphQL operations for managing GitHub Projects v2.
 * Used by various workflows to interact with project boards.
 */

const { graphql } = require('@octokit/graphql');

class ProjectV2Manager {
  constructor(token) {
    this.graphqlWithAuth = graphql.defaults({
      headers: {
        authorization: `token ${token}`,
      },
    });
  }

  /**
   * Get the first project for a repository
   */
  async getProject(owner, repo) {
    const query = `
      query GetProject($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
          projectsV2(first: 1) {
            nodes {
              id
              title
              number
              fields(first: 20) {
                nodes {
                  ... on ProjectV2Field {
                    id
                    name
                    dataType
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    dataType
                    options {
                      id
                      name
                    }
                  }
                  ... on ProjectV2IterationField {
                    id
                    name
                    dataType
                  }
                }
              }
            }
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(query, { owner, repo });
      const project = result.repository.projectsV2.nodes[0];
      
      if (!project) {
        throw new Error('No project found for repository');
      }

      // Parse fields for easy access
      project.fieldsByName = {};
      project.fields.nodes.forEach(field => {
        project.fieldsByName[field.name] = field;
      });

      return project;
    } catch (error) {
      console.error('Failed to get project:', error.message);
      throw error;
    }
  }

  /**
   * Create a new project for a repository
   */
  async createProject(owner, repo, title = 'Development Board') {
    // First get the repository ID
    const repoQuery = `
      query GetRepoId($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
          id
        }
      }
    `;

    const repoResult = await this.graphqlWithAuth(repoQuery, { owner, repo });
    const repositoryId = repoResult.repository.id;

    // Create the project
    const createMutation = `
      mutation CreateProject($ownerId: ID!, $title: String!) {
        createProjectV2(input: {
          ownerId: $ownerId,
          title: $title
        }) {
          projectV2 {
            id
            number
            url
          }
        }
      }
    `;

    // Note: ownerId should be the organization or user ID, not repo ID
    // This is a simplified version - in practice, you'd need to get the org/user ID
    const result = await this.graphqlWithAuth(createMutation, {
      ownerId: repositoryId, // This might need adjustment based on your setup
      title
    });

    return result.createProjectV2.projectV2;
  }

  /**
   * Add an issue to the project
   */
  async addIssueToProject(projectId, issueNodeId) {
    const mutation = `
      mutation AddIssueToProject($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {
          projectId: $projectId,
          contentId: $contentId
        }) {
          item {
            id
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(mutation, {
        projectId,
        contentId: issueNodeId
      });
      return result.addProjectV2ItemById.item;
    } catch (error) {
      console.error('Failed to add issue to project:', error.message);
      throw error;
    }
  }

  /**
   * Update a single-select field (like Status)
   */
  async updateSingleSelectField(projectId, itemId, fieldId, optionId) {
    const mutation = `
      mutation UpdateProjectField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
        updateProjectV2ItemFieldValue(input: {
          projectId: $projectId,
          itemId: $itemId,
          fieldId: $fieldId,
          value: $value
        }) {
          projectV2Item {
            id
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(mutation, {
        projectId,
        itemId,
        fieldId,
        value: {
          singleSelectOptionId: optionId
        }
      });
      return result.updateProjectV2ItemFieldValue.projectV2Item;
    } catch (error) {
      console.error('Failed to update field:', error.message);
      throw error;
    }
  }

  /**
   * Update a text field
   */
  async updateTextField(projectId, itemId, fieldId, text) {
    const mutation = `
      mutation UpdateProjectTextField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
        updateProjectV2ItemFieldValue(input: {
          projectId: $projectId,
          itemId: $itemId,
          fieldId: $fieldId,
          value: $value
        }) {
          projectV2Item {
            id
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(mutation, {
        projectId,
        itemId,
        fieldId,
        value: {
          text
        }
      });
      return result.updateProjectV2ItemFieldValue.projectV2Item;
    } catch (error) {
      console.error('Failed to update text field:', error.message);
      throw error;
    }
  }

  /**
   * Update a number field (like story points)
   */
  async updateNumberField(projectId, itemId, fieldId, number) {
    const mutation = `
      mutation UpdateProjectNumberField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
        updateProjectV2ItemFieldValue(input: {
          projectId: $projectId,
          itemId: $itemId,
          fieldId: $fieldId,
          value: $value
        }) {
          projectV2Item {
            id
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(mutation, {
        projectId,
        itemId,
        fieldId,
        value: {
          number
        }
      });
      return result.updateProjectV2ItemFieldValue.projectV2Item;
    } catch (error) {
      console.error('Failed to update number field:', error.message);
      throw error;
    }
  }

  /**
   * Create a custom field on the project
   */
  async createSingleSelectField(projectId, name, options) {
    const mutation = `
      mutation CreateField($projectId: ID!, $input: ProjectV2FieldInput!) {
        createProjectV2Field(input: {
          projectId: $projectId,
          field: $input
        }) {
          field {
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
              }
            }
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(mutation, {
        projectId,
        input: {
          name,
          dataType: 'SINGLE_SELECT',
          singleSelectOptions: options.map(opt => ({ name: opt }))
        }
      });
      return result.createProjectV2Field.field;
    } catch (error) {
      console.error('Failed to create field:', error.message);
      throw error;
    }
  }

  /**
   * Get all items in a project
   */
  async getProjectItems(projectId) {
    const query = `
      query GetProjectItems($projectId: ID!) {
        node(id: $projectId) {
          ... on ProjectV2 {
            items(first: 100) {
              nodes {
                id
                content {
                  ... on Issue {
                    id
                    number
                    title
                    state
                    labels(first: 10) {
                      nodes {
                        name
                      }
                    }
                  }
                }
                fieldValues(first: 10) {
                  nodes {
                    ... on ProjectV2ItemFieldTextValue {
                      text
                      field {
                        ... on ProjectV2Field {
                          name
                        }
                      }
                    }
                    ... on ProjectV2ItemFieldNumberValue {
                      number
                      field {
                        ... on ProjectV2Field {
                          name
                        }
                      }
                    }
                    ... on ProjectV2ItemFieldSingleSelectValue {
                      name
                      field {
                        ... on ProjectV2SingleSelectField {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    `;

    try {
      const result = await this.graphqlWithAuth(query, { projectId });
      return result.node.items.nodes;
    } catch (error) {
      console.error('Failed to get project items:', error.message);
      throw error;
    }
  }

  /**
   * Helper: Add issue and set initial status
   */
  async addIssueWithStatus(projectId, issueNodeId, statusFieldId, statusOptionId) {
    // Add issue to project
    const item = await this.addIssueToProject(projectId, issueNodeId);
    
    // Set status
    if (statusFieldId && statusOptionId) {
      await this.updateSingleSelectField(projectId, item.id, statusFieldId, statusOptionId);
    }
    
    return item;
  }

  /**
   * Helper: Setup default project fields
   */
  async setupDefaultFields(projectId) {
    const fields = [];

    // Create Status field
    try {
      const statusField = await this.createSingleSelectField(projectId, 'Status', [
        'Todo',
        'In Progress',
        'In Review',
        'Blocked',
        'Done'
      ]);
      fields.push(statusField);
    } catch (error) {
      console.log('Status field might already exist:', error.message);
    }

    // Create Priority field
    try {
      const priorityField = await this.createSingleSelectField(projectId, 'Priority', [
        'High',
        'Medium',
        'Low'
      ]);
      fields.push(priorityField);
    } catch (error) {
      console.log('Priority field might already exist:', error.message);
    }

    // Create Risk field
    try {
      const riskField = await this.createSingleSelectField(projectId, 'Risk', [
        'Low',
        'Medium',
        'High'
      ]);
      fields.push(riskField);
    } catch (error) {
      console.log('Risk field might already exist:', error.message);
    }

    return fields;
  }
}

// Export for use in GitHub Actions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProjectV2Manager;
}

// CLI interface for testing
if (require.main === module) {
  const token = process.env.GITHUB_TOKEN || process.env.PROJECT_TOKEN;
  const [owner, repo] = (process.env.GITHUB_REPOSITORY || '').split('/');
  
  if (!token || !owner || !repo) {
    console.error('Missing required environment variables: GITHUB_TOKEN/PROJECT_TOKEN and GITHUB_REPOSITORY');
    process.exit(1);
  }

  const manager = new ProjectV2Manager(token);
  
  // Example usage
  (async () => {
    try {
      const project = await manager.getProject(owner, repo);
      console.log('Project found:', project.title);
      console.log('Fields:', Object.keys(project.fieldsByName));
    } catch (error) {
      console.error('Error:', error.message);
    }
  })();
}