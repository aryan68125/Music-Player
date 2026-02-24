use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

fn metadata_sidecar_path(audio_path: &Path) -> PathBuf {
    let file_name = audio_path
        .file_name()
        .and_then(|name| name.to_str())
        .unwrap_or("track");
    audio_path.with_file_name(format!("{}.musicmeta.json", file_name))
}

fn candidate_artwork_paths(audio_path: &Path) -> Vec<PathBuf> {
    let mut paths: Vec<PathBuf> = Vec::new();

    if let Some(stem) = audio_path.file_stem().and_then(|value| value.to_str()) {
        let parent = audio_path.parent().unwrap_or_else(|| Path::new("."));
        paths.push(parent.join(format!("{}.jpg", stem)));
        paths.push(parent.join(format!("{}.jpeg", stem)));
        paths.push(parent.join(format!("{}.png", stem)));
        paths.push(parent.join("cover.jpg"));
        paths.push(parent.join("cover.jpeg"));
        paths.push(parent.join("cover.png"));
    }

    if let Ok(contents) = fs::read_to_string(metadata_sidecar_path(audio_path)) {
        if let Ok(parsed) = serde_json::from_str::<HashMap<String, String>>(&contents) {
            if let Some(explicit_artwork_path) = parsed.get("artwork_path") {
                paths.insert(0, PathBuf::from(explicit_artwork_path));
            }
        }
    }

    paths
}

pub fn extract_artwork(path: String) -> Result<Option<Vec<u8>>, String> {
    let audio_path = Path::new(&path);
    if !audio_path.exists() {
        return Err(format!("Track does not exist: {}", path));
    }

    for candidate in candidate_artwork_paths(audio_path) {
        if candidate.exists() && candidate.is_file() {
            match fs::read(candidate) {
                Ok(bytes) => return Ok(Some(bytes)),
                Err(err) => return Err(err.to_string()),
            }
        }
    }

    Ok(None)
}
