# Mimic DB Server setup

In order to use the GenerateFHIRFromMimic Nifi processor, an existing Mimic DB Server needs to be setup and accessible.  This can be done by following the instructions on the [Mimic website](https://mimic.physionet.org/), but below is a short-hand version for a quick deployment.

**Note**: Mimic2FHIR currently assumes the Mimic db server will be hosted on a PostgreSQL server.

### Prerequisites

The following must be available on your system:

- [PSQL CLI](https://www.postgresql.org/download/windows/) - This will allow command-line access to load data into the PostgreSQL db.
- Mimic DB files:
    * [Demo files](https://physionet.org/content/mimiciii-demo/1.4/) 
    * [Full database](https://mimic.physionet.org/gettingstarted/dbsetup/) - Requires onboarding and approval to access.
- [Mimic Code Repository](https://github.com/MIT-LCP/mimic-code) - This provides scripts for loading data into tables

### Steps

#### Deploy new PostgreSQL db on kubernetes
1. Connect to your kubernetes cluster and target namespace.
1. Run: `kubectl apply -f "mimic_postgres.yaml"`

1. Switch directories to the Mimic Code Repository listed in the pre-req section.
1. From a command line, connect to your deployed PostgreSQL db using: `psql -h <<POSTGRESQL_SERVICE_SERVER_NAME>> -p 5432 -U mimic_user -d mimic`
1. Enter the password setup for your database (default: mimic_passw0rd)
1. Run: `DROP DATABASE IF EXISTS mimic;`
1. Run: `CREATE DATABASE mimic OWNER mimic_user;`
1. Run: `\c mimic;`
1. Run: `CREATE SCHEMA mimic;`
1. Run: `set search_path to mimic;`
1. Run: `\i postgres_create_tables.sql`
1. Run: `\set ON_ERROR_STOP 1`
1. Run: `\set mimic_data_dir '<<MIMIC_DB_FILES_DIRECTORY>>'`
1. Run: `\i <<MIMIC_CODE_REPOSITORY_DIRECTORY>>/buildmimic/postgres/postgres_load_data.sql`
1. Run: `\i <<MIMIC_CODE_REPOSITORY_DIRECTORY>>/buildmimic/postgres/postgres_add_indexes.sql`

You can then verify that everything loaded successfully by running one or more of the following queries:
- `select icustay_id, intime, outtime from icustays limit 10;`
- `\i <<MIMIC_CODE_REPOSITORY_DIRECTORY>>/buildmimic/postgres/postgres_checks.sql`
- `\i <<MIMIC_CODE_REPOSITORY_DIRECTORY>>/buildmimic/postgres/postgres_add_comments.sql`