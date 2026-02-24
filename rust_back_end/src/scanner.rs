use std::path::Path;

use walkdir::WalkDir;

const AUDIO_EXTENSIONS: [&str; 9] = ["mp3", "m4a", "flac", "wav", "ogg", "aac", "opus", "aiff", "wma"];

fn is_audio_file(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| AUDIO_EXTENSIONS.contains(&ext.to_ascii_lowercase().as_str()))
        .unwrap_or(false)
}

pub fn scan_library(paths: Vec<String>) -> Result<Vec<String>, String> {
    if paths.is_empty() {
        return Err("At least one scan path is required.".to_string());
    }

    let mut collected_files: Vec<String> = Vec::new();

    for raw_path in paths {
        let root_path = Path::new(&raw_path);
        if !root_path.exists() {
            continue;
        }

        if root_path.is_file() {
            if is_audio_file(root_path) {
                collected_files.push(root_path.to_string_lossy().into_owned());
            }
            continue;
        }

        for entry in WalkDir::new(root_path)
            .follow_links(true)
            .into_iter()
            .filter_map(Result::ok)
        {
            let entry_path = entry.path();
            if entry.file_type().is_file() && is_audio_file(entry_path) {
                collected_files.push(entry_path.to_string_lossy().into_owned());
            }
        }
    }

    collected_files.sort();
    collected_files.dedup();
    Ok(collected_files)
}
