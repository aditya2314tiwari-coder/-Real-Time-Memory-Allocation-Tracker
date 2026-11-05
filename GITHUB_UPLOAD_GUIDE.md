# Publish this project on GitHub

1. Sign in to GitHub and choose **New repository**.
2. Repository name: `real-time-memory-allocation-tracker`.
3. Choose Public or Private according to your course requirements.
4. Do not initialize with a README, license, or `.gitignore` because these are already included here.
5. Create the repository.
6. Extract this ZIP and open a terminal in the extracted project folder.
7. Run these commands (replace the URL with the URL of your own GitHub repository):

```bash
git init
git add .
git commit -m "Initial project files"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/real-time-memory-allocation-tracker.git
git push -u origin main
```

## Recommended real development revisions

Make these as separate commits while implementing and testing the stages. Do not create commits for work you have not actually completed.

1. `Set up project structure and documentation`
2. `Implement paging allocation and page table`
3. `Implement segmentation with first-fit allocation`
4. `Build Tkinter dashboard and process controls`
5. `Add memory map visualizations and utilization metrics`
6. `Add event log and automatic demonstration`
7. `Add unit tests and finalize project documentation`

## Run locally

```bash
python app.py
```

## Run tests

```bash
python -m unittest discover -s tests -v
```
