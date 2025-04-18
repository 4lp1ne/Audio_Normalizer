import os
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import json
import re

# === Présets LUFS/TP par plateforme ===
PRESETS = {
    "SoundCloud": {"lufs": -14, "tp": -1.0},
    "Bandcamp": {"lufs": -14, "tp": -1.0},
    "Spotify": {"lufs": -14, "tp": -1.0},
    "YouTube": {"lufs": -14, "tp": -1.0},
    "Apple Music": {"lufs": -16, "tp": -1.0},
    "Ableton Live": {"lufs": -9, "tp": -0.3},
    "DJ Live": {"lufs": -6, "tp": -0.2}
}

def extract_json_from_output(output):
    """Extrait le bloc JSON de l'output de ffmpeg-loudnorm."""
    json_matches = re.findall(r'\{[\s\S]+?\}', output)
    if json_matches:
        return json.loads(json_matches[-1])
    else:
        raise ValueError("Bloc JSON non trouvé dans l'output ffmpeg.")

def get_lufs_level(audio_path):
    """Analyse le LUFS d'un fichier audio via ffmpeg-loudnorm."""
    try:
        cmd = [
            "ffmpeg", "-hide_banner", "-i", audio_path,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
            "-f", "null", "-"
        ]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors='ignore')
        data = extract_json_from_output(result.stderr)
        return float(data["input_i"])
    except Exception as e:
        print(f"Erreur LUFS pour {audio_path} : {e}")
        return None

def show_messagebox_safe(root, kind, title, message):
    """Affiche un message box de façon thread-safe."""
    if kind == "info":
        root.after(0, lambda: messagebox.showinfo(title, message))
    elif kind == "warning":
        root.after(0, lambda: messagebox.showwarning(title, message))
    elif kind == "error":
        root.after(0, lambda: messagebox.showerror(title, message))

def traiter_audio(dossier_entree, dossier_sortie, progress_bar, label_status, root, format_sortie, lufs_cible, tp_cible, premaster_flag):
    try:
        fichiers = [f for f in os.listdir(dossier_entree) if f.lower().endswith((".mp3", ".wav", ".flac", ".m4a", ".aac"))]
        total = len(fichiers)
        if total == 0:
            show_messagebox_safe(root, "warning", "Aucun fichier", "Aucun fichier audio valide trouvé.")
            return
        os.makedirs(dossier_sortie, exist_ok=True)
        for i, fichier in enumerate(fichiers):
            label_status.config(text=f"🔄 Traitement : {fichier}")
            label_status.update()
            try:
                chemin_entree = os.path.join(dossier_entree, fichier)
                nom_sans_ext = os.path.splitext(fichier)[0]
                chemin_temp = os.path.join(dossier_sortie, f"{nom_sans_ext}_temp.wav")
                chemin_sortie = os.path.join(dossier_sortie, f"{nom_sans_ext}_final.{format_sortie}")

                lufs_initial = get_lufs_level(chemin_entree)
                if lufs_initial is None:
                    raise RuntimeError("Impossible de mesurer le LUFS initial.")

                # Gain pour atteindre le LUFS cible
                gain_temp = lufs_cible - lufs_initial
                audio_pre = AudioSegment.from_file(chemin_entree)
                audio_pre = audio_pre.apply_gain(gain_temp)
                audio_pre.export(chemin_temp, format="wav")

                # Normalisation avec ffmpeg-normalize
                subprocess.run([
                    "ffmpeg-normalize", chemin_temp,
                    "-o", chemin_temp,
                    "--force",
                    "--normalization-type", "ebu",
                    "-t", str(lufs_cible),
                    "-tp", str(tp_cible),
                    "--sample-rate", "44100",
                    "--audio-codec", "pcm_s16le"
                ], check=True)

                # Limitation des crêtes (True Peak)
                audio = AudioSegment.from_wav(chemin_temp)
                peak = audio.max_dBFS
                if peak > tp_cible:
                    audio = audio.apply_gain(tp_cible - peak)

                # Option pré-master
                if premaster_flag:
                    audio = audio.apply_gain(-6.0)

                # Export final
                audio.export(chemin_sortie, format=format_sortie)
                os.remove(chemin_temp)
            except Exception as e:
                show_messagebox_safe(root, "warning", "Erreur fichier", f"Erreur lors du traitement de {fichier} : {e}")
            finally:
                # Mise à jour de la progression
                progress_bar["value"] = (i + 1) / total * 100
                progress_bar.update()
        label_status.config(text="✅ Terminé !")
        show_messagebox_safe(root, "info", "Succès", "Normalisation LUFS et limitation True Peak terminées.")
    except Exception as e:
        show_messagebox_safe(root, "error", "Erreur", str(e))
        label_status.config(text="❌ Erreur")

