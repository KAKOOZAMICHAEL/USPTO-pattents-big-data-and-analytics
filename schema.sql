CREATE TABLE IF NOT EXISTS patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    filing_date TEXT,
    publication_date TEXT,
    main_classification TEXT,
    cpc_section TEXT
);

CREATE TABLE IF NOT EXISTS inventors (
    inventor_id TEXT PRIMARY KEY,
    full_name TEXT,
    country TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT
);

CREATE TABLE IF NOT EXISTS patent_inventors (
    patent_id TEXT,
    inventor_id TEXT,
    PRIMARY KEY (patent_id, inventor_id)
);

CREATE TABLE IF NOT EXISTS patent_companies (
    patent_id TEXT,
    company_id TEXT,
    PRIMARY KEY (patent_id, company_id)
);

CREATE TABLE IF NOT EXISTS g_abstract (
    patent_id TEXT PRIMARY KEY,
    abstract TEXT
);

CREATE TABLE IF NOT EXISTS patent_yearly_summary (
    year INTEGER,
    cpc_section TEXT,
    country TEXT,
    count INTEGER
);

CREATE TABLE IF NOT EXISTS company_yearly_summary (
    year INTEGER,
    company_id TEXT,
    count INTEGER,
    type TEXT
);

CREATE TABLE IF NOT EXISTS monthly_volume_summary (
    month TEXT,
    count INTEGER
);

CREATE INDEX idx_patents_filing_date ON patents(filing_date);
CREATE INDEX idx_patents_cpc ON patents(cpc_section);
CREATE INDEX idx_inventors_country ON inventors(country);
CREATE INDEX idx_patent_inventors_inv ON patent_inventors(inventor_id);
CREATE INDEX idx_patent_companies_comp ON patent_companies(company_id);
