# Evidence: real end-to-end screenshots and videos in the dossier

Read from `dossier.md` when the change touches a UI flow or the repository ships an end-to-end harness.

1. Find the harness. `sh <plugin root>/scripts/checks.sh <ui path>` (`<plugin root>` is the parent of the `skills/` directory this file lives in) prints `e2e=` for Playwright and Cypress; otherwise look for Detox, Maestro, `docker-compose` or an `e2e/` folder under the touched projects. None: the dossier says so once, under "Fuori dal perimetro", and no picture is faked.

2. Run it from the worktree at HEAD, for the affected projects, with the configuration the repository already uses. Success records nothing by default, so turn recording on through the harness's own switch, never by editing the committed config:
   - Playwright: a scratch `playwright.evidence.config.ts` beside the real one, `export default defineConfig({ ...base, use: { ...base.use, screenshot: 'on', video: 'on' } })`, run with `npx playwright test -c playwright.evidence.config.ts`, delete the scratch file after; artifacts land in `test-results/` or the `outputDir` the config names.
   - Cypress: `npx cypress run --config video=true`; artifacts in `cypress/videos` and `cypress/screenshots`.
   - Other harnesses: the recording option their documentation names, else the failure screenshots they already take.

3. Select one artifact per changed UI flow: the last passing run's, named for the flow (`checkout-payment.png`, `login.webm`). A failure screenshot is evidence too when the same failure reproduces on the merge-base: attach it with that attribution. A screenshot above 1 MB or a video above 10 MB is linked, not embedded.

4. Redact before attaching. A screenshot shows real data: run against the fixtures the harness ships, and drop any frame with a token, a password, a connection string or personal data; name the flow in the prova line instead.

5. Attach where the forge can host it, and write the link in the domain's prova line:
   - GitLab: `glab api projects/:id/uploads -F file=@<path>` returns `markdown`; paste it.
   - Azure DevOps: `POST https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/{id}/attachments/{name}?api-version=7.1` with `Content-Type: application/octet-stream` and the file as body (`az rest` or `curl` with the PAT the CLI already holds); the response `url` goes in `![flow](url)`.
   - GitHub: the CLI cannot upload attachments. In order: a tree where the repository already keeps evidence files (`docs/evidence/`, `screenshots/`) gets them in the PR branch, linked by their blob URL with `?raw=true`; a CI job that already publishes the report or Pages gets linked; otherwise the files stay in the session scratch directory, their paths listed under "Fuori dal perimetro" for the author to drag into the PR by hand. Never commit binaries into a repository that does not already keep them.
   - `--dossier` alone, no PR: link the local paths.

6. One prova line per artifact: `<flow> - <harness command> - <passed n/n> - <link>`. No caption prose; the picture is the evidence, the line says what produced it.