def lancer_interface():
    root = tk.Tk()
    root.title("🎵 LUFS Normalizer + True Peak Limiter")
    root.geometry("800x600")
    root.resizable(False, False)

    # Variables
    entree_var = tk.StringVar()
    sortie_var = tk.StringVar()
    format_var = tk.StringVar(value="wav")
    premaster_var = tk.BooleanVar()
    preset_var = tk.StringVar(value="")  # Pour les presets

    # Interface dossiers
    tk.Label(root, text="🎵 Dossier source :").grid(row=0, column=0, sticky="e", padx=10, pady=10)
    tk.Entry(root, textvariable=entree_var, width=50).grid(row=0, column=1)
    tk.Button(root, text="Parcourir", command=lambda: browse(entree_var)).grid(row=0, column=2)
    tk.Label(root, text="💾 Dossier de sortie :").grid(row=1, column=0, sticky="e", padx=10, pady=10)
    tk.Entry(root, textvariable=sortie_var, width=50).grid(row=1, column=1)
    tk.Button(root, text="Parcourir", command=lambda: browse(sortie_var)).grid(row=1, column=2)

    # Format de sortie
    tk.Label(root, text="📁 Format de sortie :").grid(row=2, column=0, sticky="e", padx=10, pady=10)
    tk.OptionMenu(root, format_var, "wav", "mp3", "flac").grid(row=2, column=1, sticky="w")

    # Presets plateformes
    presets_label_row = 3
    tk.Label(root, text="🎯 Choisir une plateforme :").grid(row=presets_label_row, column=0, sticky="ne", padx=10)
    for idx, nom in enumerate(PRESETS):
        tk.Radiobutton(root, text=nom, variable=preset_var, value=nom).grid(row=presets_label_row+1+idx, column=1, sticky="w")

    # Faders et options
    base_row = presets_label_row + 1 + len(PRESETS)
    tk.Label(root, text="🎛️ LUFS personnalisé :").grid(row=base_row, column=0, sticky="e", padx=10, pady=10)
    lufs_fader = tk.Scale(root, from_=-30, to=0, resolution=0.5, orient=tk.HORIZONTAL, length=200)
    lufs_fader.set(-14)
    lufs_fader.grid(row=base_row, column=1, sticky="w")
    tk.Label(root, text="🎚️ True Peak cible :").grid(row=base_row+1, column=0, sticky="e", padx=10, pady=10)
    tp_fader = tk.Scale(root, from_=-3.0, to=0.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
    tp_fader.set(-1.0)
    tp_fader.grid(row=base_row+1, column=1, sticky="w")
    tk.Label(root, text="ℹ️ Utilisez les faders si aucune plateforme n'est sélectionnée.").grid(row=base_row+2, column=1, sticky="w")
    tk.Label(root, text="   LUFS conseillé : -14 streaming, -6 à -9 DJ/Live. True Peak : -1 dBTP.").grid(row=base_row+3, column=1, sticky="w")
    tk.Checkbutton(root, text="🎚️ Pré-master à -6 dB", variable=premaster_var).grid(row=base_row+4, column=1, sticky="w", pady=(10,0))

    # Barre de progression et statut
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
    progress_bar.grid(row=base_row+5, column=0, columnspan=3, pady=5)
    status_label = tk.Label(root, text="En attente...", fg="blue")
    status_label.grid(row=base_row+6, column=0, columnspan=3, pady=5)

    # Bouton lancer
    tk.Button(
        root, text="Lancer le traitement",
        command=lambda: start_processing(
            entree_var, sortie_var, format_var, lufs_fader, tp_fader,
            premaster_var, preset_var, progress_bar, status_label, root
        ),
        bg="#007ACC", fg="white"
    ).grid(row=base_row+7, column=1, pady=15)

    root.mainloop()

def browse(var):
    folder = filedialog.askdirectory()
    if folder:
        var.set(folder)

def get_preset_values(preset_name, lufs_slider, tp_slider):
    if preset_name and preset_name in PRESETS:
        return PRESETS[preset_name]
    else:
        return {"lufs": float(lufs_slider.get()), "tp": float(tp_slider.get())}

def start_processing(entree_var, sortie_var, format_var, lufs_fader, tp_fader, premaster_var, preset_var, progress_bar, status_label, root):
    if not entree_var.get() or not sortie_var.get():
        show_messagebox_safe(root, "warning", "Champs requis", "Merci de sélectionner les deux dossiers.")
        return
    preset = get_preset_values(preset_var.get(), lufs_fader, tp_fader)
    threading.Thread(
        target=traiter_audio,
        args=(
            entree_var.get(), sortie_var.get(), progress_bar, status_label, root,
            format_var.get(), preset["lufs"], preset["tp"], premaster_var.get()
        ),
        daemon=True
    ).start()

if __name__ == "__main__":
    lancer_interface()
