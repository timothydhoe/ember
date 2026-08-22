# Alight

[![ember tool](https://img.shields.io/static/v1?label=&message=ember%20tool&color=0B162D&style=flat-square)](https://github.com/timothydhoe/ember)

Alight is ember's source of truth for brand colours and its identity.
Other tools consume generated artifacts from it rather than duplicating the values.


---
## source files

`schemes/alight.yml` for ember's colour palette, ANSI mapping and semantic roles.
`identity.yml` for typography, logo references and which tool gets assigned which colour accent.


---
## scripts (tba)

`export_*` produces a file from the yaml.
`live_*` talk to whatever terminal you're sitting in right now
`validate_identity` for pure data check`

**status**: functional, actively maintained - scripts run end-to-end (`uv run scripts/generate_all.py`); no packaged CLI yet.
