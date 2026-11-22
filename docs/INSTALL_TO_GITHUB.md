# Install BLUE AI into your GitHub repository (phone-friendly)

This ZIP intentionally excludes `.github/` workflows because the original ZIP installer protects that folder from overwrite. It includes workflow source copies in `docs/automation/`.

## Recommended install
1. Download and extract this ZIP locally on your phone.
2. In your GitHub repo, open `incoming/` and upload the extracted project files as a ZIP archive of the project contents. The ZIP must not contain a `.github` folder or `incoming/` folder. This release archive is prepared that way.
3. Commit the ZIP. Wait for Actions → BLUE AI ZIP Installer to run.
4. The installer extracts app and docs files into repository root, strips the common outer folder if present, and commits.
5. Open the Actions tab and inspect the installer job. The repository's existing installer may not accept every file type. If it rejects an extension, install the listed files directly via GitHub web upload or replace the workflow with the updated source in `docs/automation/blue-ai-upload-workflow.yml` (create the file at `.github/workflows/blue-ai-upload.yml` and paste the source).

## Replace the installer if necessary
Open `.github/workflows/blue-ai-upload.yml` in GitHub, Edit, select all, and replace with the version in `docs/automation/blue-ai-upload-workflow.yml`. Commit. This version includes safer ZIP checks and ignores workflows in uploaded ZIPs rather than installing them.
