use std::collections::HashMap;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

mod artwork;
mod metadata;
mod scanner;

#[pyfunction]
fn backend_version() -> &'static str {
    "0.1.0"
}

#[pyfunction]
fn scan_library(paths: Vec<String>) -> PyResult<Vec<String>> {
    scanner::scan_library(paths).map_err(PyRuntimeError::new_err)
}

#[pyfunction]
fn read_metadata(path: String) -> PyResult<HashMap<String, String>> {
    metadata::read_metadata(path).map_err(PyRuntimeError::new_err)
}

#[pyfunction]
fn write_metadata(path: String, changes: HashMap<String, String>) -> PyResult<Vec<String>> {
    metadata::write_metadata(path, changes).map_err(PyRuntimeError::new_err)
}

#[pyfunction]
fn extract_artwork(path: String) -> PyResult<Option<Vec<u8>>> {
    artwork::extract_artwork(path).map_err(PyRuntimeError::new_err)
}

#[pymodule]
fn rust_back_end_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(backend_version, m)?)?;
    m.add_function(wrap_pyfunction!(scan_library, m)?)?;
    m.add_function(wrap_pyfunction!(read_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(write_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(extract_artwork, m)?)?;
    Ok(())
}
