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

fn load_sidecar_map(audio_path: &Path) -> HashMap<String, String> {
    let sidecar_path = metadata_sidecar_path(audio_path);
    let content = match fs::read_to_string(sidecar_path) {
        Ok(value) => value,
        Err(_) => return HashMap::new(),
    };

    serde_json::from_str::<HashMap<String, String>>(&content).unwrap_or_default()
}

fn write_sidecar_map(audio_path: &Path, metadata: &HashMap<String, String>) -> Result<(), String> {
    let serialized = serde_json::to_string_pretty(metadata).map_err(|err| err.to_string())?;
    fs::write(metadata_sidecar_path(audio_path), serialized).map_err(|err| err.to_string())
}

pub fn read_metadata(path: String) -> Result<HashMap<String, String>, String> {
    let audio_path = Path::new(&path);
    if !audio_path.exists() {
        return Err(format!("Track does not exist: {}", path));
    }

    let mut metadata = HashMap::new();
    metadata.insert("path".to_string(), path.clone());
    metadata.insert(
        "title".to_string(),
        audio_path
            .file_stem()
            .and_then(|stem| stem.to_str())
            .unwrap_or_default()
            .to_string(),
    );
    metadata.insert("artist".to_string(), String::new());
    metadata.insert("album".to_string(), String::new());
    metadata.insert("duration_ms".to_string(), "0".to_string());

    let sidecar = load_sidecar_map(audio_path);
    for (key, value) in sidecar {
        metadata.insert(key, value);
    }

    Ok(metadata)
}

pub fn write_metadata(path: String, changes: HashMap<String, String>) -> Result<Vec<String>, String> {
    let audio_path = Path::new(&path);
    if !audio_path.exists() {
        return Err(format!("Track does not exist: {}", path));
    }
    if changes.is_empty() {
        return Err("Metadata changes cannot be empty.".to_string());
    }

    let mut merged = load_sidecar_map(audio_path);
    let mut updated_fields: Vec<String> = Vec::new();

    for (key, value) in changes {
        if value.trim().is_empty() {
            merged.remove(&key);
            updated_fields.push(key);
            continue;
        }

        merged.insert(key.clone(), value);
        updated_fields.push(key);
    }

    write_sidecar_map(audio_path, &merged)?;
    updated_fields.sort();
    Ok(updated_fields)
}
