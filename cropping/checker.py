import os
import json
from pathlib import Path
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk

FIXED_OPTIONS_FOLDER = "fixed_options"
SAVED_FOLDER = "saved"
SKIPPED_FILE = "skipped.json"
SELECTIONS_FILE = "selections.json"

fixed_path = Path(FIXED_OPTIONS_FOLDER)
saved_path = Path(SAVED_FOLDER)
saved_path.mkdir(parents=True, exist_ok=True)

# Load skipped list
skipped = []
if Path(SKIPPED_FILE).exists():
    with open(SKIPPED_FILE, "r") as f:
        skipped = json.load(f)

# Load selections log
selections = {}
if Path(SELECTIONS_FILE).exists():
    with open(SELECTIONS_FILE, "r") as f:
        selections = json.load(f)


def save_skipped():
    with open(SKIPPED_FILE, "w") as f:
        json.dump(skipped, f, indent=2)


def save_selections():
    with open(SELECTIONS_FILE, "w") as f:
        json.dump(selections, f, indent=2)


def get_already_processed():
    """Get list of images already saved or skipped."""
    saved_stems = {p.stem for p in saved_path.glob("*.jpg")}
    saved_stems.update(p.stem for p in saved_path.glob("*.JPG"))
    skipped_set = set(skipped)
    return saved_stems | skipped_set


