# Wildfire

[![ember tool](https://img.shields.io/static/v1?label=&message=ember%20tool&color=0B162D&style=flat-square)](https://github.com/timothydhoe/ember)

Plain markdown notes; part of the ember toolkit.
*A note-taking app that lets you catch your wisps and turns them into sparks.*

- **wisps**: fast, timestamped daily notes.
- **sparks**: durable notes.

Link anything to a *spark* by writing `[[a phrase]]` in a wisp or another spark. You can even do that before the spark exists!

Everything's plain markdown, readable with or without *wildfire* installed.

---
## Installation

```bash
uv tool install --editable .
uv tool update-shell
```
(from inside `wildfire/` - editable, so changes to source are picked up without reinstalling)

see the [uv tools guide](https://docs.astral.sh/uv/guides/tools/) and [uv tools concepts](https://docs.astral.sh/uv/concepts/tools/) for details, as well as [PEP 660](https://peps.python.org/pep-0660/)

---

**status**: installable, in active development. See [ARCHITECTURE.md](ARCHITECTURE.md)
