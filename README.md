# Real-Time Memory Allocation Tracker

A Python + Tkinter educational desktop simulator for two Operating Systems memory-management techniques:
- **Paging:** fixed-size pages are assigned to available frames; a page table shows process/page/frame mapping.
- **Segmentation:** variable-size contiguous blocks are allocated using the First-Fit strategy; the memory map shows free holes and allocated segments.

> This is a simulator, not a live monitor of the computer's physical RAM. It does not inspect or modify operating-system memory.

## Requirements
- Python 3.9 or newer
- Tkinter (normally included with standard Python installations)

No third-party Python packages are required.

## Run
1. Extract the ZIP.
2. Open a terminal in this folder.
3. Run: `python app.py`

## How to use
1. Open the Paging tab or Segmentation tab.
2. Enter a unique process ID (for example `P1`) and a positive memory size.
3. Select **Allocate** to request memory.
4. Enter the same process ID and choose **Deallocate by ID** to release it.
5. Use **Start Auto Demo** to see allocations and releases happen automatically.
6. Use **Reset Simulation** to clear both models.

## Model assumptions
- Paging has 24 frames and each page/frame represents 4 abstract memory units.
- A process of size `s` needs `ceil(s / 4)` pages.
- Segmentation has 100 abstract memory units.
- Segmentation uses First-Fit: the first free contiguous hole large enough is selected.
- External fragmentation indicator = total free space minus the largest free hole.

## Project structure
- `app.py` — Tkinter user interface, charts, controls, auto-demo and event log.
- `memory_engine.py` — paging and segmentation allocation logic.
- `tests/test_memory_engine.py` — unit tests for allocation and deallocation.
- `flowchart.mmd` — Mermaid flow diagram.
- `project_report.pdf` — report draft aligned to the CSE316 CA3 format.

## Test the core logic
Run: `python -m unittest discover -s tests -v`

## Suggested GitHub revision plan (make real commits as you implement)
1. `Initial project structure and README`
2. `Implement paging allocation engine`
3. `Implement segmentation first-fit engine`
4. `Build Tkinter dashboard and controls`
5. `Add memory visualizations and page table`
6. `Add event log, auto demo and reset`
7. `Add unit tests and final documentation`

Create your own GitHub repository, push your own tested changes, and replace the repository placeholders in the report. Do not claim commits that you have not actually made.
