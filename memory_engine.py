"""Core simulation engine for the Real-Time Memory Allocation Tracker.

This is an educational simulator. It models paging and segmentation; it does
not inspect or modify the host operating system's actual memory.
"""
from dataclasses import dataclass
from math import ceil


@dataclass
class Page:
    process_id: str
    page_number: int
    frame_number: int


class PagingManager:
    def __init__(self, frame_count=24, page_size=4):
        self.frame_count = frame_count
        self.page_size = page_size  # abstract memory units per page
        self.frames = [None] * frame_count
        self.process_pages = {}
        self.events = []

    def allocate(self, process_id, size):
        process_id = process_id.strip()
        if not process_id or size <= 0:
            return False, "Enter a process ID and a size greater than zero."
        if process_id in self.process_pages:
            return False, f"Process {process_id} already exists in paging."
        needed = ceil(size / self.page_size)
        free = [i for i, value in enumerate(self.frames) if value is None]
        if needed > len(free):
            return False, f"Not enough free frames: need {needed}, available {len(free)}."
        selected = free[:needed]
        pages = []
        for page_no, frame_no in enumerate(selected):
            page = Page(process_id, page_no, frame_no)
            self.frames[frame_no] = page
            pages.append(frame_no)
        self.process_pages[process_id] = {"size": size, "frames": pages, "pages": needed}
        self.events.append(f"Allocated {process_id}: {size} units -> {needed} page(s).")
        return True, f"Allocated {process_id} in {needed} page(s)."

    def deallocate(self, process_id):
        process_id = process_id.strip()
        record = self.process_pages.pop(process_id, None)
        if record is None:
            return False, f"Process {process_id or '(blank)'} was not found."
        for frame_no in record["frames"]:
            self.frames[frame_no] = None
        self.events.append(f"Deallocated {process_id}; released {len(record['frames'])} frame(s).")
        return True, f"Deallocated {process_id}."

    @property
    def used_frames(self):
        return sum(frame is not None for frame in self.frames)

    @property
    def free_frames(self):
        return self.frame_count - self.used_frames

    @property
    def utilization(self):
        return (self.used_frames / self.frame_count) * 100

    def page_table_rows(self):
        rows = []
        for pid in sorted(self.process_pages):
            for page_no, frame_no in enumerate(self.process_pages[pid]["frames"]):
                rows.append((pid, page_no, frame_no))
        return rows


class SegmentationManager:
    def __init__(self, total_size=100):
        self.total_size = total_size
        self.segments = []  # sorted allocated blocks: {pid, start, size}
        self.processes = {}
        self.events = []

    def holes(self):
        holes = []
        cursor = 0
        for block in sorted(self.segments, key=lambda item: item["start"]):
            if block["start"] > cursor:
                holes.append({"start": cursor, "size": block["start"] - cursor})
            cursor = block["start"] + block["size"]
        if cursor < self.total_size:
            holes.append({"start": cursor, "size": self.total_size - cursor})
        return holes

    def allocate(self, process_id, size):
        process_id = process_id.strip()
        if not process_id or size <= 0:
            return False, "Enter a process ID and a size greater than zero."
        if process_id in self.processes:
            return False, f"Process {process_id} already exists in segmentation."
        for hole in self.holes():  # First-fit allocation
            if hole["size"] >= size:
                block = {"pid": process_id, "start": hole["start"], "size": size}
                self.segments.append(block)
                self.segments.sort(key=lambda item: item["start"])
                self.processes[process_id] = block
                self.events.append(
                    f"Allocated {process_id}: {size} units at address {block['start']} (first fit)."
                )
                return True, f"Allocated {process_id} at address {block['start']}."
        largest = max((hole["size"] for hole in self.holes()), default=0)
        return False, f"No contiguous hole of {size} units. Largest free hole: {largest}."

    def deallocate(self, process_id):
        process_id = process_id.strip()
        block = self.processes.pop(process_id, None)
        if block is None:
            return False, f"Process {process_id or '(blank)'} was not found."
        self.segments.remove(block)
        self.events.append(f"Deallocated {process_id}; released {block['size']} units.")
        return True, f"Deallocated {process_id}."

    @property
    def used_size(self):
        return sum(block["size"] for block in self.segments)

    @property
    def free_size(self):
        return self.total_size - self.used_size

    @property
    def utilization(self):
        return (self.used_size / self.total_size) * 100

    @property
    def external_fragmentation(self):
        holes = self.holes()
        if not holes:
            return 0
        return sum(hole["size"] for hole in holes) - max(hole["size"] for hole in holes)
