"""Single source of truth for the engine version.

Avoids version drift across modules (main, schemas, routes, n8n envelope) — bump
this one constant on a release. Reported in the API (`engine_version`, /health),
the OpenAPI metadata, the root discovery endpoint, and the n8n webhook envelope.
"""

ENGINE_VERSION = "2.2.0"
