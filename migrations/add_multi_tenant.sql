-- =====================================================
-- MULTI-TENANT MIGRATION
-- Run this on your database
-- For SQLite (your current database)
-- =====================================================

-- 1. Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    license_number VARCHAR(100) UNIQUE,
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    subscription_status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMP,
    subscription_ends_at TIMESTAMP,
    max_staff INTEGER DEFAULT 10,
    max_patients INTEGER DEFAULT 500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 2. Create default organization for existing data
INSERT INTO organizations (name, subscription_status, is_active) 
VALUES ('Default Organization', 'active', 1);

-- 3. Add organization_id to users table
ALTER TABLE users ADD COLUMN organization_id INTEGER REFERENCES organizations(id);

-- 4. Update existing users to default organization
UPDATE users SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 5. Add organization_id to patients table
ALTER TABLE patients ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE patients SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 6. Add organization_id to fertility_entries
ALTER TABLE fertility_entries ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE fertility_entries SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 7. Add organization_id to mens_health_entries
ALTER TABLE mens_health_entries ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE mens_health_entries SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 8. Add organization_id to mens_health_intake
ALTER TABLE mens_health_intake ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE mens_health_intake SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 9. Add organization_id to womens_health_entries
ALTER TABLE womens_health_entries ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE womens_health_entries SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 10. Add organization_id to womens_health_intake
ALTER TABLE womens_health_intake ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE womens_health_intake SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 11. Add organization_id to prenatal_entries
ALTER TABLE prenatal_entries ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE prenatal_entries SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 12. Add organization_id to postnatal_entries
ALTER TABLE postnatal_entries ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE postnatal_entries SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 13. Add organization_id to lifelong_entries
ALTER TABLE lifelong_entries ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE lifelong_entries SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 14. Add organization_id to medical_records
ALTER TABLE medical_records ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
UPDATE medical_records SET organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');

-- 15. Create indexes for performance
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_patients_organization_id ON patients(organization_id);
CREATE INDEX idx_fertility_entries_organization_id ON fertility_entries(organization_id);
CREATE INDEX idx_mens_health_entries_organization_id ON mens_health_entries(organization_id);
CREATE INDEX idx_womens_health_entries_organization_id ON womens_health_entries(organization_id);
CREATE INDEX idx_prenatal_entries_organization_id ON prenatal_entries(organization_id);
CREATE INDEX idx_postnatal_entries_organization_id ON postnatal_entries(organization_id);
CREATE INDEX idx_lifelong_entries_organization_id ON lifelong_entries(organization_id);
CREATE INDEX idx_medical_records_organization_id ON medical_records(organization_id);