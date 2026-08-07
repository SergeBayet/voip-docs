# voip-docs
Internal/shared VoIP documentation

## Publication is blocked pending approval

The onboarding course is internal-only. The current repository and GitHub Pages
site are public; a page warning does not provide access control. The Pages workflow
therefore fails before building or uploading an artifact, including manual runs.
Do not remove that guard until the owner approves both the repository access
policy and the hosting destination. A private repository alone does not prove
that a Pages site requires authentication.

This local guard does not unpublish the existing site or conceal already-pushed
branches. Those remote changes require explicit authorization. Local builds and
the offline course remain available.

## Getting Started

You can either:
- configure your own python environment, see `requirements.txt`
- or use [mise-en-place](https://mise.jdx.dev/) then run `mise trust && mise install`.

Once your python env is ready with all dependencies installed,
run: `mkdocs serve --livereload` to start the local development server.
