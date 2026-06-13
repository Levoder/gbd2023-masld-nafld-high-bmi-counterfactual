# Upload instructions

Recommended route: GitHub for versioned code/source-data + Zenodo for a citable DOI.

## GitHub web route

1. Create a new repository at https://github.com/new.
2. Name suggestion: `gbd2023-masld-nafld-high-bmi-counterfactual`.
3. Choose `Private` during internal checking or `Public` when ready for journal submission.
4. Upload the contents of this folder, not the parent `lrhwp_revision` folder.
5. Add a repository description: `Derived data, source figures, QC logs, and scripts for a GBD 2023 MASLD/NAFLD-related liver burden counterfactual analysis.`

## Command-line route after creating the empty GitHub repository

```powershell
cd "<path-to-public_repository_package>"
git status
git add .
git commit -m "Prepare reproducibility package for manuscript submission"
git remote add origin https://github.com/<OWNER>/gbd2023-masld-nafld-high-bmi-counterfactual.git
git push -u origin main
```

## Zenodo DOI route

1. Log in to Zenodo with GitHub.
2. Enable the GitHub repository in Zenodo.
3. Make a GitHub release, for example `v0.1.1-submission`.
4. Zenodo will archive the release and mint a DOI.
5. Add the DOI badge and citation to `README.md`, then update the manuscript Data Availability statement.

## What not to upload

Do not upload the full submission document folder, current manuscript Word files, backup Word files, local browser HTML caches, or writing-planning drafts unless the journal explicitly asks for them.
