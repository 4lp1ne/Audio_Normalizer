import os
import shutil
from pydub import AudioSegment
from tkinter import filedialog, Tk, StringVar, BooleanVar, Label, Entry, Button, Checkbutton, OptionMenu, Toplevel, messagebox
import tkinter as tk
import zipfile

# === Categorized folders ===
CATEGORIES = {
    "kick": [-12, -1.0],
    "bass": [-9, -1.0],
    "lead": [-10, -1.0],
    "atmo": [-20, -1.0],
    "fx": [-18, -1.0],
    "vocal": [-16, -1.0],
    "drum": [-12, -1.0],
    "perc": [-14, -1.0],
    "zap": [-15, -1.0],
    "noise": [-20, -1.0],
    "ambience": [-22, -1.0],
    "synth": [-14, -1.0]
}

# === Simple normalization using pydub ===
def normalize_sample(filepath, outpath, lufs_target, tp_limit, output_format):
    try:
        audio = AudioSegment.from_file(filepath)
        gain_needed = lufs_target - audio.dBFS
        audio = audio.apply_gain(gain_needed)

        if audio.max_dBFS > tp_limit:
            reduction = tp_limit - audio.max_dBFS
            audio = audio.apply_gain(reduction)

        audio.export(outpath, format=output_format)
    except Exception as e:
        print(f"Error processing {filepath}:", e)

# === Process by selected category ===
def process_samples_by_selected_categories(category_dirs, dest_dir, output_format):
    os.makedirs(dest_dir, exist_ok=True)

    for category, source_dir in category_dirs.items():
        if not source_dir or not os.path.isdir(source_dir):
            continue

        lufs, tp = CATEGORIES[category]
        out_subdir = os.path.join(dest_dir, category)
        os.makedirs(out_subdir, exist_ok=True)

        for filename in os.listdir(source_dir):
            if not filename.lower().endswith((".wav", ".flac", ".mp3")):
                continue

            input_path = os.path.join(source_dir, filename)
            output_path = os.path.join(out_subdir, os.path.splitext(filename)[0] + f".{output_format}")
            normalize_sample(input_path, output_path, lufs, tp, output_format)
            print(f"✅ {filename} → {category} ({lufs} LUFS, TP {tp})")

# === GUI ===
def launch_interface():
    def browse_path(var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def start():
        destination = output_var.get()
        if not destination:
            messagebox.showwarning("Missing info", "Please choose an output folder.")
            return

        selected_dirs = {cat: path.get() for cat, (enabled, path) in selections.items() if enabled.get()}

        if not selected_dirs:
            messagebox.showwarning("No category", "Select at least one category with a folder.")
            return

        process_samples_by_selected_categories(selected_dirs, destination, format_var.get())

        if zip_var.get():
            zip_path = destination + ".zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root_dir, _, files in os.walk(destination):
                    for file in files:
                        full_path = os.path.join(root_dir, file)
                        arcname = os.path.relpath(full_path, destination)
                        zipf.write(full_path, arcname)
            print(f"📦 Archive created: {zip_path}")

        status_label.config(text="✅ Processing complete")

    root = tk.Tk()
    root.title("🎶 Sample Normalizer by Instrument")
    root.geometry("700x600")

    selections = {}
    output_var = StringVar()
    zip_var = BooleanVar()
    format_var = StringVar(value="wav")

    row = 0
    Label(root, text="🎯 Select the categories to process:").grid(row=row, column=0, columnspan=3, pady=10)
    row += 1

    for category in CATEGORIES.keys():
        enabled = BooleanVar()
        path_var = StringVar()
        selections[category] = (enabled, path_var)

        Checkbutton(root, text=category, variable=enabled).grid(row=row, column=0, sticky="w", padx=10)
        Entry(root, textvariable=path_var, width=40).grid(row=row, column=1)
        Button(root, text="Browse", command=lambda v=path_var: browse_path(v)).grid(row=row, column=2)
        row += 1

    Label(root, text="📤 Output folder:").grid(row=row, column=0, sticky="e", padx=10, pady=10)
    Entry(root, textvariable=output_var, width=40).grid(row=row, column=1)
    Button(root, text="Browse", command=lambda: browse_path(output_var)).grid(row=row, column=2)
    row += 1

    Label(root, text="💾 Output format:").grid(row=row, column=0, sticky="e", padx=10)
    OptionMenu(root, format_var, "wav", "flac", "mp3").grid(row=row, column=1, sticky="w")
    row += 1

    Checkbutton(root, text="📦 Create ZIP archive after processing", variable=zip_var).grid(row=row, column=1, sticky="w")
    row += 1

    Button(root, text="Start Processing", command=start, bg="#4CAF50", fg="white").grid(row=row, column=1, pady=15)
    row += 1

    status_label = Label(root, text="Waiting...", fg="blue")
    status_label.grid(row=row, column=0, columnspan=3)

    root.mainloop()

if __name__ == "__main__":
    launch_interface()