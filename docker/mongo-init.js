// MongoDB initialization script
// This runs when MongoDB container is first created

// Switch to the application database
db = db.getSiblingDB('sentimatrix_studio');

// Create collections with schema validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'password_hash', 'created_at'],
      properties: {
        email: {
          bsonType: 'string',
          description: 'User email address'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Hashed password'
        },
        full_name: {
          bsonType: 'string',
          description: 'User full name'
        },
        is_active: {
          bsonType: 'bool',
          description: 'Account active status'
        },
        is_verified: {
          bsonType: 'bool',
          description: 'Email verification status'
        },
        role: {
          enum: ['user', 'admin'],
          description: 'User role'
        },
        created_at: {
          bsonType: 'date',
          description: 'Account creation timestamp'
        }
      }
    }
  }
});

// Create indexes for users
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ created_at: -1 });
// Sparse indexes for OAuth providers (only index documents that have these fields)
db.users.createIndex({ 'oauth.google_id': 1 }, { sparse: true, unique: true });
db.users.createIndex({ 'oauth.github_id': 1 }, { sparse: true, unique: true });

// Create projects collection
db.createCollection('projects');
db.projects.createIndex({ user_id: 1 });
db.projects.createIndex({ user_id: 1, status: 1 });
db.projects.createIndex({ created_at: -1 });
db.projects.createIndex({ 'config.schedule.next_run_at': 1 });

// Create targets collection
db.createCollection('targets');
db.targets.createIndex({ project_id: 1 });
db.targets.createIndex({ project_id: 1, status: 1 });
db.targets.createIndex({ user_id: 1 });
db.targets.createIndex({ url: 1 });

// Create results collection
db.createCollection('results');
db.results.createIndex({ project_id: 1, created_at: -1 });
db.results.createIndex({ target_id: 1, created_at: -1 });
db.results.createIndex({ user_id: 1 });
db.results.createIndex({ scrape_job_id: 1 });
db.results.createIndex({ 'analysis.sentiment.label': 1 });
db.results.createIndex({ 'content.date': -1 });
db.results.createIndex({ platform: 1 });
db.results.createIndex(
  { 'content.text': 'text', 'content.title': 'text' },
  { default_language: 'english', weights: { 'content.title': 10, 'content.text': 5 } }
);

// Create scrape_jobs collection
db.createCollection('scrape_jobs');
db.scrape_jobs.createIndex({ project_id: 1, created_at: -1 });
db.scrape_jobs.createIndex({ user_id: 1 });
db.scrape_jobs.createIndex({ status: 1 });
db.scrape_jobs.createIndex({ created_at: -1 });

// Create schedules collection
db.createCollection('schedules');
db.schedules.createIndex({ project_id: 1 }, { unique: true });
db.schedules.createIndex({ user_id: 1 });
db.schedules.createIndex({ enabled: 1, next_run: 1 });

// Create api_keys collection
db.createCollection('api_keys');
db.api_keys.createIndex({ user_id: 1 });
db.api_keys.createIndex({ user_id: 1, provider: 1 });

// Create webhooks collection
db.createCollection('webhooks');
db.webhooks.createIndex({ user_id: 1 });
db.webhooks.createIndex({ enabled: 1, events: 1 });

// Create webhook_deliveries collection with TTL
db.createCollection('webhook_deliveries');
db.webhook_deliveries.createIndex({ webhook_id: 1, created_at: -1 });
db.webhook_deliveries.createIndex({ user_id: 1 });
db.webhook_deliveries.createIndex({ status: 1 });
db.webhook_deliveries.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 604800 } // 7 days TTL
);

// Create audit_logs collection with TTL
db.createCollection('audit_logs');
db.audit_logs.createIndex({ user_id: 1, created_at: -1 });
db.audit_logs.createIndex({ event_type: 1 });
db.audit_logs.createIndex({ created_at: -1 });
db.audit_logs.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 31536000 } // 1 year TTL
);

// Create refresh_tokens collection with TTL
db.createCollection('refresh_tokens');
db.refresh_tokens.createIndex({ user_id: 1 });
db.refresh_tokens.createIndex({ token: 1 }, { unique: true });
db.refresh_tokens.createIndex(
  { expires_at: 1 },
  { expireAfterSeconds: 0 }
);

// Create presets collection for custom user presets
db.createCollection('presets');
db.presets.createIndex({ user_id: 1 });
db.presets.createIndex({ user_id: 1, name: 1 }, { unique: true });
db.presets.createIndex({ created_at: -1 });

print('MongoDB initialization completed successfully!');
print('Collections created: users, projects, targets, results, scrape_jobs, schedules, api_keys, webhooks, webhook_deliveries, audit_logs, refresh_tokens, presets');