class ImageChecker:
    def __init__(self, root, to_process):
        self.root = root
        self.to_process = to_process
        self.current_idx = 0
        self.current_images = []
        self.image_labels = []
        self.current_image_name = ""

        self.root.title("Image Checker")
        self.root.configure(bg="#1e1e1e")

        # Header
        self.header_label = Label(
            root,
            text="",
            font=("Arial", 14, "bold"),
            bg="#1e1e1e",
            fg="white"
        )
        self.header_label.pack(pady=10)

        # Progress label
        self.progress_label = Label(
            root,
            text="",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#888888"
        )
        self.progress_label.pack()

        # Instructions
        self.instructions_label = Label(
            root,
            text="Click on an image to save it, or use Skip/Quit buttons",
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#aaaaaa"
        )
        self.instructions_label.pack(pady=5)

        # Image grid frame
        self.grid_frame = Frame(root, bg="#1e1e1e")
        self.grid_frame.pack(padx=20, pady=10, expand=True, fill="both")

        # Button frame
        self.button_frame = Frame(root, bg="#1e1e1e")
        self.button_frame.pack(pady=15)

        self.skip_btn = Button(
            self.button_frame,
            text="Skip (S)",
            command=self.skip_image,
            font=("Arial", 12),
            bg="#444444",
            fg="white",
            width=15,
            height=2
        )
        self.skip_btn.pack(side="left", padx=10)

        self.quit_btn = Button(
            self.button_frame,
            text="Quit (Q)",
            command=self.quit_app,
            font=("Arial", 12),
            bg="#662222",
            fg="white",
            width=15,
            height=2
        )
        self.quit_btn.pack(side="left", padx=10)

        # Keyboard bindings
        self.root.bind("<s>", lambda e: self.skip_image())
        self.root.bind("<S>", lambda e: self.skip_image())
        self.root.bind("<q>", lambda e: self.quit_app())
        self.root.bind("<Q>", lambda e: self.quit_app())
        self.root.bind("<Escape>", lambda e: self.quit_app())

        # Load first image
        self.load_current_image()

    def load_current_image(self):
        # Clear previous images
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.image_labels = []
        self.current_images = []

        if self.current_idx >= len(self.to_process):
            self.show_done()
            return

        folder = self.to_process[self.current_idx]
        self.current_image_name = folder.name

        self.header_label.config(text=f"Image: {self.current_image_name}")
        self.progress_label.config(
            text=f"Progress: {self.current_idx + 1} / {len(self.to_process)}"
        )

        # Load original
        original_path = folder / "original.jpg"
        if not original_path.exists():
            print(f"No original found for {self.current_image_name}, skipping")
            self.current_idx += 1
            self.load_current_image()
            return

        # Collect all images
        all_images = []

        # Original first
        all_images.append(("ORIGINAL", original_path))

        # Then all options
        for opt_file in sorted(folder.glob("*.jpg")):
            if opt_file.name != "original.jpg":
                all_images.append((opt_file.stem.upper(), opt_file))

        # Calculate grid layout
        n = len(all_images)
        cols = min(4, n)
        rows = (n + cols - 1) // cols

        # Calculate thumbnail size based on screen
        screen_w = self.root.winfo_screenwidth() - 100
        screen_h = self.root.winfo_screenheight() - 300

        thumb_w = screen_w // cols
        thumb_h = screen_h // rows
        max_thumb = min(thumb_w, thumb_h, 400)

        # Create image grid
        for idx, (name, path) in enumerate(all_images):
            row = idx // cols
            col = idx % cols

            # Load and resize image
            try:
                img = Image.open(path)
                img.thumbnail((max_thumb - 20, max_thumb - 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                self.current_images.append((name, path, img))

                # Create frame for image + label
                frame = Frame(self.grid_frame, bg="#2a2a2a", padx=5, pady=5)
                frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

                # Image label
                img_label = Label(frame, image=photo, bg="#2a2a2a", cursor="hand2")
                img_label.image = photo
                img_label.pack()

                # Bind click
                img_label.bind("<Button-1>", lambda e, p=path, n=name: self.select_image(p, n))

                # Text label
                text_label = Label(
                    frame,
                    text=name,
                    font=("Arial", 10, "bold"),
                    bg="#2a2a2a",
                    fg="white"
                )
                text_label.pack(pady=5)
                text_label.bind("<Button-1>", lambda e, p=path, n=name: self.select_image(p, n))

                self.image_labels.append(img_label)

            except Exception as e:
                print(f"Error loading {path}: {e}")

        # Configure grid weights for centering
        for i in range(cols):
            self.grid_frame.columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_frame.rowconfigure(i, weight=1)

    def select_image(self, path, name):
        """Save the selected image."""
        save_file = saved_path / f"{self.current_image_name}.jpg"

        # Copy the image
        img = Image.open(path)
        img.save(save_file, "JPEG", quality=95)

        # Log the selection
        selections[self.current_image_name] = {
            "method": name.lower(),
            "source_file": str(path)
        }
        save_selections()

        print(f"Saved: {self.current_image_name} ({name})")

        self.current_idx += 1
        self.load_current_image()

    def skip_image(self):
        """Skip current image."""
        skipped.append(self.current_image_name)
        save_skipped()
        print(f"Skipped: {self.current_image_name}")

        self.current_idx += 1
        self.load_current_image()

    def quit_app(self):
        """Save progress and quit."""
        save_skipped()
        save_selections()
        print("\nProgress saved!")
        print(f"Saved: {len(list(saved_path.glob('*.jpg')))} images")
        print(f"Skipped: {len(skipped)} images")
        self.root.quit()
        self.root.destroy()

    def show_done(self):
        """Show completion message."""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.header_label.config(text="All Done!")
        self.progress_label.config(text="")

        done_label = Label(
            self.grid_frame,
            text=f"✓ All images have been processed!\n\n"
                 f"Saved: {len(list(saved_path.glob('*.jpg')))} images\n"
                 f"Skipped: {len(skipped)} images",
            font=("Arial", 16),
            bg="#1e1e1e",
            fg="#44aa44",
            justify="center"
        )
        done_label.pack(expand=True, pady=50)

        self.skip_btn.config(state="disabled")


def main():
    processed = get_already_processed()

    # Get all image folders
    image_folders = [f for f in fixed_path.iterdir() if f.is_dir()]
    image_folders.sort()

    # Filter out already processed
    to_process = [f for f in image_folders if f.name not in processed]

    print(f"Total images: {len(image_folders)}")
    print(f"Already processed: {len(processed)}")
    print(f"Remaining: {len(to_process)}")

    if not to_process:
        print("\nAll images have been processed!")
        return

    print("\nStarting review...")
    print("Click on an image to save it, or press S to skip, Q to quit\n")

    root = Tk()
    root.state("zoomed")

    app = ImageChecker(root, to_process)
    root.mainloop()


if __name__ == "__main__":
    main()