# Module 5 Database Least-Privilege Evidence

The Grad Cafe app is not read-only. The Flask page includes a Pull Data button that triggers the loader and writes newly scraped applicant rows into the PostgreSQL `applicants` table. Because the app both reads analysis results and inserts new rows, the application database user needs `SELECT` and `INSERT` permissions.

## Database User

The least-privilege application user is:

```text
gradcafe_app
```

This role is configured as a login role, but it is not a superuser and cannot create databases, create roles, replicate data, or create objects in the public schema.

Verified role attributes:

```text
gradcafe_app | rolsuper=false | rolcreatedb=false | rolcreaterole=false | rolreplication=false | rolcanlogin=true
```

## Permissions Granted and Why

```text
CONNECT on gradcafe_db
```

Allows the app user to connect to the application database.

```text
USAGE on schema public
```

Allows the app user to access objects inside the public schema.

```text
SELECT on public.applicants
```

Required for the analysis page to read rows and compute summary answers.

```text
INSERT on public.applicants
```

Required because the Pull Data button loads new applicant rows into the database.

The app user was not granted `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`, `ALTER`, table ownership, superuser, createdb, or createrole privileges.

Verified table privileges:

```text
SELECT=true
INSERT=true
UPDATE=false
DELETE=false
TRUNCATE=false
CREATE on public schema=false
```

The `applicants` table owner remains the local admin/developer role, not `gradcafe_app`, so the application user does not have owner-level permissions.

## SQL Snippet Used

```sql
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gradcafe_app') THEN
        CREATE ROLE gradcafe_app LOGIN PASSWORD 'local-password-not-committed';
    END IF;
END
$$;

ALTER ROLE gradcafe_app NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT CONNECT ON DATABASE gradcafe_db TO gradcafe_app;
GRANT USAGE ON SCHEMA public TO gradcafe_app;
REVOKE CREATE ON SCHEMA public FROM gradcafe_app;
GRANT SELECT, INSERT ON TABLE public.applicants TO gradcafe_app;
```

The real local password is not committed to the repository. The repository includes `.env.example` with placeholder values only, and `.env` is ignored by Git.
